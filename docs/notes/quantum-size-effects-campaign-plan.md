# Quantum Size Effects Campaign Plan

## Purpose

This note turns the accepted Quantum Size Effects proposal into a reviewable
APL campaign plan.

The campaign is about **size-dependent measurement residuals with curated
datasets and conservative baselines**, not about discovering new quantum-dot
design rules or supporting any device-fabrication or biomedical claim.

## Target Question

The central question is:

Can APL compare conservative size-scaling baselines against curated
quantum-dot measurement data in a way that exposes interpretable residual
structure across materials and size regimes, without drifting into
material-design overclaim or accidental absorption-versus-emission mixing?

This is intentionally narrower than:

- modeling all quantum-dot electronic structure;
- proposing new effective-mass theory;
- claiming a universal size-property law for any material family.

## Planned Queue

1. `TASK-0222` — campaign scaffold and guardrails (DONE).
2. `TASK-0223` — pinned dataset schema and source manifest (READY).
3. `TASK-0224` — holdout protocol (READY).
4. `TASK-0225` — baseline residual benchmark.
5. `TASK-0226` — first sandbox-only autonomous hypothesis pilot.

`TASK-0223` and `TASK-0224` may now run in parallel because both depend on the
completed scaffold and touch different artifact surfaces. `TASK-0225` remains
blocked until both foundation tasks are reviewed.

## First Benchmark Shape

When `TASK-0225` is unblocked, the first canonical benchmark should focus on:

- one pinned quantum-dot measurement dataset surface defined by `TASK-0223`;
- one conservative baseline family such as Brus-style effective-mass
  approximation, with explicit per-material applicability flags;
- one chosen property kind as the primary residual target — absorption peak,
  emission peak, or bandgap in eV — with the other two reported separately;
- per-material and per-size-range breakdown metrics;
- conservative error reporting in eV with explicit uncertainty handling when
  the dataset task records it.

The first benchmark does **not** need:

- advanced multi-model condensed-matter comparison;
- live online fetching or scraping of publication tables;
- discovery, design-law, or material-selection wording;
- autonomous correction search before baseline and holdout are encoded.

## Candidate Diagnostic Surfaces

The campaign should make at least these diagnostic surfaces explicit when the
benchmark task lands:

- per-material residual maps for common quantum-dot families;
- size-regime residuals across small, mid, and large diameters or radii;
- absorption-versus-emission diagnostic panels to keep semantics separated;
- composition-family residuals when alloyed or mixed-composition entries
  exist;
- publication-source residuals to expose source-specific systematics.

These surfaces matter even if no compact correction term survives a holdout.
A clean failure map is still useful scientific memory.

## Holdout Outlook

The holdout protocol is formalised in `docs/quantum-size-effect-holdout-protocol.md`
(delivered by `TASK-0224`). Key split families:

- material holdout (drop one material family at training time) — required for
  the first baseline;
- size-range holdout (drop the largest or smallest size bin) — required for
  the first baseline;
- publication-source holdout (drop one source dataset) — optional until at
  least two independent sources are registered;
- composition-family holdout (drop alloyed or doped entries) — optional until
  sufficient composite entries exist.

Every benchmark task must include at least one explicit negative control.
Absorption, emission, and bandgap values must use separate residual axes;
they may not be merged into a single metric.

If a later curated post-baseline measurement batch becomes available, a
time-split or source-pinned external holdout may become a stronger
generalization check. That is a future extension and not a scaffold
requirement.

## Dataset Policy

The campaign treats dataset handling as a scientific surface rather than
plumbing.

Required discipline under `TASK-0223`:

- pin source, year, and citation;
- store a pinned copy or checksum policy for any redistributable source;
- preserve unit and field semantics explicitly;
- never silently mix absorption peak, emission peak, and bandgap values under
  one residual metric;
- never silently mix measured and theoretical or extrapolated values;
- preserve inclusion and exclusion decisions as reviewable fields rather than
  as silent data cleaning.

## Autonomy Policy

The campaign is **not** autonomy-ready.

Before any autonomous pilot under `TASK-0226`, APL must already have:

- the campaign scaffold (this task);
- the dataset and source-manifest layer;
- the holdout protocol;
- the baseline residual benchmark;
- the campaign profile and guardrails;
- clear negative-result handling.

The pilot is downstream of all of the above by design and must remain
sandbox-only until a maintainer explicitly approves a different posture.

## Success Condition for the First Wave

The first wave is successful if it yields:

- a reproducible baseline residual surface for at least one property kind;
- a holdout contract reviewers trust across material, size, and source axes;
- a campaign page that keeps scope honest with respect to synthesis,
  fabrication, and biomedical exclusions;
- at least one later sandbox pilot path that cannot overclaim by accident.

It does not need to yield a strong empirical correction term immediately.

## Microtask Queue

`tasks/microtasks/quantum-size-effects.yaml` exists as a small planning-only
microtask queue. Items must:

- stay planning, notes, scope, and limitation only;
- name an explicit excluded direction (synthesis, fabrication, biomedical,
  device-performance, or claim promotion) when relevant;
- not produce canonical results, claims, hypotheses, experiments, or
  datasets;
- defer dataset and benchmark work to the queued canonical tasks.

The queue may be expanded once `TASK-0223` lands, but only with maintainer
review.
