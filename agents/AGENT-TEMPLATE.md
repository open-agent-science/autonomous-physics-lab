---
role_id: <role-id-kebab-case>
role_name: "<Human-Readable Role Name>"
short_description: "<one-sentence purpose>"
status: planned                              # active | planned | deprecated | legacy_test_fixture
phase: ""                                    # optional, e.g. "Phase 1 (topic-driven)"

activation_intent: >
  Language-agnostic concept describing what the user is asking for when
  invoking this role. The agent should match on this concept regardless
  of the language or exact wording of the request.

example_activation_phrases:                  # informational only; not authoritative
  - "act as <role>"
  - "switch to <role> mode"

scope:
  description: "<2-3 sentences>"
  primary_concerns:
    - "<concern 1>"
    - "<concern 2>"
  out_of_scope:
    - "<out-of-scope item 1>"

goals:                                       # global, durable goals — not current-state metrics
  - "<goal 1>"
  - "<goal 2>"

required_reading:                            # files to load before acting in this role
  - AGENTS.md
  - docs/agent-task-protocol.md
  - <other authoritative protocol files>

allowed_tools:                               # generic capability descriptions, not machine paths
  - "<capability 1>"
  - "<capability 2>"

scripts_to_use:                              # repository scripts the role typically calls
  - scripts/apl_mission.py
  - <other scripts>

can_invoke_other_roles:                      # cross-role calling: list role_ids this role may delegate to
  - role_id: <other-role-id>
    when: "<short trigger description>"

restrictions:
  - "<must-not 1>"
  - "<must-not 2>"

operating_mode_summary: >
  Short paragraph: how the role works day to day, who triggers it, what the
  steady-state cadence looks like.
---

# Role: <Human-Readable Role Name>

> Short tagline: what this role exists to do.

## Purpose

(2-4 sentences explaining when and why this role is used. Treat as the
first thing a fresh agent reads after loading this file. Keep it
generic and durable; specific names, dates, or current-state numbers
do not belong here.)

## When To Use This Role

- (concrete trigger 1)
- (concrete trigger 2)

## When NOT To Use This Role

- (anti-trigger 1)
- (anti-trigger 2)

## Required Reading (Authoritative Protocols)

These files are the **deep protocols** for the role. The soul file above
is the compact activation layer; the documents below are the canonical
rules. In case of contradiction, the linked document wins.

- `<path>` — what it covers
- `<path>` — what it covers

## Typical Activities

A short bulleted list of what the role does in a steady-state session.
Each item should map to a real file or script in the repository when
possible.

- (activity 1)
- (activity 2)
- (activity 3)

## Allowed Outputs

What this role is expected to produce. Reference the canonical
output classes from `docs/result-promotion-protocol.md` where applicable.

- (output 1, e.g. "TASK-PROPOSAL YAML under tasks/proposals/")
- (output 2, e.g. "RESULT-* with review_tier: AGENT_PUBLISHED")

## Cross-Role Invocation

When this role may invoke another role (handing off a bounded sub-task,
or requesting a review). List the target role and the trigger.

- `<other-role-id>` — when (short condition)

## Restrictions

Repeat the frontmatter restrictions in human-readable form. Anti-patterns
specific to this role belong here, not in a generic anti-patterns doc.

- (restriction 1)
- (restriction 2)

## Cadence and Reporting

How often the role acts, and whether it reports back on a schedule or
only on request.

## Template Compliance

This file conforms to `agents/AGENT-TEMPLATE.md`. Schema-level checks
run in `tests/test_agent_role_soul_files.py`.
