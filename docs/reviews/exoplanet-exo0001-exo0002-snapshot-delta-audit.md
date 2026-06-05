# Exoplanet EXO-0001 vs EXO-0002 snapshot delta audit

- Task: `TASK-0581`
- Campaign: `exoplanet_mass_radius`
- Protocol class: committed-snapshot delta audit
- Inputs:
  - `data/exoplanets/exo-0001-pscomppars-snapshot.yaml`
  - `data/exoplanets/exo-0002-pscomppars-snapshot.yaml`
- Code reference: `scripts/run_exoplanet_snapshot_delta_audit.py`

## Scope

This audit compares the two committed normalized PSCompPars snapshots before
any mass-radius benchmark replay. It reports data-surface changes only:
row counts, included/excluded counts, mass-provenance classes, planet-name
identifier overlap, overlapping-row field drift, and target overlap for the
previously used exoplanet audit slices.

It does not fetch live archive data, compute residual metrics, refit a
baseline, infer composition, rank planets, create prediction entries, or
promote claims.

## Method

The audit runs:

```text
python scripts/run_exoplanet_snapshot_delta_audit.py
```

The script loads both committed YAML snapshots with the existing exoplanet
loader, applies the same inclusion filters used by the campaign, joins rows by
exact `planet_name`, and compares only metadata, row-class, and slice-membership
state. True-mass and minimum-mass axes remain separate throughout.

## Snapshot counts

| Metric | EXO-0001 | EXO-0002 | Delta |
| --- | ---: | ---: | ---: |
| Total rows | 6291 | 6298 | +7 |
| Pre-filter included rows | 6157 | 6164 | +7 |
| Post-filter included rows | 4301 | 4308 | +7 |
| True-mass rows | 2103 | 2110 | +7 |
| Minimum-mass rows | 986 | 985 | -1 |
| Not-measured mass rows | 3202 | 3203 | +1 |
| Transit-radius rows | 4638 | 4640 | +2 |
| Not-measured radius rows | 1590 | 1595 | +5 |

The exclusion histogram is unchanged between snapshots:

| Exclusion reason | Count |
| --- | ---: |
| `mass_and_radius_absent` | 16 |
| `mass_provenance_requires_source_specific_review` | 10 |
| `mass_relative_uncertainty_above_threshold` | 578 |
| `radius_inferred_from_non_transit_method` | 34 |
| `radius_relative_uncertainty_above_threshold` | 1278 |
| `solution_type_not_confirmed` | 74 |

## Identifier and overlap delta

| Metric | Count |
| --- | ---: |
| EXO-0001 planet names | 6291 |
| EXO-0002 planet names | 6298 |
| Overlap planet names | 6291 |
| New planet names in EXO-0002 | 7 |
| Removed planet names from EXO-0001 | 0 |
| Post-filter included overlap planet names | 4301 |
| New post-filter included names in EXO-0002 | 7 |
| Removed post-filter included names from EXO-0001 | 0 |

Among overlapping planet names, row-class counts are unchanged. The audit found
two overlapping rows whose `mass_class` changed and seven overlapping rows
whose `source_table_ref` changed. Detection method, host name,
inclusion status, radius class, mass-value presence, and radius-value presence
are unchanged across the overlap.

## Previous-audit slice overlap

| Slice | EXO-0001 | EXO-0002 | Overlap | New | Removed |
| --- | ---: | ---: | ---: | ---: | ---: |
| Compact true-mass, `R < 1.5 R_earth` | 92 | 92 | 92 | 0 | 0 |
| Sub-Neptune true-mass, `1.5 <= R < 4 R_earth` | 340 | 340 | 340 | 0 | 0 |
| Jovian-radius true-mass, `8 <= R < 16 R_earth` | 567 | 568 | 567 | 1 | 0 |
| Hot-Jupiter true-mass, `P < 10 d`, `8 <= R < 16 R_earth` | 445 | 445 | 445 | 0 | 0 |
| Minimum-mass transit-radius axis | 2 | 2 | 2 | 0 | 0 |

The main residual-audit slices are therefore stable as target surfaces. The
second snapshot adds rows overall, but it does not materially change compact,
sub-Neptune, or hot-Jupiter true-mass slice membership under the declared
predicates.

## Verdict

`VALID_IN_RANGE`

The second snapshot is eligible for later replay-preflight discussion as a
committed data surface: it adds seven planet identifiers and seven post-filter
included rows while preserving the prior compact, sub-Neptune, and hot-Jupiter
true-mass slice membership. Because two overlapping rows changed mass class,
any later benchmark replay must keep row-class drift visible and must not merge
true-mass and minimum-mass axes into one metric.

This is not a residual result and does not say that any mass-radius model
improved or failed on EXO-0002.

## Limitations

- The audit joins by exact `planet_name`; renamed or merged catalog identities
  would require a separate identity-resolution task.
- The audit reports field-presence and class changes, not numeric value deltas.
- No source-row provenance review is performed for the two overlapping
  mass-class changes.
- No baseline replay, residual metric, or null-baseline competition is run.

## Output routing

- Task verdict: `VALID_IN_RANGE`.
- Canonical destination:
  `docs/reviews/exoplanet-exo0001-exo0002-snapshot-delta-audit.md`.
- Review tier: `none`.
- Gate A status: not attempted; no `RESULT-*` or `PRED-*` artifact.
- Gate B status: not attempted; no independent replay target.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result artifact impact: no `results/` artifacts modified.
- Publication blocker: later benchmark replay still needs a separate task with
  frozen metrics, null-baseline rules, and row-class drift handling.
