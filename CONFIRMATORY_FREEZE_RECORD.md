# Confirmatory freeze record

Freeze tag: confirmatory-v1-frozen-before-run.
Freeze commit: resolve this immutable tag; the explicit SHA and external receipt
will be recorded in a separate provenance-only follow-up commit after push.
The freeze commit cannot contain its own SHA without a circular dependency.

## Frozen artifact SHA-256

- Registry: 090ce3fe480c045750b741844e6e45311c183e2b29656c1b28d45a4ea307d465
- Priors CSV: b7136bbc2de852b9b8f668cada95b87b00654fa4d793ba687ce15ff09c154f0d
- Code manifest: f4cef7ca756d4ab3ef86542fcc800c42a724ad2dad3abebfb501e55b5e022cad
- Environment record: 25844d3a7da0668d6fe088deaed0b04dff98769481939bd528d8bc233a82cf79
- Protocol: e4de025ddd396d61c3985d8d94cd4799fd7175d3ea2438779c9eb65973a3f2ef

## Pre-freeze verification

48/48 full-precision prior vectors distinct; frozen CSV byte-identical to
the approved draft. Phase 1D duplicates: 0; core-positive duplicates: 0;
development seed collisions: 0. Family composition: 10/20/10/8 unchanged.
Local integrity/environment guard PASS. No-solve regression tests: 12/12.
Tests replace CVXPY Problem.solve with a raising guard. Timeout fixtures use
mock workers and temporary directories, not scientific data. No batch runner
--execute invocation or confirmatory worker invocation occurred.

NO CONFIRMATORY SDP WAS RUN BEFORE THIS FREEZE

This assertion covers the repository-observable workflow and this execution
session: draft audit reports zero new solver calls, no confirmatory result
files exist, and only prior copying, integrity tests, policy tests and legacy
read-only traceability aggregation were run. It does not assert knowledge of
unrecorded calculations outside this repository.

Legacy traceability was independently reaggregated read-only: 707/707 PASS.
The v2 manuscript/SM TeX/PDF hashes match the Phase 2 inputs; no manuscript
patches were applied. PRA frozen tag remains
e7b69ae4bcc3f47f9121bc2d35ddb130fe419880. No Zenodo upload or modification.

## External visibility

Pending push and remote retrieval. Execution guard requires the final external
receipt and matching remote tag before any later human-authorized batch.
The receipt will distinguish retrieval/server timestamps from Git author dates;
public Git visibility is an external freeze witness, not formal preregistration.
