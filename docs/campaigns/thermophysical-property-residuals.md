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

**New active benchmark surface.** The first slice is already stronger than a
scaffold: `TASK-0869` packaged the bounded ThermoML `Tb` family-stratified
Joback transfer benchmark as `RESULT-0026`, now an `AGENT_VALIDATED`,
`VALID_IN_RANGE` result after formal Gate B workflow replay.

The evidence is deliberately narrow. The committed fixture contains 40 factual
audit rows, five rows from each of eight predeclared chemical families. The raw
ThermoML archive bytes and any substantial normalized corpus are not committed.
The source route is pinned to the NIST TRC ThermoML Archive DOI
`10.18434/mds2-2422` and the published archive SHA-256 recorded in
`data/thermophysical/source_manifest.yaml`.

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
clear the family margin. That failed family is part of the result, not a detail
to hide behind the aggregate win.

**Replay state:** the formal workflow Gate B bridge reproduced the aggregate
and per-family `RESULT-0026` metrics with zero drift and updated the result tier
to `AGENT_VALIDATED`. This validates the bounded 40-row `Tb` fixture only; it
does not remove the esters/lactones failed-family limitation.

**Not a claim:** `RESULT-0026` is not a universal validation of Joback, not a
new thermophysical law, and not a chemical-design or process-design result. It
does not say anything about critical temperature, vapor pressure, heat capacity,
or other ThermoML properties. `Tc` is intentionally excluded because Joback's
`Tc` estimator depends on `Tb`, which creates an upstream-property leakage path
for this first audit.

## Active Next Work

The campaign should move through two narrow gates:

1. **Local-only source-expansion preflight** - decide whether a larger
   ThermoML `Tb` fixture can be described with identity mapping, family counts,
   row class, and rights blockers before any values or archive bytes are
   committed.
2. **Failed-family negative RESULT packaging** - package the landed
   `esters/lactones` negative/control memory as a bounded result so future
   agents do not overstate aggregate transfer.

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

1. **Replay task** - formal Gate B bridge or independent replay of
   `RESULT-0026`.
2. **Source-readiness task** - local-only corpus-expansion or extraction
   preflight, including rights, identity-map, and family-count blockers.
3. **Negative-memory task** - failed-family or control-memory packaging only
   when a new failed slice appears or a task explicitly asks for public
   synthesis.
4. **Maintainer-review packet** - safe public wording after replay.

## Guardrails

Allowed current work:

- replay or formally bridge `RESULT-0026`;
- inspect committed fixture, source manifest, result metadata, and runner code;
- write source-readiness or negative-memory notes;
- draft task-queue entries for bounded future work.

Not allowed:

- rerun Gate A packaging as a new result;
- edit `RESULT-0026` metrics outside an explicit repair task;
- fetch or commit raw ThermoML archive bytes;
- commit a broader normalized ThermoML corpus;
- broaden from `Tb` to `Tc` or other properties;
- claim Joback is universally right, universally wrong, or physically
  explanatory.

## Recommended Next Tasks

1. `TASK-0936` - package the esters/lactones failed-family memory as a bounded
   negative/control RESULT without mutating `RESULT-0026`.
2. `TASK-0940` - prepare the maintainer decision packet for any 80-row
   ThermoML `Tb` expansion route: bounded public extract, local-only analysis,
   external permission, or no expansion. This happens before any row extraction.

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
