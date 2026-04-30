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

- Add optional strict mode for `validate-repo`.
- Add detection of orphaned artifacts not referenced by any experiment or claim.
- Add validation that claim status is consistent with available result evidence.
- Add artifact-hash drift checks so committed result metadata can be revalidated after input changes.

## Scientific Verification

- Extend symbolic validation helpers in `physics_lab/engines/symbolic.py` beyond pendulum formula families.
- Add explicit asymptotic checks for pendulum candidates.
- Add theory-aware candidate families that can match separatrix behavior as amplitude approaches `pi`.
- Add benchmark workflows beyond pendulum:
  - orbital perturbation
  - diffusion scaling
  - damped oscillator correction

## Workflow and Reporting

- Add plots as optional artifacts.
- Add structured report sections for limitations and failure cases.
- Make claim and knowledge update artifacts more structured and easier to apply automatically.

## Contributor Experience

- Add a contributor guide for humans and LLM agents.
- Add a repo-level command that prints current project status.
- Add a compact architecture index for quick onboarding.

## Longer-Term

- Literature ingestion adapters for arXiv, OpenAlex, and Crossref.
- Importers into graph or database backends.
- Open task assignment and external agent submission workflow.
- Public dashboard once the scientific core is mature enough.
