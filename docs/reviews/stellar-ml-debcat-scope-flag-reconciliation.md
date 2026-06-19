# Stellar M-L DEBCat Scope Flag Reconciliation

- Task: `TASK-0779`
- Domain: textbook formula audit, Stellar M-L
- Decision: `DEBCAT_SCOPE_FLAGS_RECONCILED`

## Scope

This task reconciles stale seed-stage DEBCat metadata after TASK-0763 published
the full normalized DEBCat rows and frozen holdout manifest under explicit
CC BY 4.0 permission, and after RESULT-0022 used the committed rows for the
scoped Stellar M-L controlled benchmark.

This task changes metadata only. It does not edit row values, split assignments,
RESULT-0022 metrics, claims, knowledge artifacts, or `results/golden-results.yaml`.

## Before

`data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml` still carried
the TASK-0708 seed flags:

- `status: sandbox_first_seed`
- `scope.sandbox_only: true`
- `scope.benchmark_allowed: false`
- `scope.alpha_fit_allowed: false`

The extractor also regenerated those same flags, and the DEBCat test module and
sample notices still described the full dataset as not redistributed.

Those flags were correct for the seed-stage row package but stale after:

- TASK-0763 recorded explicit DEBCat CC BY 4.0 permission and committed the full
  normalized rows plus frozen holdout manifest.
- TASK-0759 and TASK-0762 completed the stage-control and baseline-adequacy
  audits.
- TASK-0764 published RESULT-0022 as an AGENT_PUBLISHED, scope-limited
  controlled DEBCat benchmark.

## After

The full row package now records:

- `status: cc_by_4_0_benchmark_source`
- `publication_task_id: TASK-0763`
- `scope_reconciliation_task_id: TASK-0779`
- `scope.sandbox_only: false`
- `scope.benchmark_allowed: true`
- `scope.alpha_fit_allowed: true`
- `scope.live_external_fetch_allowed: false`
- `scope.claim_promotion_allowed: false`
- `scope.prediction_registry_allowed: false`

The extractor now emits the same reconciled metadata, so future regeneration
does not reintroduce the seed-stage flags. The DEBCat provenance metadata now
marks the rows as accepted for the frozen, scope-limited benchmark lane while
preserving the Route 2 raw-artifact boundary.

The sample artifacts remain intentionally small and non-substitutive, but their
notices now state that the full normalized rows and frozen holdout manifest are
committed under CC BY 4.0 with sibling license markers.

## No-Claim Boundary

The reconciled metadata means the committed DEBCat rows may support the frozen,
scope-limited Stellar M-L benchmark lane. It does not imply:

- universal M-L validation;
- falsification of the mass-luminosity relation as a universal textbook formula;
- stellar-evolution claims;
- application-domain claims;
- claim or knowledge promotion;
- prediction-registry use;
- raw `debs.dat` redistribution.

RESULT-0022 keeps its historical metrics and limitations unchanged. This task
only removes the stale source-scope metadata mismatch that RESULT-0022 recorded
as a follow-up.

## Files Touched

- `data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml`
- `scripts/extract_debcat_stellar_ml_rows.py`
- `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/provenance.yaml`
- `data/textbook_formula_audit/stellar_ml/source_artifacts/debcat/extraction_notes.md`
- `data/textbook_formula_audit/stellar_ml/debcat_component_rows.sample.yaml`
- `data/textbook_formula_audit/stellar_ml/debcat_holdout_manifest.sample.yaml`
- `tests/test_stellar_ml_debcat_rows.py`

## Output Routing

- Task verdict: `DEBCAT_SCOPE_FLAGS_RECONCILED`
- Canonical destination:
  `docs/reviews/stellar-ml-debcat-scope-flag-reconciliation.md`
- Review tier: `none`
- Gate A status: not applicable; no new `RESULT-*` artifact was created.
- Gate B status: not applicable; no independent replay was performed.
- Claim impact: no claim created or modified.
- Knowledge impact: no knowledge artifact created or modified.
- Result impact: no RESULT metrics or verdict changed.
- Dataset impact: DEBCat metadata now matches the TASK-0763 publication route
  and RESULT-0022 scope-limited benchmark use.
