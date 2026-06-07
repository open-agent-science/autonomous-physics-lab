# Atomic Pizzocaro VLBI Per-Window Diagnostic Ledger

- Task: `TASK-0636`
- Campaign: Atomic Clock Residuals
- Verdict: `LEDGER_CREATED_DIAGNOSTIC_ONLY_COV_BLOCKED`
- Decision: machine-readable per-window ledger committed; windows remain
  diagnostic-only, not benchmark rows

## Scope

This task implements the per-window diagnostic ledger recommended by the
`TASK-0627` covariance gate
([`atomic-pizzocaro-vlbi-row-aggregation-covariance-gate.md`](atomic-pizzocaro-vlbi-row-aggregation-covariance-gate.md)).
It deterministically extracts the committed Figure 2a VLBI time-series from the
Pizzocaro 2020 Yb/Sr source CSV into a machine-readable ledger with stable
window ids, MJD fields, ratio orientation, component uncertainties, and
covariance-state labels.

It does **not** fetch live data, add `data/atomic_clocks/acr-*.yaml` benchmark
rows, compute any cross-window aggregate value or uncertainty, run constants-drift
fits or cross-source benchmarks, or create prediction, claim, knowledge, or
result artifacts.

## Inputs

- [`atomic-pizzocaro-vlbi-row-aggregation-covariance-gate.md`](atomic-pizzocaro-vlbi-row-aggregation-covariance-gate.md) (`TASK-0627`)
- [`atomic-pizzocaro-source-to-row-extraction-ledger.md`](atomic-pizzocaro-source-to-row-extraction-ledger.md) (`TASK-0615`)
- [`atomic-first-benchmark-covariance-policy.md`](atomic-first-benchmark-covariance-policy.md) (`TASK-0486`)
- `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/Yb-Sr-ratio-measuremets.csv`
- `physics_lab/engines/atomic_clock_residuals.py`

## What was created

- `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/vlbi_per_window_diagnostic_ledger.yaml`
  — the diagnostic ledger (`ledger_id`
  `ACLOCK-PIZZOCARO-VLBI-WINDOW-DIAGNOSTIC-LEDGER-0001`).
- `scripts/build_atomic_pizzocaro_vlbi_window_ledger.py` — a deterministic
  generator that parses the committed CSV by header name and emits the ledger.
- `tests/test_atomic_pizzocaro_window_ledger.py` — a regeneration guard (the
  committed ledger must equal a fresh rebuild from the source CSV) plus
  structural/covariance invariants.

## Per-window surface

The ledger records 10 VLBI campaign windows (`PIZZOCARO-VLBI-W01`–`W10`) over
`MJD 58405.652`–`58529.616`. For each window it records `MJDstart`, `MJDstop`,
`MJDmed`, the final `yVLBI=Yb/Sr` relative value, the final `u` uncertainty
(1 sigma), and the statistical (`uA1`–`uA4`), systematic (`uB1_comb`,
`uB1_clock`, `uB2`, `uB4_comb`, `uB4_clock`), and extrapolation deadtime/drift
components. Values are copied deterministically from the committed source CSV
(sha256 `fa81da6f…`); no cross-window aggregate is computed.

## Covariance assessment

Covariance state: `COV_BLOCKED_SHARED_SYSTEMATICS` (per the Atomic
first-benchmark covariance policy).

The windows share clocks, the frequency comb, the maser/optical and VLBI links,
campaign systematics, and deadtime/drift components. The ledger flags the
window-invariant systematic components — `uB1_comb` and `uB4_comb` (both
`8.00e-17`) and `uB2` (`1.00e-16`) — as load-bearing shared systematics. The
committed source artifacts do not expose a signed off-diagonal covariance or a
deterministic reconstruction recipe, so the windows cannot be treated as
independent benchmark rows, and no single summary row is admissible yet.

**Unblock condition (frozen):** a future task may move toward
`COV_SOURCE_DERIVED_PSD_APPROX` only by committing a deterministic covariance
reconstruction (row order, unit convention, shared-component sign convention,
pairwise decomposition, PSD check, omitted-component list), or
`COV_EXACT_COMMITTED` only if the source publishes the full matrix. Until then
the ledger stays diagnostic-only and no ACR row, drift fit, or cross-source
benchmark may consume it.

## Stop conditions preserved

- Do not add `data/atomic_clocks/acr-*.yaml` benchmark rows from this ledger.
- Do not compute a cross-window aggregate value or uncertainty.
- Do not run constants-drift fits, cross-source benchmarks, predictions, claims,
  knowledge, or result artifacts.
- Do not relabel the covariance state without a committed reconstruction that
  clears the covariance policy.

## Output routing

- Task verdict: `INCONCLUSIVE` for benchmark readiness; ledger created as
  diagnostic-only readiness memory.
- Canonical destination:
  `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/vlbi_per_window_diagnostic_ledger.yaml`
  and this review note.
- Review tier: `none`.
- Gate A status: not attempted; no `RESULT-*` or `PRED-*` artifact.
- Gate B status: not applicable.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result artifact impact: no `results/` artifacts modified; no ACR benchmark
  rows added.
- Limitations / blockers: `COV_BLOCKED_SHARED_SYSTEMATICS`; the ledger is
  diagnostic-only and does not unblock an Atomic Yb/Sr benchmark until a
  covariance reconstruction is committed.
