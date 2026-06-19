# Nuclear Reveal Source Manifest Preflight

- Task: `TASK-0778`
- Date: `2026-06-19`
- Mode: metadata-only source-manifest preflight
- Registry surface: `prediction_registry/nuclear_masses/`
- Decision: `SOURCE_MANIFEST_BLOCKED`

## Scope

This preflight checks whether the current Nuclear prediction registry has a
source-manifest route that can advance to reveal scoring without weakening the
no-peek boundary. It reviews source classes, release timing, locator stability,
license or reuse notes, checksum feasibility, value-semantics requirements, and
the no-peek compatibility gate.

This task did not fetch or inspect target mass values, did not parse external
mass tables, did not score predictions, did not edit `PRED-*` entries, and did
not promote a result, claim, or knowledge artifact.

## Inputs Reviewed

- `docs/nuclear-prediction-reveal-protocol.md`
- `docs/nuclear-mass-holdout-protocol.md`
- `docs/nuclear-reveal-source-readiness-checklist.md`
- `docs/reviews/nuclear-prediction-reveal-readiness-matrix.md`
- `docs/reviews/nuclear-prediction-reveal-checklist-reference-repair.md`
- `docs/reviews/nuclear-post-ame2020-reveal-source-manifest-scout.md`
- `docs/reviews/nuclear-shell-axis-mini-wave-source-preflight.md`
- `docs/reviews/nuclear-shell-axis-reveal-source-manifest-review.md`
- `data/nuclear_masses/reveal_source_manifest_template.yaml`
- `data/nuclear_masses/shell_axis_reveal_source_manifest_template.yaml`
- `data/nuclear_masses/post_ame2020_sources.yaml`
- registry metadata for `prediction_registry/nuclear_masses/PRED-*.yaml`

Metadata-only web/source checks on `2026-06-19` used source landing pages and
search metadata only:

- IAEA/AMDC Atomic Mass Data Center page:
  `https://www-nds.iaea.org/amdc/`
- Argonne Atomic Mass Data Resources page:
  `https://www.anl.gov/phy/atomic-mass-data-resources`
- AME2020 Part I article DOI:
  `https://doi.org/10.1088/1674-1137/abddb0`
- AME2020 Part II article DOI:
  `https://doi.org/10.1088/1674-1137/abddaf`
- Qu et al. 2025 post-AME2020 new-mass survey DOI:
  `https://doi.org/10.1007/s41365-025-01821-1`
- AME/NUBASE status presentation metadata:
  `https://indico.bnl.gov/event/24322/contributions/95567/attachments/57582/98875/USNDP_AME2025.pdf`

No raw mass table, target-row query, or value-bearing source download was used.

## Registry Metadata Boundary

The current registry contains 60 actual prediction entries plus one template.
The readiness matrix records:

- actual prediction entries: `60`
- target rows: `261`
- ready for reveal review: `0`
- awaiting source preflight: `60`
- blocked before reveal scoring: `60`

The current preflight preserves that boundary. All actual entries remain
source-gated and require no-peek review plus maintainer approval before any
comparison.

The latest shell-axis entries `PRED-0063` through `PRED-0068` share:

- registered timestamp: `2026-05-20T00:00:00Z`
- source-state commit: `9e8d7d339a4f0f432e41689862a649eb029b8575`
- target batch: `shell-axis-balanced-001`
- quantity: `mass_excess_mev`

Any prospective source for those entries must therefore postdate the registry
freeze and must be pinned before row-level values are inspected.

## Source Classes Checked

| Source class | Metadata decision | Reason |
| --- | --- | --- |
| Official AME/NUBASE evaluation | Not admissible for current prospective reveal | The currently available reviewed surfaces are AME2020/NUBASE2020, published in 2021, so they predate the 2026 registry freeze. They remain baseline/source-format references only. |
| AMDC or IAEA live service endpoint | Not a manifest by itself | A live service can be a discovery aid, but without an immutable post-registration source, release date, checksum, archive policy, and measured/non-measured row semantics it does not satisfy the reveal checklist. |
| Post-AME2020 Qu et al. 2025 compilation | Not admissible for current prospective reveal | The source predates the 2026 registry freeze and is a secondary compilation. It can support retrospective time-split work already captured by the committed post-AME2020 manifest, not a prospective reveal for current registry entries. |
| Conference/status material about future AME/NUBASE work | Not a source manifest | Status or workshop material can indicate that future evaluations may exist, but it is not a checksumable measured source table with accepted reuse and row semantics. |
| Future post-freeze official evaluation, peer-reviewed primary table, collaboration release, or archive copy | Potentially admissible later | No concrete accepted source was identified in this task. A future task can reopen the gate once a post-freeze source can be pinned without target-row exposure. |

## Missing Source-Manifest Fields

A future reveal task must fill these fields before scoring:

- `manifest_id`
- `task_id`
- `source_class`
- `source_title`
- `issuing_body`
- `publication_or_release_date`
- `source_state_timestamp_utc`
- `accessed_at_utc`
- `source_locator`
- `license_or_reuse_notes`
- `archive_policy`
- `raw_artifact_checksum`
- `normalized_artifact_checksum` when normalized rows are produced
- `parser_or_normalizer` command, code reference, version, input paths, and output paths
- `quantity`
- source and normalized `units`
- `uncertainty_fields` and uncertainty semantics
- `value_semantics`
- `measurement_flag_field`
- deterministic `target_id_fields`
- deterministic `target_matching_rules`
- exclusion policy for ambiguous, non-measured, duplicate, and missing rows
- registry snapshot commit and included `PRED-*` ids
- per-entry no-peek audit outcome

If any of these fields remains unknown or ambiguous, the reveal task should
stop with `SOURCE_MANIFEST_INCOMPLETE`, `BLOCKED_SOURCE_NOT_PINNED`, or
`BLOCKED_VALUE_SEMANTICS` rather than inspect target values.

## No-Peek Compatibility Decision

No accepted source exists yet, so a real no-peek audit cannot be completed.
The current status is:

- source pinning: blocked
- source release timing: no accepted post-freeze source identified
- checksum feasibility: unknown until a concrete source exists
- measured/non-measured separation: unknown until a concrete source exists
- target matching: unknown until a concrete source exists
- maintainer approval: not available for reveal scoring

The next reveal-scoring task must not proceed until a concrete source manifest
is accepted and reviewed. If a source predates any included registry entry, the
entry must be labeled `SOURCE_PREDATES_REGISTRATION` or routed to a separate
retrospective diagnostic task with weaker wording.

## Preserved Stop Conditions

- Do not inspect source rows for target nuclides before source acceptance.
- Do not download or parse value-bearing mass tables during source discovery.
- Do not modify frozen `prediction_registry/nuclear_masses/PRED-*.yaml` values,
  targets, reveal conditions, or source-state metadata.
- Do not score partial reveals from a source that predates registration.
- Do not infer missing rows from live, informal, or unpinned sources.
- Do not promote a result, claim, or knowledge artifact from this preflight.

## Handoff

The next useful action is to wait for or identify a qualifying post-freeze
source and run a new source-manifest preparation task. Acceptable future source
classes are:

- a new official AME/NUBASE-style release with row-level measured/extrapolated
  flags and an immutable electronic distribution;
- a primary peer-reviewed mass-measurement table with a publication date after
  the relevant registry freeze and a source route that can be pinned before
  row-level inspection;
- a collaboration or facility release with explicit reuse terms,
  checksumable artifacts, and measured/non-measured row flags;
- an archive copy of one of the above, used only as a reproducibility mirror.

If no such source is available, reveal scoring remains blocked. If the
maintainer wants a weaker retrospective comparison, that should be a separate
task with a different evidence class and wording boundary.

## Output Routing

- Task verdict: `SOURCE_MANIFEST_BLOCKED`
- Canonical destination:
  `docs/reviews/nuclear-reveal-source-manifest-preflight.md`
- Review tier: `none`
- Gate A status: not applicable; no `RESULT-*` artifact was created.
- Gate B status: not applicable; no independent replay target was created.
- Claim impact: no claim created or modified.
- Knowledge impact: no knowledge artifact created or modified.
- Result impact: no `results/` artifact created or modified.
- Prediction impact: frozen prediction registry values, targets, source-state
  metadata, and reveal conditions are unchanged.
- Publication blocker: no accepted post-freeze measured-source manifest is
  pinned; future reveal scoring remains blocked.
