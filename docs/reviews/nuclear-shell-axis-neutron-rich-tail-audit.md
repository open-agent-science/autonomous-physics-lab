# Nuclear Shell-Axis Neutron-Rich Tail Audit

**Task:** `TASK-0324`  
**Agent run:** `agent_runs/AGENT-RUN-0024/`  
**Script:** `scripts/run_nuclear_shell_axis_neutron_rich_tail_audit.py`  
**Metrics:** `agent_runs/AGENT-RUN-0024/metrics.json`  
**Baseline:** `RESULT-0015::model_fitted_semi_empirical`  
**Evidence class:** sandbox-only retrospective neutron-rich tail audit

## Scope

This review isolates the neutron-rich high-error tail surfaced by the
`TASK-0315` validity-domain map. It reuses only committed repository data and
the existing `TASK-0310` shell-axis candidate definitions.

Inputs:

- `agent_runs/AGENT-RUN-0018/metrics.json`
- `agent_runs/AGENT-RUN-0019/metrics.json`
- `agent_runs/AGENT-RUN-0020/metrics.json`
- `docs/reviews/nuclear-shell-axis-validity-domain-after-0310.md`
- `docs/reviews/nuclear-shell-axis-coefficient-stability-audit.md`
- `data/nuclear_masses/post_ame2020_holdout.yaml`

No live external data were fetched. No new correction terms were created. No
prediction registry entries, canonical `RESULT-*` artifacts, claims, or
knowledge files were edited.

## Deterministic Subset Rules

The audit uses the following fixed rules:

- **Neutron-rich:** `(N - Z) / A >= 0.25`, matching the `TASK-0315`
  `neutron_rich_high` rule.
- **High-error:** baseline absolute error at or above the 75th percentile of
  the full-known committed surface, `6.110141840131 MeV`.
- **Tail subset:** rows satisfying both rules above.
- **Matched non-neutron-rich control:** for each neutron-rich high-error row,
  sorted by descending baseline absolute error, select one unused
  non-neutron-rich high-error row minimizing baseline-error distance, then
  `A` distance, source-surface mismatch, `Z` distance, and `row_id`.

The resulting subsets are:

| Subset | Rows |
| --- | ---: |
| Full-known committed surface | 306 |
| Neutron-rich rows | 31 |
| Neutron-rich high-error tail | 20 |
| Matched non-neutron-rich high-error control | 20 |

## Candidate Outcomes

Negative deltas mean lower error than the frozen baseline.

| Candidate | Neutron-rich all delta MAE MeV | Tail delta MAE MeV | Tail delta RMSE MeV | Tail improved rows | Drop largest 2 tail delta MAE MeV | Matched control delta MAE MeV |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `FULLKNOWN-SHELL-001` | -0.357017 | -0.537487 | -0.524949 | 20/20 | -0.519230 | -0.407744 |
| `FULLKNOWN-SHELL-002` | -0.229458 | -0.355659 | -0.394825 | 17/20 | -0.308976 | -0.433131 |
| `FULLKNOWN-SHELL-003` | -0.276888 | -0.429173 | -0.483854 | 19/20 | -0.369228 | -0.618650 |

The neutron-rich high-error tail improves for all three primary shell-axis
candidates. Removing the largest two baseline-error rows does not flip the
tail delta positive, so the tail improvement is not solely a single-row
artifact.

## Outlier Contribution Check

The largest baseline-error neutron-rich row is `Ga-84` with baseline absolute
error `37.636806 MeV`. Removing it, or removing it plus the next largest
baseline-error row, leaves all three candidate tail delta-MAE values negative.

The top row-level delta contributors are still concentrated in a small number
of high-error rows:

- `FULLKNOWN-SHELL-001`: largest single-row improvements are `Ni-75` and
  `Ca-54`, each contributing `-0.058137 MeV` to tail MAE.
- `FULLKNOWN-SHELL-002`: largest single-row improvement is `In-131`,
  contributing `-0.077431 MeV` to tail MAE.
- `FULLKNOWN-SHELL-003`: largest single-row improvement is `In-131`,
  contributing `-0.080245 MeV` to tail MAE.

This supports preserving row-level diagnostics rather than promoting only the
aggregate tail result.

## Matched-Control Interpretation

The matched non-neutron-rich high-error control also improves for all three
primary candidates. For `FULLKNOWN-SHELL-002` and `FULLKNOWN-SHELL-003`, the
matched control improves more than the neutron-rich tail.

That means this audit should not be read as a neutron-rich-specific support
claim. The safer interpretation is that the shell-axis candidates reduce some
high-error committed rows, including the neutron-rich tail, while the evidence
does not isolate neutron richness as the unique driver.

## Preserved Limitations

The light-nuclei and coefficient-stability limitations remain binding:

- `TASK-0320` found light `A<50` rows regress for all three primary
  shell-axis candidates.
- `TASK-0316` found coefficient signs can flip under deterministic 8-of-11
  resampling of the 11-row training surface.
- This audit inherits those coefficients and does not tune new ones.
- The high-error cutoff is deterministic, but it is post hoc over the
  committed full-known surface.
- The matched control is deterministic and row-count matched, not a
  statistical bootstrap.

## Verdict

`OUTLIER_DIAGNOSTIC`

The neutron-rich high-error tail is favorable for all three primary
shell-axis candidates and survives removal of the largest one or two baseline
errors. However, the matched non-neutron-rich high-error control also improves,
and sometimes improves more. Treat this as a high-error tail diagnostic, not a
broad neutron-rich support zone or a claim-promotion surface.

Maintainer review is required before any shell-axis expansion, reveal scoring,
canonical result update, claim, or knowledge promotion.
