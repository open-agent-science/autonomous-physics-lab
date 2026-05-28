# Campaign Curator Brief — 2026-05-24

## Scope

This maintainer-facing brief reviews the latest merged agent results and turns
them into the next science queue. It does not promote claims, rewrite canonical
results, score reveal data, or mark any task as done.

Inputs reviewed:

- `AGENT-RUN-0030` / `TASK-0343` nuclear high-error cluster lane;
- `AGENT-RUN-0031` / `TASK-0351` nuclear local-curvature adversarial controls;
- `AGENT-RUN-0032` / `TASK-0361` exoplanet mass-radius baseline benchmark;
- `TASK-0363` atomic-clock Beloy 2021 source-artifact and covariance
  preflight;
- current `python3 scripts/apl_mission.py --json` live task candidates.

## Current Read

APL is moving in the right direction, but the current bottleneck is no longer
general infrastructure. The bottleneck is turning sandbox diagnostics and
source-preflight artifacts into a small number of reviewable science decisions
without creating endless audit loops.

The strongest current scientific surfaces are:

1. **Nuclear Mass Surface** — still the flagship. The shell-axis lane should
   stay diagnostic-only, but high-error clustering and local-curvature remain
   useful bounded residual surfaces.
2. **Exoplanet Mass-Radius** — now has the first executed baseline benchmark.
   It is not claim-ready, but it is the fastest path to a readable residual
   failure-map result.
3. **Atomic-Clock Residuals** — source discipline is now strong enough to
   attempt a tightly scoped Beloy 2021 direct-ratio row-curation task.
4. **Quantum Size Effects** — still active, but blocked on source/table
   curation rather than hypothesis search. Existing READY tasks are sufficient
   for the next agent wave.

## Latest Agent Results

### Nuclear: High-Error Cluster Lane

`TASK-0343` / `AGENT-RUN-0030` produced a `PARTIALLY_VALID` sandbox result.

Key signal:

- `HIGHCLUSTER-001`: full-known delta MAE `-0.629378` MeV;
- primary holdout delta `-0.624190` MeV;
- high-error subset delta `-2.501166` MeV;
- neutron-rich subset delta `-2.573153` MeV;
- matched controls were included and the best candidate beat the best control.

Interpretation:

- useful diagnostic evidence that high-error residual structure is not random;
- not blind prediction evidence, because high-error membership comes from
  committed residuals;
- needs adversarial stability/leakage testing before any predictive framing.

### Nuclear: Local Curvature

`TASK-0351` / `AGENT-RUN-0031` preserved a stronger local-curvature signal
through adversarial controls:

- `LOCAL-CURVATURE-001`: full-known delta MAE `-2.286136` MeV;
- holdout delta `-2.360363` MeV;
- strongest-control margin `+0.544296` MeV;
- subset win rate `13/19`.

Interpretation:

- this is the best current Nuclear sandbox signal;
- it still uses committed neighbor residual context and is not reveal-ready;
- the next step is no-leakage predictive-feature discipline, not registry
  expansion.

### Exoplanets: First Baseline Benchmark

`TASK-0361` / `AGENT-RUN-0032` ran the first exoplanet mass-radius baseline.
Verdict: `INCONCLUSIVE`.

Key signal:

- snapshot rows: `6291`;
- post-filter included rows: `4301`;
- `true_mass_with_transit_radius`: Chen-Kipping beats per-class median null
  (`0.158170` vs `0.242713` log10 RMSE);
- `minimum_mass_with_transit_radius`: Chen-Kipping loses to the null on only
  `2` eligible rows (`0.207728` vs `0.031917` log10 RMSE).

Interpretation:

- the true-mass axis is already useful for a residual failure map;
- the minimum-mass axis is too sparse and should be treated as diagnostic or
  excluded from headline metrics until a separate axis policy says otherwise;
- Exoplanets should move to residual-slice audits and a public-readable
  failure-map package.

### Atomic Clocks: Beloy 2021 Preflight

`TASK-0363` is `PARTIALLY_CLEARED`:

- arXiv-vs-Nature redistribution policy is locked;
- first extraction shape is locked to per-ratio totals;
- covariance verification protocol is locked;
- actual artifact retrieval and SI/covariance fact-check remain undone.

Interpretation:

- the campaign can now attempt a tightly scoped first real-row curation task;
- the task must halt if covariance or version drift cannot be verified;
- a small manifest stop-condition update should be done independently.

## Queue Decision

Add the next wave as independent tasks:

- `TASK-0367` — Nuclear high-error cluster adversarial stability audit.
- `TASK-0368` — Nuclear residual-feature no-leakage contract.
- `TASK-0369` — Exoplanet true-mass residual failure-map slice audit.
- `TASK-0370` — Exoplanet regime-specific residual scout.
- `TASK-0371` — Atomic Beloy 2021 direct-ratio row curation.
- `TASK-0372` — Atomic source-artifact version-drift stop condition.
- `TASK-0373` through `TASK-0379` — cross-campaign Fresh Data Intake
  protocol, templates, schemas, ledgers, stop conditions, readiness matrix, and
  validator follow-up.

Together with existing `TASK-0364` and `TASK-0356`, this restores a queue of
more than five parallel science tasks across Nuclear, Exoplanets, Atomic, and
Quantum without claim promotion.

Fresh-data ingestion remains the largest cross-campaign blocker. The next
infrastructure wave should standardize source-to-row handoffs so agents stop
solving source admissibility, checksums, redistribution, extraction ledgers,
and row-class semantics from scratch in every campaign.

## Guardrails

- Do not score `PRED-0063` through `PRED-0068`.
- Do not add new Nuclear registry entries from retrospective evidence.
- Do not treat high-error cluster labels as blind predictive features.
- Do not make exoplanet habitability, biosignature, or planet-priority claims.
- Do not ingest atomic-clock real rows without source artifact, checksum,
  covariance, and version-drift checks.
- Do not run Quantum formula search before direct rows or an explicit
  calibration-consistency waiver benchmark exists.

## Curator Verdict

`CONTINUE_WITH_BOUNDED_PARALLEL_SCIENCE_LANES`

The next wave should emphasize high-signal, low-overclaim tasks: Nuclear
leakage/stability gates, Exoplanet residual maps, Atomic source-to-row
discipline, and Quantum direct-source curation. This is the right shape for
APL's current stage: fast agent throughput, but with every result forced
through deterministic validation and conservative interpretation.
