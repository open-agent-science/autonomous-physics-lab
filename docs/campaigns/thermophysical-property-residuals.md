# Thermophysical Property Residuals

## Goal

Build a source-pinned benchmark campaign for thermophysical property estimation,
starting with normal boiling temperature (`Tb`) in the NIST TRC ThermoML
Archive and a frozen Joback and Reid group-contribution baseline.

The target is not chemical design, process design, safety guidance, synthesis
guidance, or a new thermophysical law. The target is a replayable residual
surface where agents can test whether simple published estimators survive
source, identity, family-split, and control gates.

## Current Status

**Source-readiness benchmark surface with preserved failed-family memory.** The
first slice is already stronger than a scaffold: `TASK-0869` packaged the bounded
ThermoML `Tb` family-stratified Joback transfer benchmark as `RESULT-0026`, now
an `AGENT_VALIDATED`, `VALID_IN_RANGE` result after formal Gate B workflow
replay. `TASK-0936` then packaged the esters/lactones failed-family slice as
`RESULT-0028`, now an `AGENT_VALIDATED` bounded negative/control result after
formal Gate B workflow replay. It keeps the aggregate-positive context visible
without changing the `RESULT-0026` metrics or verdict.

The evidence is deliberately narrow. The committed fixture contains 40 factual
audit rows, five rows from each of eight predeclared chemical families. The raw
ThermoML archive bytes and any substantial normalized corpus are not committed.
The source route is pinned to the NIST TRC ThermoML Archive DOI
`10.18434/mds2-2422` and the published archive SHA-256 recorded in
`data/thermophysical/source_manifest.yaml`.

A checksum-matching local archive has now been checked with the frozen
count-only preflight. The exact 80-row design is not feasible under its
predeclared ten-per-family rule: acids provide 6 admissible non-conflict
identities and ketones provide 8. No rows or values were emitted. This closes
the exact-80 route under the current contract; it is no longer an archive-access
blocker.

The frozen Joback estimator is structure-only for `Tb`:

```text
Tb = 198.2 K + sum(Joback and Reid Tb group increments)
```

APL fits no Joback coefficient or correction in this result.

## Public Monitoring Snapshot

**Current question:** can a frozen, published thermophysical estimator beat
simple controls under a bounded, source-pinned ThermoML `Tb` fixture?

**Shareable result:** `RESULT-0026` reports that the frozen Joback `Tb`
estimator beats the best non-oracle control on the committed 40-row fixture.
Aggregate Joback MAE is `14.925825 K`; the best non-oracle aggregate control is
`molecular_weight_only` at `43.427943 K`, giving a `28.502118 K` margin against
the predeclared `5 K` survival threshold. Seven of eight held-out families clear
the family-survival margin.

**Important negative/control memory:** the `esters/lactones` family does not
clear the family margin. That failed family is now first-class result memory:
`RESULT-0028` records Joback MAE `26.134 K` versus `20.584245 K` for the
molecular-weight-only control across the five committed esters/lactones rows.
This does not weaken `RESULT-0026`; it prevents the aggregate win from hiding a
failed family.

**Replay state:** the formal workflow Gate B bridges reproduced `RESULT-0026`
and `RESULT-0028` with zero drift and updated both result tiers to
`AGENT_VALIDATED`. Both artifacts validate or package only the bounded 40-row
`Tb` fixture; they do not remove the esters/lactones failed-family limitation.

**Not a claim:** `RESULT-0026` is not a universal validation of Joback, not a
new thermophysical law, and not a chemical-design or process-design result. It
does not say anything about critical temperature, vapor pressure, heat capacity,
or other ThermoML properties. `Tc` is intentionally excluded because Joback's
`Tc` estimator depends on `Tb`, which creates an upstream-property leakage path
for this first audit.

## Current Decision

The exact-80 contract remains stopped. `TASK-1084` made the one authorized
counts-only decision and returned `REVISED_CONTRACT_READY_NO_SCORE`: an
availability-capped surface of at most 74 rows, weighted equally across the
eight chemical families. It emitted no target rows and ran no metric.

1. **Exact 80-row expansion is stopped** - the checksum-matched count preflight
   found acids at 6/10 and ketones at 8/10 admissible non-conflict identities.
   Lowering those gates after seeing the counts would be post-result contract
   shopping, not a valid completion of the frozen design.
2. **Revised contract is bounded** - family targets are capped by admissible
   availability, the five-row per-article cap is mandatory, and a frozen
   effective-information floor must pass. Failure produces no partial fixture.
3. **No further replay loop for `RESULT-0028`** - it is already
   `AGENT_VALIDATED`; future work should use it as failed-family memory while
   preserving the bounded aggregate context.
4. **Extraction and scoring stay separate** - the revised contract authorizes
   one complete value-blind fixture only after the exact checksum-matched local
   archive is supplied. A later task would have to freeze any benchmark score.

## Admissible Source Classes

Currently admitted:

- bounded factual ThermoML normal-boiling-temperature extracts with attribution;
- source manifests that record archive DOI, filename, checksum, license/reuse
  posture, row class, identity mapping, and exclusion rules;
- frozen Joback `Tb` group-count fixtures used for implementation fidelity
  before scoring.

Not currently admitted:

- raw ThermoML archive bytes in the repository;
- a substantial normalized ThermoML corpus;
- mixtures, ionic liquids, salts, charged species, or ambiguous systems;
- `Tc`, vapor-pressure, heat-capacity, critical-property, or multi-property
  audits without a separate source and leakage gate.

## Allowed Task Types

1. **Source-readiness task** - deterministic extraction of the frozen revised
   fixture after archive identity, rights, article-cap, and information-floor
   checks pass.
2. **Negative-memory task** - failed-family or control-memory packaging only
   when a new failed slice appears or a task explicitly asks for public
   synthesis; the existing esters/lactones memory is already packaged as
   `RESULT-0028`.
3. **Future benchmark task** - only after a complete revised fixture exists;
   extraction itself does not authorize a score.

## Guardrails

Allowed current work:

- inspect committed fixture, source manifest, result metadata, and runner code;
- supply the exact checksum-matched archive outside version control;
- extract one complete revised fixture under the frozen contract.

Not allowed:

- rerun Gate A packaging as a new result;
- edit `RESULT-0026` metrics outside an explicit repair task;
- fetch or commit raw ThermoML archive bytes;
- commit a broader normalized ThermoML corpus;
- commit a partial revised fixture after any hard-stop gate fails;
- score the revised fixture in the extraction task;
- broaden from `Tb` to `Tc` or other properties;
- claim Joback is universally right, universally wrong, or physically
  explanatory.

## Recommended Next Work

- Keep `RESULT-0026` and `RESULT-0028` paired in public wording: aggregate win
  plus explicit failed-family memory.
- Do not reopen the exact 80-row route by lowering the acids or ketones family
  thresholds after the count result.
- The immediate next artifact is one complete, rights-bounded at-most-74-row
  fixture after the exact archive, article-cap, and information-floor gates
  pass; a hard stop is preferable to a partial fixture.
- Benchmark scoring, RESULT packaging, and any broader property route remain
  separate future decisions.

## Why It Matters

Thermophysical property estimation is a good APL campaign because it has
published source archives, recognizable baselines, natural family holdouts, and
strong negative-result value. It also has obvious traps: rights boundaries,
identity resolution, property leakage, and aggregate metrics that can hide
family failures. That makes it useful as both a real benchmark lane and a public
demonstration of verification-first agent science.

## Evidence Trail

- [ThermoML source manifest](../../data/thermophysical/source_manifest.yaml)
- [ThermoML bounded Tb audit fixture](../../data/thermophysical/thermoml_tb_audit_fixture.yaml)
- [ThermoML family-stratified transfer benchmark review](../reviews/thermoml-tb-family-stratified-transfer-benchmark.md)
- [RESULT-0026 report](../../results/EXP-0020/RUN-0001/report.md)
- [RESULT-0026 Gate A report](../../results/EXP-0020/RUN-0001/gate_a_report.md)
- [RESULT-0026 replay note](../reviews/thermoml-result0026-gate-b-replay.md)
- [RESULT-0026 result metadata](../../results/EXP-0020/RUN-0001/result.yaml)
- [RESULT-0028 Gate B workflow bridge](../reviews/thermoml/result0028-gate-b-workflow-bridge.md)
- [RESULT-0028 report](../../results/EXP-0020/RUN-0002/report.md)
- [RESULT-0028 result metadata](../../results/EXP-0020/RUN-0002/result.yaml)
- [ThermoML 80-row local count preflight](../reviews/thermoml-tb-80row-local-count-preflight.md)
- [ThermoML 80-row source blocker](../reviews/thermoml-80-row-fixture-source-blocker.md)
- [ThermoML feasible expansion contract](../../data/thermophysical/thermoml_tb_feasible_expansion_contract.yaml)
- [ThermoML feasible-contract review](../reviews/thermoml/thermoml-tb-feasible-expansion-contract-task1084.md)
