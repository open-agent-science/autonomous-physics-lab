# Scientific Ledger Hygiene Batch - 2026-07-09

Task: `TASK-0961`
Claim issue: `#1447`

## Scope

This batch is status accounting only. It synchronizes canonical hypothesis
statuses with already-committed `RESULT-*` evidence, records why `EXP-0019`
stays completed without a canonical result artifact, and drafts knowledge-entry
content for maintainer adoption.

No metric, result verdict, result review tier, claim status, prediction
registry entry, source row, or `KNOW-*` file is changed.

## Hypothesis Ledger Sync

| Hypothesis | Previous | New | Evidence and reason |
| --- | --- | --- | --- |
| `HYP-0001` | `TESTING` | `PARTIALLY_VALID` | `RESULT-0001`, `RESULT-0003`, and `RESULT-0013` support range-limited pendulum corrections; `RESULT-0017` records an overfit boundary. |
| `HYP-0002` | `TESTING` | `VALID_IN_RANGE` | `RESULT-0002` validates the configured damped-oscillator regime checks. |
| `HYP-0004` | `TESTING` | `VALID_IN_RANGE` | `RESULT-0005` reproduces the charged-lepton Koide quantity in the scoped benchmark. |
| `HYP-0005` | `TESTING` | `VALID_IN_RANGE` | `RESULT-0006` records the charged-lepton tau holdout as valid in range. |
| `HYP-0006` | `TESTING` | `VALID_IN_RANGE` | `RESULT-0007` and `RESULT-0020` are both `VALID`; `RESULT-0020` is independently Gate-B-validated and records 74/74 correct classifications. |
| `HYP-0007` | `TESTING` | `FALSIFIED` | `RESULT-0009` returned `INVALID` for the configured neutrino Koide consistency test. |
| `HYP-0008` | `TESTING` | `FALSIFIED` | `RESULT-0010` returned `INVALID` for the tested quark phase/Brannen variants. |
| `HYP-0009` | `TESTING` | `FALSIFIED` | `RESULT-0011` returned `INVALID` and is `AGENT_VALIDATED`; the standard target does not survive the committed family guardrails. |
| `HYP-0010` | `TESTING` | `INCONCLUSIVE` | `RESULT-0012` is `INCONCLUSIVE`; the line remains stress-test memory only. |
| `HYP-0011` | `TESTING` | `VALID_IN_RANGE` | `RESULT-0014` and `RESULT-0016` support the scoped weak-regime anharmonic benchmark; `RESULT-0016` is `AGENT_VALIDATED`. |
| `HYP-0012` | `TESTING` | `PARTIALLY_VALID` | `RESULT-0015` is `PARTIALLY_VALID`; `RESULT-0018` preserves the uncertainty/diagnostic boundary as `INCONCLUSIVE`. |
| `HYP-0013` | `FORMALIZED` | `VALID_IN_RANGE` | `RESULT-0019` is `VALID_IN_RANGE` for exact-reference software fixtures only. |
| `HYP-0014` | `TESTING` | `VALID_IN_RANGE` | `RESULT-0021` is `AGENT_VALIDATED` and `VALID_IN_RANGE` for the frozen MD-0002 slice. |
| `HYP-0015` | `TESTING` | `VALID_IN_RANGE` | `RESULT-0022` is `AGENT_VALIDATED` and `VALID_IN_RANGE` for the frozen DEBCat main-sequence slice. |
| `HYP-0016` | `TESTING` | `VALID_IN_RANGE` | `RESULT-0023` is `AGENT_VALIDATED` and `VALID_IN_RANGE` for the pinned FIRAS/Wien slice. |
| `HYP-0017` | `TESTING` | `VALID_IN_RANGE` | `RESULT-0024` is `AGENT_VALIDATED` and `VALID_IN_RANGE` for same-source high-mass DEBCat transfer. |
| `HYP-0018` | `TESTING` | `PARTIALLY_VALID` | `RESULT-0025` is `AGENT_VALIDATED` and `PARTIALLY_VALID`; uncertainty calibration remains unresolved. |
| `HYP-0020` | `TESTING` | `PARTIALLY_VALID` | `RESULT-0026` is `AGENT_VALIDATED` and `VALID_IN_RANGE`, while `RESULT-0028` records the esters/lactones failed-family negative control. |

Already synchronized before this task:

| Hypothesis | Status | Reason |
| --- | --- | --- |
| `HYP-0021` | `INCONCLUSIVE` | `RESULT-0027` already records control-sensitive exoplanet null-baseline memory. |
| `HYP-0022` | `INCONCLUSIVE` | `RESULT-0029` already records the ZnSe no-refit transfer failure/borderline outcome. |

Held without a status flip:

| Hypothesis | Status | Reason |
| --- | --- | --- |
| `HYP-0019` | `FORMALIZED` | `EXP-0019` is completed, but TASK-0875 intentionally held canonical RESULT packaging. The useful output is a software/convention quality floor, not a claim-bearing result. |

## EXP-0019 Resolution

`EXP-0019` remains `COMPLETED`, but its `data.notes` now records the TASK-0875
resolution:

- `AGENT-RUN-0086`, `docs/reviews/light-clock-quality-floor-routing-scorecard.md`,
  and regression tests preserve the useful TE-001 implementation evidence.
- Canonical RESULT packaging is held because it would duplicate an internal
  consistency check without empirical input, independent replay, or a new
  operational consumer.
- No claim or knowledge artifact follows from the light-clock consistency
  fixture.

## Draft Knowledge Proposals

These are maintainer-adoption drafts only. They are not `KNOW-*` files and do
not imply Gate C endorsement.

### Materials MD-0002

Proposed entry title: `MD-0002 formation-energy benchmark scope and public DOI`

Draft scope:

APL has a reusable MD-0002 stable ternary-oxide benchmark surface with a
checksum-pinned split, a published Zenodo record (`10.5281/zenodo.21207072`),
and `RESULT-0021` as `AGENT_VALIDATED` / `VALID_IN_RANGE`. The entry should
describe the formation-energy benchmark as a scoped dataset-and-baseline memory
surface, including the validation-independence clarification that the replay is
same-owner-different-account rather than independent-contributor validation.

Required no-claim wording:

- not a materials-discovery result;
- not a general formation-energy law;
- not external lab replication;
- validation tier and validation-independence qualifier must be visible.

Primary references:

- `results/EXP-0014/RUN-0001/result.yaml`
- `docs/reviews/md0002-zenodo-validation-independence-note.md`
- `docs/reviews/materials-md0002-zenodo-release-integrity.md`

### Stellar M-L

Proposed entry title: `DEBCat scoped mass-luminosity benchmark memory`

Draft scope:

APL has a frozen DEBCat main-sequence-compatible benchmark where `RESULT-0022`
is `AGENT_VALIDATED` / `VALID_IN_RANGE`: a train-fitted exponent near `4.53`
outperforms the fixed `alpha=3.5` baseline in the committed scope, and
`RESULT-0024` records a same-source high-mass transfer result. The entry should
preserve the single-source and population-boundary limitations.

Required no-claim wording:

- no universal mass-luminosity law;
- no stellar-evolution claim;
- no external-catalog replication until a future source task lands;
- same-owner validation-independence qualifiers remain visible where applicable.

Primary references:

- `results/EXP-0015/RUN-0001/result.yaml`
- `results/EXP-0017/RUN-0001/result.yaml`
- `docs/reviews/stellar-ml-result0022-maintainer-review-packet.md`
- `docs/reviews/stellar-result0024-high-mass-transfer-maintainer-review-packet.md`

### ThermoML Tb

Proposed entry title: `ThermoML Tb bounded Joback transfer benchmark memory`

Draft scope:

APL has a rights-bounded 40-row ThermoML normal-boiling-temperature fixture and
`RESULT-0026` as `AGENT_VALIDATED` / `VALID_IN_RANGE`. The entry should describe
the Joback transfer as aggregate-positive but family-dependent: 7/8 families
clear the 5 K margin and esters/lactones is an explicit failed-family boundary
captured by `RESULT-0028`.

TASK-0955 is still a review-ready extraction lane in the current tree, so this
draft does not treat an 80-row fixture as adopted canonical knowledge. If
TASK-0955 merges first, this draft should be reconciled to include its final
rights and fixture description before any `KNOW-*` file is created.

Required no-claim wording:

- no broad thermophysical-property validation;
- no chemical-design recommendation;
- no raw ThermoML archive vendoring;
- preserve the esters/lactones negative/control boundary.

Primary references:

- `results/EXP-0020/RUN-0001/result.yaml`
- `results/EXP-0020/RUN-0002/result.yaml`
- `docs/reviews/thermoml-result0026-gate-b-replay.md`
- `docs/reviews/thermoml-esters-lactones-negative-result-packaging.md`

### Exoplanet Snapshots

Proposed entry title: `Exoplanet PSCompPars snapshot and null-control memory`

Draft scope:

APL has a committed EXO-0001 PSCompPars snapshot workflow and `RESULT-0027` as
`AGENT_PUBLISHED` / `INCONCLUSIVE`: nearest-radius null controls match or beat
the frozen CK17-style baseline in highlighted true-mass transit-radius slices,
while minimum-mass slices remain underpowered. The entry should describe this as
control-sensitive negative/control memory, not a physical mass-radius law.

Required no-claim wording:

- no planet-composition, habitability, or universal mass-radius claim;
- no prospective prediction from nearest-radius controls;
- Gate B formal helper is blocked by command packaging until TASK-0959 or an
  equivalent workflow bridge lands;
- future source-version triggers remain separate from this memory entry.

Primary references:

- `results/EXP-0021/RUN-0001/result.yaml`
- `docs/reviews/exoplanet-result-0027-gate-b-replay.md`
- `docs/reviews/exoplanet-null-baseline-negative-memory-replay.md`

## Output Routing

- Task verdict: `not_applicable` for scientific evidence; `LEDGER_SYNCED` for
  the docs/status task.
- Canonical destination: hypothesis ledger edits, `EXP-0019` notes, and this
  review packet.
- Review tier: `none`; no `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*` artifact
  is created or promoted.
- Gate A status: not applicable.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: draft maintainer proposals only; no knowledge artifact
  created or edited.
- Limitations: status sync follows existing committed results; it does not
  strengthen result verdicts, cure validation-independence qualifiers, or decide
  any maintainer-only knowledge adoption.
