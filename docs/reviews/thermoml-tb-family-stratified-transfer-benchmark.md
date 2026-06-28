# ThermoML Tb Family-Stratified Transfer Benchmark

Task: `TASK-0851`
Sandbox run: `AGENT-RUN-0087`

## Scope

The frozen Joback and Reid normal-boiling-point estimator is tested against a
balanced, value-blind 40-row audit fixture extracted from the checksum-verified
NIST ThermoML Archive. The fixture spans eight chemical families with five
molecular-weight-quantile rows each. The raw archive and a substantial
normalized corpus are not committed.

The implementation-fidelity gate is evaluated before benchmark error. APL fits
no Joback coefficient or correction.

## Controls and verdict rule

Each held-out family is compared with global median, molecular-weight-only,
nearest-group-homolog, shuffled Joback group counts, and an oracle-like
within-family constant. Transfer support requires a 5 K aggregate advantage over
the best non-oracle control and the same margin in at least two thirds of family
holdouts.

Detailed aggregate and per-family metrics are generated in
`agent_runs/AGENT-RUN-0087/metrics.json` and summarized in `report.md`.

## Rights and routing

- Source: NIST TRC ThermoML Archive, DOI `10.18434/mds2-2422`.
- Local analysis: allowed; archive-byte redistribution: not allowed.
- Published repository surface: 40 factual audit rows with attribution, not a
  substantial extraction or normalized archive.
- Gate A: bounded sandbox evidence only.
- Gate B: fixture hash, replay command, code references, engine version, and git
  commit are recorded.
- Claim and knowledge impact: none.

