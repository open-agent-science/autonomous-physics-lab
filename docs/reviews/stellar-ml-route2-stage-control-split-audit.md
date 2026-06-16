# Stellar M-L Route 2 Stage-Control and Split-Sensitivity Audit (TASK-0759)

**Task:** `TASK-0759`
**Campaign:** Textbook Formula Audit (Stellar mass-luminosity)
**Agent run:** `agent_runs/AGENT-RUN-0073/`
**Verdict:** `CONTROLS_PASS` — the `TASK-0753` control gaps are resolved; advance
toward Gate A after one baseline-adequacy step. Sandbox evidence only; no
universal M-L law and no `RESULT-*` is promoted here.
**Scope note:** dated control audit, not a live board or RESULT promotion.

## Method (predeclared, no-peek)

`scripts/run_stellar_ml_stage_control_audit.py` scores `log L = 3.5 log M` over
`0.5-2.0 M_sun` on the locally regenerated, checksum-pinned DEBCat rows (Route 2;
raw `debs.dat` and full rows not committed). Predeclared before inspecting
metrics: main-sequence primary lane; per-mass-band train-median null; system-level
70/30 split sensitivity over seeds `{11,23,37,53,71}`; luminosity-shuffle control.

## Results

**Stage control.** Restricting to `main_sequence_compatible` rows makes the
formula stronger and grows the holdout margin:

| Slice | Holdout rows | Formula MAE | Null MAE | Formula − null |
| --- | ---: | ---: | ---: | ---: |
| Mixed stages (TASK-0740) | 132 | 0.347 | 0.445 | −0.098 |
| Main-sequence only | 65 | **0.185** | 0.332 | **−0.147** |

Per-stage holdout formula MAE (dex): main-sequence `0.185`, unknown `0.238`,
subgiant `0.308`, **evolved `1.709`**. The evolved population is the confound;
`M^3.5` is a main-sequence relation and fails (as expected) off it.

**Split-sensitivity.** null − formula holdout margin per seed:
`[0.180, 0.155, 0.127, 0.102, 0.134]` dex — positive on **5/5** seeds
(`stable_positive`). Not a single-split artifact.

**Shuffle control.** Real margin `+0.147`; shuffled-pairing margins all negative
(mean `−0.125`); real exceeds every shuffled margin. The signal is real.

## Gate A Readiness (update to TASK-0753 checklist)

| Criterion | TASK-0753 | Now |
| --- | --- | --- |
| Confounder control (evolutionary stage) | ❌ | ✅ main-sequence restriction (margin 0.098 → 0.147; evolved isolated) |
| Margin robustness (split-sensitivity / controls) | ❌ | ✅ 5/5 seeds positive + shuffle control passes |
| Baseline adequacy (vs textbook piecewise) | ❌ | ⏳ still single-alpha; piecewise/fitted comparison recommended |
| Gate A RESULT packaging | ❌ | maintainer-only (not attempted) |

## Recommendation

Advance Stellar M-L toward a **maintainer-gated Gate A reusable-dataset +
benchmark RESULT candidate** (main-sequence DEBCat M-L), framed scope-limited
(0.5-2.0 M_sun, main-sequence, catalogue-luminosity provenance) — **not** a
universal mass-luminosity law claim. One control remains before packaging:

- **Baseline-adequacy step (recommended, not blocking):** compare the single-alpha
  `M^3.5` against the textbook piecewise-bin M-L (the campaign's named target)
  and/or a train-fitted alpha, to state how much of the margin is the specific
  exponent vs any monotincreasing mass-luminosity baseline. This can be a small
  follow-up task; if the maintainer accepts single-alpha framing, Gate A may
  proceed directly.

## Limitations

- 65 main-sequence holdout rows (small); catalogue-level luminosity provenance.
- Stage flags are best-effort metadata; `unknown` (the largest subset) is kept as
  a diagnostic, not folded into the primary lane.
- Sandbox-only; raw DEBCat stays local-only (Route 2); cite DEBCat
  (Southworth 2015) and the original sources on any publication.

## Output-Routing Summary

- **Task verdict:** `CONTROLS_PASS`; benchmark-readiness now blocked only on the optional baseline-adequacy step + maintainer Gate A.
- **Canonical destination:** this dated audit + `agent_runs/AGENT-RUN-0073/`; `TASK-0759` → `REVIEW_READY`.
- **Review tier:** `none`; no `RESULT-*`/`PRED-*` promoted.
- **Gate A status:** ready pending baseline-adequacy + maintainer packaging. **Gate B:** not applicable.
- **Claim impact:** none. **Knowledge impact:** none.
- **Recommendation:** baseline-adequacy follow-up task, then maintainer-gated Gate A; keep main-sequence, scope-limited, reusable-dataset/benchmark framing (no universal-law claim).
