"""Isolated frozen conditional solve. Called only by the authorized batch runner."""

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter

import cvxpy as cp
import numpy as np

from phase1d_model import ROOT
from run_phase1d_registered import conditional_bounds
from confirmatory_inputs import install_outcome_firewall
sys.path.insert(0, str(ROOT / "code"))
from decoding_sdp import _feasible_povm, density


def fullspace(states, p, config, archive):
    """Original uncompressed primal/dual formulation with archived operators."""
    q = p / p.sum()
    d, m = states.shape[1], len(p)
    rhos = [density(s) for s in states]
    effects = [cp.Variable((d, d), hermitian=True) for _ in p]
    problem = cp.Problem(cp.Maximize(cp.real(sum(q[i] * cp.trace(effects[i] @ rhos[i]) for i in range(m)))),
                         [e >> 0 for e in effects] + [sum(effects) == np.eye(d)])
    problem.solve(solver=config["solver"], eps=config["eps"], max_iters=config["max_iters"], verbose=False)
    if any(e.value is None for e in effects):
        raise RuntimeError("Full-space primal unavailable")
    repaired = _feasible_povm([e.value for e in effects], max(1e-10, config["eps"] * 1e-2))
    y = cp.Variable((d, d), hermitian=True)
    dual = cp.Problem(cp.Minimize(cp.real(cp.trace(y))), [y - q[i] * rhos[i] >> 0 for i in range(m)])
    dual.solve(solver=config["solver"], eps=config["eps"], max_iters=config["max_iters"], verbose=False)
    if y.value is None:
        raise RuntimeError("Full-space dual unavailable")
    matrix = (y.value + y.value.conj().T) / 2
    slack = min(float(np.linalg.eigvalsh(matrix - q[i] * rhos[i]).min()) for i in range(m))
    matrix += (max(0, -slack) + max(1e-10, config["eps"] * 1e-2)) * np.eye(d)
    archive["X_g0_effects"], archive["X_g0_dual"] = np.asarray(repaired), matrix
    if problem.status not in config["accepted_statuses"] or dual.status not in config["accepted_statuses"]:
        raise RuntimeError(f"Unaccepted full-space statuses {problem.status}/{dual.status}")


def inspect(states, q, archive, config):
    effects, y = archive["X_g0_effects"], archive["X_g0_dual"]
    d, m = states.shape[1], len(q)
    rhos = [density(s) for s in states]
    error = float(np.linalg.norm(sum(effects) - np.eye(d), ord=2))
    psd = max(0., -min(float(np.linalg.eigvalsh(e).min()) for e in effects))
    slack = max(0., -min(float(np.linalg.eigvalsh(y - q[i] * rhos[i]).min()) for i in range(m)))
    lower = float(np.real(sum(q[i] * np.trace(effects[i] @ rhos[i]) for i in range(m))))
    upper = float(np.trace(y).real)
    herm = max(float(np.linalg.norm(x - x.conj().T)) for x in [*effects, y])
    pr = max(float(np.linalg.norm(sum(effects) - np.eye(d))), psd, herm)
    finite = all(np.isfinite(x) for x in (lower, upper, error, psd, slack, pr))
    if not finite or max(pr, slack) > config["feasibility_tolerance"] or lower > upper + 1e-8:
        raise RuntimeError("Ambient certificate feasibility/weak-duality check failed")
    return {"lower": lower, "upper": upper,
            "safe_lower": lower / (1 + error + m * (psd + 1e-10)),
            "safe_upper": upper + d * (slack + 1e-10),
            "primal_residual": pr, "dual_residual": max(slack, herm),
            "hermiticity_residual": herm, "completeness_operator_norm": error,
            "effect_psd_violation": psd, "dual_slack_violation": slack,
            "conditional_prior": q.tolist(), "valid": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--fullspace", action="store_true")
    parser.add_argument("--authorized-worker", action="store_true", required=True)
    args = parser.parse_args()
    registry = json.loads((ROOT / "CONFIRMATORY_REGISTRY_FROZEN.json").read_text())
    config = registry["sdp"]
    install_outcome_firewall(ROOT)
    archive, stats, result = {}, [], {}
    original_solve = cp.Problem.solve

    def logged_solve(problem, *a, **kw):
        start = perf_counter()
        try:
            return original_solve(problem, *a, **kw)
        finally:
            s = problem.solver_stats
            stats.append({"status": problem.status, "wall_seconds": perf_counter() - start,
                          "solve_time": getattr(s, "solve_time", None),
                          "setup_time": getattr(s, "setup_time", None),
                          "iterations": getattr(s, "num_iters", None),
                          "extra_stats": getattr(s, "extra_stats", None)})

    cp.Problem.solve = logged_solve
    try:
        with np.load(args.input, allow_pickle=False) as data:
            states, q = data["states"], data["q"]
        if abs(float(q.sum()) - 1) > config["aggregation_tolerance"]:
            raise ValueError("Conditional prior normalization failed")
        if args.fullspace and len(q) > 1:
            fullspace(states, q, config, archive)
        else:
            conditional_bounds(states, q, [list(range(len(q)))], "X", config, archive)
        result = inspect(states, q, archive, config)
    except Exception as exc:
        result = {"valid": False, "error": f"{type(exc).__name__}: {exc}"}
    finally:
        cp.Problem.solve = original_solve
        result["solver_stats"] = stats
        target = Path(args.output)
        np.savez_compressed(target.with_suffix(".npz"), **archive)
        target.with_suffix(".json").write_text(json.dumps(result, indent=2,
            default=lambda x: x.tolist() if isinstance(x, np.ndarray) else str(x)) + "\n")


if __name__ == "__main__":
    main()
