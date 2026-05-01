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
- Add `--fail-on-warnings` support for `validate-repo --strict`.

## Scientific Verification

- Extend symbolic validation helpers in `physics_lab/engines/symbolic.py` beyond pendulum formula families.
- Add explicit asymptotic checks for pendulum candidates.
- Explore whether a future pendulum candidate can outperform the current range-limited best model while also preserving the improved separatrix behavior from `RUN-0002`.
- Add benchmark workflows beyond pendulum:
  - orbital perturbation
  - diffusion scaling
  - driven or nonlinear oscillator

## Workflow and Reporting

- Add plots as optional artifacts.
- Add structured report sections for limitations and failure cases.
- If maintainers want stronger automation later, add a machine-readable companion format for claim and knowledge patch artifacts.

## Contributor Experience

- Add a compact architecture index for quick onboarding.
- Add a lightweight release-review checklist for public-alpha milestones.

## Longer-Term

- Literature ingestion adapters for arXiv, OpenAlex, and Crossref.
- Importers into graph or database backends.
- Open task assignment and external agent submission workflow.
- Public dashboard once the scientific core is mature enough.
