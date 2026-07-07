# NMD-0003 Tier-1 Point-Only Frontier Prediction Freeze

- Task: `TASK-0933`
- Domain: nuclear physics (NMD-0003 GP residual mass extrapolation)
- Freeze outcome: **`FREEZE_EXECUTED`** (tier-1, `freeze_tier: point_only`)
- Authorization: maintainer Gate C decision of 2026-07-05 — Option A on the
  `TASK-0929` decision packet
  ([nmd0003-two-tier-point-only-freeze-contract-packet.md](./nmd0003-two-tier-point-only-freeze-contract-packet.md))
- Registered entries: `PRED-0069` (GP point forecasts), `PRED-0070`
  (DZ10-published-variant comparator), `PRED-0071` (frozen liquid-drop
  baseline-of-record comparator), `PRED-0072` (`smooth_a_gp` predeclared
  control comparator), all under `prediction_registry/nuclear_masses/`
- Registered at: `2026-07-05T19:35:00Z`; source commit:
  `d2ad3d192cce50eaa08d776a39e2ed8c1c712d88`
- Target set: `FRONTIER-PRED-TARGETS-0001`
  (`data/nuclear_masses/frontier_prediction_targets.yaml`), 37 candidate
  targets across 4 extrapolation-dominated shell regions; **37 survived**
  freeze-time source-state re-verification, **0 dropped**
- Registry state: `REGISTERED` / reveal-pending; nothing is revealed, scored,
  or compared by this freeze

This is the project's first prospective prediction freeze under the two-tier
amendment. It freezes **central values only**. The GP posterior standard
deviation and every derived interval quantity are excluded from every payload:
they are the miscalibrated quantity (`TASK-0899`) and are not frozen, recorded,
or cited anywhere in this freeze.

## Mandatory Caveat (verbatim from the approved packet)

> **Tier-1 point-only freeze — mandatory caveat.** The NMD-0003 predictive
> uncertainty calibration **failed** the no-peek audit (`TASK-0899`): all three
> predeclared route families missed the predeclared coverage and
> standardized-residual conditions (best family ~`0.62` 1-sigma coverage,
> RMS standardized residual ~`4.3`). **Calibrated prediction intervals are
> unavailable.** This freeze registers **point (central-value) forecasts
> only**. It makes **no interval or uncertainty claim**, **no** statement of
> trustworthy 1-sigma / 2-sigma predictive coverage, and **no** prediction-
> readiness or "prediction-ready" wording. It is scored at reveal by **MAE and
> rank against frozen baselines only**. It is **not** a reveal result and **not**
> a blind-prediction success until an admissible source is revealed and scored.
> This tier-1 freeze does **not** unblock `TASK-0827`: `TASK-0827` remains the
> interval-bearing freeze and remains **blocked** for interval-bearing freezes
> until calibration is validated on a fresh surface per the `TASK-0925`
> contract. It establishes **no** nuclear-mass law, **no** broad mass formula,
> and **no** discovery.

The same caveat is carried, unweakened, inside every `PRED-*` artifact of this
freeze (first `limitations` item) and in the `TASK-0933` PR body.

## What Was Frozen

All four surfaces are reproduced deterministically from committed inputs by one
pinned command (no re-fit policy change, no hyperparameter retune, no baseline
change, no network access, no measured value read for any target):

```bash
python3 scripts/freeze_nmd0003_tier1_point_only_frontier.py \
  --source-commit d2ad3d192cce50eaa08d776a39e2ed8c1c712d88 \
  --registered-at 2026-07-05T19:35:00Z \
  --output-dir prediction_registry/nuclear_masses
```

| Entry | Frozen surface | Code reference | Engine version | Frozen parameter source |
| --- | --- | --- | --- | --- |
| `PRED-0069` | `model_nmd0003_residual_gp_zn_rbf` posterior **mean** (RESULT-0025) | `physics_lab/engines/nmd0003_residual_gp.py` | `0.1.0` | Deterministic refit from committed training + gate inputs; hyperparameters must equal RESULT-0025 exactly |
| `PRED-0070` | DZ10 published-equation variant (`nmd0003_dz10_published_equation_variant_v2`) | `physics_lab/engines/nmd0003_duflo_zuker_baseline.py` | `nmd0003_dz10_published_equation_variant_v2` | Coefficient vector pinned verbatim from committed `agent_runs/AGENT-RUN-0078/metrics.json` |
| `PRED-0071` | Frozen liquid-drop baseline of record (`nmd0003_train_fitted_ols`) | `physics_lab/engines/nuclear_mass_baselines.py` | `0.1.0` | Committed coefficients in `data/nuclear_masses/nmd-0003-stratified-baseline-gate.yaml` |
| `PRED-0072` | `smooth_a_gp` predeclared control (RESULT-0025 survival test) | `physics_lab/engines/nmd0003_residual_gp.py` | `0.1.0` | Deterministic refit with the engine control's exact initialisation, bounds, optimizer, and linear algebra |

Input file hashes (sha256), also recorded inside every `PRED-*` entry:

| Input | sha256 |
| --- | --- |
| `agent_runs/AGENT-RUN-0078/metrics.json` | `7bb12460b4489233e988db93520f1c2a059557f53171526d5c24e95e0dda2830` |
| `data/nuclear_masses/frontier_prediction_targets.yaml` | `27e624dade2aec22b43d92c8b007348d293e5f2cec1a6a37043a063e1c340307` |
| `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml` | `ec2e9917a28120de2cc7914570612b2f581a521aa1b5ff1bbd01549f63f66c68` |
| `data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml` | `f36ca012704ad8d5ffd039f2b8f01b5553690685d447aee3bab0f9983edf9d52` |
| `data/nuclear_masses/nmd-0003-stratified-baseline-gate.yaml` | `2988c2eb28e0e1bee783bd4824a9680313b5ef81f1e9ae96698893e4525b8cd2` |
| `data/nuclear_masses/post_ame2020_holdout.yaml` | `47bfe520df8ca4a95c1614192c5da165782b2308ba58110e6832afb1b8151e49` |
| `results/EXP-0018/RUN-0001/metrics.json` | `294405890bb90e0079ca34fb950d52738d482fc95dce861df27d04e9f97b7bbc` |

## Frozen-Surface Identity Checks (all exact, enforced before any freeze)

The freeze runner refuses to emit anything (`FREEZE_BLOCKED`) unless the
reproduced surfaces equal the committed published records:

| Identity check | Reproduced | Committed record | Status |
| --- | --- | --- | --- |
| Frozen liquid-drop baseline post-AME2020 holdout MAE (MeV) | `2.979273` | `2.979273` (RESULT-0025) | exact |
| GP-corrected post-AME2020 holdout MAE (MeV) | `0.462129` | `0.462129` (RESULT-0025) | exact |
| GP hyperparameters (`sigma_f`, `l`, `sigma_n`, log-ML) | `20.742879 / 0.136302 / 0.432527 / -2458.565811` | identical (RESULT-0025) | exact |
| `smooth_a_gp` post-AME2020 holdout MAE (MeV) | `2.331441` | `2.331441` (RESULT-0025) | exact |
| DZ10-published-variant post-AME2020 holdout MAE (MeV) | `1.256383` | `1.256383` (AGENT-RUN-0078) | exact |
| DZ10 coefficient vector | freeze uses the committed AGENT-RUN-0078 vector verbatim | deterministic refit reproduces it within `2e-12` per coefficient | pinned + cross-checked |

DZ10 refit note: a freeze-time ordinary-least-squares refit reproduced the
committed coefficient vector to within one unit in the last published decimal
(`surface_asymmetry` differs by `1e-12`, i.e. last-ulp `lstsq` variance across
linear-algebra backends). To keep the frozen comparator a deterministic
function of committed bytes, the frozen DZ10 vector is the committed
AGENT-RUN-0078 record itself; the refit is retained as a `<= 2e-12` per-
coefficient cross-check, and the holdout-MAE identity check above remains
exact. No gate was weakened.

Baseline-of-record citation note: the approved packet cites the frozen
liquid-drop comparator's lineage as "RESULT-0012
(`results/EXP-0012/RUN-0001/result.yaml`)". The committed file at that path is
`RESULT-0015` (the origin of the inherited liquid-drop family), and the
operative frozen coefficients — the null the GP correction is layered on, with
the packet's quoted post-AME2020 MAE `2.979273` MeV — are the
`nmd0003_train_fitted_ols` audit-baseline coefficients in the committed
stratified baseline gate file. The `PRED-*` entries pin `RESULT-0015` plus the
gate file accordingly; the packet's result-id citation appears to be an id
slip, recorded here rather than silently corrected.

## Source-State Re-Verification And Dropped-Target Ledger

Per the reveal protocol
([nuclear-prediction-reveal-protocol.md](../nuclear-prediction-reveal-protocol.md)),
every `FRONTIER-PRED-TARGETS-0001` target identity was re-screened at freeze
time against the committed in-repo measured surfaces — by `(Z, N)` and by
nuclide id — using:

- `data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml` (2309 rows);
- `data/nuclear_masses/post_ame2020_holdout.yaml` (all rows, primary and
  non-primary);
- `data/nuclear_masses/nmd-0002-curated-measured-slice.yaml`.

Result: **37 of 37 targets survived; the dropped-target ledger is empty** (no
target gained a committed measured value between design time and freeze time).
Had any target been dropped, it would have been recorded here and **not**
replaced. The manifest's excluded committed neighbors (for example `Ni-78`,
`Sn-132`, `Cd-130`) were verified absent from the target list and were **not**
added. The screen covers committed in-repo files only; it is not a positive
claim that any target is unmeasured in the wider literature.

## Frozen Per-Target Central Values (binding energy, MeV)

Values below are the frozen `predicted_value_mev` payloads of the four
`PRED-*` entries (the registry files are the artifacts of record; this table is
a review convenience). Quantity semantics: total binding energy in MeV, the
native output space of all four committed surfaces.

| Nuclide | Z | N | A | Region | GP mean (`PRED-0069`) | DZ10 v2 (`PRED-0070`) | Liquid drop (`PRED-0071`) | `smooth_a_gp` (`PRED-0072`) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| V-73 | 23 | 50 | 73 | n50_below_ni78 | 528.32988 | 533.693169 | 524.536269 | 521.125894 |
| Cr-74 | 24 | 50 | 74 | n50_below_ni78 | 555.779662 | 559.209216 | 550.029752 | 546.718497 |
| Mn-75 | 25 | 50 | 75 | n50_below_ni78 | 579.258272 | 580.687734 | 571.776464 | 568.603351 |
| Fe-76 | 26 | 50 | 76 | n50_below_ni78 | 603.101877 | 603.945266 | 594.619083 | 591.617841 |
| Co-77 | 27 | 50 | 77 | n50_below_ni78 | 622.297889 | 623.360675 | 613.835425 | 611.033987 |
| Fe-78 | 26 | 52 | 78 | n50_below_ni78 | 606.848497 | 605.181099 | 596.888852 | 594.309096 |
| Co-79 | 27 | 52 | 79 | n50_below_ni78 | 626.819193 | 625.633362 | 617.222042 | 614.879759 |
| Ni-80 | 28 | 52 | 80 | n50_below_ni78 | 647.013054 | 647.840686 | 638.672878 | 636.577925 |
| Ni-82 | 28 | 54 | 82 | n50_below_ni78 | 648.810217 | 649.883736 | 642.073738 | 640.480894 |
| Ru-126 | 44 | 82 | 126 | n82_neutron_rich_cd_sn | 1000.42961 | 1005.491819 | 1000.257949 | 1001.758366 |
| Rh-127 | 45 | 82 | 127 | n82_neutron_rich_cd_sn | 1017.483991 | 1021.896649 | 1016.130041 | 1017.962211 |
| Pd-128 | 46 | 82 | 128 | n82_neutron_rich_cd_sn | 1036.545874 | 1039.925152 | 1033.050311 | 1035.20265 |
| Ag-129 | 47 | 82 | 129 | n82_neutron_rich_cd_sn | 1053.885058 | 1054.95139 | 1047.366535 | 1049.817412 |
| Rh-129 | 45 | 84 | 129 | n82_neutron_rich_cd_sn | 1020.096868 | 1025.325263 | 1021.392001 | 1023.842878 |
| Pd-130 | 46 | 84 | 130 | n82_neutron_rich_cd_sn | 1040.336448 | 1044.025967 | 1038.992509 | 1041.710875 |
| Ag-131 | 47 | 84 | 131 | n82_neutron_rich_cd_sn | 1058.948476 | 1059.695603 | 1054.00239 | 1056.948842 |
| Cd-133 | 48 | 85 | 133 | n82_neutron_rich_cd_sn | 1079.543526 | 1078.53811 | 1072.54945 | 1075.807873 |
| Er-194 | 68 | 126 | 194 | n126_rprocess_waiting_point | 1489.617427 | 1486.759394 | 1489.919319 | 1491.424025 |
| Yb-196 | 70 | 126 | 196 | n126_rprocess_waiting_point | 1515.429981 | 1514.905319 | 1515.789679 | 1517.922815 |
| Hf-198 | 72 | 126 | 198 | n126_rprocess_waiting_point | 1539.856497 | 1539.958867 | 1539.440903 | 1542.295304 |
| W-200 | 74 | 126 | 200 | n126_rprocess_waiting_point | 1563.000519 | 1563.0307 | 1560.923059 | 1564.523789 |
| Os-202 | 76 | 126 | 202 | n126_rprocess_waiting_point | 1583.482144 | 1584.203151 | 1580.284316 | 1584.566828 |
| Pt-204 | 78 | 126 | 204 | n126_rprocess_waiting_point | 1602.101221 | 1603.553152 | 1597.571039 | 1602.3708 |
| Yb-198 | 70 | 128 | 198 | n126_rprocess_waiting_point | 1522.664914 | 1516.370074 | 1522.614643 | 1525.469044 |
| Hf-200 | 72 | 128 | 200 | n126_rprocess_waiting_point | 1547.978077 | 1542.677679 | 1547.182645 | 1550.783375 |
| W-202 | 74 | 128 | 202 | n126_rprocess_waiting_point | 1571.092875 | 1566.980327 | 1569.580231 | 1573.862743 |
| Os-204 | 76 | 128 | 204 | n126_rprocess_waiting_point | 1590.949463 | 1589.322258 | 1589.855171 | 1594.654933 |
| O-28 | 8 | 20 | 28 | light_neutron_rich_drip_o_ne_mg | 164.009032 | 162.378181 | 152.275032 | 151.358459 |
| O-30 | 8 | 22 | 30 | light_neutron_rich_drip_o_ne_mg | 159.105785 | 158.273778 | 145.238897 | 143.855054 |
| F-31 | 9 | 22 | 31 | light_neutron_rich_drip_o_ne_mg | 186.479455 | 183.309891 | 175.602135 | 173.955472 |
| Ne-32 | 10 | 22 | 32 | light_neutron_rich_drip_o_ne_mg | 213.853425 | 210.522142 | 206.491794 | 204.567548 |
| Ne-34 | 10 | 24 | 34 | light_neutron_rich_drip_o_ne_mg | 215.400693 | 209.771919 | 202.638649 | 200.142245 |
| Na-35 | 11 | 24 | 35 | light_neutron_rich_drip_o_ne_mg | 237.755547 | 233.158121 | 229.398848 | 226.625782 |
| Na-37 | 11 | 26 | 37 | light_neutron_rich_drip_o_ne_mg | 238.561302 | 234.165911 | 226.096985 | 222.841405 |
| Mg-38 | 12 | 26 | 38 | light_neutron_rich_drip_o_ne_mg | 263.415118 | 261.526453 | 255.84128 | 252.40085 |
| Mg-40 | 12 | 28 | 40 | light_neutron_rich_drip_o_ne_mg | 263.518619 | 264.627663 | 252.932528 | 249.280159 |
| Mg-42 | 12 | 30 | 42 | light_neutron_rich_drip_o_ne_mg | 260.201134 | 261.572253 | 248.512447 | 244.895348 |

No posterior standard deviation, interval multiplier, or any derived
uncertainty value exists for any row, in any artifact of this freeze. Every
`uncertainty_mev` field is intentionally `null`.

## Reveal Conditions (point-only)

- **Admissible source classes:** the next AME/NUBASE-class evaluation
  published after `2026-07-05T19:35:00Z` (source class A), or a qualifying
  flagged Penning-trap / storage-ring measurement subset in a watched frontier
  region — each admitted only by a separate maintainer-reviewed reveal task
  with its own source manifest, checksum record, registry snapshot, and
  no-peek audit per the reveal protocol and
  [nuclear-reveal-source-readiness-checklist.md](../nuclear-reveal-source-readiness-checklist.md).
- **Reveal metrics:** MAE (MeV) of the GP point forecast over the revealed
  subset, per region and pooled, and **rank** of the GP against the three
  frozen comparators on the same revealed subset — **only**. No interval
  coverage, sharpness, or calibration metric exists or is in scope for tier-1.
- **Partial reveals** follow the reveal protocol: only eligible revealed
  targets are scored; unrevealed targets stay unchanged and remain eligible.
- Until an admissible post-freeze source exists, the entries sit in a no-peek
  `REGISTERED` / reveal-pending state. Registration is not a reveal result and
  not a success verdict.

## Disjointness Requirement (recorded with the Gate C approval)

Any future tier-2 calibration-validation set (set A) under the `TASK-0925`
fresh-surface contract must be **disjoint from these 37 frozen tier-1
targets**; tier-2 interval coverage is never reported in-sample on them. This
requirement is carried inside every `PRED-*` entry of this freeze. A future
tier-2 upgrade, if calibration is ever validated on a fresh surface, adds
intervals as an additive amendment bound to these already-frozen central
values without re-freezing or re-timing them.

## Determinism, Tooling, And Security Notes

- The freeze runner `scripts/freeze_nmd0003_tier1_point_only_frontier.py` is a
  new executor-visible `scripts/` path (treat as security-relevant on review):
  it is deterministic, performs no network access, reads only committed
  repository files, and refuses to write anything unless every identity check
  passes.
- Determinism was verified operationally: two independent runs of the pinned
  command produced **byte-identical** `PRED-*` files and freeze summaries.
- `tests/test_nmd0003_tier1_frontier_freeze.py` guards the frozen artifacts:
  structural point-only invariants, caveat and disjointness presence,
  re-verified target identity, exact recompute of the two closed-form
  comparator surfaces, and (as a `full_repo` smoke test) the full GP /
  `smooth_a_gp` surface recompute with all identity checks.
- The prediction-entry schema gained one optional field, `freeze_tier`
  (`point_only` | `interval_bearing`), implementing the two-tier amendment
  marker; all pre-existing entries remain valid and unchanged.
- `prediction_registry/nuclear_masses/registry_summary.yaml` was regenerated
  with the committed report script (64 entries; all remain reveal-blocked
  pending source preflight, no-peek review, and maintainer approval).

## Output-Routing Summary

- Task verdict: `FREEZE_EXECUTED` — tier-1 point-only freeze executed under
  the approved `TASK-0929` amendment (Option A).
- Canonical destinations: `prediction_registry/nuclear_masses/PRED-0069.yaml`
  … `PRED-0072.yaml` (REGISTERED, reveal-pending) plus this review note.
- Review tier: prediction-registry entries under Gate A; no `RESULT-*` created
  or modified.
- Gate A status (PRED mechanical conditions): **met** — no-peek source state
  re-verified at freeze time; frozen model references with `code_reference`,
  engine versions, pinned command, git commit, and input sha256 hashes
  recorded; named target set (`FRONTIER-PRED-TARGETS-0001`); reveal conditions
  explicit (MAE + rank vs frozen baselines only); non-claim ceiling carried;
  schema validation passes strict repo validation.
- Gate B status: not attempted here; the pinned command is replayable and the
  committed test suite re-verifies the frozen values deterministically.
- Prediction impact: four new tier-1 `PRED-*` entries registered; no existing
  `PRED-*` entry was edited, re-timed, or superseded.
- Claim impact: **none** — no `CLAIM-*` created, edited, or promoted.
- Knowledge impact: **none** — no `KNOW-*` created or edited.
- `TASK-0827` impact: **none** — not modified; remains BLOCKED as the
  interval-bearing freeze. This freeze does not unblock it.
- `TASK-0925` impact: **none** — remains the BLOCKED protocol-only tier-2
  gate; referenced only for the disjointness requirement above.
- Limitations and blockers:
  - Point-only pre-registration: no interval, uncertainty, coverage, or
    prediction-readiness claim exists or may be derived from this freeze
    (`TASK-0899` calibration failure stands).
  - Not a reveal result: scoring waits for an admissible post-freeze source
    under the reveal protocol; negative or inconclusive reveal outcomes must
    stay visible when scored.
  - Scope inherited from RESULT-0025: one frozen NMD-0003 residual surface
    over one frozen liquid-drop audit baseline; a different baseline or model
    class would shift the residual surface.
  - The source-state screen covers committed in-repo files only; it is not a
    positive claim that any target is unmeasured in the wider literature.

## External Anchor (2026-07-07, TASK-0945)

The sealing recorded above is now third-party verifiable without trusting
repository branch history:

- Annotated tag: `pred-nmd0003-tier1-20260705` at freeze commit `f1eba9a2`.
- GitHub Release (capsule attached):
  <https://github.com/open-agent-science/autonomous-physics-lab/releases/tag/pred-nmd0003-tier1-20260705>
- Zenodo deposit (published 2026-07-07, CC BY 4.0): version DOI
  [10.5281/zenodo.21240451](https://doi.org/10.5281/zenodo.21240451),
  concept DOI 10.5281/zenodo.21240450, record
  <https://zenodo.org/records/21240451>.
- Capsule `nmd0003-tier1-anchor-v1.0.0.zip`: 127,617 bytes, SHA-256
  `82e3a872ad5e3fb1cd7841d29ed53ef3223945a73ba64e71866f0de209804272`
  (Zenodo-verified md5 `af2c3234796f0357c6a4263ffc04b1ab`), containing the
  four sealed PRED entries plus this note byte-identical to `f1eba9a2`.
- Note on self-reference: the anchored capsule froze this file's pre-anchor
  bytes; this section postdates the capsule by design. Any capsule rebuild
  is a v1.0.1 with refreshed pins and a new version DOI — the builder
  (`scripts/package_nmd0003_tier1_anchor_capsule.py`) fails loudly on the
  stale pin to prevent silently shadowing the published v1.0.0.
- Any future reveal grading must cite the anchored capsule checksum above.

