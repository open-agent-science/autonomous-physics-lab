# COBE/FIRAS CMB Monopole Spectrum v1

This package pins the NASA LAMBDA `firas_monopole_spec_v1.txt` source used by
the Textbook Formula Audit Wien-displacement lane.

The raw file contains 43 rows with native wavenumber, absolute monopole
intensity, residual, one-sigma uncertainty, and a Galactic-pole model column.
NASA LAMBDA defines the absolute intensity as a 2.725 K blackbody plus the
published Table 4 residual.

TASK-0801 performs source curation only. It does not fit a spectrum, convert
`B_nu` to `B_lambda`, locate a peak, or test Wien displacement.

Deterministic normalization:

```bash
python scripts/normalize_firas_monopole_source.py \
  --source data/textbook_formula_audit/wien_firas/source_artifacts/cobe-firas-monopole/firas_monopole_spec_v1.txt \
  --output data/textbook_formula_audit/wien_firas/firas_monopole_rows.yaml
```
