"""Read stored certificates and generate prior-only drafts; never invoke a solver."""

import ast
import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "audit_phase2_5"
sys.path.insert(0, str(ROOT / "code"))
from huffman_support import huffman_lengths, source_probabilities


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phash(p):
    return hashlib.sha256(np.asarray(p, dtype="<f8").tobytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=True)
    registry = json.loads((ROOT / "PHASE_1D_REGISTRY.json").read_text())
    manifest = json.loads((ROOT / "data/phase1d_run_manifest.json").read_text())
    assert digest(ROOT / "PHASE_1D_REGISTRY.json") == manifest["registry_sha256"]
    for file, h in registry["file_sha256"].items():
        assert digest(ROOT / file) == h
    frame = pd.read_csv(ROOT / "data/phase1d_registered_results.csv")
    assert digest(ROOT / "data/phase1d_registered_results.csv") == manifest["results_sha256"]
    assert digest(ROOT / "data/phase1d_pre_sdp_diagnostics.csv") == manifest["pre_sdp_diagnostics_sha256"]
    assert len(frame) == 220 and frame.row_id.is_unique
    sources = {}
    for rec in manifest["sources"]:
        assert digest(ROOT / rec["file"]) == rec["sha256"]
        sources[rec["source_id"]] = np.load(ROOT / rec["file"])
        a = sources[rec["source_id"]]
        p = a["p"]
        for arm in ("H", "F"):
            d = a[arm+"_states"].shape[1]
            reconstructed = np.zeros_like(a[arm+"_states"])
            cursor = 0
            supports = [None]*len(p)
            for i in np.argsort(-p):
                b = 2**(int(np.log2(d))-int(a[arm+"_lengths"][i]))
                support = np.unique((cursor+np.arange(b)) % d)
                supports[i] = support.tolist()
                theta = 2*np.pi*(i+1)*(np.arange(b)+1)/(b+1)
                reconstructed[i,support] = np.exp(1j*theta)/np.sqrt(b)
                cursor = (cursor+max(1,b//2)) % d
            assert supports == rec[arm+"_supports"]
            assert np.max(abs(reconstructed-a[arm+"_states"])) < 1e-13
    records = {r["row_id"]: r for r in manifest["rows"]}
    rows = []
    norm_error = herm_error = 0.0
    min_effect = min_slack = float("inf")
    sets = 0
    for row in frame.itertuples(index=False):
        assert row.certificate_status == "PASS"
        source = sources[row.source_id]
        p = source["p"]
        assert phash(p) == row.source_hash and np.all(p > 0)
        assert abs(p.sum() - 1) < 1e-12
        assert np.array_equal(huffman_lengths(p), source["H_lengths"])
        assert abs(p @ source["H_lengths"] - row.Lbar_H) < 1e-12
        assert np.all(source["F_lengths"] == row.n_fix)
        groups = json.loads(row.partition)
        assert len(groups) == row.G and all(groups)
        assert sorted(i for g in groups for i in g) == list(range(row.M))
        assert row.C_A == int(np.ceil(np.log2(row.G)))
        # Reconstruct G2 from priors alone, independent of the implementation helper.
        if row.group_rule == "G2":
            test = [[] for _ in range(row.G)]
            masses = np.zeros(row.G)
            for i in sorted(range(row.M), key=lambda i: (-p[i], i)):
                g = min(range(row.G), key=lambda g: (masses[g], g))
                test[g].append(i)
                masses[g] += p[i]
            assert groups == [sorted(g) for g in test]
        record = records[row.row_id]
        for key in ("operators", "details"):
            assert digest(ROOT / record[key]) == record[key + "_sha256"]
        operators = np.load(ROOT / record["operators"])
        values, conservative = {}, {}
        nontrivial = {}
        for arm in ("H", "F"):
            states = source[arm + "_states"]
            d = states.shape[1]
            assert states.shape == (row.M, 2**row.n_max)
            norm_error = max(norm_error, float(abs(np.linalg.norm(states, axis=1)**2 - 1).max()))
            low = high = safe_low = safe_high = 0.0
            nt = []
            for g, members in enumerate(groups):
                pg = p[members].sum()
                q = p[members] / pg
                assert abs(q.sum() - 1) < 1e-12
                E = operators[f"{arm}_g{g}_effects"]
                Y = operators[f"{arm}_g{g}_dual"]
                herm_error = max(herm_error, float(np.linalg.norm(Y-Y.conj().T)),
                                 max(float(np.linalg.norm(e-e.conj().T)) for e in E))
                e = np.linalg.norm(E.sum(axis=0) - np.eye(d), ord=2)
                mine = min(np.linalg.eigvalsh(x).min() for x in E)
                slacks = [np.linalg.eigvalsh(Y-q[j]*np.outer(states[i], states[i].conj())).min()
                          for j, i in enumerate(members)]
                mins = min(slacks)
                min_effect = min(min_effect, float(mine))
                min_slack = min(min_slack, float(mins))
                assert e < 1e-7 and mine > -1e-7 and mins > -1e-7
                lg = float(sum(q[j]*np.vdot(states[i], E[j] @ states[i]).real
                               for j, i in enumerate(members)))
                ug = float(np.trace(Y).real)
                low += pg*lg
                high += pg*ug
                # An algebraic sensitivity envelope, not an interval-certified error bound.
                delta = max(0.0, -float(mine)) + 1e-10
                gamma = max(0.0, -float(mins)) + 1e-10
                safe_low += pg*lg/(1+e+len(members)*delta)
                safe_high += pg*(ug+d*gamma)
                gram = states[members].conj() @ states[members].T
                off = np.abs(gram[np.triu_indices(len(members), 1)])
                nt.append(bool(len(off) and off.max() > 1e-10))
                sets += 1
            values[arm] = (low, high)
            conservative[arm] = (safe_low, safe_high)
            nontrivial[arm] = nt
        gap = values["H"][0] - values["F"][1]
        safe_gap = conservative["H"][0] - conservative["F"][1]
        assert abs(gap-row.delta_pair) < 1e-12
        assert abs(values["H"][0]-row.P_H_primal_lower) < 1e-12
        assert abs(values["F"][1]-row.P_F_dual_upper) < 1e-12
        multi = [j for j,g in enumerate(groups) if len(g)>1]
        assert bool(multi) and all(nontrivial["H"][g] and nontrivial["F"][g] for g in multi) == row.matched_E2
        assert any(a and b for a,b in zip(nontrivial["H"],nontrivial["F"])) == row.matched_E1
        assert (not any(nontrivial["F"])) == row.fixed_trivial_after_grouping
        assert (gap > .0005) == row.robust_positive
        rows.append({"row_id":row.row_id, "gap":gap, "sensitivity_gap":safe_gap,
                     "envelope":gap-safe_gap, "status":"PASS"})
    pd.DataFrame(rows).to_csv(OUT / "stored_certificate_recheck.csv", index=False)
    full = pd.read_csv(ROOT / "data/phase1d_fullspace_crosscheck.csv")
    repeat = pd.read_csv(ROOT / "data/phase1d_robust_replication.csv")
    verify = json.loads((ROOT / "data/phase1d_fullspace_verification.json").read_text())
    assert digest(ROOT / "data/phase1d_fullspace_crosscheck.csv") == verify["output_sha256"]
    verify2 = json.loads((ROOT / "data/phase1d_verification.json").read_text())
    assert digest(ROOT / "data/phase1d_robust_replication.csv") == verify2["replication_sha256"]
    assert set(full.row_id) == set(repeat.row_id) == set(frame.loc[frame.robust_positive,"row_id"])
    assert full.robust_positive_confirmed.all() and repeat.robust_positive_reproduced.all()
    assert np.allclose(full.fullspace_H_lower-full.fullspace_F_upper,full.fullspace_gap,atol=1e-14,rtol=0)
    summary = {"rows":220, "conditional_sets":sets, "status":"PASS",
               "max_state_norm_error":norm_error, "max_hermiticity_error":herm_error,
               "minimum_effect_eigenvalue":min_effect,"minimum_dual_slack_eigenvalue":min_slack,
               "max_numerical_envelope":max(r["envelope"] for r in rows),
               "robust_positive_counts":frame.groupby("group_rule").robust_positive.sum().astype(int).to_dict(),
               "fullspace_csv_checked":True, "fullspace_operators_available":False,
               "new_solver_calls":0}
    (OUT / "certificate_summary.json").write_text(json.dumps(summary,indent=2)+"\n")

    # Only source vectors: do not construct supports, states, Gram matrices, or endpoints.
    specs = [("zipf",x,None) for x in (.25,.45,.65,.85,1.05,1.25,1.45,1.65,1.85,2.05)]
    specs += [("dirichlet",a,901000+1000*int(a)+37*j) for a in (1.,2.) for j in range(10)]
    specs += [("near_uniform",.04,904000+37*j) for j in range(10)]
    specs += [("strong_skew",x,None) for x in (.32,.42,.52,.62,.67,.72,.82,.92)]
    oldpriors = [a["p"] for a in sources.values() if len(a["p"])==8]
    oldseeds = {s["seed"] for s in registry["sources"]}
    legacy = ROOT/"Error_Corrected_Probabilistic_Quantum_Huffman_Coding_with_Group_Ancilla_and_Posterior_Correction__1_"
    paths = set((ROOT/"data").glob("*.csv")) | set((legacy/"SM/data").glob("*.csv")) | set((legacy/"paper_data/results").glob("*.csv"))
    for archive in sorted((ROOT/"data/pairwise_matched_evidence").glob("*.npz")):
        p = np.load(archive)["p"]
        if len(p)==8: oldpriors.append(p)
    scans = []
    for path in sorted(paths):
        f = pd.read_csv(path)
        if "seed" in f:
            oldseeds.update(int(s) for s in f.seed.dropna().unique())
        col = next((k for k in ("probabilities","priors") if k in f),None)
        if col:
            for value in f[col].dropna().unique():
                try:
                    raw = str(value)
                    p = np.array([float(x) for x in raw.split(";")],dtype=float) if ";" in raw else np.array(ast.literal_eval(raw),dtype=float)
                    if p.shape==(8,): oldpriors.append(p/p.sum())
                except (ValueError,SyntaxError):
                    raise RuntimeError(f"Unparseable prior {path}")
            scans.append(str(path.relative_to(ROOT)))
    initial_collisions = []
    for family,param,seed in specs:
        p = source_probabilities(8,family,param,seed if seed is not None else 0)
        if any(np.allclose(p,old,atol=5e-8,rtol=0) for old in oldpriors):
            initial_collisions.append({"family":family,"parameter":param,"seed":seed})
    assert initial_collisions == [{"family":"strong_skew","parameter":.82,"seed":None},
                                  {"family":"strong_skew","parameter":.92,"seed":None}]
    specs = [(family,({.82:.83,.92:.93}.get(param,param) if family=="strong_skew" else param),seed)
             for family,param,seed in specs]
    drafts = []
    for j,(family,param,seed) in enumerate(specs):
        if seed is not None: assert seed not in oldseeds
        p = source_probabilities(8,family,param,seed if seed is not None else 0)
        assert all(not np.allclose(p,old,atol=5e-8,rtol=0) for old in oldpriors), (family,param,seed,"archival prior collision")
        assert all(phash(p)!=r["prior_sha256"] for r in drafts)
        assert all(not np.allclose(p,np.array(json.loads(r["prior_vector"])),atol=1e-14,rtol=0) for r in drafts)
        drafts.append({"prior_id":f"C25_{j+1:02d}", "M":8,"G":2,"prior_family":family,
                       "family_parameter":param,"seed":seed,"prior_vector":json.dumps(p.tolist()),
                       "prior_sha256":phash(p)})
    assert len(drafts)==48
    fields = list(drafts[0])
    with (ROOT/"CONFIRMATORY_PRIORS_DRAFT.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(drafts)
    draft = {"study_id":"CONFIRMATORY-M8-G2-G2-V1-DRAFT", "status":"DRAFT_ONLY",
             "human_approval_required":True, "frozen":False, "M":8, "G":2,
             "prior_count":48,"priors":drafts,"prior_hash_format":"SHA256 little-endian float64 p[0:8] bytes",
             "priors_csv_sha256":digest(ROOT/"CONFIRMATORY_PRIORS_DRAFT.csv"),
             "encoder":registry["encoder"],"implementation_sha256":registry["file_sha256"],
             "encoder_hash":registry["file_sha256"]["code/payload_generation.py"],
             "grouping_rule":"G2; sorted (-p_i,i); least accumulated mass, group-index ties",
             "sdp":registry["sdp"],"environment":registry["environment"],
             "orthogonality_tolerance":1e-10,"orthogonality_sensitivity":1e-8,
             "robust_threshold":.0005,
             "primary_endpoint":"Distinct held-out priors with raw delta_pair>0.0005 and all certificate, repeat and independent full-space validation gates passed; E2 never filters rows",
             "residual_gate":"Feasibility <=1e-7; also sensitivity-adjusted gap>0.0005 using predeclared algebraic envelope with 1e-10 numerical padding; not interval certification",
             "validation_policy":"All initial candidates >0.0005 undergo one unchanged repeat solve and one uncompressed full-space check. Both exceed 0.0005, pass residual/sensitivity checks. Save all full-space operators, solver stats, statuses and runtime.",
             "success_gate":{"STRONG":">=2 validated distinct priors and every raw-positive candidate passes all validation gates","LIMITED":"1 validated distinct prior and every raw-positive candidate passes all validation gates","FAIL":"0 validated distinct priors in a completely adjudicated batch","VALIDATION_FAILURE":"Any raw-positive candidate fails a completed repeat/fullspace validation gate","INCOMPLETE":"Missing or time-limited primary/validation outputs; retain all48 intended priors"},
             "incomplete_policy":"Failed/time-limited/missing outputs stay in denominator; completed-run gate INCOMPLETE until all validation attempts resolve; never silently treat missing as scientifically negative",
             "all_output_retention_rule":"All 48 priors and every solve/status retained, regardless of sign, E1/E2 or triviality",
             "stopping_rule":"One fixed batch; no adaptive sample size, prior replacement after outcomes, retries, tolerance changes or new group regimes",
             "fullspace_execution":"Same frozen fullspace SDP objective/tolerance/max_iters/postprocessing; external 300-s process ceiling per nonsingleton conditional sdp_success invocation (primal+dual), wall limit only, TIMEOUT retained",
             "draft_generation":"Prior-only; no payloads/Gram matrices/certificates created; initial .82/.92 skew priors collided with archived sweep, replaced with .83/.93 before any endpoint evaluation; superseded draft preserved",
             "superseded_prior_collisions":initial_collisions}
    (ROOT/"CONFIRMATORY_REGISTRY_DRAFT.json").write_text(json.dumps(draft,indent=2)+"\n")
    (OUT/"heldout_check.json").write_text(json.dumps({"candidate_count":48,"phase1d_prior_duplicates":0,
         "archival_prior_duplicates":0,"within_draft_duplicates":0,"seed_collisions":0,
         "archival_prior_vectors_scanned":len(oldpriors),"files_with_prior_vectors":scans,
         "initial_draft_collisions":initial_collisions,"replacements":{"0.82":0.83,"0.92":0.93},
         "archive_comparison_absolute_tolerance":5e-8,
         "scope":"Accessible root/legacy SM/legacy paper_data CSV vector fields, Phase1C and Phase1D archives; cannot certify nonexposure outside repository",
         "new_encoder_evaluations":0,"new_solver_calls":0,"status":"DRAFT_ONLY"},indent=2)+"\n")
    cell = frame[(frame.M==8)&(frame.group_rule=="G2")&(frame.G==2)]
    sizes = [Path(ROOT/r["operators"]).stat().st_size for r in manifest["rows"] if r["row_id"] in set(cell.row_id)]
    timing = {"matched_G2_M8_G2_rows":len(cell),"mean_seconds":float(cell.runtime.mean()),
              "median_seconds":float(cell.runtime.median()),"p95_seconds":float(cell.runtime.quantile(.95)),
              "max_seconds":float(cell.runtime.max()),"mean_operator_bytes":float(np.mean(sizes)),
              "max_operator_bytes":max(sizes),"fullspace_historical_runtime_recorded":False,
              "compressed_calls_per_prior_max":8,"repeat_calls_per_positive_max":8,
              "fullspace_calls_per_positive_max":8}
    dims = [2**(max(3,int(huffman_lengths(np.array(json.loads(r["prior_vector"]))).max()))+1) for r in drafts]
    timing["draft_ambient_dimension_counts"] = {str(d):dims.count(d) for d in sorted(set(dims))}
    timing["draft_uncompressed_one_archive_bytes"] = sum(320*d*d + 16*16*d for d in dims)
    timing["estimate_table"] = [{"N":n,"initial_solve_calls_max":8*n,
        "initial_matched_runtime_mean_extrapolation_seconds":n*timing["mean_seconds"],
        "initial_matched_runtime_observed_max_extrapolation_seconds":n*timing["max_seconds"],
        "initial_operator_storage_mean_extrapolation_MB":n*timing["mean_operator_bytes"]/1e6,
        "all_positive_total_solve_calls_max":24*n,
        "all_positive_solver_process_ceiling_hours":n*(8*30+8*30+4*300)/3600}
        for n in (32,40,48,64)]
    (OUT/"runtime_inputs.json").write_text(json.dumps(timing,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    print(json.dumps(timing,indent=2))
    print("DRAFT ONLY: 48 unique prior vectors; no new encoder, Gram or SDP evaluation")


if __name__ == "__main__":
    main()
