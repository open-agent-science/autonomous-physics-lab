# AGENT-RUN-0084 - ThermoML bounded Tb transfer benchmark

**Task:** `TASK-0841`
**Benchmark:** `thermoml-bounded-tb-transfer`
**Verdict:** `IMPLEMENTATION_INCONCLUSIVE`
**Fetch executed:** `no`

## Summary

Bounded audit of the FROZEN Joback Tb estimator under the maintainer-approved ThermoML local-fetch posture. The implementation-fidelity gate is evaluated first; the family-stratified transfer evaluation runs only when the approved local fetch + Tb corpus parse are executed. APL fits nothing: it audits whether the frozen published estimator transfers under specified family holdouts, not whether Joback's method is right or wrong. No claim, prediction, knowledge entry, or discovery is promoted.

## Implementation-fidelity gate (FIRST)

- Result: **PASS** - 25 compounds, 0 mismatches, max abs error 0.0 K (tolerance 0.05 K).
- Match criterion: computed Tb within tolerance of each compound's published PREDICTED Tb, using that compound's own source intercept (198.2 canonical Joback&Reid or 198.12 molecularknowledge).

| Compound | base | computed Tb (K) | published Tb (K) | abs err (K) | match |
| --- | ---: | ---: | ---: | ---: | :---: |
| Acetone | 198.2 | 322.11 | 322.11 | 0.0 | Y |
| Benzene | 198.12 | 358.5 | 358.5 | 0.0 | Y |
| Toluene | 198.12 | 386.36 | 386.36 | 0.0 | Y |
| o-Xylene | 198.12 | 414.22 | 414.22 | 0.0 | Y |
| Styrene | 198.12 | 405.92 | 405.92 | 0.0 | Y |
| Isopropylbenzene | 198.12 | 431.68 | 431.68 | 0.0 | Y |
| Bromobenzene | 198.12 | 429.64 | 429.64 | 0.0 | Y |
| 1,2-Dichlorobenzene | 198.12 | 443.32 | 443.32 | 0.0 | Y |
| 2-Butyne | 198.12 | 300.04 | 300.04 | 0.0 | Y |
| 1-Octanol | 198.12 | 474.74 | 474.74 | 0.0 | Y |
| Ethyl acetate | 198.12 | 349.26 | 349.26 | 0.0 | Y |
| Tetrahydrofuran | 198.12 | 337.94 | 337.94 | 0.0 | Y |
| Cyclohexanone | 198.12 | 428.84 | 428.84 | 0.0 | Y |
| Cyclohexanol | 198.12 | 448.53 | 448.53 | 0.0 | Y |
| Ethanethiol | 198.12 | 308.14 | 308.14 | 0.0 | Y |
| Tetrahydrothiophene | 198.12 | 358.82 | 358.82 | 0.0 | Y |
| Acrylonitrile | 198.12 | 366.92 | 366.92 | 0.0 | Y |
| Benzaldehyde | 198.12 | 435.02 | 435.02 | 0.0 | Y |
| n-Heptanoic acid | 198.12 | 505.19 | 505.19 | 0.0 | Y |
| n-Decanoic acid | 198.12 | 573.83 | 573.83 | 0.0 | Y |
| (+/-)-1-Phenylethanol | 198.12 | 500.98 | 500.98 | 0.0 | Y |
| Methyl salicylate | 198.12 | 548.08 | 548.08 | 0.0 | Y |
| Succinic acid | 198.12 | 582.06 | 582.06 | 0.0 | Y |
| gamma-Butyrolactone | 198.12 | 405.76 | 405.76 | 0.0 | Y |
| Ethyl thioacetate | 198.12 | 413.69 | 413.69 | 0.0 | Y |

## Transfer evaluation

- Status: **not executed** - local fetch not executed (archive ~181 MB; faithful Tb corpus extraction with InChI identity resolution, dedup, family classification, and deterministic group decomposition is the deferred bounded row-curation task). Per the local-fetch posture this is a complete, valid IMPLEMENTATION_INCONCLUSIVE outcome.
- Declared split: `leave_one_family_out`.
- Declared family taxonomy (frozen before any error reading): acids, esters/lactones, aldehydes, ketones, alcohols/phenols, ethers, nitriles, amines, nitro, thiols/sulfides, halocarbons, aromatic hydrocarbons, alkenes/alkynes, alkanes/cycloalkanes.
- Declared controls:
  - `global_median`: Predict every held-out compound's Tb as the global median Tb of the training (non-held-out-family) compounds. Null baseline.
  - `molecular_weight_only`: Predict Tb from a molecular-weight-only regression fit on the training families (size-only baseline; tests whether Joback beats bulk size).
  - `nearest_homolog`: Predict Tb as the Tb of the nearest training homolog (closest molecular weight within the nearest compatible series).
  - `shuffled_group_counts`: Joback applied to group counts randomly permuted across compounds (seed-controlled); breaks the structure -> Tb link while preserving the group-count marginal. Falsification control.
  - `within_family_constant`: Predict every held-out compound's Tb as the held-out family's own mean Tb (an oracle-ish within-family constant; upper bound on what a family-label-only predictor achieves).
- Per-family outcome: inconclusive (transfer not executed).

## Pinned source

- Product: NIST TRC ThermoML / Data Archive (DOI `10.18434/mds2-2422`, version `1.2.6`).
- PDR landing: https://data.nist.gov/od/id/mds2-2422
- Archive: `ThermoML.v2020-09-30.tgz` (189433115 bytes).
- Official published SHA-256: `231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2`
  - Provenance: NIST-published checksum, cross-verified 2026-06-26 from the PDR component metadata and the authoritative .tgz.sha256 sidecar. NOT an APL-computed-from-downloaded-bytes hash: archive not fetched.
  - APL-computed-from-fetched-bytes SHA-256: `PENDING_FIRST_FETCH`.
- Source manifest: `data/thermophysical/source_manifest.yaml`.

## Rights determination (3-question framework)

- local_analysis_allowed: `yes`
- source_bytes_redistribution: `no`
- derived_rows_publication: `conditional`
- substantial_extraction_review_required: `yes`
- covered_by_repo_license: `false`
- Cite the ThermoML Archive per NIST TRC request; facts extractable with attribution, file bytes not re-hosted.

## Replay (Gate-B-replayable)

- Command: `python3 scripts/run_thermoml_tb_transfer.py --output-dir agent_runs/AGENT-RUN-0084`
- Code reference: `scripts/run_thermoml_tb_transfer.py`
- Engine reference: `physics_lab/engines/joback_tb.py`
- Engine version: `0.1.0`
- Git commit: `fb2c2920701ee1b8ddd9fba69e9c27d45eb40b8a`
- Input file hashes:
  - `physics_lab/engines/joback_tb.py`: `sha256:e40c60fd4b6382ab21de845896eec9809206dfa7dcde134a9a0641b55ae17212`
  - `data/thermophysical/source_manifest.yaml`: `sha256:756dd0a89f1ea310ddb541f15d9e14a84266c1c1ab62ff7a2fb21db731e2e6d0`

## Limitations

- Tb-only; Tc excluded for Joback leakage.
- Frozen published Joback estimator audited; APL fits nothing and no discovery is claimed.
- Fetch not executed in this bounded slice: no ThermoML Tb corpus was parsed and no transfer metric was computed (none fabricated).
- Family-holdout transfer scope is declared (leave-one-family-out vs five controls) but conditional on the deferred license-cleared corpus-parse/row-curation task.
- Fidelity fixture is solvent/hydrocarbon/oxygenate-heavy and does not stress Joback's rare heteroatom-ring/multifunctional groups at scale.
- Two intercept conventions exist (198.2 canonical vs 198.12 in one reference table); a future scoring run must pin one (recommend 198.2).

## Output-routing summary

- Task verdict: `IMPLEMENTATION_INCONCLUSIVE`.
- Fetch executed: `no`.
- Canonical destination: `sandbox_agent_run_plus_review_note`.
- Review tier: `none`.
- Gate A status: `not_attempted_bounded_inconclusive`.
- Gate B status: `replayable_metadata_recorded_transfer_not_executed`.
- Claim impact: `none`.
- Knowledge impact: `none`.

