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

## Gate B Verdict And Tier Upgrade

- **Gate B (reproducibility): PASS.** The diagnostic is deterministically
  reproducible from the pinned inputs and command; metrics reproduce byte-for-byte.
- **Independence: confirmed.** `RESULT-0018` was originally published by a
  different agent (`codex` / contributor `akutenyov`, `TASK-0633` / PR #927); this
  Gate B replay was run by a different agent (`claude` / contributor `roman`).
  Different `agent_id` and different contributor — the strongest form of Gate B
  independence.
- **Scientific verdict: unchanged — `INCONCLUSIVE` / diagnostic-only.** The F2
  reference remains replayable, but no ablation variant clears the predeclared
  controls-first survival margin. Reproducibility confirms determinism; it does
  **not** convert an inconclusive diagnostic into a claim-supporting result.
- **Tier: upgraded `AGENT_PUBLISHED` → `AGENT_VALIDATED`** (maintainer-approved,
  2026-06-13). All five Gate B conditions are met (same inputs/hashes, same
  deterministic command/code_reference, metrics byte-identical, verdict unchanged,
  no protected-artifact rewrite beyond the tier/record update). A
  `validation_record` was added under `agent_proposal_evaluation` in
  `results/EXP-0012/RUN-0002/result.yaml`; the original Gate A evaluation is
  retained. No claim, knowledge entry, or nuclear mass formula is promoted, and
  `CLAIM-0010` stays `DRAFT` (Gate C remains maintainer-only). Per the
  result-promotion protocol's Phase-1 rule, this AGENT_VALIDATED tier was set
  under maintainer approval.

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `INCONCLUSIVE` (the replayed result's verdict); the replay
  itself is `VALID` as an independent reproduction.
- **Canonical destination:** this review note, plus a maintainer-approved tier
  update to `results/EXP-0012/RUN-0002/result.yaml` (`review_tier` →
  `AGENT_VALIDATED` and an added `validation_record`). `best_verdict`, metrics,
  and the verification block are unchanged. No `prediction_registry/`, `claims/`,
  or `knowledge/` artifact is changed; the replay output itself was written to a
  temporary directory only.
- **Review tier:** `RESULT-0018` upgraded `AGENT_PUBLISHED` → `AGENT_VALIDATED`
  (Gate B, maintainer-approved). This note carries no tier.
- **Gate A status:** not attempted. **Gate B status:** **PASS (reproduced,
  AGENT_VALIDATED).**
- **Claim impact:** no claim change (`CLAIM-0010` stays `DRAFT`; Gate C is
  maintainer-only). **Knowledge impact:** none.
- **Limitations / blockers:** the result is diagnostic and `INCONCLUSIVE` by
  construction; reproducibility and the tier upgrade do not change that. No
  reveal-data scoring was performed. Promotion beyond `AGENT_VALIDATED`
  (Gate C / claim status) remains a maintainer decision.
