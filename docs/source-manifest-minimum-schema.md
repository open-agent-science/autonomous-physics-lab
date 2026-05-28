# Source Manifest Minimum Schema

`physics_lab/schemas/source_manifest_minimum.schema.json` defines the minimum
cross-campaign provenance contract for source artifacts before row curation,
baseline work, benchmark metrics, prediction entries, or claim promotion.

The schema is intentionally a floor, not a replacement for campaign-specific
manifests. Nuclear, Quantum, Atomic, and Exoplanet manifests may add stricter
local fields for units, row identifiers, covariance semantics, holdout
boundaries, source-specific table labels, or campaign-specific row classes.

## Required Surface

Each source records:

- DOI, arXiv, archive URL, source URL, and citation locator fields.
- Artifact type, path or locator, checksum, checksum scope, and whether the
  artifact is value-bearing.
- Retrieval date, retriever, and live-fetch policy after pinning.
- Redistribution status plus license and citation notes.
- Row class, inclusion status, blocker reason, and target row schema kind.
- Extraction method, uncertainty semantics, and review status.
- Review notes plus the next allowed workflow step.

## Extension Pattern

Campaign-specific manifests should extend the minimum by adding local fields
instead of weakening the shared fields. For example:

- Exoplanet snapshots can add query contracts, method maps, mass-provenance
  maps, row counts, and filter summaries.
- Quantum source artifacts can add material, property kind, size axis, table or
  figure reference, and digitization protocol references.
- Atomic clock manifests can add transition labels, ratio partner labels,
  covariance or correlation notes, and reveal-boundary fields.
- Nuclear manifests can add baseline-boundary fields, measured/extrapolated
  semantics, reveal-source roles, and isotope-chain row contracts.

The shared schema does not make rows admissible by itself. It only makes source
provenance reviewable and machine-checkable before later campaign tasks consume
the source.
