# Registration terminology and timestamp audit

PREREGISTRATION_WORDING: **DOWNGRADE_TO_PRE_SPECIFIED**.

Local freeze SHA: 830fe5a91348088710b1409de9f4c329d09f5419, author/committer time 2026-10-08T03:47:46+08:00. Result commit 7607907 is dated 04:07:43 that day. Local reflog agrees. The runner refuses a registry unequal to its committed file, verifies implementation hashes, refuses an existing output, and writes all diagnostics before solving. These are evidence of a prospectively fixed local analysis, not an independently witnessed registration timestamp. Git timestamps/reflogs can be changed.

Read-only GitHub checks in this audit:
- GET repos/songyaoxue/Quantum_Huffman/branches: only main at 1abe2cf9096ec71f37db2f9b206dfd7860c104a4.
- GET .../commits/830fe5a91348088710b1409de9f4c329d09f5419: HTTP422, "No commit found for SHA".
- Repository metadata: public, pushed_at 2026-09-24T18:30:50Z, earlier than Phase1D.
- Local origin/v2 tracking ref does not exist; origin/main reflog records earlier pushes, not Phase1D.
- git ls-remote did not return and was interrupted; no conclusion is drawn from that failed check.

There is no verified remote receipt preceding evaluation and no public/external immutable timestamp. Current absence cannot prove the SHA was never on any remote; it establishes that such evidence has not been supplied. Even a later public push would not retroactively establish external registration before evaluation. A current remote committer date would also not be an independent received-at timestamp.

Use "pre-specified evaluation matrix, locally frozen before evaluation". Keep the historical commit hashes and existing registry identifiers unmodified. Change visible preregistration/pre-registered prose and captions, not historical filenames or commit messages. Preserve POST_SELECTION=NO at the row/source/partition level; distinguish it from development-informed architecture selection and later highlighting of positive priors.

For the future protocol, obtain human approval, freeze a manifest including priors and the eventual runner/verifier hashes, then obtain an independently recorded public registration/release receipt before any SDP. A public Git push is useful provenance; a formal timestamped registration is stronger. This stage creates only DRAFT files and supplies no such receipt.
