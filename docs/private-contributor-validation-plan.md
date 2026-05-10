# Private Contributor Validation Plan

This phase is a controlled validation pass before public opening.

Private contributors and their agents are not yet a public contributor network.
They are a small test cohort used to verify that APL can support external work
without maintainer side-channel explanations.

## Goal

Validate the full workflow:

`task -> branch -> PR -> validation -> review -> merge -> closeout`

The main question is not whether one more scientific result can be produced.
The main question is whether invited contributors using agents can produce
reviewable scientific and technical PRs without breaking repository protocol or
promoting claims automatically.

## What This Phase Tests

- a new human plus agent can understand the repository from committed docs
- branches, PR titles, task IDs, and metadata follow the protocol
- PRs contain enough artifacts for review
- validation commands are run and reported
- review helpers catch protocol, claim, and artifact problems
- closeout works after merge
- sandbox and negative results are preserved
- claims and knowledge are not promoted automatically
- generated boards and context files do not stay dirty after merge

## Private Alpha Gates

Before treating the repository as public-ready, collect evidence for:

- 3-5 invited contributors or contributor-agent pairs
- 10 or more task-based PRs
- 3 or more scientific sandbox PRs
- 2 or more technical, docs, or test PRs
- 2 or more independent replay or audit PRs
- 0 direct pushes to `main`
- 0 automatic claim promotions
- 0 dirty active-board or context sync after merge
- 0 public-facing local path leaks
- green GitHub CI on a release-candidate branch or PR

## Contributor Tracks

Level 1 contributors should start with replay, audit, docs-path checks, or small
artifact validation tasks.

Level 2 contributors may run one sandbox proposal batch, create visual evidence,
or validate one campaign profile.

Level 3 contributors may run a scientific pilot only inside an approved campaign
profile, with sandbox-only outputs and maintainer review before any promotion.

## Current Focus

Use the Nuclear Mass Surface as the flagship private-validation campaign, but do
not run a second nuclear sandbox batch until the independent audit of
`HYP-PROPOSAL-0021` is complete.

Near-term queue:

- `TASK-0173` - independent replay and audit of `HYP-PROPOSAL-0021`
- `TASK-0174` - nuclear pilot evidence card and visual funnel
- `TASK-0175` - public docs sync after the nuclear wave
- `TASK-0177` - private agent challenge pack

Keep hype-sensitive topics such as muon g-2, Hubble tension, and broad
mass-relation searches on the watchlist until the private validation phase has
strong replay and review evidence.

