# Codex Task: Post-release Evidence Review and Knowledge Application

Read `AGENTS.md`, `docs/status.md`, `docs/claim-promotion-policy.md`, and
`results/EXP-0001/RUN-0002/report.md` first.

## Goal

Stabilize the post-release public-alpha state after `RUN-0002`.

## Required Work

1. Update `docs/status.md` from `candidate` to `released`.
2. Update `CODEX_TASK.md` to this post-release task.
3. Remove `.DS_Store` noise from snapshot output and ensure it is ignored.
4. Review `CLAIM-0001` and `CLAIM-0002`:
   - do not auto-promote;
   - suggest whether each should stay `DRAFT`, become `PARTIALLY_SUPPORTED`, or be split.
5. Apply section-aware knowledge updates:
   - update `KNOW-0001` with `RESULT-0001` and `RESULT-0003`;
   - update `KNOW-0002` with `RESULT-0002` verification checks.
6. Add `docs/notes/pendulum-separatrix-followup.md` explaining:
   - `RUN-0001` failure mode;
   - `TASK-0003` motivation;
   - `RUN-0002` improvement;
   - remaining limits.

## Scientific Rules

- Keep verdicts range-aware.
- Do not auto-promote claims from generated evidence suggestions.
- Prefer explicit review notes over silent semantic drift.

## Constraints

- Do not add `EXP-0003`.
- Do not add dashboard.
- Do not add LLM calls.
- Do not add literature ingestion.
- Keep tests fast.

## Before Finishing

Run:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
python3 -m physics_lab.cli validate-repo .
git diff --exit-code
```
