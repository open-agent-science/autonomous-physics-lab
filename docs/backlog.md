# Backlog

## Purpose

This file stores important but not-immediate work.

It should contain:

- medium-term engineering tasks;
- scientific extensions;
- quality improvements;
- contributor-experience work.

Items can move from here into [next-steps.md](./next-steps.md)
when they become active priorities.

## Registry and Validation

- Add detection of orphaned artifacts not referenced by any experiment or claim.
- Add validation that claim status is consistent with available result evidence.
- Add a lighter-weight report that explains detected artifact drift before regeneration.

## Scientific Verification

- Extend symbolic validation helpers in `physics_lab/engines/symbolic.py` beyond pendulum formula families.
- Add explicit asymptotic checks for pendulum candidates.
- Explore whether a future pendulum candidate can outperform the current range-limited best model while also preserving the improved separatrix behavior from `RUN-0002`.
- Implement `EXP-0003` only after the pendulum gauntlet milestone has been completed and reviewed.
- Add benchmark workflows beyond pendulum:
  - orbital perturbation
  - diffusion scaling
  - driven or nonlinear oscillator

## Future Research Portfolio

Use [future-research-portfolio.md](./future-research-portfolio.md) before
promoting backlog ideas into active tasks.

- Keep Nuclear Mass Surface as the current `NOW` research track, with
  audit-first follow-up and no broad mass-formula claims.
- Treat quantum dots or quantum size effects, thought-experiment consistency,
  and electromagnetic invariance as `NEXT` candidates only when they are scoped
  into conservative planning, dataset, or validator tasks.
- Keep Hubble tension, muon g-2 follow-up, broad physical-constants
  derivation, and broad mass-relation searches in `WATCHLIST` until stronger
  guardrails exist.
- Do not create public article tasks from portfolio curation.

## Workflow and Reporting

- Add plots as optional artifacts.
- Add structured report sections for limitations and failure cases.
- If maintainers want stronger automation later, add a machine-readable companion format for claim and knowledge patch artifacts.

## Contributor Experience

- Add a compact architecture index for quick onboarding.
- Add a lightweight release-review checklist for public-alpha milestones.
- Add a contributor map if the shared task board grows large enough that `architecture-index.md` is no longer sufficient.
- Improve the live task board only when it clearly reduces handoff friction rather than adding management overhead.

## Longer-Term

- Literature ingestion adapters for arXiv, OpenAlex, and Crossref.
- Importers into graph or database backends.
- Open task assignment and external agent submission workflow.
- Public dashboard once the scientific core is mature enough.
