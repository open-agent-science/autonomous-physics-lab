# Materials MD-0001 Benchmark Promotion Preflight

**Task:** `TASK-0566` (promotion preflight for the `TASK-0550` benchmark)
**Benchmark:** `materials-md0001-baseline-residual-benchmark` (`agent_runs/AGENT-RUN-0057/`)
**Recommended route:** **STAY REVIEW-NOTE ONLY (do not promote)**

This preflight runs the promotion checklist on the existing MD-0001 baseline
benchmark output. It adds no new metrics, tunes nothing, and makes no
material-discovery, material-selection, synthesis, device, biomedical, or
new-law claim.

## Inputs (all committed, no live fetch)

| Input | Source |
| --- | --- |
| Benchmark metrics | `agent_runs/AGENT-RUN-0057/metrics.json` (verdict `INCONCLUSIVE`) |
| Independent replay | `TASK-0578` — `REPRODUCED` exactly (`tests/test_materials_md0001_replay.py`) |
| Null-control audit | `TASK-0579` — `SIGNAL_SURVIVES_CONTROLS`, modest (p ≈ 0.04, n = 33), diagnostic only |
| Dataset / snapshot | MD-0001, db version 2025.09.25, sha256 `bdcd57f0…f7101` |
| Holdout / no-peek | `data/materials/holdout_manifest.yaml` |

## Promotion checklist

| Check | Status | Evidence |
| --- | --- | --- |
| Source provenance | PASS | Materials Project CC BY 4.0 with attribution + citation recorded on every dataset file. |
| Checksum references | PASS | Snapshot sha256 pinned and reproduced; replay (`TASK-0578`) matches the committed result exactly. |
| Holdout / no-peek binding | **BLOCK (for promotion)** | `holdout_manifest.promotion_boundary` sets `results_allowed: false`, `claims_allowed: false`, `benchmark_allowed_by_this_manifest: false`, `prediction_registry_allowed: false`. The frozen manifest forbids promoting a RESULT/PRED/CLAIM from this slice. |
| Axis separation | PASS | `formation_energy_per_atom` and `band_gap` are separate files and never pooled into one score. |
| Null controls | CONCERN | Band-gap composition signal survives shuffles but only modestly (p ≈ 0.04) on a small holdout (n = 33) — weak evidence; explicitly diagnostic. |
| Uncertainty / limitations | PASS (with caveat) | `uncertainty.basis = absent_in_source_snapshot`; computed-DFT stable binary oxides only — no experimental error bars, limited applicability. |
| Public wording | PASS | Benchmark verdict is `INCONCLUSIVE`; no discovery/claim wording anywhere. |
| Reproducibility | PASS | `TASK-0578` exact replay + CI guard against drift. |

## Decision

**Route: stay review-note only — do not package an `AGENT_PUBLISHED` RESULT
candidate.** Exactly one route is chosen, for four independent reasons:

1. **Manifest boundary (hard block):** the frozen MD-0001 holdout manifest
   explicitly disallows results, claims, and prediction-registry promotion from
   this slice. Gate A cannot be attempted without violating the no-peek contract.
2. **Benchmark verdict is `INCONCLUSIVE`:** the baselines are null/composition
   controls, not tuned models; there is no positive result to promote.
3. **Null-control signal is weak:** survives at p ≈ 0.04 with n = 33 — far below a
   defensible promotion margin; it is diagnostic, not evidence of a reusable law.
4. **Campaign is `SCAFFOLD_ONLY`:** the Materials campaign is still scaffold-stage.

## Output Routing Summary

- Task verdict: `DO_NOT_PROMOTE` (stay review-note only).
- Canonical destination: this preflight review.
- Review tier: `none`. No RESULT-* artifact is created (Gate A intentionally not
  attempted — forbidden by the frozen manifest).
- Gate A status: `not_attempted` (blocked by holdout-manifest promotion boundary).
- Gate B status: `not_applicable`.
- Claim impact: none. Knowledge impact: none.
- Campaign status: unchanged (`scaffold`); no `docs/campaigns/` update needed.

## What would change this verdict (future, separate tasks)

- Widen MD-0001 (more rows / additional chemistries) to grow the holdout beyond
  n = 33 so a null-control survival margin becomes meaningful.
- Only then, and only if the maintainer relaxes the holdout-manifest promotion
  boundary, reconsider a scoped baseline RESULT candidate.

## Limitations

- This preflight assesses promotion-readiness only; it neither creates nor blocks
  any scientific claim and adds no metrics.
- Computed-DFT values only; small pilot slice; band-gap result remains diagnostic.
