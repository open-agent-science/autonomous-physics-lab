# ThermoML esters/lactones negative memory

## Decision record

| Field | Value |
|---|---|
| Task | `TASK-0896` |
| Evidence source | `RESULT-0026` (`results/EXP-0020/RUN-0001/`) |
| Campaign | Thermophysical Property Residuals |
| Decision date | 2026-06-29 |
| Memory verdict | `ESTERS_LACTONES_TRANSFER_NOT_SUPPORTED_IN_SCOPE` |
| Routing | Negative/control memory only |

This note packages an already committed failed-family result. It does not rerun
the benchmark, alter its fixture or coefficients, or create a new result.

## Evidence

The benchmark used a committed 40-row normal-boiling-temperature fixture with
eight predeclared families and five held-out rows per family. The family
survival rule required Joback to beat the best non-oracle control by at least
5 K in at least six of the eight families.

| Scope | Joback MAE (K) | Best non-oracle control | Control MAE (K) | Joback margin (K) | Required margin (K) | Outcome |
|---|---:|---|---:|---:|---:|---|
| Aggregate, 40 rows | 14.925825 | `molecular_weight_only` | 43.427943 | 28.502118 | 5.0 | Clears |
| Esters/lactones, 5 rows | 26.134000 | `molecular_weight_only` | 20.584245 | -5.549755 | 5.0 | Does not clear |

Joback cleared seven of eight family margins, so `RESULT-0026` remains
`TRANSFER_SUPPORTED_IN_SCOPE`. Esters/lactones is the exception: the
molecular-weight-only control is better by 5.549755 K, and Joback is
10.549755 K short of the predeclared +5 K survival margin. The family-level
Joback RMSE is 45.894144 K and its uncertainty-weighted MAE is 22.672456 K.

## Interpretation and scope

The aggregate result supports the bounded benchmark verdict, but it does not
support uniform transfer across every chemical family. In particular, the
committed evidence does not support wording that Joback outperforms the
controls for esters/lactones.

This is a five-row held-out family observation from one value-blind fixture.
It is not evidence that Joback universally fails for esters or lactones, that
the molecular-weight control is generally preferable, or that the observed
gap transfers to other properties or datasets. No mechanism or coefficient
failure is inferred from this benchmark.

## Public-safe wording

> On the committed 40-row ThermoML normal-boiling-temperature fixture, Joback
> beat the non-oracle controls overall and cleared seven of eight held-out
> family margins. Esters/lactones was the exception: its five-row Joback MAE
> was 26.134 K versus 20.584 K for the molecular-weight-only control, so the
> predeclared +5 K family-survival margin was not met.

Do not shorten this to a universal Joback success or failure statement. Keep
the fixture size, property, family exception, control comparison, and bounded
scope visible wherever the result is summarized.

## Implications for follow-up

Any future corpus expansion or family-specific audit should retain
esters/lactones as a predeclared stress family rather than omit it from the
aggregate. A confirmatory run should freeze a larger, disjoint held-out set
before scoring, preserve the same non-oracle controls and +5 K margin, and
avoid reusing these five rows as blind confirmation data.

The 80-row expansion considered in
`docs/reviews/thermoml-tb-corpus-expansion-preflight.md` may provide that route
only after its source-rights and row-eligibility decisions are resolved. This
memory note does not authorize data acquisition, model tuning, or a new run.

## Stop conditions

- Do not edit `RESULT-0026`, its metrics, fixture rows, or Joback coefficients
  to remove the failed family.
- Do not create a claim, prediction, knowledge entry, or new result from this
  note.
- Do not tune on the five esters/lactones rows and then report them as an
  independent confirmation set.
- Stop before making chemical-design, process, safety, synthesis, universal
  accuracy, or broad property-estimation claims.
- Require a separate maintainer-approved task before any new benchmark run or
  family-specific correction study.

## Output routing

| Destination | Action |
|---|---|
| Negative/control memory | Record this bounded failed-family observation |
| `RESULT-0026` | Unchanged; existing Gate A pass remains |
| Gate B | Not attempted by this task |
| Claims and predictions | No impact |
| Knowledge registry | No impact |
| Campaign page | No edit required; existing wording already records the family exception |
