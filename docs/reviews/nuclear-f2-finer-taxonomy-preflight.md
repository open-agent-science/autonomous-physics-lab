# Nuclear F2 Finer-Taxonomy Preflight

**Task:** `TASK-0478`
**Campaign:** Nuclear Mass Surface
**Feature family:** F2 (high-error cluster), residual-free promotion path
**Status:** pre-metric protocol (no candidate metrics computed)
**Verdict:** `PREFLIGHT_ONLY_F2_REMAINS_DIAGNOSTIC_ONLY`

## Scope

This is a **pre-metric** protocol. It defines what a future finer residual-free
F2 taxonomy would need, declares the minimum training-cell counts and stop
conditions, lists the post-hoc choices that would invalidate the next audit, and
recommends the next move. It does **not** compute candidate metrics, fit a
candidate, score a reveal, fetch data, or write `PRED-*`, `CLAIM-*`, `KNOW-*`,
or `RESULT-*` artifacts.

It is downstream of and consistent with:

- [`docs/reviews/nuclear-residual-free-high-error-cluster-hypothesis-audit.md`](./nuclear-residual-free-high-error-cluster-hypothesis-audit.md) (TASK-0449 / AGENT-RUN-0043);
- [`docs/nuclear-residual-feature-no-leakage-contract.md`](../nuclear-residual-feature-no-leakage-contract.md) (F2 promotion path);
- [`docs/notes/nuclear-controls-first-hypothesis-gauntlet.md`](../notes/nuclear-controls-first-hypothesis-gauntlet.md).

F2 stays `diagnostic_only` under the no-leakage contract. Nothing here re-enters
F2 into predictive-eligible scope.

## Why TASK-0449 Collapsed

TASK-0449 ran the contract-compliant residual-free F2 taxonomy
(`near_magic_z_or_n` / `neutron_rich` / `light_a_lt_50` / `other`,
magic-distance threshold = 2) on the NMD-0002 training slice and hit the
gauntlet's `INCONCLUSIVE` stop:

- NMD-0002 training slice = **11 rows**;
- `near_magic_z_or_n` swallowed **10 of 11** rows (threshold = 2 matches most
  curated mid/heavy rows), `neutron_rich` = 1, `light_a_lt_50` = 0, `other` = 0;
- only **one** cluster had ≥2 training rows, so leave-one-out cannot evaluate
  per-cluster structure; the gauntlet stop "fewer than two clusters have ≥2
  training rows" fired before any usable comparison.

The binding constraint is therefore **data coverage, not label cleverness**. A
*finer* taxonomy subdivides the same 11 rows into *more* cells, which makes the
per-cell sparsity strictly worse on the current slice. So this preflight's main
output is a coverage gate, with the finer taxonomy declared (but not scored)
behind it.

## Declared Finer Residual-Free Taxonomy (frozen before any score)

All bins are deterministic functions of `Z`, `N`, `A`, parity, magic-distance,
and asymmetry only. No baseline residual, error rank, residual quantile,
source-status, or any residual-derived quantity may enter label construction
(no-leakage contract, Forbidden Inputs). Published magic-number list:
`{2, 8, 20, 28, 50, 82, 126, 184}`. Let `dZ = min|Z - m|`, `dN = min|N - m|`,
and asymmetry `eta = (N - Z) / A`.

The coarse `near_magic_z_or_n` family (the cell that swallowed TASK-0449) is
split, and a tighter magic threshold is used to stop one cell dominating:

1. `doubly_magic_near`: `dZ <= 1` AND `dN <= 1`.
2. `magic_z_near`: `dZ <= 1` AND `dN > 1`.
3. `magic_n_near`: `dN <= 1` AND `dZ > 1`.
4. `mid_shell_neutron_rich`: not (1-3) AND `eta >= 0.18`.
5. `mid_shell_balanced`: not (1-4) AND `eta < 0.18` AND `A >= 50`.
6. `light_a_lt_50`: not (1-5) AND `A < 50`.

Parity (`even_even`, `even_odd`, `odd_even`, `odd_odd`) is a declared optional
**secondary** split applied only inside a primary bin that already clears the
cell-count floor below; it may never be used to manufacture new cells out of a
bin that is otherwise below floor.

The threshold change (2 -> 1), the asymmetry edge (0.18), the `A` cut (50), the
bin order, and the parity-as-secondary rule are all frozen now. They may not be
re-tuned after seeing residuals or scores (see Forbidden Post-Hoc Choices).

## Minimum Training-Cell Counts (declared before any score)

A future F2 scoring task may compute candidate metrics on the declared taxonomy
only if, computed deterministically from the curated training slice using `Z`,
`N`, `A` only (no residuals):

- **Per-cell floor:** each *scored* bin contains at least **5 training rows**.
  This is stricter than the ~3-row leave-one-out stability floor noted in
  TASK-0449 so that a per-cell offset and its LOO estimate are both meaningful.
- **Multi-cell floor:** at least **3 bins** independently clear the per-cell
  floor, and at least **2** of those are not the single dominant near-magic
  family, so the partition cannot collapse to one cell as in TASK-0449.
- **Total floor:** the scored bins together cover at least **30 training rows**.

Bins below the per-cell floor are context-only: they are reported for coverage
accounting but are excluded from scoring and cannot drive a verdict. A scoring
task may not merge sub-floor bins to reach the floor after inspecting which bins
are sparse (that is a forbidden post-hoc choice).

## Data-Coverage Threshold (the reopen gate)

F2 scoring is **not allowed** on any training slice that fails the floors above.
On the current NMD-0002 slice (11 rows) no residual-free taxonomy — coarse or
finer — can clear them, so F2 scoring stays blocked.

A future F2 scoring task may reopen **only** when a curated training slice
exists for which the deterministic `Z/N/A`-only bin populations satisfy:

- ≥ 3 declared bins each with ≥ 5 training rows;
- ≥ 2 of those bins outside the dominant near-magic family;
- ≥ 30 total scored training rows.

This coverage check is run and recorded **before** any candidate is fit. It is a
pre-score gate, not a result.

## Required Controls And Survival Margin (inherited, not relaxed)

A future scoring task still runs the full gauntlet:

- at least two controls run against the same `Z/N/A`-only label construction —
  `matched_random`, `smooth_a`, `asymmetry_only`, and the F2
  `cluster_label_shuffle` control;
- survival margin **≥ 0.25 MeV on `full_known`** (inherited from the TASK-0352
  freeze protocol; not relaxed here);
- the candidate must not regress the primary holdout panel;
- verdict drawn only from `{BOUNDED_FOLLOWUP_CANDIDATE, DIAGNOSTIC_ONLY,
  NEGATIVE_RESULT, INCONCLUSIVE}`.

## Forbidden Post-Hoc Choices (would invalidate the next audit)

The next F2 audit is invalid if any of these occur:

1. changing the magic-distance threshold, asymmetry edge (0.18), `A` cut (50),
   bin order, or parity grouping **after** seeing residuals or scores;
2. merging or splitting bins to reach the cell-count floor after inspecting
   which bins are sparse;
3. choosing the subset/aggregate on which the candidate "wins" after scoring;
4. dropping or weakening a declared control after seeing it beat the candidate;
5. re-running with a "slightly different" taxonomy in the same PR (the gauntlet
   forbids a follow-up wave; a failed candidate is preserved, not iterated);
6. consuming any forbidden input (target residual/mass/binding energy, baseline
   error rank, residual quantile, source-status, AME-update "was extrapolated"
   flag, candidate-fit residuals, or any feature that differs between the
   training and holdout copies of the same row);
7. reporting a verdict outside the four-item vocabulary or mixing categories
   ("inconclusive but worth a follow-up wave").

## Recommendation

Of the three task allows (future scoring task / source-data expansion task /
retirement of F2), this preflight recommends the **source/data-expansion path
first**, then a gated scoring task, and explicitly **not** retirement:

1. **Open a curated-training-slice expansion task** (separate,
   maintainer-approved) to grow the curated NMD training coverage until the
   deterministic `Z/N/A`-only bin populations clear the coverage gate above.
   This is the binding blocker; without it, no F2 taxonomy can be scored.
2. **Only after the coverage gate passes**, open a future F2 finer-taxonomy
   scoring task that runs the gauntlet with the taxonomy frozen here. That task
   authors no `PRED-*` entry; promotion remains a separate downstream task.
3. **Do not retire F2.** Retirement is premature: the contract already holds F2
   at `diagnostic_only` as a legitimate failure-mode atlas, and the failure in
   TASK-0449 was sparsity, not a clean falsification of the residual-free idea.

Until the coverage gate passes, F2 stays `diagnostic_only` and no F2 scoring
task should run on the NMD-0002 slice.

## Public Wording Boundary

Allowed: "pre-metric preflight", "coverage gate", "diagnostic only",
"residual-free taxonomy", "inconclusive", "preserved as failure-mode atlas".
Forbidden: "discovery", "new nuclear law", "near-magic regularity", "predicts"
without a frozen `PRED-XXXX`, "shell-axis breakthrough", or any claim that F2
explains nuclear masses.

## What This Preflight Does Not Do

- It does not compute candidate metrics or fit any candidate.
- It does not add a `PRED-*`, `CLAIM-*`, `KNOW-*`, or `RESULT-*` artifact.
- It does not re-enter F2 into predictive-eligible scope.
- It does not expand the curated dataset or fetch external data.
- It does not relax the no-leakage contract, the freeze protocol, the gauntlet,
  or the survival margin.

## Output Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `not_applicable` for a scientific claim;
  `PREFLIGHT_ONLY_F2_REMAINS_DIAGNOSTIC_ONLY` for the protocol artifact.
- **Canonical destination:** this review note,
  `docs/reviews/nuclear-f2-finer-taxonomy-preflight.md`.
- **Review tier:** `none` (no `RESULT-*`/`PRED-*` artifact).
- **Gate A status:** not attempted. **Gate B status:** not attempted.
- **Claim impact:** no claim change. **Knowledge impact:** no knowledge change.
- **Result artifact impact:** no `results/` artifact created or modified.
- **Limitations / blockers:** F2 scoring is blocked by training-slice coverage,
  not by label design; the declared floors (5 per cell, 3 cells, 30 total) and
  taxonomy are pre-score declarations amendable only before scoring, never after
  residual inspection; a curated-slice expansion task is the prerequisite.

## Limitations

- The numeric floors are conservative declarations chosen to avoid the
  TASK-0449 single-cell collapse; a maintainer may revise them only in a
  pre-score amendment, never after seeing residuals.
- The finer taxonomy is declared, not validated against data; whether the
  curated slice can ever populate ≥3 bins at the floor is exactly what the
  expansion task must establish.
- NMD-0002 is curated for mid/heavy nuclei, so `light_a_lt_50` may stay empty
  even after expansion; that bin is expected to remain context-only.
