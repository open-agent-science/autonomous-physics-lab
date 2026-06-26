# ThermoML Bounded Tb Transfer Benchmark (Frozen Joback Estimator)

Task: `TASK-0841`
Campaign: Thermophysical Property Transfer Audit (boiling-point slice)
Mode: bounded transfer audit of a frozen published estimator under the
maintainer-approved local-fetch posture
Property in scope: normal boiling point (Tb) **only**
Sandbox run: `AGENT-RUN-0084`
Review date: 2026-06-26
Verdict: **IMPLEMENTATION_INCONCLUSIVE** (fidelity gate clean; local fetch + Tb
corpus parse not executed)

## Scope and Non-Goals

This task audits the **frozen** Joback & Reid (1987) Tb group-contribution
estimator against experimental ThermoML boiling points under family-stratified
holdouts and controls. **APL fits nothing here**: the estimator is published and
frozen, and the audit measures whether it *transfers* under specified family
holdouts -- not whether Joback's method is "right" or "wrong". No discovery
wording is used.

The implementation-fidelity gate is run first. The local fetch + family-stratified
transfer evaluation runs only when the approved local fetch and a license-cleared
Tb corpus parse are executed. In this bounded slice the fetch was **not** executed
(see [Local-fetch posture](#local-fetch-posture-fetch-executed-no)), so no transfer
metric is computed and **none is fabricated**. Per the task's local-fetch posture,
delivering the frozen implementation + the zero-mismatch fidelity fixture + the
pinned source manifest + the family-stratified selection/control protocol + replay
instructions, with verdict `IMPLEMENTATION_INCONCLUSIVE`, is a complete, valid
bounded outcome.

This task does **not**: vendor the raw ThermoML archive; commit a normalized Tb
corpus; relicense ThermoML values under the repository license; include Tc (Joback
Tc depends on Tb, a leakage path); or promote any `RESULT` / `PRED` / `CLAIM` /
`KNOW` / discovery.

This benchmark builds on the source-readiness scout
[thermoml-joback-source-readiness-scout.md](thermoml-joback-source-readiness-scout.md)
(`TASK-0833`, verdict `SOURCE_LIMITED`), which pinned the source route and froze
the identity / group-assignment / family taxonomy. Conventions follow
[../published-source-dataset-standard.md](../published-source-dataset-standard.md)
and [../fresh-data-intake-protocol.md](../fresh-data-intake-protocol.md).

## 1. Implementation-fidelity gate (FIRST) -- PASS, 0 mismatches / 25

The frozen estimator is `Tb = base + sum_i n_i * dTb_i` (K), structure-only,
implemented in [../../physics_lab/engines/joback_tb.py](../../physics_lab/engines/joback_tb.py).
Before any transfer error is read, the implementation reproduces the
25-compound Joback Tb fidelity fixture (group decompositions and published
*predicted* Tb reproduced from the `TASK-0833` scout note) with **zero
mismatches** (max abs error 0.0000 K, tolerance 0.05 K). The acetone anchor
reproduces 322.11 K exactly with the canonical 198.2 K intercept.

The fixture compares computed vs each compound's published **predicted** Tb (the
audit target is "did our implementation reproduce the published method"), and
uses each compound's own source intercept to avoid a false 100% mismatch across
the documented 198.2 (Joback & Reid) vs 198.12 (molecularknowledge.com)
intercept gap. Two construction traps the scout caught are retained as worked
regression evidence: the intercept variant, and the ethyl-thioacetate
decomposition (a missing `-CH2-` once manufactured a ~23 K outlier; the corrected
grouping matches). Both are asserted in
[../../tests/test_joback_tb.py](../../tests/test_joback_tb.py).

Because the fidelity gate is clean, the run is *allowed* to proceed to transfer.
Had any compound mismatched, the run would STOP at `IMPLEMENTATION_INCONCLUSIVE`
with no transfer metric, so an off-by-one group assignment cannot masquerade as a
method failure.

## 2. Tb-only scope and the Tc exclusion

Only Tb is in scope. Tc is excluded because Joback's Tc estimator is an explicit
function of Tb (`Tc = Tb * [0.584 + 0.965*sum(dTc) - sum(dTc)**2]**-1`); auditing
Tc with an experimental Tb substituted is an information-leakage path. Tb has no
such upstream dependency in Joback (structure-only), so it is the clean first
axis. The frozen estimator module deliberately does **not** implement Tc.

## 3. Pinned source and rights determination

The official source is pinned exactly (cross-verified 2026-06-26):

| Field | Value |
| --- | --- |
| Product | NIST TRC ThermoML / Data Archive |
| DOI | `10.18434/mds2-2422` |
| Product version | `1.2.6` (PDR record, modified 2021-03-05) |
| PDR landing | `https://data.nist.gov/od/id/mds2-2422` |
| Archive | `ThermoML.v2020-09-30.tgz` (189433115 bytes) |
| Official published SHA-256 | `231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2` |
| APL-computed-from-fetched-bytes SHA-256 | `PENDING_FIRST_FETCH` (archive not downloaded) |

The SHA-256 above is the **NIST-published** checksum, cross-verified from the PDR
component metadata AND the authoritative `.tgz.sha256` sidecar (both agree). It is
the source-of-truth published checksum, **not** an APL-computed hash of downloaded
bytes; the archive was not fetched, so the APL-computed value remains
`PENDING_FIRST_FETCH`. This is honest source-pinning, not a fabricated checksum.

Rights determination (3-question framework). The NIST open-data license wrapper
plus a TRC citation request apply, but the ThermoML files are present "with
permission of the journal publishers" and the license carries a foreign /
non-NIST copyright carve-out. Numerical facts (a boiling point, its uncertainty,
the compound identity) are not copyrightable and are extractable with attribution;
the file bytes are an aggregation under publisher permission to NIST and are not
re-hosted.

| Question | Determination |
| --- | --- |
| local_analysis_allowed | yes |
| source_bytes_redistribution | no |
| derived_rows_publication | conditional (bounded row-curation task, with attribution) |
| substantial_extraction_review_required | yes |
| covered_by_repo_license | false |

Cite the ThermoML Archive per NIST TRC request; NIST does not critically evaluate
the deposited values. The full source-pinning is recorded metadata-only in
[../../data/thermophysical/source_manifest.yaml](../../data/thermophysical/source_manifest.yaml)
(no corpus, no archive bytes).

## 4. Local-fetch posture (fetch executed: no)

The archive HEAD and the PDR metadata were reachable and the official checksum was
cross-verified, but the **~181 MB archive was not downloaded and no Tb corpus was
parsed** in this bounded slice. A faithful Tb corpus extraction -- resolving each
ThermoML substance to a canonical InChI identity, excluding salts / ionic liquids
/ mixtures / out-of-coverage molecules, deduplicating cross-article measurements,
classifying chemical families, and producing a deterministic, spot-checked Joback
group decomposition per molecule -- is the deferred bounded **row-curation** task
that the `TASK-0833` scout explicitly sequenced before any scoring. Performing a
rushed parse here would risk fabricating benchmark numbers, which is forbidden.

Therefore the fetch is recorded as **not executed** and the verdict is
`IMPLEMENTATION_INCONCLUSIVE`. The metrics payload records `fetch_executed: no`
explicitly.

## 5. Declared family-stratified transfer protocol (conditional, not executed)

When the license-cleared corpus exists, the frozen Joback Tb estimator is to be
evaluated by **leave-one-family-out** transfer (hold out whole chemical families)
against the controls below, with compound-level aggregation, uncertainty-aware
error, and the covered-Joback-groups-only subset reported separately from the
out-of-coverage tail. The family taxonomy (highest-priority functional group wins;
families partition the set) is frozen as: acids, esters/lactones, aldehydes,
ketones, alcohols/phenols, ethers, nitriles, amines, nitro, thiols/sulfides,
halocarbons, aromatic hydrocarbons, alkenes/alkynes, alkanes/cycloalkanes.

| Control | Role |
| --- | --- |
| `global_median` | null baseline: held-out Tb = global median of training compounds |
| `molecular_weight_only` | size-only regression baseline (does Joback beat bulk size?) |
| `nearest_homolog` | Tb of the nearest training homolog |
| `shuffled_group_counts` | Joback on permuted group counts (seed-controlled falsification control) |
| `within_family_constant` | held-out family's own mean Tb (family-label-only upper bound) |

The bounded verdict vocabulary for the executed run is
`TRANSFER_SUPPORTED_IN_SCOPE` / `FAMILY_DEPENDENT` / `SIZE_DEPENDENT_FAILURE` /
`GROUP_COVERAGE_FAILURE` / `IMPLEMENTATION_INCONCLUSIVE`. The report must say
whether the frozen estimator transfers under the specified family holdouts -- never
"Joback is wrong".

## 6. Gate-B replayability

The sandbox run is replayable:

- Command: `python3 scripts/run_thermoml_tb_transfer.py --output-dir agent_runs/AGENT-RUN-0084`
- Code reference: [../../scripts/run_thermoml_tb_transfer.py](../../scripts/run_thermoml_tb_transfer.py)
- Engine reference: [../../physics_lab/engines/joback_tb.py](../../physics_lab/engines/joback_tb.py)
- Engine version: `0.1.0`
- Input file hashes (engine + source manifest) and the git commit are recorded in
  [../../agent_runs/AGENT-RUN-0084/metrics.json](../../agent_runs/AGENT-RUN-0084/metrics.json).

## 7. Verdict

| Gate | Outcome |
| --- | --- |
| Implementation-fidelity gate | **PASS** -- 25 compounds, 0 mismatches, max abs error 0.0000 K. |
| Source route + checksum pinned | Yes -- DOI `10.18434/mds2-2422`, version `1.2.6`, official published SHA-256 cross-verified; APL-computed hash `PENDING_FIRST_FETCH`. |
| Rights determination | local_analysis yes; source_bytes redistribution no; derived rows conditional; substantial extraction review required; not covered by repo license. |
| Tb-only + Tc exclusion | Yes -- Tc excluded for leakage. |
| Local fetch executed | **No** -- archive not downloaded, no Tb corpus parsed, no transfer metric (none fabricated). |
| Family-stratified transfer | Declared (leave-one-family-out vs five controls); conditional on the deferred corpus-parse/row-curation task. |
| Bounded verdict | `IMPLEMENTATION_INCONCLUSIVE`. |

## Output-routing summary

- Task verdict: `IMPLEMENTATION_INCONCLUSIVE`.
- Fetch executed: **no** (HEAD/metadata reachable and checksum cross-verified, but
  the ~181 MB archive was not downloaded and no Tb corpus was parsed).
- Transfer outcome per family: **inconclusive** (transfer not executed); the
  leave-one-family-out split and five controls are declared and frozen for the
  deferred corpus-parse/row-curation task.
- Fidelity-fixture result: 25 compounds, **0 mismatches**, max abs error 0.0000 K.
- Rights determination: local_analysis_allowed yes; source_bytes_redistribution
  no; derived_rows_publication conditional; substantial_extraction_review_required
  yes; covered_by_repo_license false; cite the ThermoML Archive per NIST request.
- Canonical destination: sandbox `AGENT-RUN-0084` plus this review note and the
  metadata-only source manifest. No raw archive or normalized corpus committed.
- Review tier: `none`. Gate A: not attempted (bounded inconclusive). Gate B:
  replay metadata recorded; transfer not executed.
- Claim impact: **none**. Knowledge impact: none (a future corpus-parse /
  row-curation task at most, which is separate and maintainer-gated).
- Limitations: Tb-only; frozen Joback estimator; fetch not executed so no transfer
  metric; family-holdout transfer scope declared but conditional on the deferred
  license-cleared corpus parse; fidelity fixture is solvent/hydrocarbon/oxygenate-heavy
  and does not stress rare heteroatom-ring/multifunctional Joback groups at scale;
  two intercept conventions exist (pin 198.2 before any scoring).

## Sources (consulted)

- NIST ThermoML Archive: https://www.nist.gov/mml/acmd/trc/thermoml/thermoml-archive
- NIST PDR (DOI 10.18434/mds2-2422): https://data.nist.gov/od/id/mds2-2422
- ThermoML archive `.tgz` + `.sha256` sidecar: https://data.nist.gov/od/ds/mds2-2422/
- NIST open-data license: https://www.nist.gov/open/license
- Joback method (group table, intercept 198.2, acetone 322.11 K): https://en.wikipedia.org/wiki/Joback_method
- `thermo` library Joback docs: https://thermo.readthedocs.io/thermo.group_contribution.joback.html
- molecularknowledge.com "Boiling Point: Joback's Method" (25-compound predicted-Tb reference table): http://www.molecularknowledge.com/Techniques/TbJoback/TbJoback.html
