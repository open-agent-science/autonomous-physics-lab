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

## Suggested Challenge Lanes

These lanes are onboarding and validation suggestions, not permission levels.
They help maintainers offer appropriately scoped first tasks and measure where
the repository workflow is unclear.

Any invited contributor may use their own agent to run approved automated
scientific tracks, propose new tracks, or execute sandbox work when the task,
campaign profile, and repository protocol allow it.

Level 1 tasks are good first checks: replay one result, audit one proposal, or
check one documentation path.

Level 2 tasks exercise a larger workflow: run one sandbox proposal batch, create
visual evidence, or validate one campaign profile.

Level 3 tasks are end-to-end scientific pilots inside approved campaign
profiles: generate proposals, filter weak candidates, run sandbox experiments,
and prepare reviewable result artifacts.

The guardrail is not who may run science. The guardrail is where outputs land:
sandbox evidence and proposal artifacts are encouraged, while canonical results,
claims, and knowledge remain maintainer-review-gated.

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
