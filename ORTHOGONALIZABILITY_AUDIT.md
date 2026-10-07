# Orthogonalizability audit (Phase 1C)

**The broad cyclic equal-modulus family permits orthogonal realizations on some inputs.** For the five declared smoke cases, independent feasibility optimization and analytic bounds classify four H/F pairs as globally nonorthogonalizable and one H/F pair as orthogonalizable. These are payload classifications; group-label orthogonality must be audited separately.

## A. Support incidence with arbitrary amplitudes

An injective assignment of one supported basis position to each symbol is an explicit orthogonal-state witness when arbitrary amplitudes, including zeros, are allowed. The script searches for that matching. Such witnesses exist for H and F in cases 1, 2, 4, and 5. Case 3 has duplicate singleton supports and no matching: its states cannot all be orthogonal even with arbitrary amplitudes. Thus supports alone generally do not remove the unrestricted-design obstruction.

## B--E. Actual equal-modulus phase parameterization

If two supports intersect at exactly one basis position, their squared state overlap is exactly `1/(|S_i|*|S_j|)` for every phase choice. A sum of these contributions is an analytic lower bound on `sum_{i<j}|<Phi_i|Phi_j>|^2`. It proves impossibility of orthogonalization; a failed local search alone would not do so.

The independent test uses SciPy `least_squares` on real/imaginary off-diagonal Gram entries, fixes one irrelevant global phase per symbol, and uses three seeded starts with maximum 500 evaluations each. It uses `ftol=xtol=gtol=1e-10` and orthogonality objective threshold `1e-10`. Exact witnesses and nonzero analytic lower bounds take precedence over optimizer termination status. Every reported minimum below reaches its analytic lower bound within numerical tolerance.

| Case | M | H minimum found / analytic bound | F minimum found / analytic bound | Global phase-orthogonalizable H/F |
| --- | --- | --- | --- | --- |
| smoke_1 | 4 | 0.750000 / 0.750000 | 0.750000 / 0.750000 | NO / NO |
| smoke_2 | 4 | 0.750000 / 0.750000 | 0.750000 / 0.750000 | NO / NO |
| smoke_3 | 4 | 2.000000 / 2.000000 | 2.000000 / 2.000000 | NO / NO |
| smoke_4 | 8 | 0.187500 / 0.187500 | 0.437500 / 0.437500 | NO / NO |
| smoke_5 | 8 | 0 / 0 | 0 / 0 | YES / YES |

The five actual heuristic H objectives in this *unweighted* metric are approximately `1.029947, 0.750000, 2, 0.207292, 0`; the deterministic H objectives are approximately `0.755463, 0.755463, 2, 0.293693, 0`. Full precision, starts, supports and states are stored in `data/pairwise_matched_smoke_details.json` and the NPZ evidence. The current optimizer cannot reach an impossible orthogonal point in cases 1--4. In case 5 the supports are disjoint, so both deterministic and optimized rules already produce orthogonal states regardless of their phases. There is no general global-convergence guarantee for the heuristic.

## Existing deterministic restriction: global nonorthogonality

With cyclic shift zero, `extra_qubits=1`, and the existing deterministic phase rule, consider the first two probability-ranked symbols. Their supports begin at 0 and `s_0/2`, with sizes `s_0,s_1` that are powers of two at least two. Neither wraps, and their intersection has `r=min(s_0/2,s_1)>0` positions, a power of two. Their overlap is a nonzero constant times a geometric sum of r terms with ratio `z=exp(2*pi*i*(a/(s_0+1)-b/(s_1+1)))`, for integer symbol-index frequencies a,b. The order of z divides an odd integer. If the geometric sum vanished, then `z^r=1` and `z!=1`; but r is a power of two, so an odd-order root satisfying `z^r=1` must be 1, a contradiction. If z=1, the sum is r. Hence the first pair has nonzero overlap. This applies to both specified length vectors with the same deterministic architecture.

This existing narrower rule is valid at the global payload level. It cannot eliminate all trivial cases after grouping: inter-group payload overlaps are removed by the label. In the five optimized smoke cases, **every fixed pair inside each declared group has disjoint supports**, so the grouped fixed optimum is exactly one even in cases with nonzero global overlap. Consequently these pairs cannot have a positive strict success certificate. The broader optimized family still contains orthogonal realizations, and no theorem asserting uniformly nontrivial conditional discrimination is justified. A future partition/architecture study must be predeclared and symmetric; no current result is discarded or weakened.
