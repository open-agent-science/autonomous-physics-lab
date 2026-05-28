# Private Agent Challenge Pack

This challenge pack gives invited contributors and their agents a controlled
set of challenge options before public opening.

The goal is workflow validation, not output volume. Each challenge should show
that a contributor-agent pair can find the right protocol, stay inside one
task, produce reviewable artifacts, report validation, and avoid claim
promotion.

The levels below describe challenge size and review intensity, not permission
to do science. A maintainer may assign any contributor-agent pair to a
research-first task, including hypothesis testing, replay, audit, or sandbox
pilot work. Use the levels only to choose a good first scope for a private
validation run.

Use this pack with:

- [Private Contributor Pilot](./private-contributor-pilot.md)
- [Private Contributor Validation Plan](./private-contributor-validation-plan.md)
- [Private Contributor Scorecard](./private-contributor-scorecard.md)
- [Agent Task Protocol](./agent-task-protocol.md)
- [Use Your Agent](./use-your-agent.md)

## Before Starting

Every contributor-agent pair should begin with the same baseline:

1. Read `AGENTS.md`.
2. Read [Agent Task Protocol](./agent-task-protocol.md).
3. Run `python3 scripts/apl_mission.py --output onboarding`.
4. Pick exactly one `READY` task, one approved microtask item, or one
   maintainer-assigned challenge. Prefer research, replay, audit, or
   hypothesis-testing tasks when the maintainer has not asked for support work.
5. Create the canonical branch before editing files.
6. Keep claims, canonical results, and knowledge unchanged unless the task
   explicitly authorizes that scope.

If the contributor is not sure which level to attempt, start with a small
Level 1 scope or ask the maintainer to assign a research-first challenge.

## Level 1: Orientation And Replay

Level 1 checks whether the contributor and agent can navigate the repository,
follow branch protocol, and produce a small reviewable PR.

Expected time: 30 to 60 minutes.

Good first challenge types:

| Challenge | Output | Validation |
| --- | --- | --- |
| Replay one result | A short note under `docs/notes/` describing the command, output location, expected metric, and limitation. | `python3 scripts/reproduce_core_results.py` or the relevant example run into `/tmp`. |
| Audit one proposal | A narrow review note for one proposal or candidate, with verdict ceiling and open questions. | `python3 -m physics_lab.cli validate-repo .` |
| Check one doc path | A small docs PR fixing stale navigation, missing links, or confusing onboarding text. | `python3 -m pytest tests/test_docs_links.py` and `python3 -m physics_lab.cli validate-repo .` |
| Validate one registry entry | A note confirming schema, target semantics, and no-claim wording for one prediction or proposal artifact. | Targeted pytest or `python3 -m physics_lab.cli validate <path>`. |

Level 1 success criteria:

- branch uses canonical format;
- PR links exactly one task, proposal, or approved queue item;
- no generated board files are left dirty unless the task requires sync;
- validation commands are listed in the PR body;
- no claim or result status changes are made.

Level 1 is a good fit for first-time agent use. It should not introduce new
scientific candidates unless the selected `READY` task or maintainer challenge
assigns that scope.

## Level 2: Bounded Workflow Exercise

Level 2 checks whether the contributor-agent pair can complete a larger but
still bounded workflow with artifacts, limitations, and review notes.

Expected time: 1 to 3 hours.

Good challenge types:

| Challenge | Output | Validation |
| --- | --- | --- |
| Run one sandbox proposal batch | Sandbox-only proposals, metrics, and review note under the task-approved paths. | Task-specific command plus full repository validation. |
| Create a visualization | A committed static visual or review note tied to an existing result, with no strengthened claim language. | Docs/image checks plus `validate-repo`. |
| Validate one campaign profile | A review note checking profile scope, allowed outputs, forbidden outputs, and active queue alignment. | Targeted tests if present plus `validate-repo --strict --fail-on-warnings`. |
| Complete a small microtask batch | Queue-approved microtask outputs from one campaign, with limitations and `REVIEW_NEEDED` where uncertain. | Microtask helper status/preflight and queue-specific validation. |

Level 2 success criteria:

- all outputs are sandbox-only or documentation-only unless the task says
  otherwise;
- negative, blocked, or inconclusive outcomes are preserved;
- task-specific validation is run before full validation;
- PR body includes changed files, limitations, and result-artifact impact;
- review bundle is generated before handoff.

Level 2 is the right level for contributors who already completed one small PR
or who are pairing with an agent under close maintainer review.

## Level 3: Approved Scientific Pilot

Level 3 is for end-to-end scientific pilot work inside an approved campaign
profile. It should be assigned by a maintainer or selected from a canonical
`READY` task that explicitly allows autonomous scientific pilot work.

Expected time: 3 hours or more, often split across review cycles.

Good challenge types:

| Challenge | Output | Validation |
| --- | --- | --- |
| Approved campaign pilot | Proposals, sandbox runs, metrics, failure cases, and a review summary under task-approved paths. | Full task validation plus repository validation. |
| Independent replay or audit | Reproduced metrics, split sensitivity, failure analysis, and conservative verdict. | Replay command, targeted tests, full validation. |
| Adversarial review of a candidate family | Leakage review, negative controls, overfit analysis, limitations, and recommended next action. | Task-specific audit checks and full validation. |

Level 3 success criteria:

- campaign profile and task scope explicitly allow the work;
- candidate generation, filtering, and execution are deterministic where
  possible;
- no live external data fetch is used unless the task explicitly allows it;
- canonical `results/`, `claims/`, and `knowledge/` are not promoted
  automatically;
- verdict vocabulary stays scoped, for example `INCONCLUSIVE`,
  `OVERFITTED`, `PARTIALLY_VALID`, or `VALID_IN_RANGE`;
- a maintainer can review the artifact trail without reconstructing hidden
  agent reasoning.

Level 3 can be used as a first contribution when the maintainer deliberately
assigns a capable contributor-agent pair to a research-first pilot. Otherwise,
use a smaller challenge first to validate protocol discipline.

## Validation By Level

Use the task file as the source of truth. When the task does not provide a
narrower path, use this minimum set.

Level 1:

```bash
python3 -m ruff check .
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
git diff --check
```

Level 2 and Level 3:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli run examples/pendulum.yaml --output-dir /tmp/apl-pendulum
python3 -m physics_lab.cli run examples/damped_oscillator.yaml --output-dir /tmp/apl-damped
python3 -m physics_lab.cli validate-repo .
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
git diff --check
```

Before PR handoff:

```bash
./scripts/apl_review_bundle.sh
```

If a command cannot run because of local environment or sandbox restrictions,
record the failure and the safer retry path in the PR body.

## Handoff Scorecard

Maintainers can copy this block into a review note or private validation log.

```text
Contributor:
Agent tool:
Challenge level:
Task or queue item:
PR:

Score: PASS | PASS_WITH_NOTES | NEEDS_REWORK | BLOCKED

Orientation:
- Found the correct starting docs:
- Chose an appropriate level:
- Avoided side-channel assumptions:

Protocol:
- Branch format correct:
- PR title/body format correct:
- One task or queue item only:
- Review bundle present:

Validation:
- Local validation reported:
- CI result:
- Generated files synced or intentionally unchanged:

Scientific safety:
- No automatic claim promotion:
- Sandbox outputs stayed sandbox-only:
- Limitations and negative results preserved:
- Overclaim wording avoided:

Maintainer notes:
Follow-up task needed:
```

## Level Selection Guidance

Use this simple routing rule:

- choose Level 1 for a first PR, uncertain contributor, or docs/replay focus;
- choose Level 2 after one successful small PR or when testing a bounded
  workflow;
- choose Level 3 only for maintainer-approved scientific pilot work.

Do not advance levels by title or confidence alone. Advance when the previous
PR showed protocol discipline, validation discipline, and conservative
scientific wording.

## What Counts As A Good Outcome

A good challenge outcome can be:

- a clean positive result;
- a negative result with clear evidence;
- an inconclusive audit with well-stated blockers;
- a docs or workflow fix that reduces maintainer side-channel support.

The challenge pack is successful when the maintainer can tell why the work is
reviewable, what was validated, what remains limited, and whether the
contributor-agent pair is ready for a harder level.
