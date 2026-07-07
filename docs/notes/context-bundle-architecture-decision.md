# Generated CONTEXT.md Bundle — Architecture Decision

**Task:** TASK-0591 (decision task + first safe migration step)
**Status:** superseded by TASK-0953 public-root cleanup
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

**2026-07-07 update (TASK-0953):** after public-alpha opening, the maintainer
accepted the public-root hygiene tradeoff and retired the committed root
`CONTEXT.md`. The generator remains available and now writes the ignored local
artifact `_generated/CONTEXT.md` by default. Canonical docs, mission YAML, and
`apl_mission.py` remain the source of truth; the single-file bundle is a local
handoff convenience only.

## Survey: generation, validation, links, consumption

**Generated.** `scripts/generate_context_bundle.py` concatenates core project
docs (`AGENTS.md`, `CLAUDE.md`, `docs/strategy.md`, `docs/current-missions.md`,
`missions/current.yaml`, `docs/mission-control.md`, `docs/agent-task-protocol.md`,
`docs/agent-scientific-work-mode.md`, plus optional extended docs with
`--full`) into a single markdown file. As of TASK-0953, the default output is
the ignored local path `_generated/CONTEXT.md`; callers may still use `--stdout`
or `--out FILE`. The header carries a UTC `Generated:` timestamp. TASK-0185
made regeneration idempotent when only that timestamp changes
(`write_bundle_if_changed`, `differs_only_by_generated_timestamp`).

**Not committed on main.** Unlike `docs/task-views/*.md`, there is no
post-merge GitHub Action that rewrites a committed `CONTEXT.md`. Maintainers or
agents regenerate the ignored local bundle only when a handoff needs it
(`context_bundle_followups` in `maintainer_review.py`).

**Validated.** `validate-repo --strict` does not require a committed context
bundle. Lane preconditions list `_generated/` among generated surfaces agents
should not treat as hand-editable (`apl_lane_precondition.py`).

**Linked.** Before TASK-0953, `CONTEXT.md` was referenced in roughly **20
places** across README, `AGENTS.md`, snapshot metadata, closeout checklists, and
maintainer docs. Those current surfaces now point to command-based local
generation instead of a committed root file.

**Consumed.** Maintainers and strategy agents can still generate it for chat
handoff; README mentions the generator command. Agent entry remains
`apl_mission.py` + canonical YAML, not the bundle.

**Size.** The bundle is large (multi-section aggregate of core docs), which is
why it no longer belongs in the public repo root.

## Friction history

The original churn class matched the generated-board problem TASK-0470
addressed for task navigation: a volatile aggregate lived in the committed tree,
so local regeneration could dirty the worktree. TASK-0185 removed
timestamp-only rewrites; TASK-0953 removed the committed root bundle.

## Historical options

TASK-0591 originally compared three options: generate the bundle on demand,
keep a committed-but-ephemeral root `CONTEXT.md`, or regenerate a committed
bundle on `main` through automation. At that time the repository still valued a
browsable one-file handoff enough to choose the committed-but-ephemeral route.

TASK-0953 supersedes that recommendation. The active policy is now
generate-on-demand local output only: use
`python3 scripts/generate_context_bundle.py`, `--stdout`, or an explicit
artifact path, and do not commit a root `CONTEXT.md`. A post-merge action for a
committed bundle is also rejected for public-root hygiene.

## Decision

**Current decision (TASK-0953): retire the committed root bundle; keep local
generation.**

The original TASK-0591 decision adopted Option B, but public-alpha hygiene
shifted the tradeoff. Root `CONTEXT.md` looked like a public source of truth
while duplicating canonical docs and mission state. The current policy is:

- canonical docs, mission YAML, task YAML, and `apl_mission.py` are source of
  truth;
- `scripts/generate_context_bundle.py` remains the supported one-file context
  mechanism;
- default output is `_generated/CONTEXT.md`, which is ignored and not committed;
- current public docs must not link to root `CONTEXT.md` or instruct agents to
  stage it.

**Historical decision:** TASK-0591 originally adopted Option B — committed but
strictly ephemeral. The rationale below records why that was reasonable before
public-root cleanup; it is no longer the active policy.

Rationale:

- Preserves README/snapshot handoff links without a large docs migration.
- Aligns with the repository's established generated-state policy for task
  views: canonical sources are hand-edited; derived aggregates must not block
  review.
- Stage 1 is small and safe; Option C remains a precise follow-up if main still
  sees chronic `CONTEXT.md` merge conflicts.

Current guiding rule: **`AGENTS.md`, mission YAML, and source docs are
canonical; `_generated/CONTEXT.md` is a local convenience aggregate that is not
committed.**

## Migration plan

1. **Stage 1 (TASK-0591, done).** Record this decision; add `CONTEXT.md` and
   `docs/task-views/*` to review cleanliness ignore paths; add
   `generate_context_bundle.py --check`; clarify closeout/review guidance that
   agents need not commit regenerated `CONTEXT.md`.
2. **Stage 2 (TASK-0953, done).** Retire committed root `CONTEXT.md`; change the
   generator default to `_generated/CONTEXT.md`; update public docs and helper
   messages to command-based local generation.
3. **Future optional.** If external contributors need downloadable bundles,
   publish them through snapshot or CI artifacts rather than a committed root
   file.

## What this decision does not do

- Superseded by TASK-0953: the public repository no longer commits root
  `CONTEXT.md`.
- It does not add a post-merge Action (Stage 2 follow-up).
- It does not change bundle source content or scientific claims.

## Cross-references

- `docs/notes/generated-task-navigation-architecture-decision.md` — task-view
  analogue (B2 retired `tasks/ACTIVE.md`).
- `tasks/proposals/20260530-roman-decouple-context-bundle.yaml` — original
  proposal accepted as TASK-0591.
