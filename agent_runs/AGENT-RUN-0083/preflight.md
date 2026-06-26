# Preflight

- PASS: only direct-size rows enter the judge (six InP TEM qd-0003, ten ZnSe SAXS qd-0004); Yu CdSe / Moreels PbS excluded.
- PASS: residual axis is the confinement term E1s - E_bulk with bulk gaps as explicit per-material inputs, not fitted to the holdout.
- PASS: C and n are frozen from the calibration material and applied to the holdout with no refit; no absolute-energy fallback.
- PASS: per_material_mean and shuffled_size controls run; the 0.05 eV survival margin was predeclared before the reveal and not relaxed.

## Gate-B replayability

- Command: `python scripts/run_quantum_cross_material_transfer.py --write`
- Code reference: `physics_lab/engines/quantum_cross_material_transfer.py`
- Engine version: `0.1.0`
- Git commit: `fb2c2920701ee1b8ddd9fba69e9c27d45eb40b8a`
- Input file SHA-256:
  - `data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml`: `9501499584735094aba1a3243d4329969e0d9fe09e9bbc156c677c8408189077`
  - `data/quantum_dots/qd-0004-toufanian-2021-znse-absorption.yaml`: `78332c1cb95f20c18dafd0a2eefd4ae3cd654e8732fb1ff6ec8e546f004cf4e8`
- Deterministic: re-running the writer twice yields identical `metrics.json`.
