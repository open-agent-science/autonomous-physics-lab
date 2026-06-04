# Textbook Stellar M-L Pinned-Source Package

**Task:** `TASK-0564`
**Campaign:** Textbook Formula Audit
**Status:** source-acquisition package prepared; no live fetch
**Verdict:** `SOURCE_PACKAGE_READY`

## Scope

This task turns the Stellar Mass-Luminosity planning note from `TASK-0555`
into a pinned-source acquisition package. It does not fetch Gaia rows,
cross-match stars, ingest values, fit exponents, inspect residuals, run
metrics, or promote a scientific claim.

## Package Added

`docs/runbooks/textbook-stellar-ml-source-acquisition-runbook.md` defines:

- candidate source surfaces for Gaia DR3 context, literature benchmark-star
  anchors, and a future normalized APL ingestion surface;
- selected field groups for identity, mass, luminosity, uncertainty,
  photometry, stellar context, row roles, and exclusions;
- acquisition lanes and stop conditions;
- the first planning-level baseline convention and audit slice.

`data/textbook_formula_audit/stellar_ml/source_manifest.yaml` records the
metadata-only manifest shape:

- `live_fetch_performed: false`;
- no stellar values or rows recorded;
- candidate source blockers (`T4_snapshot_approval` for Gaia DR3 and
  `T1_access` for literature anchors);
- row-class separation for direct observations, derived luminosities,
  model-derived masses, holdout rows, and excluded rows;
- no-peek and checksum requirements for later acquisition.

## Baseline And Slice Boundary

The first empirical audit remains frozen at the planning level:

```text
L / L_sun = (M / M_sun)^3.5
```

with a primary main-sequence slice of `0.5 <= M / M_sun <= 2.0`. This is a
pre-metric convention only. The package does not validate, falsify, tune, or
fit the exponent.

## Boundaries Preserved

- No live external source was fetched.
- No source rows, Gaia values, literature tables, or cross-match outputs were
  committed.
- Direct observations, derived luminosities, model-derived masses, and
  excluded rows remain distinct row classes.
- No mass-luminosity residual metric, prediction entry, result artifact, claim,
  knowledge artifact, or discovery wording was produced.

## Output Routing Summary

- Task verdict: `SOURCE_PACKAGE_READY`
- Canonical destination:
  `docs/runbooks/textbook-stellar-ml-source-acquisition-runbook.md`,
  `data/textbook_formula_audit/stellar_ml/source_manifest.yaml`, and this
  review note.
- Review tier: `none`; source package requires maintainer review before any
  acquisition run.
- Gate A status: not attempted; no benchmark result was produced.
- Gate B status: not applicable.
- Claim impact: no claim change.
- Knowledge impact: no knowledge promotion.
- Publication blocker: future acquisition still needs exact source selection,
  maintainer approval, retrieval timestamp, row count, source version, raw and
  normalized checksums, license/attribution text, and no-peek attestation.
