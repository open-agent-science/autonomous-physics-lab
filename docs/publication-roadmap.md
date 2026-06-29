# Publication Roadmap

APL should become citable only through the same discipline it expects from
scientific results: source-pinned artifacts, explicit limitations, replayable
validation, and maintainer-reviewed release gates.

This roadmap is a planning surface, not a claim that the repository, datasets,
or citable outputs are already DOI-backed or publication-ready.

## Organization Context

Open Agent Science is the umbrella organization for shared, public scientific
memory produced by human-owned agents. Autonomous Physics Lab is the first
physics proof-of-work under that umbrella.

Repository transfer to `open-agent-science/autonomous-physics-lab` is complete,
and the public repository opening was recorded on 2026-06-28. Current
contributor entrypoints, software citation metadata, and release-facing docs
should use that live repository path. Historical PR links, review logs, CI
evidence, source artifacts, result artifacts, and prediction-registry
provenance should not be rewritten merely to replace old owner paths.

Public visibility does not by itself make datasets, release tags, DOI records,
or claims publication-ready; those remain separately gated.

## Short-Term Release Layer

For public-alpha stabilization and any future release tag, APL should keep:

- a `CITATION.cff` file for software citation;
- a `.zenodo.json` file or equivalent release metadata;
- release notes that distinguish software, dataset, result, and claim
  artifacts;
- public-safe wording that describes APL as a verification-first agent research
  system, not a source of automatic discoveries;
- at least one documented pathway from a source-pinned dataset to a
  replayable, citable result candidate.

## Dataset Publication Layer

Dataset publication should be handled separately from raw source ingestion.
A reusable dataset candidate should have:

- a stable dataset id and version;
- source attribution, source license, and redistribution status;
- row schema and excluded-row semantics;
- checksum and snapshot provenance;
- holdout or replay discipline where benchmark claims are possible;
- citation/reuse wording;
- limitations and known blockers;
- a maintainer-approved decision before any DOI or external publication.

Current near-term candidates:

| Dataset surface | Current status | Publication posture |
| --- | --- | --- |
| Materials `MD-0001` | Source-pinned, replayed, and useful as an emerging reusable-dataset candidate | Candidate for citation/reuse metadata and public-safe evidence packaging, but benchmark promotion remains blocked |
| Exoplanet PSCompPars snapshots | Pinned-snapshot benchmark surface with control-sensitive residual evidence | Candidate for replication capsule and no-live-fetch snapshot protocol, not a planet-law claim |
| Atomic Yb/Sr rows | Beloy rows exist; second-source rows remain blocked | Not publication-ready until second-source, covariance, direct-vs-derived, and holdout semantics clear |
| Nuclear prediction registry | Frozen predictions await future source-grade reveal | Prediction artifacts are citable as pre-registered forecasts only if reveal-source discipline is maintained |

## Citable Output Path

APL's lowest-risk citable outputs are methodology and dataset release packages
before scoped physics-result packages:

1. **Software / methodology release package:** APL as a verification-first,
   multi-agent scientific-memory workflow.
2. **Dataset or benchmark release package:** a source-pinned, reusable dataset
   with replayable baseline evidence and limitations.
3. **Scoped result publication package:** only after a result survives
   promotion gates, independent replay, and maintainer/scientific review.

Physics discovery remains upside, not the base plan.

## Success Metrics

Publication readiness should be measured by durable output quality:

- promoted result artifacts with explicit review tiers;
- independent replay or external reviewer PRs;
- source-pinned datasets with stable citation metadata;
- negative-result and blocker preservation;
- release artifacts with no overclaim wording;
- external contributors who can reproduce the workflow.

Raw task count is not a publication metric.
