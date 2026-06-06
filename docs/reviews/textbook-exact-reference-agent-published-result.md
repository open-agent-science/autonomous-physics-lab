# Textbook Exact-Reference AGENT_PUBLISHED Result

**Task:** `TASK-0634`
**Campaign:** Textbook Formula Audit
**Verdict:** `PUBLISHED_SCOPED_SOFTWARE_RESULT` (`VALID_IN_RANGE`, software/convention scope only)

## Decision

This task publishes the first scoped `AGENT_PUBLISHED` RESULT for the Textbook
Formula Audit exact-reference software fixtures, resolving the blockers recorded
by `TASK-0586` (`BLOCKED_CANONICAL_RESULT_IDENTITY_MISSING`) and `TASK-0603`
(identities defined, fixture boundaries still sandbox-only).

Published artifact: `results/EXP-0013/RUN-0001/result.yaml` (`RESULT-0019`).
Replay command recorded in the RESULT:
`physics-lab run examples/textbook_stefan_boltzmann_exact_reference.yaml`.

## What changed to make publication consistent

1. **Fixture route boundaries** flipped from sandbox-only to scoped
   software-result packaging for the `EXP-0013` / `HYP-0013` identity, with
   empirical ingestion and claim promotion kept blocked:
   - `data/textbook_formula_audit/textbook_stefan_boltzmann_exact_reference.yaml`
     (`promotion_boundary.sandbox_only: false`, `writes_canonical_result: true`,
     `empirical_rows_allowed: false`, `claim_promotion_allowed: false`);
   - `data/textbook_formula_audit/fixtures/wien_displacement_exact_reference.yaml`
     (`publication_scope.route: scoped_software_result_packaging`).
2. **Engine boundary made config-driven.** The Stefan-Boltzmann engine
   previously hardcoded `promotion_boundary`; it now echoes the manifest's
   declared boundary (`physics_lab/engines/stefan_boltzmann.py`), with
   `empirical_audit_performed` always `false`. The runner report and the two
   fixture tests were updated to match.
3. **Result-only metadata kept honest.** `review_metadata.yaml` records
   `claim_id: null`, `knowledge_id: null`, and `proposed_claim_status: null`.
   This preserves the task's default "no CLAIM/KNOW" boundary while still
   keeping the run artifact package complete.

## Gate A status

`python3 scripts/apl_check_result_publication.py results/EXP-0013/RUN-0001/result.yaml`
returns `PASS`. All nine Gate A keys are recorded true in
`agent_proposal_evaluation.gates_checked`: deterministic_run,
verification_block_populated, input_hashes_recorded, limitations_listed,
engine_version_and_commit_pinned, schema_validation_passes,
no_protected_artifact_rewrite, no_forbidden_overclaim_wording,
dataset_provenance_valid.

## Replay evidence

Deterministic Stefan-Boltzmann exact-reference run:

- verdict: `VALID_IN_RANGE`;
- rows: 16 (8 reference, 8 holdout);
- max exact-reference relative error: `0.0` (tolerance `1e-12`);
- gates: dimensional consistency, CODATA 2022 constant convention, `T^4` and
  `R^2` scaling, monotonicity all `PASS`;
- declared negative controls (wrong temperature exponent, wrong area
  multiplier) rejected as expected.

The Wien wavelength-domain fixture is supporting software evidence verified by
`tests/test_textbook_wien.py`.

## Interpretation boundary

This RESULT validates deterministic software, units, and the frozen CODATA 2022
constant convention only. It does not validate or falsify Stefan-Boltzmann, Wien
displacement, blackbody radiation, stellar observations, laboratory spectra, or
any textbook formula as empirical physics, and it implies no universal-law
statement.

## Output routing

- Task verdict: `VALID_IN_RANGE` (software/convention fixture scope).
- Canonical destination: `results/EXP-0013/RUN-0001/result.yaml` (`RESULT-0019`).
- Review tier: `AGENT_PUBLISHED` (agent-published, not independently validated or
  maintainer-reviewed).
- Gate A status: PASS (recorded above).
- Gate B status: not attempted; this RESULT is the intended replay target for
  the first Gate B independent-replay task (`TASK-0635`).
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Limitations / blockers: synthetic software fixture only; no empirical rows; no
  empirical formula validation or universal-law wording.

## Gate B handoff

`TASK-0635` can replay `RESULT-0019` with a different agent identity using
`scripts/apl_validate_agent_published_result.py`. If replay reproduces the
deterministic gates within tolerance, that task may add a `validation_record`
and propose `AGENT_VALIDATED`; it must not edit the metrics, verdict, command,
inputs, or claim/knowledge status.

The publication branch includes a workflow adapter for
`python3 -m physics_lab.cli run examples/textbook_stefan_boltzmann_exact_reference.yaml`,
so Gate B uses the standard safe replay path rather than an arbitrary script
entrypoint.
