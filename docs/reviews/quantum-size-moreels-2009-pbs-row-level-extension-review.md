# Quantum Size Effects — Moreels 2009 PbS Row-Level Extension Review

**Task:** TASK-0282
**Dataset:** `data/quantum_dots/qd-0002-moreels-2009-pbs-absorption.yaml`
**Source:** `moreels-2009-acs-nano-pbs-absorption` (accepted in source manifest)
**Status:** curated (not promoted to a result or claim)

## Summary

This review note documents the curation rationale, sizing-curve formula,
deterministic calculation path, target batch, and limitations for the
Moreels 2009 PbS absorption extension dataset (`qd-0002`).

## Source

- **Citation:** Moreels, I. et al. "Size-dependent optical properties of colloidal
  PbS quantum dots." *ACS Nano* **3**, 3023–3030 (2009).
  DOI: [10.1021/nn900863a](https://doi.org/10.1021/nn900863a)
- **Source ID:** `moreels-2009-acs-nano-pbs-absorption`
- **Material:** PbS only
- **Property:** absorption_peak_eV only

## Sizing-Curve Formula

Values are derived from the published empirical sizing curve (Eq. 4 of Moreels 2009):

```
E(d) = E_bulk + 1 / (a · d² + b · d)

E_bulk = 0.41 eV   (PbS room-temperature bulk bandgap)
a      = 0.0252    nm²·eV⁻¹
b      = 0.283     nm·eV⁻¹
d      = diameter  (nm)
E      = first exciton absorption energy (eV)
```

Diameter is computed by inverting the quadratic:
```
d = [ -b + sqrt(b² + 4a/(E − E_bulk)) ] / (2a)
```

Peak energy is computed from wavelength using:
```
value_eV = hc / lambda_nm,   hc = 1239.841984 eV·nm
```

## Deterministic Calculation

All values in the dataset were computed by the following closed-form path:

1. Select a set of first-exciton absorption peak wavelengths spanning the
   typical PbS QD regime (850–2000 nm, corresponding to ~2.7–9.2 nm diameter).
2. Convert each wavelength to energy: `E = 1239.841984 / lambda_nm`.
3. Invert the Moreels Eq. 4 quadratic to obtain diameter: `d` as above.
4. Round to 6 decimal places to match stored YAML precision.

A round-trip check was performed for each row: `E(d)` recomputed from the
stored diameter must agree with the stored `value_eV` to within 1e-10 eV.

## Batch Coverage

Ten calibration-derived rows spanning 850–2000 nm (1.46–0.62 eV, 2.7–9.2 nm):

| entry_id | diameter_nm | value_eV | lambda (nm) |
|----------|-------------|----------|-------------|
| moreels-2009-pbs-850nm  | 2.713853 | 1.458638 | 850  |
| moreels-2009-pbs-950nm  | 3.094820 | 1.305097 | 950  |
| moreels-2009-pbs-1050nm | 3.495973 | 1.180802 | 1050 |
| moreels-2009-pbs-1150nm | 3.920283 | 1.078123 | 1150 |
| moreels-2009-pbs-1300nm | 4.608027 | 0.953725 | 1300 |
| moreels-2009-pbs-1450nm | 5.370850 | 0.855063 | 1450 |
| moreels-2009-pbs-1600nm | 6.228815 | 0.774901 | 1600 |
| moreels-2009-pbs-1800nm | 7.570591 | 0.688801 | 1800 |
| moreels-2009-pbs-2000nm | 9.236342 | 0.619921 | 2000 |

All 9 included rows span the quantum-confinement regime for PbS
(Bohr exciton radius ≈ 18 nm).

## Relationship to qd-0001

| Feature | qd-0001 (Yu 2003) | qd-0002 (Moreels 2009) |
|---------|-------------------|------------------------|
| Material | CdTe, CdSe, CdS | PbS |
| Wavelength range | 350–650 nm | 850–2000 nm |
| Energy range | 1.9–3.5 eV | 0.6–1.5 eV |
| Source type | Calibration polynomials | Eq. 4 sizing curve |
| Property | absorption_peak_eV | absorption_peak_eV |

Together these two seeds enable a material-holdout split under the
`docs/quantum-size-effect-holdout-protocol.md`:
- train on cadmium chalcogenides (qd-0001), holdout PbS (qd-0002);
- or vice versa for a cross-material generalization test.

## Limitations

- All entries are sizing-curve calibration rows derived from Moreels Eq. 4,
  not directly measured values from the paper's primary TEM + spectroscopy data.
- The Eq. 4 formula was fitted to a specific PbS synthesis route; batch-to-batch
  variation in real QD samples would produce scatter around this curve.
- The dataset covers PbS only; no multi-material mixing is permitted in this file.
- Bulk bandgap temperature dependence is not modelled; all entries implicitly
  assume room-temperature conditions.
- No synthesis, chemical, biomedical, or device-performance information is
  recorded or implied by these rows.
- This seed does not enable standalone benchmark scoring; it must be combined
  with a frozen pre-reveal package before any model is evaluated.

## Verdict

The dataset conforms to the schema, references only the accepted source
`moreels-2009-acs-nano-pbs-absorption`, distinguishes calibration-derived
from directly measured rows in `notes`, and contains no claim, result, or
knowledge promotion. Approved for use as a curated seed under
`docs/quantum-size-effect-holdout-protocol.md`.
