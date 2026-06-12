# Atomic Pizzocaro Observable Harmonization Contract

**Task:** `TASK-0706`  
**Campaign:** `atomic-clock-residuals`  
**Decision:** `SENSITIVITY_ONLY_RESIDUAL_CONTRACT_DEFINED_NO_BENCHMARK_ROW`  
**Review date:** 2026-06-12

## Scope

This review defines the narrow observable-harmonization contract that may be
used by a future diagnostic-only Beloy/Pizzocaro sensitivity task. It consumes
only committed repository artifacts and does not compute metrics, aggregate
windows, fit drift, write `acr` rows, create results, or promote claims.

The contract exists to preserve useful Pizzocaro VLBI window information while
keeping the benchmark boundary from `TASK-0686` intact: Pizzocaro windows are
fractional frequency-ratio deviations, whereas the Beloy Yb/Sr reference row is
an absolute frequency ratio.

## Inputs Reviewed

| Input | Role |
| --- | --- |
| `docs/reviews/atomic-pizzocaro-row-admissibility-after-psd-covariance.md` | Prior gate that preserved the aggregation and observable-harmonization blocker |
| `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/vlbi_per_window_diagnostic_ledger.yaml` | Ten diagnostic-only VLBI windows and source-reported fractional-deviation values |
| `data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/vlbi_source_derived_psd_covariance_approximation.yaml` | Source-derived approximate covariance and diagonal-only sensitivity labels |

## Decision

Pizzocaro fractional-deviation windows may be mapped to a Beloy-comparable
**residual axis** only for a sensitivity-only diagnostic. This mapping does not
create an absolute frequency-ratio row, does not make the ten windows
independent benchmark rows, and does not unblock `TASK-0456`.

The permitted diagnostic axis is a dimensionless relative residual:

```text
delta_pizzocaro_i = source-reported fractional Yb/Sr deviation for window i
delta_beloy_ref = (R_beloy - R_beloy_ref) / R_beloy_ref = 0
delta_residual_i = delta_pizzocaro_i - delta_beloy_ref
```

For the Beloy central reference itself, `delta_beloy_ref` is zero by definition
on the residual axis. A future metric task may include the Beloy uncertainty
only after reading it from the committed Beloy row and converting it to
fractional units as `sigma_R / R_beloy_ref`.

## Frozen Observable Contract

Future consumers must preserve these fields and labels:

| Contract field | Required value |
| --- | --- |
| Ratio orientation | `Yb/Sr` |
| Pizzocaro input quantity | `fractional_frequency_ratio_deviation_relative_units` |
| Diagnostic output quantity | `fractional_residual_relative_to_beloy_reference` |
| Units | `dimensionless_relative` |
| Window granularity | Ten source windows, reported separately |
| Beloy central residual | `0` on the residual axis |
| Pizzocaro value source | `value_yb_sr_relative` from the committed VLBI ledger |
| Pizzocaro diagonal uncertainty source | `final_uncertainty` from the committed VLBI ledger |
| Approximate covariance source | `ACLOCK-PIZZOCARO-VLBI-COV-APPROX-0001` |
| Allowed covariance label | `COV_SOURCE_DERIVED_PSD_APPROX_SENSITIVITY_ONLY` |
| Required diagonal label | `DIAGONAL_ONLY_NO_CROSS_WINDOW_COVARIANCE` |
| Allowed sensitivity bounds | `rho_clock = 0` and `rho_clock = 1` as separate sensitivity views |
| Benchmark row admission | Forbidden |
| Cross-window aggregation | Forbidden |
| Claim or knowledge promotion | Forbidden |

The residual-axis mapping is therefore a unit and semantics harmonization, not
a new measurement extraction. The future diagnostic may ask whether the
Pizzocaro fractional windows look sensitive to the same Yb/Sr reference scale,
but it must not state that Pizzocaro has supplied a second absolute Yb/Sr
benchmark row.

## Comparator Rules

Any future Beloy/Pizzocaro diagnostic under this contract must report both
uncertainty views below, side by side:

1. **Diagonal-only comparator:** use each window's `final_uncertainty` as an
   independent per-window uncertainty and label the surface
   `DIAGONAL_ONLY_NO_CROSS_WINDOW_COVARIANCE`.
2. **Approximate-covariance sensitivity comparator:** use the committed
   `COV_SOURCE_DERIVED_PSD_APPROX` matrix only as a sensitivity diagnostic,
   preserving the `rho_clock = 0` and `rho_clock = 1` bounds separately.

The diagnostic must keep the ten windows visible. It must not average them,
compress them into a single value, fit a time trend, or select a preferred
covariance view as a benchmark result.

## Do-Not-Run Boundary

This task does not authorize:

- `acr-0002` or any other benchmark row from Pizzocaro VLBI windows;
- a cross-window aggregate value or uncertainty;
- Beloy/Pizzocaro consistency metrics in this PR;
- drift fits or temporal trend claims;
- result, claim, prediction, or knowledge registry updates;
- `TASK-0456` unblock.

The remaining publication blocker is unchanged: Atomic still lacks a second
admissible Yb/Sr absolute-ratio benchmark row. Pizzocaro remains useful
diagnostic evidence, not row-of-record benchmark evidence.

## Future Task Preconditions

A future metric task may consume this contract only if it:

- cites this review as its observable mapping source;
- reads Pizzocaro window values and uncertainties from the committed ledger;
- reads the approximate covariance matrix from the committed covariance
  artifact;
- reads any Beloy uncertainty contribution from the committed Beloy row and
  converts it to fractional units;
- reports all outputs as sensitivity-only diagnostics;
- repeats the no-aggregation and no-claim boundaries in its own output routing.

If the Beloy uncertainty field cannot be mapped to `sigma_R / R_beloy_ref`
from committed data, that future task must stop with a do-not-run blocker
instead of inventing an uncertainty model.

## Limitations

- Repository evidence only; no live source fetch.
- No numerical metric was computed in this task.
- The contract defines a residual-axis diagnostic surface, not an absolute
  ratio ingestion rule.
- The covariance matrix remains approximate and sensitivity-only.
- No maintainer endorsement of consistency, stability, or anomaly language is
  implied.

## Output Routing

- Task verdict:
  `SENSITIVITY_ONLY_RESIDUAL_CONTRACT_DEFINED_NO_BENCHMARK_ROW`.
- Canonical destination:
  `docs/reviews/atomic-pizzocaro-observable-harmonization-contract.md`.
- Review tier: `none`.
- Gate A status: not attempted; no rows or metrics.
- Gate B status: not applicable.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result artifact impact: no `results/` artifact created or modified.
- Publication blocker: no second admissible Yb/Sr absolute-ratio benchmark row;
  Pizzocaro remains diagnostic-only even with a defined residual-axis contract.
