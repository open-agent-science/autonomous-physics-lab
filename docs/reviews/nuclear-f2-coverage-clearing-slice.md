# Nuclear F2 Coverage-Clearing Slice — Review (TASK-0539)

**Task:** `TASK-0539`
**Campaign:** Nuclear Mass Surface
**Feature family:** F2 (high-error cluster), residual-free promotion path
**Status:** pre-score coverage check (no candidate metrics computed)
**Verdict:** `COVERAGE_GATE_CLEARS_F2_REMAINS_DIAGNOSTIC_ONLY`

## Scope

This note records a **pre-score coverage check** of the committed NMD-0003
AME2020 measured training surface against the F2 reopen coverage gate frozen by
[TASK-0478](./nuclear-f2-finer-taxonomy-preflight.md). It computes the frozen
residual-free finer-taxonomy bin populations deterministically from `Z`, `N`,
`A`, parity, magic-distance, and asymmetry only. It does **not** fit a
candidate, compute candidate metrics, score F2, run controls, add residual
features, write `PRED-*`/`CLAIM-*`/`KNOW-*`/`RESULT-*` artifacts, or fetch
external data. F2 stays `diagnostic_only`.

It is downstream of and consistent with:

- [`docs/reviews/nuclear-f2-finer-taxonomy-preflight.md`](./nuclear-f2-finer-taxonomy-preflight.md) (TASK-0478);
- [`docs/nuclear-residual-feature-no-leakage-contract.md`](../nuclear-residual-feature-no-leakage-contract.md) (F2 promotion path).

## Inputs

- Dataset: `data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml`
  (2309 committed measured AME2020 rows; post-AME2020 primary holdout excluded).
- Source pin: `source_dataset_sha256 =`
  `f36ca012704ad8d5ffd039f2b8f01b5553690685d447aee3bab0f9983edf9d52`
  (matches `data/nuclear_masses/nmd-0003-split-manifest.yaml`).
- Selection manifest written:
  `data/nuclear_masses/f2-coverage-selection-manifest.yaml`.
- Coverage helper: `physics_lab/engines/nuclear_f2_coverage.py`.

## Frozen Taxonomy And Floors (inherited from TASK-0478, not re-tuned)

Published magic numbers `{2, 8, 20, 28, 50, 82, 126, 184}`;
`dZ = min|Z - m|`, `dN = min|N - m|`, asymmetry `eta = (N - Z) / A`. Ordered,
first-match-wins bins:

1. `doubly_magic_near`: `dZ <= 1` AND `dN <= 1`.
2. `magic_z_near`: `dZ <= 1` AND `dN > 1`.
3. `magic_n_near`: `dN <= 1` AND `dZ > 1`.
4. `mid_shell_neutron_rich`: not (1-3) AND `eta >= 0.18`.
5. `mid_shell_balanced`: not (1-4) AND `eta < 0.18` AND `A >= 50`.
6. `light_a_lt_50`: not (1-5) AND `A < 50`.

Floors: per-cell `>= 5` training rows; multi-cell `>= 3` bins clearing the
per-cell floor, of which `>= 2` are outside the dominant near-magic family
(`doubly_magic_near`, `magic_z_near`, `magic_n_near`); total `>= 30` scored
training rows.

## Result — The Gate Clears

Deterministic `Z/N/A`-only bin populations on the 2309-row NMD-0003 training
surface:

| bin | count | role | near-magic family |
| --- | ---: | --- | :---: |
| `doubly_magic_near` | 70 | scored | yes |
| `magic_z_near` | 303 | scored | yes |
| `magic_n_near` | 207 | scored | yes |
| `mid_shell_neutron_rich` | 739 | scored | no |
| `mid_shell_balanced` | 895 | scored | no |
| `light_a_lt_50` | 95 | scored | no |

Gate criteria:

- bins clearing the per-cell floor (`>= 5`): **6** (need `>= 3`) — pass;
- of those, outside the near-magic family: **3** (`mid_shell_neutron_rich`,
  `mid_shell_balanced`, `light_a_lt_50`; need `>= 2`) — pass;
- total scored training rows: **2309** (need `>= 30`) — pass.

**The NMD-0003 training surface clears the TASK-0478 F2 reopen coverage gate on
all three criteria, with every declared bin populated above the per-cell floor.**

This is the opposite of the TASK-0449 collapse: there, the 11-row NMD-0002 slice
put 10 of 11 rows in a single near-magic cell and only one cell held `>= 2`
rows. On NMD-0003 no bin is empty, the smallest bin (`doubly_magic_near`, 70) is
14x the per-cell floor, and the two largest bins are mid-shell (non-near-magic),
so the partition cannot collapse to one cell. Note that `light_a_lt_50`, which
TASK-0478 expected might remain empty on the mid/heavy-curated NMD-0002 slice, is
populated (95 rows) on the broader NMD-0003 surface.

### Robustness To A Future Internal Holdout

A future F2 scoring task will hold out part of this surface for evaluation. Even
under a 70/30 train/holdout split, the smallest scored bin (`doubly_magic_near`,
70) retains roughly 49 train rows — still an order of magnitude above the
per-cell floor — so the coverage margin is not an artifact of scoring on the
full surface.

## Recommendation

The binding blocker identified by TASK-0449 and TASK-0478 — training-slice
coverage, not label design — is **cleared on NMD-0003**. The next move is to
open a **separate, maintainer-approved, gated F2 finer-taxonomy scoring task**
that:

1. uses the taxonomy and floors frozen by TASK-0478 and the bins frozen in
   `data/nuclear_masses/f2-coverage-selection-manifest.yaml`;
2. runs the full controls-first gauntlet (`matched_random`, `smooth_a`,
   `asymmetry_only`, `cluster_label_shuffle`) against the same `Z/N/A`-only
   label construction, with the `>= 0.25 MeV` survival margin on `full_known`;
3. authors no `PRED-*` entry and keeps F2 `diagnostic_only` until a separate
   downstream promotion task is approved.

This note does not start that scoring task and does not re-enter F2 into
predictive-eligible scope.

## Forbidden Post-Hoc Choices (unchanged, inherited from TASK-0478)

The bins, magic threshold (`1`), asymmetry edge (`0.18`), `A` cut (`50`), bin
order, and floors are frozen pre-score. They may not be re-tuned after seeing
residuals or scores; sub-floor bins may not be merged after inspection; no
forbidden input (target residual/mass/binding energy, baseline error rank,
residual quantile, source-status, AME-update flag) may enter label construction.

## Output Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `not_applicable` for a scientific claim;
  `COVERAGE_GATE_CLEARS_F2_REMAINS_DIAGNOSTIC_ONLY` for the protocol artifact.
- **Canonical destination:** this review note plus the pre-score selection
  manifest `data/nuclear_masses/f2-coverage-selection-manifest.yaml`.
- **Review tier:** `none` (no `RESULT-*`/`PRED-*` artifact).
- **Gate A status:** not attempted. **Gate B status:** not attempted.
- **Claim impact:** no claim change. **Knowledge impact:** no knowledge change.
- **Result artifact impact:** no `results/` artifact created or modified.
- **Limitations / blockers:** coverage is a pre-score gate, not a score; both the
  taxonomy and floors are TASK-0478 pre-score declarations amendable only before
  scoring; the surface is retrospective inside AME2020 measured rows, not a
  post-AME2020 reveal; F2 remains `diagnostic_only`.

## Public Wording Boundary

Allowed: "coverage gate clears", "pre-score coverage check", "diagnostic only",
"residual-free taxonomy". Forbidden: "discovery", "new nuclear law",
"near-magic regularity", "predicts" without a frozen `PRED-XXXX`, or any claim
that F2 explains nuclear masses.

## Limitations

- This is a coverage count, not an F2 score; clearing the gate does not imply any
  F2 candidate will survive the controls-first gauntlet.
- The floors and taxonomy are TASK-0478 declarations; they are not re-derived or
  re-tuned here.
- The training surface is retrospective inside AME2020 measured rows; the
  post-AME2020 primary holdout is excluded and unscored.
