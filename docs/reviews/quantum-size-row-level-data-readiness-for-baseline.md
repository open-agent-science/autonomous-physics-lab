# Quantum Size Row-Level Data Readiness for Baseline Review

**Task:** TASK-0283
**Status:** review (no baseline fitting performed)
**Inputs reviewed:**

- `data/quantum_dots/source_manifest.yaml`
- `data/quantum_dots/qd-0001-yu-2003-absorption.yaml`
- `data/quantum_dots/qd-0002-moreels-2009-pbs-absorption.yaml`
- `physics_lab/schemas/quantum_dot_size_effect.schema.json`
- `docs/quantum-size-effect-holdout-protocol.md`
- `docs/reviews/quantum-size-yu-2003-row-level-seed-review.md`
- `docs/reviews/quantum-size-moreels-2009-pbs-row-level-extension-review.md`

## Scope

This note evaluates whether the two committed Quantum Size Effects row-level
seeds (qd-0001, qd-0002) constitute a sufficient row-level data surface to
unblock the first baseline residual benchmark (TASK-0225). No baseline model
fitting, holdout reveal, autonomous hypothesis search, or claim promotion
was performed.

The decision recorded here governs only the readiness of TASK-0225 to leave
`BLOCKED` and the configuration of its pre-reveal package, not the result of
any benchmark.

## Inventory

| File | Source | Materials | Rows | Property | Diameter range (nm) | Energy range (eV) | Provenance class |
|------|--------|-----------|------|----------|---------------------|-------------------|------------------|
| qd-0001 | `yu-2003-cm-absorption` | CdTe, CdSe, CdS | 12 | `absorption_peak_eV` | 2.07–6.23 | 1.91–3.54 | Calibration-derived |
| qd-0002 | `moreels-2009-acs-nano-pbs-absorption` | PbS | 9 | `absorption_peak_eV` | 2.71–9.24 | 0.62–1.46 | Calibration-derived |

Per-material breakdown for qd-0001: CdS (n=4, 2.07–4.85 nm),
CdSe (n=4, 2.17–6.23 nm), CdTe (n=4, 2.34–4.34 nm).

## Gate Checks

### 1. Schema validation and source-manifest binding

- Both files validate against `quantum_dot_size_effect.schema.json` and are
  exercised by `test_committed_quantum_dot_datasets_validate_and_reference_manifest_sources`.
- Every `source_id` appears in `source_manifest.yaml` with an `accepted`
  inclusion decision.
- Every row carries a `source_table_ref` and a `notes` field that distinguish
  calibration-derived rows from any future direct table rows.
- No emission, bandgap, synthesis, biomedical, or device-performance content
  is recorded.

Result: **PASS**.

### 2. Property kind separation

- `property_kind_covered` is `absorption_peak_eV` for both files.
- No file mixes absorption with emission or bandgap on a shared residual axis.

Result: **PASS** (`absorption_peak_eV` is the only viable first benchmark
property axis with current data).

### 3. Provenance traceability of included rows

- Every included row references a specific calibration source and selected
  wavelength.
- The Yu 2003 seed uses the published CdTe/CdSe/CdS sizing polynomials.
- The Moreels 2009 seed uses Eq. 4 with the published constants.
- No uncertain or partially-traceable rows are included; both files mark all
  rows `inclusion_status: included`.

Result: **PASS**.

### 4. Measurement-row availability

- TASK-0225 requires "at least one reviewed row-level `data/quantum_dots/qd-*.yaml`
  dataset file with **measurement rows**".
- Both qd-0001 and qd-0002 are explicitly labeled in their reviews as
  calibration-derived from published sizing curves, not directly measured
  TEM+spectroscopy values from the source publications.
- No directly-measured row is currently committed for any material.

Result: **NOT PASS** under a literal reading of TASK-0225's `measurement
rows` requirement.

This is the binding constraint for the readiness decision.

### 5. Holdout-family viability (informational)

Even though gate 4 fails, the data structure for each holdout family is
already worth recording so that a future direct-measurement seed can drop
into the same scaffolding.

- **Material holdout** (required for first baseline per protocol §1):
  natural single-material PbS holdout (1 source, 1 material) or
  cadmium-chalcogenide leave-one-out from CdTe/CdSe/CdS (each n=4).
  No alloyed or doped rows exist yet, so composition-family holdout is
  unavailable.
- **Size-range holdout** (required for first baseline per protocol §2):
  the joint diameter distribution is roughly 2–9 nm; the 7.6 nm and 9.2 nm
  rows are PbS only. A simple size cut at d ≤ 3 nm or d ≥ 6 nm is possible,
  but small/large bins will be PbS-dominated. Bin-boundary documentation in
  the pre-reveal package is mandatory.
- **Source / publication holdout** (optional): two independent publication
  sources are now registered, but they do not share a material; a meaningful
  publication-holdout for a single material would require a second
  PbS source or a second Cd-chalcogenide source.
- **Composition-family holdout** (optional): zero qualifying rows.
- **Negative controls**: bulk-bandgap constant predictor is well-defined
  per material (PbS 0.41 eV; CdSe ~1.74 eV @ 300 K; CdTe ~1.49 eV @ 300 K;
  CdS ~2.42 eV @ 300 K) and is a valid first negative control. Wrong-material
  Brus parameters are also feasible across the four materials.

Result: structurally viable for material and size holdouts under the
holdout protocol, but only on a calibration-derived surface.

## Decision

**Keep TASK-0225 BLOCKED.**

Concrete blocker: every committed row in `data/quantum_dots/qd-*.yaml` is
calibration-derived from a published empirical sizing curve. Running a
baseline residual benchmark against these rows would compare a chosen
baseline (e.g. Brus effective-mass approximation) to other published
formulas rather than to direct measurements. The residuals would not
represent measurement-versus-model error and could easily be
misinterpreted as such in summary metrics or downstream visualization.

The conservative requirement before TASK-0225 leaves `BLOCKED` is one of
the following, decided by the maintainer:

- **Direct-measurement seed** — add at least one row-level dataset file
  containing rows whose `notes` and `measurement_type` document a direct
  table value, digitised figure point, or independently-reviewed TEM +
  spectroscopy measurement (not a calibration-curve evaluation). Even a
  small (≥6-row) direct-measurement seed would be sufficient to redo this
  gate.
- **Maintainer waiver** — explicit maintainer approval to interpret the
  first baseline as a **calibration-curve consistency benchmark**
  rather than a measurement-versus-model benchmark, with the framing
  recorded in the TASK-0225 pre-reveal package, the result note, and the
  campaign page. In that case the negative controls and material holdouts
  above are sufficient for a scoped first benchmark.

Both paths leave the existing seeds in place; the question is whether the
first baseline is permitted to score against calibration-derived rows.

## Recommended TASK-0225 Configuration (when unblocked)

If and when the gate above passes, the recommended first-baseline
configuration is:

- **Primary property kind:** `absorption_peak_eV` (the only kind currently
  covered, and the only kind that should be scored in the first benchmark).
- **Expected dataset files:** `data/quantum_dots/qd-0001-yu-2003-absorption.yaml`
  and `data/quantum_dots/qd-0002-moreels-2009-pbs-absorption.yaml`, plus any
  direct-measurement seed that the maintainer accepts before unblocking.
- **Required material holdout:** withhold PbS (single source, single
  material) and train on cadmium chalcogenides, or vice versa. The
  cadmium-chalcogenide-versus-PbS split is the natural and only viable
  first material holdout with current data.
- **Required size-range holdout:** small (d ≤ 3 nm) or large (d ≥ 6 nm),
  with explicit bin boundaries committed to the pre-reveal package.
- **Required negative control:** bulk-bandgap constant predictor per
  material, with the per-material bulk gaps recorded in the pre-reveal
  package.
- **Forbidden in the first benchmark:** mixing `absorption_peak_eV` with
  `emission_peak_eV` or `bandgap_eV`; averaging residuals across property
  kinds; using PbS-derived Brus parameters when evaluating PbS; using any
  material-specific parameter sourced from the held-out material.

## Campaign Page Update

`docs/campaigns/quantum-size-effects.md` is updated in the same change to
reflect that TASK-0281 and TASK-0282 are DONE and that TASK-0283 has run
and kept TASK-0225 BLOCKED with the explicit calibration-derived constraint.
No claim, baseline result, or holdout reveal is recorded.

## Limitations

- This review is not a benchmark and does not score any model against any
  data. No `claim`, `result`, or `knowledge` artifact is promoted.
- The recommendation does not foreclose the existing seeds; calibration-
  derived rows remain valid curated data, just insufficient for a direct
  measurement-versus-model first baseline.
- This review does not authorize live data fetches, synthesis content, or
  device-performance content.
- The recommended configuration above is a planning sketch for the
  TASK-0225 pre-reveal package, not an executed pre-reveal package.

## Verdict

**TASK-0225 stays BLOCKED.** Unblocking requires either a direct-measurement
row-level seed or a maintainer waiver permitting a scoped calibration-curve
consistency benchmark for the first baseline. The current row-level data
surface (qd-0001 + qd-0002) is schema-valid, source-pinned, provenance-
traceable, and structurally compatible with the holdout protocol — but the
absence of any directly-measured row means a baseline benchmark cannot yet
be interpreted as measurement-versus-model.
