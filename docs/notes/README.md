# Notes Directory

`docs/notes/` stores durable working notes that are useful to humans and
agents but are not themselves canonical result, claim, prediction, or knowledge
artifacts.

Notes are retained when they explain process, architecture, source selection,
campaign setup, agent discipline, or worked examples that later tasks may cite.
They should stay lightweight and should not become a parallel task board.

## Retention Classes

Use these classes when adding a new note:

- Architecture notes: repository layout, design constraints, compatibility
  expectations, factory plans, and lifecycle guidance.
- Agent workflow notes: worktree discipline, permissions, branch hygiene,
  task-selection conventions, and review-helper usage.
- Campaign planning notes: candidate lists, readiness gates, source-candidate
  surveys, and route planning that is not yet a review decision.
- Source notes: source locator, extraction, licensing, or provenance notes that
  support later source-artifact reviews.
- Historical notes: retained process or campaign context that has been
  superseded but still explains why a later route exists.

If a note becomes a final route decision, publication blocker, or
result-promotion judgement, write the durable decision in `docs/reviews/` and
link back to the note instead of overwriting the note's exploratory context.

## Naming And Future Grouping

Keep names topic-first and stable. Prefer names that identify the campaign or
workflow surface before the specific decision, for example:

- `agent-worktree-discipline.md`
- `research-factory-layer-plan.md`
- `stellar-ml-campaign-promotion-gate.md`

Avoid mass-moving existing notes until a link audit checks direct references
from docs, tasks, PR bodies, and review bundles. If new files need grouping,
prefer topic subfolders over date folders so campaign trails remain readable.

## Referencing Notes

Review agents and Scientific Campaign Director notes should cite notes directly
when they need background context. Do not create duplicate summary pages for
frequently referenced notes; instead add a concise "Related notes" section in
the new task output or review.

Generated task navigation lives under `docs/task-views/` and should not be
mirrored here.
