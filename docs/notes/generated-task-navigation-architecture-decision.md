# Generated Task-Navigation Architecture — Decision

**Task:** TASK-0470 (decision task; no board behavior changed here)
**Status:** architecture decision note + recommended migration path
**Inputs:** `tasks/proposals/20260530-roman-decouple-generated-board-files.yaml`,
`tasks/ACTIVE.md`, `docs/task-views/`, `.github/workflows/sync-active-board.yml`,
`physics_lab/registry/generated_state.py`, `physics_lab/registry/repository.py`

## Question

Should the generated task-navigation files — `tasks/ACTIVE.md` and
`docs/task-views/*.md` — stay committed, become on-demand/artifact-only, or use
a hybrid shape? This resolves the residual architectural question behind the
generated-board churn that TASK-0466 patched symptom-by-symptom.

## Survey: how the board is generated, validated, linked, consumed

**Generated.** `tasks/ACTIVE.md` (the full board, including DONE history) and
the five `docs/task-views/*.md` lighter lane views are derived from the
canonical `tasks/TASK-*.yaml` files (and `missions/current.yaml`) by
`physics_lab/registry/generated_state.py` via
`python3 -m physics_lab.cli sync-active-board`. On `main`, the post-merge
`.github/workflows/sync-active-board.yml` Action regenerates them after any push
that touches `tasks/**` or `missions/current.yaml` and commits the result with a
`[skip-board-sync]` marker. Agents are told **not** to commit regenerated
versions from a task PR.

**Validated.** `validate-repo --strict` reports a stale `tasks/ACTIVE.md` or a
stale generated view as **INFO** by default (`_board_staleness_severity`,
escalatable via `APL_ENFORCE_BOARD_STALENESS=1`), precisely so a non-regenerated
task branch passes `--fail-on-warnings`. Missing files remain `ERROR`.

**Linked.** This is the load-bearing finding. `tasks/ACTIVE.md` is referenced
**~125 times across ~20 documents** (AGENTS.md, `docs/agent-task-protocol.md`,
`docs/mission-control.md`, runbooks, onboarding, status pages, …). The five
`docs/task-views/*.md` are referenced **~22 times** more. These are in-repo
navigation anchors that humans and agents follow.

**Consumed.** New agents read `tasks/ACTIVE.md` (full status board) and the
`docs/task-views/*.md` (current-work navigation) during onboarding; humans browse
them in the repo and on the web UI.

**Sizes.** `tasks/ACTIVE.md` is ~555 lines; each task view is ~17–31 lines.

## Friction history (why this question exists)

The churn came from one root cause: generated state lives in the committed tree
and is coupled to canonical state, so any process that regenerates it dirties
the working tree. TASK-0466 already neutralised the concrete symptoms:

- board staleness is `INFO`, not a hard error (does not fail `--fail-on-warnings`);
- the live `--auto-sync` smoke test snapshots/restores the board so the required
  full pytest no longer leaves it dirty;
- the mission-action staleness on a `REVIEW_READY` reference is `INFO`.

**Residual friction (not yet fixed):** the maintainer-review tool
(`apl_review_pr.py` / `maintainer_review.py`) blocks on "git status not clean"
when a local full-pytest run regenerates the board, forcing the agent to
manually `git checkout` the board files before each review. This is the only
place the coupling still bites in routine flow.

## Options

| Option | Human browsability | External/in-repo links | Merge-conflict risk | Validation noise | Public-agent onboarding |
| --- | --- | --- | --- | --- | --- |
| **A. On-demand / artifact only** (stop committing) | lost in repo | **breaks ~147 links** | eliminated | eliminated | worse (no in-repo board) |
| **B. Committed but strictly ephemeral** | preserved | preserved | low (post-merge Action owns it) | already INFO | unchanged/good |
| **C. Hybrid** (committed pointer + artifact heavy views) | partial | partial breakage | low | mixed | mixed |

### A. Generate-on-demand only

Stop committing the files; produce them via a local command or CI artifact;
canonical task YAML stays the single source of truth. Cleanly eliminates the
friction class — but it **breaks the ~147 in-repo references** to
`tasks/ACTIVE.md` and the task views, removes the browsable board from the repo
and web UI, and makes onboarding worse for public agents who currently start
from `tasks/ACTIVE.md`. The cost is concentrated and large; the benefit
duplicates what TASK-0466 already achieved by other means.

### B. Committed but strictly ephemeral (recommended)

Keep the files committed (zero link breakage, board stays browsable), and make
**every** routine process treat them as ephemeral so they never block flow:
staleness stays `INFO` (done), the live smoke test restores them (done), and the
**review tool ignores generated board paths when assessing working-tree
cleanliness** (the one residual fix). The post-merge Action remains the only
writer on `main`. Most of this already shipped in TASK-0466; the migration is
small.

### C. Hybrid

Keep a lightweight committed pointer/board and move the heavy views to
artifacts, or relocate generated views under a path that tooling treats as
generated by convention. This adds a second mechanism and still breaks the
subset of links that point at the relocated heavy views, for a benefit Option B
already delivers without the added surface.

## Decision

Option B splits on whether `tasks/ACTIVE.md` itself is still worth keeping:

- **B1 — keep `ACTIVE.md` committed-but-ephemeral.** Worthwhile only if humans
  actually read the single full-board file.
- **B2 — retire `ACTIVE.md`, keep the task views as the human board.**

A maintainer review (2026-05-30) confirmed the deciding fact: **neither agents
nor humans use `tasks/ACTIVE.md`.** Agents enter through `apl_mission.py` (live
READY candidates from canonical YAML); humans navigate via the GitHub task list
and the lighter `docs/task-views/*.md`; and the "history" value of `ACTIVE.md`
is strictly redundant with `git log tasks/`, which is the real, richer change
record. Its ~147 inbound links are boilerplate "see the board" pointers, not
content anyone consumes.

**Decision: adopt B2 — retire `tasks/ACTIVE.md`.** With no agent or human
consumer, its only marginal value (a one-glance full board) is unused, while it
remains the largest churn source and a 147-link maintenance cost. The task views
become the canonical human navigation surface; `git log` is the history; the
mission script is the agent entry point. Option A's broader concern ("breaks
onboarding") does not apply because onboarding never depended on `ACTIVE.md`;
Option C adds complexity for no gain.

The guiding rule after B2: **canonical `tasks/TASK-*.yaml` are the source of
truth, `apl_mission.py` is the agent entry point, `docs/task-views/*.md` (still
generated and committed-but-ephemeral) are the human navigation surface, and
`git log` is the history. There is no separate full-board file.**

Scope clarification after TASK-0510: this decision does **not** authorize new
committed generated files for agent routing. The retained `docs/task-views/*.md`
are a specific human-facing navigation exception with a post-merge regeneration
owner. Frequently changing agent-facing queue filters, lane indexes, conflict
scans, and strategy summaries should be produced by scripts/CLI output,
snapshot sections, or CI artifacts rather than committed static caches.

## Migration plan (B2)

`tasks/ACTIVE.md` is woven through ~26 code files, 6 test files, ~38 docs, and
the CI/sync Actions, so the retirement is staged to keep each PR green and
reviewable. **Task views stay** — they share the generator machinery, so the
work removes only the `ACTIVE.md` branch of it.

1. **Stage 1 — decision (this note).** Record B2; no behavior changed here.
2. **Stage 2 — code, tests, and Actions.** Stop generating/syncing
   `tasks/ACTIVE.md` (`generated_state.py`, the `sync-active-board` CLI path,
   `active_board.py`); drop its staleness check in `repository.py` while keeping
   the task-view staleness check; remove it from the context bundle
   (`generate_context_bundle.py`, `CONTEXT_BUNDLE_SOURCE_FILES`), snapshot,
   closeout, campaign-curator, and mission-control consumers; update the
   `sync-active-board` workflow and CI to regenerate only the task views; delete
   `tasks/ACTIVE.md`; update/remove the affected tests. Repo stays green.
3. **Stage 3 — docs and protocols.** Redirect the ~38 documents / ~125
   references from `tasks/ACTIVE.md` to `docs/task-views/*.md` (current work) or
   `apl_mission.py` (agent entry) and `git log` (history); remove the
   `tasks/ACTIVE.md` row from `AGENTS.md`/`docs/agent-task-protocol.md` read
   orders and the PR template.

No generated-board behavior is changed by this decision task itself.

## Follow-up implementation task spec (for maintainer acceptance)

- **Title:** Retire tasks/ACTIVE.md and redirect navigation to task views (B2)
- **Type:** `maintainer_workflow`
- **Scope:** execute Stage 2 then Stage 3 above. Keep `docs/task-views/*.md`
  generated and committed-but-ephemeral; keep `git log` as history; keep
  `apl_mission.py` as the agent entry point.
- **Validation:** `python3 -m ruff check .`, `python3 -m pytest`,
  `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings`,
  `python3 -m pytest tests/test_docs_links.py`.
- **Out of scope:** changing task-view generation or `apl_mission.py`; removing
  the post-merge Action (it keeps generating the task views).

## What this decision does not do

- It does not delete `tasks/ACTIVE.md` or change generation in this PR — Stage 2
  does that under the follow-up task.
- It does not change task-view generation or `apl_mission.py`.
- It does not promote any claim.

## Cross-references

- `tasks/proposals/20260530-roman-decouple-generated-board-files.yaml` — the
  proposal that asked this question (accepted as TASK-0470).
- `TASK-0466` — fixed
  F1/F2 symptoms.
- `.github/workflows/sync-active-board.yml` — the post-merge regenerator.
- `physics_lab/registry/repository.py` — board-staleness severity logic.
