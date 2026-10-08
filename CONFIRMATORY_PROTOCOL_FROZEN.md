# Confirmatory protocol V1: frozen before evaluation

Study ID: CONFIRMATORY-M8-G2-G2-V1. Exactly 48 distinct held-out priors.
This is a pre-specified, externally witnessed Git freeze, not formal preregistration.
No confirmatory SDP execution is authorized by this freeze phase.

## Population and encoder

The approved draft CSV is copied byte-for-byte. Composition: Zipf 10,
Dirichlet 20 (10 alpha=1 and 10 alpha=2), near-uniform 10, controlled-skew 8.
Full vectors, parameters, seeds and little-endian float64 SHA-256 hashes are
authoritative. No regeneration, substitution, expansion, E1/E2 filtering, or
outcome-dependent exclusion is allowed. All 48 remain the primary population.

M=8, G=2, G2 probability-balanced grouping only. Use the existing Huffman
implementation and common n_max=max(3,max Huffman length)+1. The existing
normalization in allocate_supports is applied to each stored input vector;
both arms use its identical normalized probabilities. H uses Huffman lengths,
F lengths are all 3. Supplied-length cyclic support allocation, shift=0,
original cursor rule and symbol ordering, equal-modulus amplitudes,
deterministic phase ansatz, zero optimizer iterations, source seed+100
(null deterministic-source seed maps to 0) are unchanged. G2 sorts by
(-p_i,i), assigns the least accumulated mass with group-index tie breaking,
and sorts members. H/F use exactly the same partition, two orthogonal labels,
label-width coordinate 1 and conditional POVM model. No adaptive geometry inputs.

## Solver and certificate verification

CVXPY 1.8.2, SCS 3.2.11, eps=5e-6, max_iters=25000. Compressed solves use
SCS time_limit_secs=30 per solver call. Span rank threshold=1e-12;
dual safety shift=5e-8; ambient feasibility tolerance=1e-7;
conditional prior/aggregation tolerance=1e-12. Orthogonality tolerance=1e-10;
1e-8 is a sensitivity diagnostic only. Environment/package/build drift aborts.

Use the unchanged conditional_bounds function for compressed primary/repeat
solves. Its PSD projection, regularized normalization, complement completion,
second ambient POVM repair, dual Hermitization and maximum-slack safety shift
are fixed. The separate full-space formulation uses original ambient matrices,
no compression, identical solver tolerance/iterations, original full-space
POVM repair regularization=max(1e-10,eps*1e-2) and dual safety shift of that
size. Singleton tasks use analytical identity effects. Both arms' matrices,
conditional priors, solver stats, statuses and wall runtimes are saved.

Every ambient certificate is checked for PSD, completeness, dual slack and
weak duality. Conditional lower/upper values are weighted by p_g, never by
unweighted group counts. Record both arms' bounds, not just the pairwise gap.

## Unique robust-positive criterion

Raw Delta=P_H_lower-P_F_upper must strictly exceed 5e-4. Feasibility must
pass the 1e-7 checks. For each H group set e=||sum E-I||_2,
delta=max(0,-min_i lambda_min(E_i))+1e-10 and L_safe=L/(1+e+m delta).
For each F group set gamma=max(0,-min_i lambda_min(Y-q_i rho_i))+1e-10,
U_safe=U+d gamma. The p_g-weighted safe gap must also strictly exceed 5e-4.
This is a conservative floating-point sensitivity gate, not interval arithmetic.

Every valid primary raw gap >5e-4 automatically receives exactly one fresh
same-settings repeat and one independent uncompressed full-space validation,
including cases failing E2 or the sensitivity gate. Both validations must
individually pass feasibility and raw/safe gap thresholds to confirm a prior.
No manual candidate selection and no stopping after two successes.

## Timeout, failure and retention

Each conditional primal+dual worker invocation has a 300-second external
wall ceiling, including startup/canonicalization/postprocessing, for primary,
repeat and full-space stages. Compressed SCS additionally has its 30-second
per-call limit. No retries, alternate tolerances, extended timeouts or replacement
priors. Failure/timeout attempts are retained; primary failures have attempt
status PRIMARY_SOLVE_INCOMPLETE. Partial operators, when available, and logs
remain saved. Continue to every remaining planned prior regardless of failure.

Final prior status is exactly one of:
ROBUST_POSITIVE_CONFIRMED; ROBUST_POSITIVE_NOT_CONFIRMED;
NONPOSITIVE_CERTIFICATE; FIXED_TRIVIAL; NUMERICALLY_INCONCLUSIVE.
Primary or validation numerical failures are NUMERICALLY_INCONCLUSIVE.
Completed validation missing a required threshold is
ROBUST_POSITIVE_NOT_CONFIRMED, diagnostic VALIDATION_NOT_CONFIRMED.
For valid primary raw gap <=5e-4, use FIXED_TRIVIAL if applicable, otherwise
NONPOSITIVE_CERTIFICATE (meaning the robust sufficient test is unmet, including
small positive gaps). This enum does not infer optimal-performance inferiority.

## Endpoint and adjudication

Primary endpoint: number of distinct held-out priors confirmed robust positive
under all frozen primary, repeat, full-space and feasibility/sensitivity checks.
E2 is secondary only. STRONG: >=2 confirmed distinct priors; LIMITED: exactly 1;
FAIL: 0. Positives from >=2 families are secondary breadth, not a success gate.

The count gate is recorded alongside fully_adjudicated. This flag is false
if any candidate is unconfirmed or any prior is numerically inconclusive;
then the count gate is provisional, not an unqualified STRONG/LIMITED/FAIL
scientific conclusion. This preserves the draft's validation-failure and
incompleteness safeguard without adding a sixth final-prior status.
All 48 rows and every attempt are retained. No inference of zero scientific
positives from missing solves. No population prevalence estimate from this
fixed mixture and no adaptive optional stopping.

## Execution boundary

Guard requires the immutable freeze-tag contents, code/artifact/environment
hashes, prior-only development exclusions, fresh result directory and remote
tag receipt. Runner cannot read development gaps: only frozen priors/config
and outcome-independent functions are execution inputs. Development files are
not adaptive inputs; the prior-only exclusion snapshot is used by the guard.
The CLI requires --execute, reserved for later explicit human authorization.
Freeze tests patch Problem.solve to raise and only exercise integrity/policy.
Empty result directories are created locally; Git does not track empty directories
and the runner creates them in a fresh checkout. Historical drafts are retained.
