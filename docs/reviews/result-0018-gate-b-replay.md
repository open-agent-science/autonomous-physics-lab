# RESULT-0018 Gate B Replay (Nuclear F2 Component-Ablation Diagnostic)

**Task:** `TASK-0713`
**Result under replay:** `RESULT-0018` (`results/EXP-0012/RUN-0002/`), the Nuclear
F2 component-ablation diagnostic preflight (`EXP-0012` / `HYP-0012`; runner
`scripts/run_nuclear_f2_component_ablation.py`).
**Verdict:** `GATE_B_REPLAY_REPRODUCED` — independent replay reproduces the
committed result byte-for-byte; the scientific verdict remains
`INCONCLUSIVE` / diagnostic-only.

## Scope

This is an independent Gate B replay of the committed `RESULT-0018`
(`AGENT_PUBLISHED`, `INCONCLUSIVE`). It re-runs the pinned command from a clean
branch and compares metrics, report, outcome, and input hashes against the
committed artifacts.

It does **not** score nuclear predictions, fetch post-AME2020 reveal data, change
`PRED-*` entries, create claims, rewrite the canonical result, or claim a nuclear
mass formula. Per `TASK-0713`, a reproduced replay is reported as such and a
failed/inconclusive replay would preserve an explicit do-not-promote blocker.

## Method

- Branch: `agent/roman/claude/task-0713-result0018-gate-b-replay` from a clean
  `origin/main`. Interpreter: project 3.12 virtual environment.
- Command (the committed `RESULT-0018` command, output redirected to a temporary
  directory so no canonical artifact changes):

  ```bash
  python scripts/run_nuclear_f2_component_ablation.py \
    --output-dir <tmp> --review-path <tmp>/review.md
  ```

- Compared the produced `metrics.json` / `report.md` against
  `results/EXP-0012/RUN-0002/`, and verified the four pinned input hashes from
  `result.yaml`.

## Results

| Check | Outcome |
| --- | --- |
| Runner exit | success — `Outcome: COMPONENT_DIAGNOSTIC_ONLY` |
| Pinned input hashes (config / experiment / hypothesis / task) | all 4 **match** `result.yaml` |
| `metrics.json` | **byte-identical** (SHA-256 `eeda772f…`) to the committed file |
| `metrics.json` structural compare (excl. volatile path/timestamp keys) | equal |
| `report.md` | identical (modulo line endings) |
| Best verdict | `INCONCLUSIVE` (unchanged) |
| Review tier | `AGENT_PUBLISHED` (unchanged) |

**Line-ending sensitivity:** this replay was byte-identical with no CRLF/LF
divergence — an improvement on the original `TASK-0633` note, which reported a
metrics match only after ignoring line endings.

## Gate B Verdict And Tier Recommendation

- **Gate B (reproducibility): PASS.** The diagnostic is deterministically
  reproducible from the pinned inputs and command; metrics reproduce byte-for-byte.
- **Scientific verdict: unchanged — `INCONCLUSIVE` / diagnostic-only.** The F2
  reference remains replayable, but no ablation variant clears the predeclared
  controls-first survival margin. Reproducibility confirms determinism; it does
  **not** convert an inconclusive diagnostic into a claim-supporting result.
- **Tier:** the independent Gate B reproduction is the evidence that would support
  promoting `RESULT-0018` from `AGENT_PUBLISHED` to `AGENT_VALIDATED` (independently
  replayed). The actual tier transition is a **maintainer decision** (Phase 1
  claim/tier transitions are maintainer-only). Recommendation: a maintainer may
  mark `RESULT-0018` `AGENT_VALIDATED` and record this Gate B pass in
  `results/EXP-0012/RUN-0002/review_metadata.yaml`. No claim, knowledge entry, or
  nuclear mass formula is promoted. The diagnostic/do-not-promote-to-claim posture
  is preserved.

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `INCONCLUSIVE` (the replayed result's verdict); the replay
  itself is `VALID` as an independent reproduction.
- **Canonical destination:** this review note. No `results/`, `prediction_registry/`,
  `claims/`, or `knowledge/` artifact is changed. The replay output was written to
  a temporary directory only.
- **Review tier:** `none` for this note. The replayed `RESULT-0018` stays
  `AGENT_PUBLISHED` unless a maintainer upgrades it to `AGENT_VALIDATED`.
- **Gate A status:** not attempted. **Gate B status:** **PASS (reproduced)**.
- **Claim impact:** no claim change. **Knowledge impact:** none.
- **Limitations / blockers:** the result is diagnostic and `INCONCLUSIVE` by
  construction; reproducibility does not change that. No reveal-data scoring was
  performed. The tier upgrade and any `review_metadata.yaml` edit are left to the
  maintainer.
