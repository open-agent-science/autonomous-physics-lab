# `agents/` — Agent Role Profiles

This directory holds one **role profile** per agent role active in APL.

An agent role profile is the activation-ready operational profile for a role:
identity, scope, goals, allowed tools, scripts, restrictions, and
cross-role invocation rules. Each role lives in `agents/<role-id>.yaml`.
The deep authoritative protocol for each role lives in `docs/`; profiles
reference those docs via `required_reading`, not duplicate them.

## Format

All role files are **pure YAML** (`agents/<role-id>.yaml`), consistent
with the rest of the repository's structured data (tasks, hypotheses,
experiments, predictions, results, schemas). This directory is
agent-first: machine-parseable structure is primary; this README is
the only human-facing navigation file.

Schema: `physics_lab/schemas/agent.schema.json`.
Template: [`AGENT-TEMPLATE.yaml`](AGENT-TEMPLATE.yaml).
Conformance test: `tests/test_agent_role_profiles.py`.

## Purpose

When a maintainer or contributor asks the agent to act in a role
(in any language, with any wording), the agent matches the request
against each role file's `activation.intent`, loads the matching
`agents/<role-id>.yaml`, and applies that role's instructions for the
rest of the session.

This means agent instructions are not duplicated across sessions:
**one role, one file, one canonical activation profile**.

## Active Roles

### [Architect](architect.yaml)

Helper role that automates parts of the architecture and cross-protocol
work. Used for protocol design, bottleneck analysis, safety review,
audits, refactoring proposals, and agent-role organisation.

### [Maintainer Review Agent](review-agent.yaml)

Pre-merge pull-request review and post-merge task closeout. Returns an
explicit verdict; never merges.

### [Scientific Campaign Director](scientific-curator.yaml)

Campaign-level scientific direction assistant. Also responds to the older
Scientific Campaign Curator / campaign-curator aliases. It summarises what a
campaign has learned, maintains campaign-page and mission hygiene, recommends
promotion/replay/do-not-promote decisions, and designs useful next task waves
without creating work merely to keep agents busy.

### [Researcher](researcher.yaml)

Default role for any new agent session. Picks one READY task and
executes it through the canonical lifecycle to `REVIEW_READY`.

### [Task Proposal Agent](task-proposal-agent.yaml)

Drafts proposal-only PRs under `tasks/proposals/` when no existing
READY task fits the work that needs doing.

### [Scientific Microtask Agent](microtask-agent.yaml)

Bounded queue work from `tasks/microtasks/`. Typically used when there
is spare token or time budget and a campaign queue has items in its
available list.

### [Data Acquisition / Source-Pinning](data-acquisition.yaml)

Maintainer-run lane that turns an admissible published source into a pinned,
checksummed, provenance-rich artifact (or a precise blocker). Runs bounded
public/key-free fetches or prepares a runbook for maintainer-run key-gated
fetches; never curates rows, never commits secrets, never live-fetches inside
benchmark code. See `docs/source-acquisition-lane.md`.

## Activation Convention

When the maintainer (or any contributor) asks the agent to act in a
role, the agent:

1. Matches the request against the `activation.intent` of each role
   file. Activation is **concept-based**, not phrase-based: any
   natural-language wording in any language that expresses the same
   intent should fire the role. Do not encode or depend on literal translated
   phrases for non-English requests. The `activation.example_phrases` list in
   each role file is informational only.
2. Loads the role's `required_reading` list.
3. Applies the role's `scope`, `goals`, `restrictions`, and
   `cadence` for the rest of the session.
4. Returns to the previous role only when explicitly switched.

Activation is currently a convention, not a script. A helper script
that prints the role profile ready for context injection may be added
later if the convention proves load-bearing at scale.

## Cross-Role Invocation

A role may invoke another role for a bounded sub-task. The trigger and
target are listed in each role's `can_invoke_other_roles` field.
Examples:

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
  supports. The profiles here are operational activation files.
- **Not a place for new protocols.** Protocol content belongs under
  `docs/` (per-class protocol, claim-promotion-policy, etc.). Profiles
  reference these documents via `required_reading`.
- **Not a place for canonical scientific artifacts.** CLAIM-*,
  RESULT-*, PRED-*, KNOW-* live under their own directories per
  `docs/result-promotion-protocol.md`.

## Adding a New Role

1. Copy `AGENT-TEMPLATE.yaml` to `agents/<new-role-id>.yaml`.
2. Fill every required field per
   `physics_lab/schemas/agent.schema.json`.
3. Decide which existing roles can invoke the new role and update their
   `can_invoke_other_roles` lists symmetrically.
4. Add the new role to the "Active Roles" section above.
5. Add a cross-reference in `docs/agent-catalog.md` if the role
   represents a meaningfully new agent path.
6. Run `python3 -m pytest tests/test_agent_role_profiles.py` to
   confirm schema conformance.

If the role's deep protocol does not yet exist as a `docs/*.md` file,
create the protocol first (with appropriate maintainer review) and
then point the role profile at it. Profiles should not be the only
source of truth for a role's deep behaviour.
