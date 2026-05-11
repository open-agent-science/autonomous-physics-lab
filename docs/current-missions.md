# Current Missions

APL now uses an **Agent First** entrypoint.

The default path for a new coding agent is no longer "scan every task and pick
something small." The default path is:

```bash
python3 scripts/apl_mission.py
```

That command starts **Research Mode** and recommends the highest-value
reviewable scientific mission. Support, microtask, review, and closeout work
still exists, but it is explicit:

```bash
python3 scripts/apl_mission.py --mode support
python3 scripts/apl_mission.py --mode maintainer
```

Machine-readable mission data lives in
[`../missions/current.yaml`](../missions/current.yaml).

## Default Mode

Default mode: `research`

Research Mode is for:

- hypothesis testing;
- replay and split-sensitivity checks;
- adversarial audits of sandbox evidence;
- bounded sandbox experiments;
- negative result preservation;
- PR-ready result drafts.

It is not a claim-promotion lane. Canonical claims, knowledge, and result
artifacts still require maintainer review.

## Recommended Mission Now

**Nuclear Mass Surface** is the current flagship validation mission.

Recommended direction:

1. Run split-sensitivity replay for `HYP-PROPOSAL-0021`.
2. Adversarially audit `AGENT-RUN-0005`.
3. Only then run a second bounded nuclear sandbox batch.

Why:

- it uses a real data surface;
- the frozen baseline and holdout protocol already exist;
- the first autonomous nuclear pilot exists;
- the strongest candidate is still sandbox-only evidence;
- the next scientific value comes from validation, not from broadening claims.

Guardrails:

- do not promote `HYP-PROPOSAL-0021` to a claim automatically;
- do not describe the residual candidate as breakthrough physics;
- do not run unbounded nuclear formula search;
- do not rewrite canonical result artifacts casually.

## Alternatives

The mission script also exposes secondary research directions:

- **Anharmonic Oscillator Period Benchmark** — a safe nonlinear methodology
  benchmark with perturbative and numerical baselines.
- **Dimensional Analysis Validator** — a quality-floor track for formula sanity
  checks and adversarial edge cases.

These are good alternatives when the maintainer wants breadth, but the default
recommendation remains the current top-ranked mission.

## Support And Maintainer Modes

Support Mode is for docs, tests, packaging, task hygiene, and microtasks:

```bash
python3 scripts/apl_mission.py --mode support
```

Maintainer Mode is for review and closeout assistance:

```bash
python3 scripts/apl_mission.py --mode maintainer
```

This preserves the existing maintainer review agent and closeout workflow.
Agent First means research-first onboarding for new contributors; it does not
mean bypassing maintainer authority.

## Copy-Paste Agent Prompt

Generate the current prompt with:

```bash
python3 scripts/apl_mission.py --agent-prompt
```

Short version:

```text
You are working in Autonomous Physics Lab.

Start in Agent First Research Mode. Read AGENTS.md and docs/agent-task-protocol.md,
then run `python3 scripts/apl_mission.py --json`. Choose the recommended
research mission unless the maintainer gave a stricter task. Create a canonical
task branch before editing files. Execute the full loop autonomously: inspect
evidence, test or audit the hypothesis, preserve negative results, update
sandbox/review artifacts, run validation, generate a review bundle, and prepare
a PR. Keep outputs sandbox-only unless a canonical task explicitly allows
promotion. Do not promote claims, rewrite canonical results, or use
breakthrough-style wording.
```
