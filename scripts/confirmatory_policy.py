"""Frozen decision policy; no solvers, adaptive inputs, or file writes."""

THRESHOLD = 5e-4
FINAL_STATES = (
    "ROBUST_POSITIVE_CONFIRMED", "ROBUST_POSITIVE_NOT_CONFIRMED",
    "NONPOSITIVE_CERTIFICATE", "FIXED_TRIVIAL", "NUMERICALLY_INCONCLUSIVE",
)


def qualifies(result):
    return bool(result and result.get("valid") and
                result["gap"] > THRESHOLD and result["safe_gap"] > THRESHOLD)


def classify(primary, repeat, fullspace, fixed_trivial):
    if not primary or not primary.get("valid"):
        return "NUMERICALLY_INCONCLUSIVE"
    if primary["gap"] <= THRESHOLD:
        return "FIXED_TRIVIAL" if fixed_trivial else "NONPOSITIVE_CERTIFICATE"
    if not repeat or not fullspace or not repeat.get("valid") or not fullspace.get("valid"):
        return "NUMERICALLY_INCONCLUSIVE"
    if all(qualifies(r) for r in (primary, repeat, fullspace)):
        return "ROBUST_POSITIVE_CONFIRMED"
    return "ROBUST_POSITIVE_NOT_CONFIRMED"


def outcome(states):
    if len(states) != 48 or any(s not in FINAL_STATES for s in states):
        raise ValueError("All 48 final states are required")
    count = states.count("ROBUST_POSITIVE_CONFIRMED")
    gate = "STRONG" if count >= 2 else "LIMITED" if count == 1 else "FAIL"
    # Completeness is separate from the count gate, never silently a negative.
    complete = not any(s in ("NUMERICALLY_INCONCLUSIVE", "ROBUST_POSITIVE_NOT_CONFIRMED") for s in states)
    return {"gate": gate, "confirmed_distinct_priors": count,
            "fully_adjudicated": complete, "primary_population": 48}
