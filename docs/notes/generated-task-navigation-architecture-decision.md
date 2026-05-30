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

## Recommendation

**Adopt Option B — committed but strictly ephemeral.** It preserves the ~147
navigation links and the browsable board, keeps `tasks/ACTIVE.md` as the agent
onboarding entry point, and reduces to a single remaining mechanical fix because
TASK-0466 already handled the rest. Option A's clean-slate appeal does not
justify breaking 147 references and degrading onboarding; Option C adds
complexity for no net gain over B.

The guiding rule for Option B: **the generated board is committed for humans to
read, owned on `main` only by the post-merge Action, and treated as ephemeral by
every validator, test, and review step — never hand-edited, never a blocker.**

## Migration plan

1. **Review-tool cleanliness ignore (the residual fix).** Make the maintainer
   review path ignore `tasks/ACTIVE.md` and `docs/task-views/*.md` when it
   evaluates `git status clean`, so a local board regeneration during validation
   no longer blocks the review. This is the only behavior change required and is
   specced as the follow-up task below.
2. **Already done (TASK-0466):** board staleness `INFO`, smoke-test restore,
   mission-action `INFO`.
3. **Documentation:** the rule above is the canonical statement of the
   committed-but-ephemeral convention; the existing `AGENTS.md` /
   `docs/agent-task-protocol.md` guidance ("agents do not commit regenerated
   board files; the post-merge Action owns them") already aligns with it.

No generated-board behavior is changed by this decision task itself.

## Follow-up implementation task spec (for maintainer acceptance)

- **Title:** Make the review tool ignore generated board files in cleanliness check
- **Type:** `maintainer_workflow`
- **Scope:** in `physics_lab/registry/maintainer_review.py`, exclude
  `tasks/ACTIVE.md` and `docs/task-views/*.md` from the `git_status_clean`
  gate used by `run_task_validation` / report building, so a regenerated board
  does not disable validation or raise the "git status not clean" required-fix.
  Add a focused test. Do not change board generation, the post-merge Action, or
  staleness severity.
- **Validation:** `python3 -m ruff check .`, `python3 -m pytest`,
  `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings`.
- **Out of scope:** removing the committed board, changing links, or altering
  the Action.

## What this decision does not do

- It does not change how `tasks/ACTIVE.md` or the task views are generated.
- It does not edit generated task views or `tasks/ACTIVE.md`.
- It does not modify the post-merge Action or staleness severity.
- It does not promote any claim.

## Cross-references

- `tasks/proposals/20260530-roman-decouple-generated-board-files.yaml` — the
  proposal that asked this question (accepted as TASK-0470).
- `tasks/TASK-0466-reduce-agent-flow-friction-in-protocol-tooling.yaml` — fixed
  F1/F2 symptoms.
- `.github/workflows/sync-active-board.yml` — the post-merge regenerator.
- `physics_lab/registry/repository.py` — board-staleness severity logic.
