# Particle Mass Datasets

This directory stores explicit input datasets for the particle-mass relation
track.

The purpose of these files is to make future Koide-style reproduction,
holdout, and falsification work source-aware and reviewable before any formula
testing begins.

## Scope

These datasets are input data only.

They do not, by themselves:

- support a formula claim;
- imply a benchmark verdict;
- justify a discovery statement;
- authorize mixing incompatible mass definitions.

## Source Policy

Primary source policy:

- prefer Particle Data Group (PDG) best values or listings with explicit
  versioning;
- record the exact listing or table URL used for each entry;
- record the access date for each source;
- keep source notes when PDG values are themselves derived from CODATA or a
  specific averaging procedure.

Maintainer-approved alternatives may be added later, but they must still be
explicitly versioned and cited in the same per-entry structure.

## Mass-Definition Policy

Every entry must record:

- `mass_type`
- `scheme`
- `scale`

Rules:

- use `mass_type: pole` for on-shell charged-lepton masses unless a source
  explicitly states otherwise;
- use `scheme: null` and `scale: null` only when the source does not require a
  renormalization scheme or scale for interpretation;
- do not silently mix `pole` masses with `running` masses in one benchmark;
- if a source uses a running mass, both `scheme` and `scale` must be filled in
  explicitly.

## Initial Dataset

The first scaffolded dataset is:

- `charged_leptons.yaml`

It records electron, muon, and tau masses in MeV, with explicit uncertainty and
source metadata.
