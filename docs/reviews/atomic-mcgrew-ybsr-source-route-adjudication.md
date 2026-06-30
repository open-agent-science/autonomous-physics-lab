# Atomic McGrew/NIST Yb-Sr Source-Route Adjudication

**Task:** `TASK-0901`

**Campaign:** `atomic-clock-residuals`

**Decision date:** 2026-06-30

**Verdict:** `BLOCKED_CORRELATED_OR_NOT_DIRECT`

## Scope

This value-blind adjudication resolves the two questions left by `TASK-0889`:
whether McGrew et al. 2018 publishes a primary absolute `171Yb/87Sr` ratio,
and whether a McGrew/NIST route can count as independent of the committed
Beloy/BACON row. It transcribes no frequency values, creates no rows, and runs
no Yb/Sr metric.

## Source Identity

| Field | Pinned evidence |
|---|---|
| Candidate publication | W. F. McGrew et al., "Atomic clock performance enabling geodesy below the centimetre level," *Nature* 564, 87-90 (2018) |
| DOI | [10.1038/s41586-018-0738-2](https://doi.org/10.1038/s41586-018-0738-2) |
| Primary public audit copy | [NIST-hosted article PDF](https://tf.nist.gov/general/pdf/2963.pdf) |
| Measurement surface | local differential comparison of two `171Yb` optical lattice clocks, `Yb-1` and `Yb-2` |
| Relevant later ratio publication | Beloy/BACON, ["Frequency Ratio Measurements with 18-Digit Accuracy Using a Network of Optical Clocks"](https://www.nist.gov/publications/frequency-ratio-measurements-18-digit-accuracy-using-network-optical-clocks), *Nature* 591, 564-569 (2021) |

The McGrew article abstract, apparatus description, uncertainty table, and
reproducibility analysis consistently describe two ytterbium clocks. They do
not define an `87Sr` clock, an Yb/Sr ratio row, a Yb/Sr campaign interval, or a
Yb/Sr uncertainty budget. References to earlier Yb/Sr literature do not turn
the McGrew Yb/Yb experiment into a primary Yb/Sr measurement.

## Adjudication

| Required question | Finding | Decision |
|---|---|---|
| Does McGrew 2018 publish a primary absolute `171Yb/87Sr` ratio? | No. Its first-class observables are performance and differential reproducibility of `Yb-1` and `Yb-2`. | Fails `direct_frequency_ratio_measurement` for the requested species pair. |
| Can the candidate supply uncertainty semantics for an Yb/Sr row? | No Yb/Sr row exists in this source, so its Yb/Yb statistical/systematic budget cannot be relabelled as Yb/Sr uncertainty. | Row curation is blocked. |
| Is a McGrew-associated NIST Yb/Sr surface independent of Beloy/BACON? | The identifiable direct NIST/JILA Yb/Sr publication is Beloy/BACON 2021, with McGrew and other NIST/JILA contributors inside the same optical-clock network publication already represented by `ACR-0001`. | It is not a new independent third source. |

The independence conclusion is deliberately narrow. It does not claim that
all NIST measurements are statistically identical. It states that the route
named by `TASK-0889` resolves either to a 2018 Yb/Yb paper with no Yb/Sr row,
or to the later Beloy/BACON Yb/Sr source already committed as `ACR-0001`.
Neither interpretation satisfies the Atomic reopen condition.

## Verdict

`BLOCKED_CORRELATED_OR_NOT_DIRECT`.

The route fails before value curation because it supplies no primary Yb/Sr
observable. Reinterpreting it as the later NIST/JILA network ratio would
duplicate the existing Beloy/BACON source rather than add an independent row.
The current Beloy/Nemitz two-source, Nemitz-dominated blocker therefore remains
unchanged.

## Exact Next Task Shape

No McGrew row-pinning task should be opened. A future task may instead perform
one value-blind scout for a post-2021 primary absolute neutral-clock Yb/Sr
publication that is institutionally and experimentally distinct from all four
already exhausted surfaces: Beloy/BACON, Nemitz/RIKEN, Pizzocaro/INRIM, and
McGrew/NIST Yb/Yb.

That scout must stop before values and return only:

- a primary publication locator and direct Yb/Sr row location;
- uncertainty and covariance availability;
- lab, clock, comb, link, reference, and campaign-overlap assessment;
- one of `READY_FOR_SOURCE_ARTIFACT`, `BLOCKED_NO_INDEPENDENT_SOURCE`, or
  `NEEDS_MAINTAINER_DECISION`.

If no such source is found, the campaign remains monitor-only until a new
independent measurement appears. Yb+/Cs and same-ion transition comparisons
may broaden the campaign, but they do not satisfy this neutral Yb/Sr reopen
condition.

## Stop Conditions

- Do not curate a McGrew 2018 Yb/Sr row; no such primary row exists.
- Do not duplicate the Beloy/BACON ratio under a McGrew source identity.
- Do not derive Yb/Sr from an absolute Yb frequency and an external Sr value.
- Do not reuse the Yb/Yb uncertainty budget as Yb/Sr uncertainty.
- Do not run metrics, fit drift, or create `RESULT`, `PRED`, `CLAIM`, or
  `KNOW` artifacts from this decision.

## Output Routing

| Destination | Action |
|---|---|
| Source readiness | McGrew/NIST route blocked |
| Atomic dataset | No row or source-manifest mutation |
| Existing diagnostic | Beloy/Nemitz source-limited memory unchanged |
| Gate A / Gate B | Not attempted / not applicable |
| Claim and knowledge | No impact |
