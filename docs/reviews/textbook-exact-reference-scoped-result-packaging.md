# Textbook Exact-Reference Scoped Result Packaging

**Task:** `TASK-0586`
**Campaign:** Textbook Formula Audit
**Verdict:** `BLOCKED_CANONICAL_RESULT_IDENTITY_MISSING`

## Scope

This task starts from the TASK-0568 preflight route and decides whether the
completed Stefan-Boltzmann and Wien exact-reference fixtures can be packaged as
a scoped software/benchmark `RESULT-*` artifact. It does not fetch empirical
datasets, run a Stellar M-L audit, validate or falsify Stefan-Boltzmann/Wien
against observations, change claims, or create knowledge artifacts.

## Inputs Reviewed

- `tasks/archive/0500-0999/TASK-0568-package-textbook-exact-reference-result-preflight.yaml`
- `docs/reviews/textbook-exact-reference-fixture-result-preflight.md`
- `docs/reviews/textbook-stefan-boltzmann-exact-reference-fixture.md`
- `docs/reviews/textbook-wien-displacement-exact-reference-fixture.md`
- `data/textbook_formula_audit/textbook_stefan_boltzmann_exact_reference.yaml`
- `data/textbook_formula_audit/fixtures/wien_displacement_exact_reference.yaml`
- `physics_lab/schemas/result.schema.json`
- `docs/result-promotion-protocol.md`

## Method

1. Re-read the TASK-0568 preflight and its routing decision.
2. Replayed the Stefan-Boltzmann exact-reference runner into a disposable
   local output directory.
3. Checked the `RESULT-*` schema and existing canonical experiment/result
   conventions.
4. Searched the repository for canonical Textbook Formula Audit `EXP-*` and
   `HYP-*` identities.
5. Applied the result-promotion protocol without overriding fixture
   sandbox-only boundaries.

## Replay Evidence

Command:

```text
C:\Users\sviti\Documents\autonomous-physics-lab\.venv\Scripts\python.exe scripts\run_textbook_stefan_boltzmann_exact_reference.py --config data\textbook_formula_audit\textbook_stefan_boltzmann_exact_reference.yaml --output-dir C:\tmp\apl-stefan-fixture-0586
```

Replay result:

- verdict: `VALID_IN_RANGE`
- fixture rows: `16`
- reference rows: `8`
- holdout rows: `8`
- max exact-reference relative error: `0.0`
- dimensional consistency: `PASS`
- CODATA 2022 constant convention: `PASS`
- temperature `T^4` scaling: `PASS`
- radius `R^2` area scaling: `PASS`
- monotonicity: `PASS`
- wrong-temperature-exponent control: rejected as expected
- wrong-area control: rejected as expected

The Wien fixture evidence remains the test-backed fixture review from
`docs/reviews/textbook-wien-displacement-exact-reference-fixture.md` and the
declared validation command for this task.

## Result-Packaging Decision

No `RESULT-*` artifact is created in this PR.

The evidence surface is green for the narrow software-fixture scope, but
canonical result publication is blocked for two mechanical reasons:

1. `physics_lab/schemas/result.schema.json` requires a canonical
   `experiment_id` matching `EXP-XXXX` and `hypothesis_id` matching `HYP-XXXX`.
   The repository currently has no canonical Textbook Formula Audit experiment
   or hypothesis identity for the exact-reference software fixture pair.
2. The committed fixture manifests still explicitly mark the route as
   sandbox-only:
   - Stefan-Boltzmann runner output reports `promotion_boundary.sandbox_only:
     true` and `writes_canonical_result: false`.
   - Wien fixture metadata reports `publication_scope.route: sandbox_only`.

Creating a new `EXP-*`, `HYP-*`, or changing those fixture boundaries would be
more than packaging the existing preflight route; it would be a new canonical
identity and policy-boundary task. TASK-0586 therefore preserves the blocker
instead of inventing a result identity locally.

## Required Follow-Up To Publish A Scoped Result

A future result-packaging task may create the scoped software/convention result
only after it explicitly includes all of the following accepted outputs:

- a canonical Textbook Formula Audit experiment file, for example an
  `EXP-XXXX` exact-reference software-fixture experiment;
- a scoped hypothesis file, for example a `HYP-XXXX` statement limited to APL
  software/convention validation and not empirical formula truth;
- fixture metadata updates that remove or narrow the `sandbox_only` /
  `writes_canonical_result: false` blocker for the exact-reference software
  route only;
- one `results/EXP-XXXX/RUN-XXXX/result.yaml` with `review_tier:
  AGENT_PUBLISHED`, populated Gate A evaluation, input hashes, limitations,
  replay command, report, metrics, review metadata, and no claim/knowledge
  promotion;
- validation through `scripts/apl_check_result_publication.py` or the
  equivalent result-publication gate used by current result PRs.

## Interpretation Boundary

The replayed fixtures validate deterministic software plumbing and exact
constant/convention behavior only. They do not validate or falsify:

- Stefan-Boltzmann as an empirical physical law;
- Wien displacement as an empirical physical law;
- blackbody radiation outside the synthetic fixtures;
- stellar observations, spectra, catalog rows, or laboratory sources;
- any cross-formula Textbook Formula Audit claim.

## Metrics

- `result_artifacts_created`: 0
- `canonical_experiments_created`: 0
- `canonical_hypotheses_created`: 0
- `claims_promoted`: 0
- `knowledge_entries_promoted`: 0
- `empirical_datasets_fetched`: 0
- `stefan_boltzmann_fixture_rows_replayed`: 16
- `stefan_boltzmann_max_exact_reference_relative_error`: 0.0

## Limitations

- This task did not run a new empirical formula audit.
- This task did not package a `RESULT-*` artifact because the required
  canonical experiment/hypothesis identity and fixture boundary changes are
  absent from the accepted output contract.
- The disposable replay output under `C:\tmp` is not committed.

## Output Routing Summary

- Task verdict: `BLOCKED_CANONICAL_RESULT_IDENTITY_MISSING`
- Canonical destination:
  `docs/reviews/textbook-exact-reference-scoped-result-packaging.md`
- Review tier: `none`
- Gate A status: not attempted; no `RESULT-*` artifact was created.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Result impact: no canonical result artifact created or modified.
- Publication blocker: no canonical `EXP-*` / `HYP-*` identity exists for this
  exact-reference software scope, and fixture manifests still declare
  sandbox-only result boundaries.
