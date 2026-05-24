# Quantum Size Source Manifest Seed Review

Task: `TASK-0275`

## Scope

This review records a small DOI-pinned source-manifest seed for the Quantum
Size Effects campaign. It prepares source provenance for a later baseline
residual benchmark without adding numerical dataset rows, running model
comparisons, or promoting any scientific claim.

## Inputs

- `data/quantum_dots/README.md`
- `data/quantum_dots/source_manifest.yaml`
- `physics_lab/schemas/quantum_dot_size_effect.schema.json`
- `docs/quantum-size-effect-holdout-protocol.md`
- `docs/campaigns/quantum-size-effects.md`

## Method

The manifest seed separates candidate source surfaces by property kind:

- `absorption_peak_eV`: CdTe/CdSe/CdS optical absorption calibration candidate
  from Yu et al. 2003 and PbS optical absorption candidate from Moreels et al.
  2009.
- `bandgap_eV`: band-edge source candidate from Jasieniak, Califano, and
  Watkins 2011, with an explicit caveat that future rows must preserve the
  derivation from valence and conduction band-edge measurements.
- `emission_peak_eV`: CdSe/ZnS photoluminescence reference from Dabbousi et al.
  1997, recorded as excluded for the first pure size-effect baseline because
  core-shell passivation confounds a single-material residual axis.
- model provenance: Brus 1984 is recorded as excluded measurement data and
  reserved for baseline-model provenance in a future benchmark task.

No publication tables, figure-derived values, spectra, or measurement rows were
copied into repository memory. Each source is represented only by citation
metadata, DOI, property semantics, material family, inclusion decision,
redistribution note, and pinning policy.

## Metrics

- Source entries added: 5
- Accepted source entries: 3
- Excluded source entries: 2
- Property kinds represented: 3
- Dataset measurement rows added: 0
- Baseline comparisons run: 0
- Claims promoted: 0

## Limitations

- This is a source-manifest seed, not a curated dataset. `TASK-0225` should not
  treat these entries as measurements until a later dataset file records
  row-level values under the schema.
- DOI pinning preserves source identity but is not a redistribution license.
  Future dataset curation must avoid copying non-redistributable tables or
  figures unless a license and checksum policy explicitly allow it.
- Band-edge measurements are not automatically equivalent to optical absorption
  or photoluminescence peaks. Any future bandgap dataset must keep that
  derivation visible.
- Core-shell emission data are preserved as an explicit excluded source for the
  first baseline, not as a rejected publication.

## Verdict

`PARTIALLY_VALID`

The seed gives the Quantum Size Effects campaign a reviewable provenance
surface for future curation while preserving the campaign's sandbox-only,
no-claim posture. It does not by itself unblock a full benchmark reveal or
authorize any baseline residual claim.
