# Preflight

- PASS: masses frozen in `data/quantum_dots/effective_mass_inputs.yaml` before scoring.
- PASS: no holdout fit; both directions use `C_target=C_source*mu_source/mu_target`.
- PASS: direct-size rows only; calibration-derived datasets excluded.
- PASS: bulk-gap-only model and three controls compared under the unchanged 0.05 eV margin.
- Replay: `python scripts/run_quantum_effective_mass_transfer.py --write`; code `physics_lab/engines/quantum_effective_mass_transfer.py`; commit `09e3c0dca43da620cd69a93fabd39dac55600bc8`.
