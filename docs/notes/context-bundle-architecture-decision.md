# Generated CONTEXT.md Bundle — Architecture Decision

**Task:** TASK-0591 (decision task + first safe migration step)
**Status:** architecture decision note + Stage 1 implementation
**Inputs:** `CONTEXT.md`, `scripts/generate_context_bundle.py`,
`docs/notes/generated-task-navigation-architecture-decision.md`,
`tasks/proposals/20260530-roman-decouple-context-bundle.yaml`,
`physics_lab/registry/maintainer_review.py`, `scripts/apl_lane_precondition.py`

## Question

Should the generated `CONTEXT.md` one-file bundle stay committed, become
generate-on-demand only, or use committed-but-ephemeral handling like the task
views? The bundle is convenient for chat handoff and snapshot downloads, but
parallel agents regenerating it at different timestamps create stale diffs and
false dirty worktrees during review.

## Survey: generation, validation, links, consumption

**Generated.** `scripts/generate_context_bundle.py` concatenates core project
docs (`AGENTS.md`, `CLAUDE.md`, `docs/strategy.md`, `docs/current-missions.md`,
`missions/current.yaml`, `docs/mission-control.md`, `docs/agent-task-protocol.md`,
`docs/agent-scientific-work-mode.md`, plus optional extended docs with
`--full`) into a single markdown file. The header carries a UTC `Generated:`
timestamp. TASK-0185 made regeneration idempotent when only that timestamp
changes (`write_bundle_if_changed`, `differs_only_by_generated_timestamp`).

**Not auto-regenerated on main.** Unlike `docs/task-views/*.md`, there is no
post-merge GitHub Action that rewrites `CONTEXT.md`. Maintainers regenerate it
manually after merge batches when bundle sources change
(`context_bundle_followups` in `maintainer_review.py`).

**Validated.** `validate-repo --strict` does not currently treat a stale
`CONTEXT.md` as a hard error. Lane preconditions list `CONTEXT.md` among
generated surfaces agents should not treat as hand-editable
(`apl_lane_precondition.py`).

**Linked.** `CONTEXT.md` is referenced in roughly **20 places** across README,
`AGENTS.md`, snapshot metadata, closeout checklists, and maintainer docs — far
fewer than the retired `tasks/ACTIVE.md` board (~147 links) but still a
convenience anchor for "download one file" onboarding.

**Consumed.** Maintainers and strategy agents use it for chat handoff;
`snapshot.py` advertises it as a downloadable bundle; README mentions the
generator command. Agent entry remains `apl_mission.py` + canonical YAML, not
the bundle.

**Size.** The committed bundle is large (multi-section aggregate of core docs).

## Friction history

The churn class matches the generated-board problem TASK-0470 addressed for task
navigation: a volatile aggregate lives in the committed tree, so any local
regeneration (review prep, closeout, full pytest side effects) can dirty the
worktree. TASK-0185 removed timestamp-only rewrites, but content drift when
bundle sources change on a branch still blocks review with "git status not clean"
unless the agent manually restores `CONTEXT.md`.

## Options

| Option | Human browsability | In-repo links | Merge-conflict risk | Review noise | Handoff convenience |
| --- | --- | --- | --- | --- | --- |
| **A. Generate-on-demand only** | lost in repo | breaks ~20 links | eliminated | eliminated | worse (extra command) |
| **B. Committed but strictly ephemeral** | preserved | preserved | moderate (no central writer) | fixable via ignore + `--check` | unchanged/good |
| **C. Post-merge Action regeneration** | preserved | preserved | low on main | low on branches | unchanged/good |

### A. Generate-on-demand only

Stop committing `CONTEXT.md`; produce it via
`python3 scripts/generate_context_bundle.py --stdout` or CI artifacts. Cleanly
eliminates committed churn but breaks README/snapshot/closeout references and
removes the browsable bundle from the repo and web UI.

### B. Committed but strictly ephemeral (recommended)

Keep `CONTEXT.md` committed so links and snapshot metadata stay valid. Treat it
as **derived output that must not block agent flow**:

- review/closeout cleanliness checks ignore `CONTEXT.md` (and, for consistency,
  `docs/task-views/*`) when assessing working-tree dirtiness;
- `generate_context_bundle.py --check` verifies freshness without rewriting;
- maintainers regenerate after merge batches when bundle sources change; task
  PR branches do not need to commit regenerated `CONTEXT.md`.

This mirrors the task-view policy from
`generated-task-navigation-architecture-decision.md` without requiring an
immediate post-merge Action.

### C. Post-merge Action regeneration

Add a workflow (or extend `sync-active-board.yml`) to regenerate `CONTEXT.md` on
`main` after merges touching bundle sources. Lowest branch conflict risk, but
the bundle is larger and touches more source surfaces than task views; defer as
a follow-up once Stage 1 ignore/`--check` policy is stable.

## Decision

**Adopt Option B — committed but strictly ephemeral.**

Rationale:

- Preserves README/snapshot handoff links without a large docs migration.
- Aligns with the repository's established generated-state policy for task
  views: canonical sources are hand-edited; derived aggregates must not block
  review.
- Stage 1 is small and safe; Option C remains a precise follow-up if main still
  sees chronic `CONTEXT.md` merge conflicts.

Guiding rule after Stage 1: **`AGENTS.md`, mission YAML, and the bundled source
docs are canonical; `CONTEXT.md` is a convenience aggregate that maintainers
refresh on `main`, not something task PRs must commit.**

## Migration plan

1. **Stage 1 (this task).** Record this decision; add `CONTEXT.md` and
   `docs/task-views/*` to review cleanliness ignore paths; add
   `generate_context_bundle.py --check`; clarify closeout/review guidance that
   agents need not commit regenerated `CONTEXT.md`.
2. **Stage 2 (optional follow-up).** Post-merge Action to regenerate
   `CONTEXT.md` when `CONTEXT_BUNDLE_SOURCE_FILES` change on `main`, mirroring
   task-view sync.
3. **Stage 3 (optional).** If link count drops further, revisit generate-on-demand
   with snapshot-only distribution.

## What this decision does not do

- It does not stop committing `CONTEXT.md`.
- It does not add a post-merge Action (Stage 2 follow-up).
- It does not change bundle source content or scientific claims.

## Cross-references

- `docs/notes/generated-task-navigation-architecture-decision.md` — task-view
  analogue (B2 retired `tasks/ACTIVE.md`).
- `tasks/proposals/20260530-roman-decouple-context-bundle.yaml` — original
  proposal accepted as TASK-0591.
