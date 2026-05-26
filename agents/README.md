# `agents/` — Agent Role Soul Files

This directory holds one **soul file** per agent role active in APL.

A soul file is the **short, activation-ready** definition of a role:
identity, scope, goals, allowed tools, scripts, restrictions, and
cross-role invocation rules. The deep authoritative protocol for each
role lives in `docs/`; soul files here reference those docs, not
duplicate them.

## Purpose

When a maintainer or contributor switches an agent into a role
("режим архітектора", "Run Scientific Campaign Curator for nuclear
mass", "review PR 565"), the agent reads the corresponding
`agents/<role-id>.md` soul file as its first action and applies that
role's instructions for the rest of the session (or until the role is
switched).

This means agent instructions are not duplicated across sessions:
**one role, one file, one canonical activation source**.

## Active Roles

| Role file | Role name | When to use |
| --- | --- | --- |
| [`architect.md`](architect.md) | **APL Architect** | Cross-protocol design, bottleneck analysis, safety review for the repository as a whole. |
| [`review-agent.md`](review-agent.md) | **Maintainer Review Agent** | Pre-merge PR review and post-merge task closeout. |
| [`scientific-curator.md`](scientific-curator.md) | **Scientific Campaign Curator** | Campaign-level research brief: what did this campaign teach us, what should run next. |
| [`researcher.md`](researcher.md) | **Researcher (default agent)** | Default role: pick one READY task, execute it to REVIEW_READY. |
| [`task-proposal-agent.md`](task-proposal-agent.md) | **Task Proposal Agent** | Convert a new idea into a proposal under `tasks/proposals/` when no existing READY task fits. |
| [`microtask-agent.md`](microtask-agent.md) | **Scientific Microtask Agent** | Spare-budget queue work from `tasks/microtasks/`. |

## Template

[`AGENT-TEMPLATE.md`](AGENT-TEMPLATE.md) is the canonical shape for any
new role file. Every active soul file conforms to this template; a test
in `tests/test_agent_role_soul_files.py` enforces conformance.

## Activation Convention

When the maintainer (or any contributor) says a role's activation
phrase (e.g. "режим архітектора", "Architect mode", "run campaign
curator for X", "review PR <n>"), the agent:

1. Locates the matching `agents/<role-id>.md` by walking the
   `activation_phrases` list in each role's frontmatter.
2. Loads the role's `required_reading` list.
3. Applies the role's `scope`, `goals`, `restrictions`, and
   `operating_mode_summary` for the rest of the session.
4. Returns to the previous role only when explicitly switched.

Activation is currently a convention, not a script. A helper script
(`scripts/apl_agent_mode.py <role>` that prints the soul file ready for
context injection) may be added later as a separate task if the
convention proves load-bearing at scale.

## Cross-Role Invocation

A role may invoke another role for a bounded sub-task. The trigger and
target are listed in each role's `can_invoke_other_roles` frontmatter
field. Examples:

- The Architect opens an architectural PR and invokes the Review
  Agent (`scripts/apl_review_pr.py`) for gate verification.
- The Researcher opens a task PR and invokes the Review Agent in the
  same way.
- The Scientific Curator may invoke the Review Agent when assessing a
  campaign-impacting PR, or the Architect when the analysis surfaces a
  cross-protocol issue.

Cross-role invocation does not transfer authority — the calling role
returns to its own restrictions afterward.

## What This Directory Is Not

- **Not a replacement for `docs/agent-catalog.md`.** That doc is the
  authoritative narrative description of every agent path APL
  supports. The soul files here are operational activation files.
- **Not a place for new protocols.** Protocol content belongs under
  `docs/` (per-class protocol, claim-promotion-policy, etc.). Soul
  files reference these documents.
- **Not a place for canonical scientific artifacts.** CLAIM-*,
  RESULT-*, PRED-*, KNOW-* live under their own directories per
  `docs/result-promotion-protocol.md`.

## Legacy File

`example-agent.yaml` is a legacy placeholder used as a test fixture by
`tests/test_pendulum.py` and `tests/test_damped_oscillator.py`. It is
not an active role definition. A follow-up task will move the fixture
into `tests/fixtures/` and remove this file; until then it stays here
for test compatibility. The legacy file does **not** conform to the
`AGENT-TEMPLATE.md` shape and is intentionally excluded from the
template-compliance test.

## Adding a New Role

1. Copy `AGENT-TEMPLATE.md` to `agents/<new-role-id>.md`.
2. Fill all frontmatter fields and body sections.
3. Decide which existing roles can invoke the new role and update their
   `can_invoke_other_roles` lists symmetrically.
4. Add the new role to the "Active Roles" table above.
5. Add a cross-reference in `docs/agent-catalog.md` if the role
   represents a meaningfully new agent path.
6. Run `python3 -m pytest tests/test_agent_role_soul_files.py` to
   confirm template compliance.

If the role's deep protocol does not yet exist as a `docs/*.md` file,
create the protocol first (with appropriate maintainer review) and
then point the soul file at it. Soul files should not be the only
source of truth for a role's deep behaviour.
