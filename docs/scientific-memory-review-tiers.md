# Scientific Memory Review Tiers

> Generated from canonical scientific-memory artifacts. Refresh with
> `python3 scripts/apl_scientific_memory_index.py --write`.

This index separates publication and review tiers so `AGENT_PUBLISHED`
evidence is not mistaken for maintainer-endorsed claims. It is a
visibility layer only: it does not promote, re-tier, or edit canonical
scientific artifacts.

## Tier Meaning

| Tier | Meaning | Default next action |
| --- | --- | --- |
| `AGENT_PUBLISHED` | Agent-created canonical evidence after Gate A. | Independent replay or maintainer review, depending on artifact class. |
| `AGENT_VALIDATED` | A different agent reproduced the artifact through Gate B. | Maintainer review before stronger interpretation. |
| `MAINTAINER_REVIEWED` | Maintainer endorsed the artifact tier/scope. | External replication or monitored reveal when relevant. |
| `EXTERNAL_REPLICATED` | External source, contributor, or reveal independently replicated the artifact. | Preserve as strongest public memory. |

## Counts

| Tier | RESULT | PRED | CLAIM | KNOW | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| `AGENT_PUBLISHED` | 1 | 1 | 0 | 0 | 2 |
| `AGENT_VALIDATED` | 16 | 0 | 0 | 0 | 16 |
| `MAINTAINER_REVIEWED` | 0 | 1 | 2 | 0 | 3 |
| `EXTERNAL_REPLICATED` | 0 | 0 | 0 | 0 | 0 |

## AGENT_PUBLISHED

| Class | Artifact | Status | Independence | Next action | Path |
| --- | --- | --- | --- | --- | --- |
| `PRED` | `PRED-0001` - Prospective exoplanet second-snapshot protocol outcome forecast | `REGISTERED` | `n/a` | `reveal-needed` | [`prediction_registry/exoplanet_mass_radius/PRED-0001.yaml`](../prediction_registry/exoplanet_mass_radius/PRED-0001.yaml) |
| `RESULT` | `RESULT-0031` - Stellar M-L CHARA fixed-relation transfer - frozen RESULT-0022 relation wins narrowly but misses the predeclared margin | `INCONCLUSIVE` | `n/a` | `replay-needed` | [`results/EXP-0023/RUN-0001/result.yaml`](../results/EXP-0023/RUN-0001/result.yaml) |

## AGENT_VALIDATED

| Class | Artifact | Status | Independence | Next action | Path |
| --- | --- | --- | --- | --- | --- |
| `RESULT` | `RESULT-0011` - Particle-Mass Relation Falsifier MVP | `INVALID` | `same_account_different_tool` | `maintainer-review-needed` | [`results/EXP-0009/RUN-0001/result.yaml`](../results/EXP-0009/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0016` - Anharmonic Oscillator Period Benchmark | `VALID_IN_RANGE` | `same_account_different_tool` | `maintainer-review-needed` | [`results/EXP-0011/RUN-0002/result.yaml`](../results/EXP-0011/RUN-0002/result.yaml) |
| `RESULT` | `RESULT-0017` - Pendulum Formula Discovery — Gauntlet (101 Candidates) | `OVERFITTED` | `independent` | `maintainer-review-needed` | [`results/EXP-0001/RUN-0006/result.yaml`](../results/EXP-0001/RUN-0006/result.yaml) |
| `RESULT` | `RESULT-0018` - Nuclear F2 Component-Ablation Diagnostic Preflight Result | `INCONCLUSIVE` | `independent` | `maintainer-review-needed` | [`results/EXP-0012/RUN-0002/result.yaml`](../results/EXP-0012/RUN-0002/result.yaml) |
| `RESULT` | `RESULT-0019` - Textbook Stefan-Boltzmann Exact-Reference Software Fixture Result | `VALID_IN_RANGE` | `same_account_different_tool` | `maintainer-review-needed` | [`results/EXP-0013/RUN-0001/result.yaml`](../results/EXP-0013/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0020` - Dimensional Analysis Validator Live 74-Item Replay | `VALID` | `independent` | `maintainer-review-needed` | [`results/EXP-0006/RUN-0007/result.yaml`](../results/EXP-0006/RUN-0007/result.yaml) |
| `RESULT` | `RESULT-0021` - Materials MD-0002 Formation-Energy Cation-Pair Baseline Benchmark (stable ternary oxides) | `VALID_IN_RANGE` | `same_owner_different_account` | `maintainer-review-needed` | [`results/EXP-0014/RUN-0001/result.yaml`](../results/EXP-0014/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0022` - Stellar M-L DEBCat Controlled Baseline Benchmark — textbook alpha=3.5 inadequate as sole baseline on the frozen main-sequence slice | `VALID_IN_RANGE` | `independent` | `maintainer-review-needed` | [`results/EXP-0015/RUN-0001/result.yaml`](../results/EXP-0015/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0023` - FIRAS/Wien Spectral-Domain Peak Consistency Slice (pinned COBE/FIRAS absolute monopole) | `VALID_IN_RANGE` | `same_owner_different_account` | `maintainer-review-needed` | [`results/EXP-0016/RUN-0001/result.yaml`](../results/EXP-0016/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0024` - Stellar M-L High-Mass DEBCat Transfer - frozen RESULT-0022 relation survives stage-matched controls | `VALID_IN_RANGE` | `same_owner_different_account` | `maintainer-review-needed` | [`results/EXP-0017/RUN-0001/result.yaml`](../results/EXP-0017/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0025` - NMD-0003 GP Residual Extrapolation Replay - control-surviving gain with miscalibrated uncertainty | `PARTIALLY_VALID` | `independent` | `maintainer-review-needed` | [`results/EXP-0018/RUN-0001/result.yaml`](../results/EXP-0018/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0026` - ThermoML Tb bounded family-stratified Joback transfer benchmark | `VALID_IN_RANGE` | `same_owner_different_account` | `maintainer-review-needed` | [`results/EXP-0020/RUN-0001/result.yaml`](../results/EXP-0020/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0027` - Exoplanet EXO-0001 null-baseline control-sensitive negative result | `INCONCLUSIVE` | `independent` | `maintainer-review-needed` | [`results/EXP-0021/RUN-0001/result.yaml`](../results/EXP-0021/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0028` - ThermoML Tb esters/lactones failed-family negative control | `INVALID` | `independent` | `maintainer-review-needed` | [`results/EXP-0020/RUN-0002/result.yaml`](../results/EXP-0020/RUN-0002/result.yaml) |
| `RESULT` | `RESULT-0029` - Quantum ZnSe no-refit contract transfer inconclusive control result | `INCONCLUSIVE` | `independent` | `maintainer-review-needed` | [`results/EXP-0022/RUN-0001/result.yaml`](../results/EXP-0022/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0030` - Dimensional Validator Exact-v2 Frozen Calibration Score | `VALID` | `independent` | `maintainer-review-needed` | [`results/EXP-0006/RUN-0008/result.yaml`](../results/EXP-0006/RUN-0008/result.yaml) |

## MAINTAINER_REVIEWED

| Class | Artifact | Status | Independence | Next action | Path |
| --- | --- | --- | --- | --- | --- |
| `CLAIM` | `CLAIM-0001` - Range-Limited Approximation of the Amplitude-Dependent Pendulum Period | `PARTIALLY_SUPPORTED` | `n/a` | `external-replication-optional` | [`claims/CLAIM-0001-pendulum-period-amplitude.md`](../claims/CLAIM-0001-pendulum-period-amplitude.md) |
| `CLAIM` | `CLAIM-0009` - Anharmonic Oscillator Period Benchmark | `PARTIALLY_SUPPORTED` | `n/a` | `external-replication-optional` | [`claims/CLAIM-0009-anharmonic-oscillator-period.md`](../claims/CLAIM-0009-anharmonic-oscillator-period.md) |
| `PRED` | `PRED-0001` - FRB Catalog-1 pre-T exposure-only repeater-propensity scores | `REGISTERED` | `n/a` | `external-reveal-needed` | [`prediction_registry/radio_transients/PRED-0001.yaml`](../prediction_registry/radio_transients/PRED-0001.yaml) |

## EXTERNAL_REPLICATED

_No artifacts in this tier._

## Historical Pre-Tier Artifacts

95 canonical artifacts predate the explicit review-tier
protocol. They are preserved and discoverable, but they sit outside the
review-trust ladder above and must not be read as reviewed or endorsed.

| Class | Count |
| --- | ---: |
| `RESULT` | 14 |
| `PRED` | 64 |
| `CLAIM` | 8 |
| `KNOW` | 9 |
| Total | 95 |

Full list: [`docs/historical-scientific-memory.md`](historical-scientific-memory.md).

## Notes

- Historical pre-tier artifacts (missing `review_tier`) are summarized
  above and listed in the historical ledger only; they are not part of
  the trust ladder, and their canonical files stay unchanged.
- `PRED` entries often need reveal or source-state review rather than Gate B
  replay.
- `CLAIM` and `KNOW` artifacts remain maintainer-sensitive in Phase 1 even
  when a future agent creates draft supporting material.
- `Independence` is a separate axis from the tier: `AGENT_VALIDATED`
  means replayed; the independence value records who replayed relative
  to the publisher (see docs/result-promotion-protocol.md, Validation
  Independence). `not_recorded` marks replays that predate the axis.
