# Autonomous Research Loop

## Purpose

This document defines the first repository-native autonomous research loop for
APL.

The loop lets an agent do bounded scientific exploration inside a reviewed
campaign profile. It does not let the agent publish claims, promote hypotheses,
or write canonical result artifacts.

The goal is to make autonomous work reviewable before it becomes powerful.

## Scope

The first loop is sandbox-only.

Agents may:

- select a whitelisted campaign profile;
- draft hypothesis proposals;
- draft experiment proposals;
- run deterministic checks in a sandbox branch or temporary output directory;
- summarize sandbox evidence with metrics, limitations, and failure modes;
- open a reviewable PR that asks whether a later canonical task should exist.

Agents must not:

- write or edit `claims/` files as promoted evidence;
- write canonical `results/EXP-*/RUN-*` artifacts;
- mark hypotheses as validated knowledge;
- change claim status;
- change canonical verdicts;
- merge PRs;
- represent sandbox evidence as public success evidence.

If a sandbox run looks promising, the output is still a proposal for maintainer
review. A later task may convert reviewed work into canonical experiment and
result artifacts.

## Contract

An autonomous research run follows one contract:

1. Select exactly one campaign profile from `campaign_profiles/`.
2. Confirm the profile is eligible for autonomous work.
3. Run the research quality gate in `docs/research-quality-gate.md`.
4. Create one hypothesis proposal from
   `hypothesis_proposals/HYP-PROPOSAL-TEMPLATE.yaml`.
5. Create one experiment proposal from
   `experiment_proposals/EXP-PROPOSAL-TEMPLATE.yaml`.
6. Run only the allowed sandbox checks listed by the campaign profile.
7. Record sandbox evidence as proposal evidence, not canonical evidence.
8. Prepare a PR handoff with task id, campaign id, inputs, method, code
   references, metrics, limitations, and verdict.
9. Stop for maintainer review.

The loop is allowed to end with a negative result, inconclusive result, or
review-needed result. Failed candidates are valid scientific memory when the
method and failure mode are specific.

## Loop Phases

### 1. Campaign Selection

The agent starts from `docs/campaign-autonomy-whitelist.md` and selects one
profile.

The selected profile defines:

- allowed hypothesis families;
- allowed experiment families;
- required references;
- required quality checks;
- forbidden claims;
- required PR handoff contents.

If the campaign is not listed as whitelisted, the agent stops and proposes a
task instead of running the loop.

### 2. Proposal Drafting

The agent drafts proposal files before running exploratory work.

Hypothesis proposals describe the candidate idea, claim ceiling, assumptions,
novelty check, and expected falsification route.

Experiment proposals describe the deterministic procedure, inputs, output
metrics, validation range, sandbox output location, and failure conditions.

Proposal files are review surfaces. They are not canonical hypotheses or
experiments.

### 3. Sandbox Execution

Sandbox execution may use existing repository commands and temporary output
directories such as `/tmp/apl-*`.

Sandbox execution must preserve:

- exact command lines;
- code references;
- input file references;
- metrics;
- limitations;
- failure cases;
- verdict vocabulary.

Sandbox evidence may be summarized in proposal files or a scoped note, but it
must not be stored as canonical `RESULT-*` evidence.

### 4. Quality Gate

The agent applies `docs/research-quality-gate.md` before PR handoff.

If the gate fails, the PR may still be useful, but it must be framed as
`REVIEW_NEEDED` or `INCONCLUSIVE`, and the blocker must be explicit.

### 5. PR Handoff

The handoff PR must include:

- task id or microtask id;
- campaign profile id;
- proposal file paths;
- input references;
- method;
- code references;
- metrics;
- limitations;
- verdict;
- maintainer decision requested.

Maintainer decisions may include:

- accept as negative sandbox memory;
- request a canonical experiment task;
- request a narrower follow-up proposal;
- reject as overfit, unsafe, or out of scope.

## Evidence Boundary

Sandbox evidence can support a maintainer decision, but it cannot support a
public claim by itself.

Promotion requires a later reviewed path through the existing repository
objects:

- canonical experiment definition;
- reproducible canonical run;
- `RESULT-*` artifact;
- claim promotion review under `docs/claim-promotion-policy.md`;
- maintainer merge and closeout.

This boundary is the core safety property of the loop.

## First Pilot

The first whitelisted pilot campaign is pendulum formula falsification.

Pendulum is appropriate because it has an exact reference function, mature
range-aware wording, known failure modes, and deterministic benchmark
commands.

Particle-mass relations are allowed only in a guardrail-heavy,
falsification-first profile. Muon g-2, Hubble tension, and broad constants
derivation work are outside the first autonomy whitelist.
