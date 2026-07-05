# Preflight

- PASS: the TASK-0914 frozen contract (row ids, equal-volume factor 0.608291447, bulk gaps, seed 842, 0.05 eV margin) was verified against the engine constants and committed datasets before any metric was computed; any drift raises ContractViolationError.
- PASS: only direct-size rows enter the judge (six InP TEM qd-0003, ten ZnSe SAXS qd-0004); Yu CdSe / Moreels PbS excluded.
- PASS: residual axis is the confinement term E1s - E_bulk with bulk gaps as explicit per-material inputs, not fitted to the holdout.
- PASS: C and n are frozen from the calibration material and applied to the holdout with no refit; no correction search; no post-hoc threshold change; no absolute-energy fallback.
- PASS: per_material_mean and shuffled_size controls run; the frozen 0.05 eV survival margin was predeclared by TASK-0914 and not relaxed.

## Gate-B replayability

- Command: `python scripts/run_quantum_znse_contract_transfer.py --write`
- Code reference: `physics_lab/engines/quantum_cross_material_transfer.py`
- Runner reference: `scripts/run_quantum_znse_contract_transfer.py`
- Engine version: `0.1.0`
- Git commit: `ede31a914aecd7dd0ba98b22f2349a3ca8444b04`
- Input file SHA-256:
  - `data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml`: `9501499584735094aba1a3243d4329969e0d9fe09e9bbc156c677c8408189077`
  - `data/quantum_dots/qd-0004-toufanian-2021-znse-absorption.yaml`: `78332c1cb95f20c18dafd0a2eefd4ae3cd654e8732fb1ff6ec8e546f004cf4e8`
- Deterministic: re-running the writer twice yields identical `metrics.json`.
