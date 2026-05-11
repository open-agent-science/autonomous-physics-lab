# Nuclear Mass Campaign Plan

## Purpose

This note turns the high-level nuclear mass direction into a reviewable APL
campaign plan.

The campaign is about **baseline residuals and controlled correction tests**,
not about asserting a universal formula for nuclei.

## Target Question

The central question is:

Can APL test compact, physically constrained correction terms to a simple
nuclear mass baseline in a way that improves subset behavior or holdout
performance without drifting into overfit or overclaim?

This is intentionally narrower than:

- fully modeling nuclear structure;
- replacing mature nuclear models;
- claiming a new law for all nuclides.

## Planned Queue

1. `TASK-0166` — campaign scaffold and guardrails
2. `TASK-0167` — pinned AME-style dataset loader and schema
3. `TASK-0168` — simple baseline mass formula and residual reports
4. `TASK-0169` — holdout protocol
5. `TASK-0170` — first sandbox-only autonomous pilot

This order is important because later tasks depend on earlier surfaces being
reviewable first.

## First Benchmark Shape

The first canonical benchmark should focus on:

- one pinned nuclear mass dataset surface;
- one simple baseline family;
- one explicit residual target;
- interpretable subset metrics;
- conservative error reporting.

The first benchmark does **not** need:

- advanced multi-model comparison;
- live online fetching;
- overclaim wording;
- autonomous search before baseline and holdout are encoded.

## Candidate Diagnostic Surfaces

The campaign should make at least these diagnostic surfaces explicit:

- shell-closure neighborhoods around well-known magic numbers;
- isotope-chain generalization;
- pairing-sensitive odd-even structure;
- asymmetry-driven residual regions;
- neutron-rich edge behavior;
- uncertainty-normalized residual summaries when the dataset supports them.

These surfaces matter even if no correction family survives holdout. A clean
failure map is still useful scientific memory.

## Holdout Outlook

The default holdout plan should stay internal to the repository until it is
formalized by `TASK-0169`, but current likely slices include:

- random nuclide holdout;
- isotope-chain holdout;
- shell or magic-region holdout;
- neutron-rich extrapolation holdout.

If a later curated post-baseline measurement batch is added, a time-split
holdout may become a stronger external generalization check. That is a future
extension, not a requirement for the first scaffold.

## Dataset Policy

The campaign should treat dataset handling as a scientific surface rather than
as boring plumbing.

Required discipline:

- pin source and version;
- keep parsing deterministic;
- preserve unit and field definitions explicitly;
- avoid mixing measured and extrapolated entries silently;
- make derived target construction reviewable.

## Autonomy Policy

The campaign is not autonomy-ready yet.

Before the first autonomous pilot, APL must already have:

- the dataset layer;
- the baseline benchmark;
- the holdout protocol;
- the campaign profile and guardrails;
- clear negative-result handling.

That is why `TASK-0170` is downstream by design.

## Success Condition for the First Wave

The first wave is successful if it yields:

- a reproducible baseline residual surface;
- a holdout contract that reviewers trust;
- a campaign page that keeps scope honest;
- at least one later sandbox pilot path that cannot overclaim by accident.

It does not need to yield a strong empirical correction immediately.
