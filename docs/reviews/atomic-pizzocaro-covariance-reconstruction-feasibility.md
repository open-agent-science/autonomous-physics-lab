# Atomic Pizzocaro Covariance Reconstruction Feasibility

**Task:** `TASK-0651`
**Campaign:** Atomic-Clock Residuals
**Mode:** workflow / review only (no benchmark, no aggregation, no live fetch)
**Verdict:** `FEASIBLE_AS_SOURCE_DERIVED_PSD_APPROX` (well-posed as an approximation; under-specified for an exact matrix)
**Recommended route:** open a scoped covariance-reconstruction task targeting `COV_SOURCE_DERIVED_PSD_APPROX`

## Scope And Boundaries

This review decides whether the committed Pizzocaro 2020 Yb/Sr source artifacts
contain enough information for a later covariance reconstruction across the 10
VLBI campaign windows. It uses only committed source artifacts. It does **not**:

- aggregate windows into benchmark rows or compute a cross-window value/uncertainty;
- fit constants drift or compute residual metrics;
- fetch live data;
- create any `RESULT-*`, `CLAIM-*`, `PRED-*`, `KNOW-*`, or `data/atomic_clocks/acr-*.yaml` row;
- create the recommended follow-up task (task creation is maintainer/proposal-gated).

## Inputs

- [vlbi_per_window_diagnostic_ledger.yaml](../../data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/vlbi_per_window_diagnostic_ledger.yaml) (`TASK-0636`)
- [Yb-Sr-ratio-measuremets.csv](../../data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/Yb-Sr-ratio-measuremets.csv) (VLBI, Figure 2a)
- [Yb-Sr-ratio-measurements-IPPP.csv](../../data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/Yb-Sr-ratio-measurements-IPPP.csv) (IPPP/PPP, Extended Data Fig. 4)
- [provenance.yaml](../../data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/provenance.yaml)
- [atomic-pizzocaro-vlbi-row-aggregation-covariance-gate.md](./atomic-pizzocaro-vlbi-row-aggregation-covariance-gate.md) (`TASK-0627`, `BLOCKER_PRESERVED`)
- [atomic-pizzocaro-source-to-row-extraction-ledger.md](./atomic-pizzocaro-source-to-row-extraction-ledger.md) (`TASK-0615`)
- [atomic-first-benchmark-covariance-policy.md](./atomic-first-benchmark-covariance-policy.md) (`TASK-0486`)
- precedent: [acr-0001-beloy-2021-cross-ratio-covariance-approximation.yaml](../../data/atomic_clocks/acr-0001-beloy-2021-cross-ratio-covariance-approximation.yaml)

## Uncertainty-Component Inventory (Committed Source)

Each of the 10 VLBI windows exposes a full per-link decomposition of the final
`u`. The components fall into three correlation classes:

| Component | Source columns | Per-window behaviour | Cross-window correlation class |
| --- | --- | --- | --- |
| Statistical (per link) | `uA1`, `uA2`, `uA3`, `uA4` | varies every window | **independent** (diagonal) |
| Extrapolation deadtime/drift | `udead12/23/34`, `udrift12/23/34` | varies every window (campaign-window specific) | **independent** (diagonal) |
| Comb systematic | `uB1-comb`, `uB4-comb` | window-invariant (`8.00e-17`) | **common-mode / fully shared** |
| Maser-optical-link systematic | `uB2` | window-invariant (`1.00e-16`) | **common-mode / fully shared** |
| Clock systematic | `uB1-clock` (Yb), `uB4-clock` (Sr) | slowly varying (`~2.5e-17–4.4e-17`, `~7.3e-17–9.9e-17`) | **same physical clocks → highly correlated, correlation coefficient not published** |

Key structural facts read from the committed source:

1. The **load-bearing shared systematics are individually exposed and numerically
   committed** (comb, maser-link, clock B-type terms). This is exactly the
   information the [covariance gate](./atomic-pizzocaro-vlbi-row-aggregation-covariance-gate.md)
   and the [per-window ledger](../../data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/vlbi_per_window_diagnostic_ledger.yaml)
   flagged as the blocker (`COV_BLOCKED_SHARED_SYSTEMATICS`).
2. The comb and `uB2` terms are **constant across all windows**, so their
   off-diagonal contribution is unambiguously common-mode (correlation +1).
3. The clock terms are the **same two physical clocks (Yb, Sr) in one campaign**;
   they are physically common-mode, but the source publishes per-window magnitudes
   rather than a correlation coefficient.
4. **No paper-published full covariance matrix** is committed (or referenced) in
   the source artifacts. Confirmed against `provenance.yaml` and the source CSVs.
5. **Cross-processing-path coupling exists:** the VLBI and IPPP/PPP tables share
   the `y1=Yb/HMI` and `y4=HMN/Sr` links verbatim (identical columns at matching
   MJD). Any future metric that mixes VLBI and IPPP/PPP final ratios would carry a
   large, structurally-known cross-path correlation. This is out of scope for a
   single-path (VLBI-only) reconstruction but must be named as an excluded risk.

## Feasibility Decision

The covariance reconstruction is **well-posed as a `COV_SOURCE_DERIVED_PSD_APPROX`**
and **under-specified (not blocked) for `COV_EXACT_COMMITTED`**.

Reasoning against the [first-benchmark covariance policy](./atomic-first-benchmark-covariance-policy.md):

- The policy permits a source-derived approximation when "the shared component
  has a committed sign convention and uncertainty decomposition." The uncertainty
  decomposition **is** committed per window, and a sign convention **can** be
  committed (all B-type systematics are common-mode, sign +1). This clears the
  policy's bar for `COV_SOURCE_DERIVED_PSD_APPROX`.
- The same bar was already cleared in this repository by the Beloy 2021 precedent
  [`ACR-0001-COV-APPROX-BELOY-2021`](../../data/atomic_clocks/acr-0001-beloy-2021-cross-ratio-covariance-approximation.yaml),
  which records row order, diagonal source, off-diagonal reconstruction rule,
  shared-clock sign convention, pairwise decomposition, PSD eigenvalue check, and
  an omitted-component list. Pizzocaro VLBI exposes the analogous components, so
  the same construction is reproducible here.
- It is **not** `COV_EXACT_COMMITTED` because no published matrix exists and the
  clock-term cross-window correlation coefficient is an assumption, not a source
  value. Under the policy, that makes any downstream metric **sensitivity-only**
  with an `approximate covariance` banner — never a headline exact result.
- It is **not** `BLOCKED` (the gate's current conservative state), because the
  blocker reason in the gate/ledger — "the source does not expose a signed
  off-diagonal covariance or a deterministic reconstruction recipe" — is about a
  *missing recipe*, not *missing component data*. The components needed to author
  a deterministic recipe are present. The block lifts once a task commits the
  recipe; it does not require new source information.

In one line: the data is sufficient to *build* a defensible approximate
covariance; it is insufficient to *claim an exact* one.

## Recommended Route (exactly one)

**Open a scoped covariance-reconstruction task** (maintainer-assigned `TASK-XXXX`
or a `TASK-PROPOSAL`) that moves the Pizzocaro VLBI windows from
`COV_BLOCKED_SHARED_SYSTEMATICS` to `COV_SOURCE_DERIVED_PSD_APPROX` only — never
to `COV_EXACT_COMMITTED`, and never to a benchmark row in the same task.

That reconstruction task must freeze, at minimum (matching the ledger
`unblock_condition` and the Beloy precedent):

1. **Row/window order** — the 10 `PIZZOCARO-VLBI-W01..W10` ids from the ledger.
2. **Unit + confidence convention** — relative units, 1σ, as in the source headers.
3. **Diagonal source** — committed per-window final `u²`.
4. **Off-diagonal recipe** — common-mode block from `uB1_comb² + uB2² + uB4_comb²`
   (+ a single, explicitly-stated clock-term correlation convention for
   `uB1_clock`, `uB4_clock`).
5. **Shared-component sign convention** — common-mode, +1, documented.
6. **Clock-correlation assumption** — stated explicitly as the approximation's
   main free parameter, with a sensitivity check across at least the
   fully-correlated and uncorrelated clock-term bounds.
7. **PSD check** — eigenvalue/PSD verdict on the reconstructed matrix.
8. **Omitted-component list** — at least: cross-processing-path (VLBI↔IPPP/PPP)
   correlation via shared `y1`/`y4` links; any network/geopotential term not in
   the CSV; treatment of `udead`/`udrift` as diagonal.
9. **Promotion ceiling** — sensitivity-only, no benchmark verdict, no drift fit,
   no claim/knowledge promotion, consistent with the covariance policy table.

If — and only if — that task cannot commit a PSD-passing recipe under a defensible
clock-correlation convention, it should fall back to preserving the existing
diagnostic-only ledger and prioritise a different second-source Atomic row
(`TASK-0652` Lange/PTB Yb⁺ preflight is the standing fallback lane). This review
does not select the fallback now, because the component data supports the
reconstruction attempt.

### Routes considered and not chosen
- **Diagnostic-only memory (status quo):** rejected as the *primary* route because
  it leaves recoverable covariance information unused; the components clear the
  policy bar for an approximation. It remains the correct fallback if the PSD/clock
  convention fails.
- **Fallback-source priority:** rejected as the primary route for the same reason;
  Pizzocaro is not exhausted. Keep `TASK-0652` as the parallel hedge, not the
  replacement.

## Limitations

- Review of committed artifacts only; no digitization, recomputation, aggregation,
  or live fetch was performed.
- Feasibility is asserted for a **VLBI-only** single-path reconstruction. A
  multi-path (VLBI + IPPP/PPP) covariance is a strictly harder problem because of
  the shared `y1`/`y4` links and is explicitly out of scope here.
- The clock-term cross-window correlation coefficient is unpublished; the
  recommended task must treat it as an assumption with a sensitivity bound, which
  is why the ceiling is `COV_SOURCE_DERIVED_PSD_APPROX`, not exact.
- This review creates no task file; it recommends one. Canonical task creation
  remains maintainer/proposal-gated.

## Output Routing Summary

- **Task verdict:** `FEASIBLE_AS_SOURCE_DERIVED_PSD_APPROX` (well-posed as an
  approximation; under-specified for an exact matrix; not blocked by missing
  source information).
- **Canonical destination:**
  `docs/reviews/atomic-pizzocaro-covariance-reconstruction-feasibility.md`.
- **Review tier:** `none` — no tiered artifact created.
- **Gate A status:** not attempted (no result published).
- **Gate B status:** not applicable.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Result artifact impact:** no `results/` or `data/atomic_clocks/acr-*.yaml`
  artifact created or modified.
- **Limitations / blockers:** Pizzocaro VLBI stays `COV_BLOCKED_SHARED_SYSTEMATICS`
  until a follow-up reconstruction task commits a deterministic, PSD-checked,
  sensitivity-bounded `COV_SOURCE_DERIVED_PSD_APPROX` recipe; `TASK-0456`
  (first Yb/Sr benchmark) remains blocked.
