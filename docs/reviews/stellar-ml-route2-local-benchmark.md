# Stellar M-L Route 2 Local-Extractor Benchmark

**Task:** `TASK-0740`
**Agent run:** `AGENT-RUN-0070`
**Campaign:** Textbook Formula Audit (Stellar mass-luminosity)
**Mode:** sandbox-only local-extractor benchmark
**Verdict:** `SANDBOX_PASS`

## Scope

This task runs the first empirical Stellar M-L benchmark on DEBCat Route 2
without redistributing the full catalogue. It uses the committed source
metadata, checksum, extractor, and frozen holdout rule to regenerate the full
component rows locally, then scores a predeclared single-alpha baseline:

```text
L / L_sun = (M / M_sun)^3.5
```

The primary interpreted range is `0.5 <= M/M_sun < 2.0`, matching the
source-manifest primary audit window. Rows outside that range are reported as
diagnostics only. No alpha fit, residual-tuned filter, raw `debs.dat` commit,
full normalized row commit, `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*`
artifact is created.

## Local Reproduction

The local-only source path was:

1. Fetch `debs.dat` through `scripts/fetch_source_artifact.py`.
2. Verify SHA-256
   `326902535b4da2fd94f227806ff339247d6df224ef8faea8857703e553b464da`.
3. Regenerate full rows and the full holdout manifest through
   `scripts/extract_debcat_stellar_ml_rows.py`.
4. Run `scripts/run_stellar_ml_route2_local_benchmark.py` against the regenerated
   local rows.

The raw DEBCat table, full row file, and full manifest stayed in an ignored
local work directory and are not committed.

## Inputs Reviewed

| Input | Role |
| --- | --- |
| `TASK-0739` | Authorizes the Route 2 local-extractor benchmark route. |
| `TASK-0740` | Benchmark task contract. |
| `docs/reviews/stellar-ml-benchmark-readiness-after-route2.md` | Gate decision and guardrails. |
| `docs/reviews/stellar-ml-debcat-row-package.md` | Route 2 extraction ledger and row-package limitations. |
| `data/textbook_formula_audit/stellar_ml/source_manifest.yaml` | Frozen alpha and primary mass-range convention. |
| `scripts/extract_debcat_stellar_ml_rows.py` | Deterministic row and holdout-manifest extractor. |
| `scripts/run_stellar_ml_route2_local_benchmark.py` | Benchmark scoring runner added by this task. |

## Dataset Boundary

The extractor reproduced the same Route 2 row-package counts:

| Quantity | Value |
| --- | ---: |
| Unique systems | 373 |
| Systems admitted | 372 |
| Component rows admitted | 742 |
| Component rows excluded | 6 |
| Direct-luminosity rows | 597 |
| Derived-luminosity rows | 145 |
| System lanes | train 191, validation 81, holdout 100, excluded 1 |

## Primary-Range Result

The benchmark compares the frozen alpha `3.5` formula against a deterministic
null baseline: per-mass-band train-lane median `log_luminosity_solar`.

| Lane | Rows | Formula MAE (dex) | Median residual (dex) | Within 0.2 dex | Beats null |
| --- | ---: | ---: | ---: | ---: | --- |
| train | 254 | 0.313852 | 0.15585 | 0.5 | n/a |
| validation | 103 | 0.316253 | 0.14125 | 0.466019 | true |
| holdout | 132 | 0.347101 | 0.141623 | 0.515152 | true |

On the holdout lane, the formula MAE is `0.347101` dex and the train-median
null MAE is `0.44492` dex. The formula therefore beats the predeclared null by
`0.097819` dex on this sandbox primary range.

## Sensitivity

The committed metrics also report:

- all admitted rows, including out-of-primary-range diagnostics;
- per-lane summaries;
- per-mass-band summaries;
- direct-luminosity vs derived-luminosity subsets;
- luminosity-uncertainty class subsets;
- best-effort evolutionary-stage flags.

The strongest caution is stage sensitivity. In the primary mass range,
`main_sequence_compatible` rows have much smaller residuals than `evolved` rows;
unknown-stage rows remain a large subset. This is useful benchmark evidence, but
it is not enough to make a universal formula statement.

## Decision

`SANDBOX_PASS`: the Route 2 local-extractor benchmark ran end-to-end, preserved
the storage boundary, and the frozen alpha `3.5` baseline beat the train-median
null on validation and holdout in the declared primary mass range.

This is sandbox evidence only. It does not validate the stellar
mass-luminosity relation universally, does not establish a stellar-evolution
claim, and does not promote a canonical result.

## Limitations

- Full DEBCat rows remain local-only because no explicit open-redistribution
  licence is recorded.
- The benchmark uses catalogue-level luminosity provenance; `debs.dat` does not
  expose per-row primary-literature luminosity pointers.
- The primary run uses the `TASK-0740` single-alpha route. A later task should
  decide whether to run the older piecewise textbook-bin baseline.
- Unknown and evolved spectral-stage flags are retained rather than excluded
  after scoring; interpretation requires maintainer/domain review.
- No Gate A `RESULT-*` packaging is attempted in this task.

## Output-Routing Summary

- **Task verdict:** `SANDBOX_PASS`.
- **Canonical destination:** `agent_runs/AGENT-RUN-0070/metrics.json`,
  `agent_runs/AGENT-RUN-0070/report.md`, and this review note.
- **Review tier:** `none`.
- **Gate A status:** not attempted; no `RESULT-*` artifact is created.
- **Gate B status:** not applicable.
- **Claim impact:** no claim change.
- **Knowledge impact:** no knowledge change.
- **Publication blocker:** sandbox-only first empirical benchmark; full DEBCat
  rows remain local-only under Route 2 and interpretation needs maintainer review.
