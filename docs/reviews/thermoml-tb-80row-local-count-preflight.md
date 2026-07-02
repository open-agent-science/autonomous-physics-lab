# ThermoML Tb 80-row Local Count Preflight

**Task:** `TASK-0906`
**Campaign:** `thermophysical-property-residuals`
**Verdict:** `FAMILY_UNDERPOPULATED`
**Review date:** 2026-07-02

## Scope

This local-only preflight tested whether the frozen TASK-0895 ThermoML `Tb`
expansion contract can supply ten admissible, non-conflict, Joback-covered
identities in each of the eight existing families before any public row extract
or benchmark metric is authorized.

The run used only the pinned ThermoML v1.2.6 archive route from
`data/thermophysical/source_manifest.yaml`. It did not commit archive bytes,
extracted XML/JSON, normalized rows, selected compound identities, `Tb` values,
or benchmark metrics.

## Local Replay

Command:

```bash
python scripts/preflight_thermoml_tb_80row_identity_counts.py \
  --archive C:\tmp\APL-private-sources\ThermoML.v2020-09-30.tgz
```

Archive verification:

| Field | Value |
| --- | --- |
| Product | NIST TRC ThermoML Archive |
| DOI | `10.18434/mds2-2422` |
| Product version | `1.2.6`, archive dated `2020-09-30` |
| Archive filename | `ThermoML.v2020-09-30.tgz` |
| Archive size | `189433115` bytes |
| SHA-256 | `231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2` |
| RDKit | `2025.09.3` |
| thermo | `0.6.0` |
| Public output class | aggregate counts only |

The helper enforces `no_values_emitted: true` and `no_rows_emitted: true` and
rejects public payloads containing row/value keys such as `rows`,
`experimental_tb_k`, `standard_inchi`, `source_member`, or selected identities.

## Count Result

Target: exactly `10` admissible non-conflict identities per existing family.

| Family | Before conflict/uncertainty exclusion | Conflict-flagged | Missing uncertainty | Admissible non-conflict | Target | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| acids | 7 | 1 | 0 | 6 | 10 | shortfall 4 |
| esters/lactones | 51 | 3 | 0 | 48 | 10 | pass |
| ketones | 9 | 1 | 0 | 8 | 10 | shortfall 2 |
| alcohols/phenols | 31 | 2 | 0 | 29 | 10 | pass |
| ethers | 13 | 1 | 0 | 12 | 10 | pass |
| halocarbons | 15 | 0 | 0 | 15 | 10 | pass |
| aromatic hydrocarbons | 20 | 0 | 0 | 20 | 10 | pass |
| alkanes/cycloalkanes | 13 | 2 | 0 | 11 | 10 | pass |

Aggregate screening counts:

| Counter | Count |
| --- | ---: |
| archive_json_files | 11923 |
| normal_boiling_files | 167 |
| normal_boiling_data_blocks | 590 |
| identified_single_component_blocks | 590 |
| raw_normal_boiling_observations | 501 |
| joback_covered_observations | 501 |
| joback_covered_unique_compounds | 184 |
| charged_or_multifragment_blocks | 2 |
| unsupported_element_blocks | 5 |
| joback_out_of_coverage_blocks | 81 |
| unclassified_family_blocks | 1 |

Representative-level exclusions after Joback coverage and deduplication:

| Exclusion category | Count |
| --- | ---: |
| conflict_flagged_identities | 10 |
| outside_selected_family_identities | 21 |
| selected_family_element_mismatch_identities | 4 |

## Decision

The proposed exact 80-row expansion is not feasible under the frozen TASK-0895
rules because two families fail the ten-identity count gate after conflict
exclusion:

- `acids`: `6 / 10` admissible non-conflict identities;
- `ketones`: `8 / 10` admissible non-conflict identities.

Task verdict: `FAMILY_UNDERPOPULATED`.

This result does not authorize relaxing the family taxonomy, conflict rule,
identity filters, Joback coverage gate, or source-rights posture. Any future
larger ThermoML row-curation task would need a revised maintainer-approved
contract, such as a lower per-family ceiling, a different family set, a separate
conflict-sensitivity task, or an explicitly local-only non-public analysis lane.

## Rights And Publication

The source manifest still permits local analysis but not raw-byte
redistribution. Derived row publication remains conditional and requires
maintainer review. Because the count gate already fails, no public 80-row
fixture should be prepared from this task even if a later rights decision were
favorable.

No archive bytes, extracted archive members, selected identities, `Tb` values,
normalized corpus files, benchmark metrics, `RESULT-*`, `PRED-*`, `CLAIM-*`, or
`KNOW-*` artifacts are produced here.

## Output Routing

- Canonical destination: this source-readiness review note.
- Review tier: none; source-curation preflight only.
- Gate A status: not applicable; no result or prediction artifact.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Result impact: none; `RESULT-0026` is unchanged.
- Dataset impact: no new values, rows, archive bytes, selected identities, or
  corpus.
- Publication blocker: `FAMILY_UNDERPOPULATED`; public rows also remain behind
  the existing ThermoML derived-row rights decision.

## Limitations

- This is a local-only run against the pinned `ThermoML.v2020-09-30.tgz`
  archive; the archive itself is not committed.
- The preflight counts identities and exclusions only. It does not score Joback,
  rerun `RESULT-0026`, inspect model residuals, or make a property-estimation
  claim.
- The result is specific to normal boiling temperature under the frozen
  ThermoML/TASK-0895 rules. It does not cover `Tc`, other properties, chemical
  design, process design, safety, synthesis, or universal Joback validity.