# Atomic Post-2021 Independent Yb/Sr Source Scout

**Task:** `TASK-0913`

**Campaign:** `atomic-clock-residuals`

**Review date:** 2026-07-03

**Verdict:** `BLOCKED_NO_INDEPENDENT_SOURCE`

## Scope

This value-blind scout evaluates exactly one post-2021 publication outside the
exhausted Beloy/BACON, Nemitz/RIKEN, Pizzocaro/INRIM, and McGrew/NIST surfaces.
It records source identity, measurement class, rights, uncertainty visibility,
network independence, and species compatibility without transcribing any
frequency or ratio value.

## Candidate

| Field | Finding |
|---|---|
| Publication | P. Morzynski et al., "Intercontinental frequency ratio measurement of 171Yb and 88Sr optical lattice clocks," *Metrologia* 61, 045009 (2024) |
| DOI | [10.1088/1681-7575/ad6a1e](https://doi.org/10.1088/1681-7575/ad6a1e) |
| Primary public locator | [Nicolaus Copernicus University publication record](https://omega.umk.pl/info/article/UMK3c1ca43c7356427b92336909dadec6c5?lang=en) |
| Clock pair | neutral `171Yb` lattice clock at NMIJ/AIST and neutral `88Sr` lattice clock at UMK |
| Measurement route | primary intercontinental ratio comparison mediated by local optical-frequency-comb measurements, hydrogen masers, fiber transfer on the Polish side, and GPS precise-point-positioning transfer |
| Campaign epoch | five-day campaign in March 2020 |
| License | CC BY; attribution required |

## Gate Assessment

| Gate | Assessment | Decision |
|---|---|---|
| Post-2021 primary publication | Peer-reviewed 2024 article reporting its own intercontinental clock-ratio campaign. | clears |
| Neutral-clock ratio | Both endpoints are neutral-atom optical lattice clocks. The reported ratio is a first-class result, although the intercontinental leg is GNSS-mediated rather than a direct optical link. | clears with method qualifier |
| Institutional independence | NMIJ/AIST and UMK are distinct from NIST/JILA, RIKEN, and INRIM. No clock, comb, or network overlap with the four excluded source surfaces is identified in the publication metadata. | clears for source independence |
| Uncertainty visibility | The paper exposes separate clock systematic budgets and transfer/statistical contributions, so uncertainty semantics are reviewable before any row task. | clears at source-review level |
| Covariance visibility | The comparison architecture and shared transfer chain are described. A future row would still need its within-campaign shared-systematic notes preserved. | reviewable |
| Rights and access | Institutional metadata identifies CC BY and links the publication of record. A limited factual metadata pin is feasible. | clears |
| Species compatibility | The strontium endpoint is bosonic `88Sr`, not the `87Sr` transition used by the committed Beloy and Nemitz `171Yb/87Sr` rows. | **fails the reopen role** |

## Independence And Compatibility Decision

The candidate is institutionally and experimentally independent of the four
excluded routes. It is also a genuine primary neutral-clock Yb/Sr publication.
However, it does not measure the same frequency ratio as the existing
`171Yb/87Sr` consistency axis. The isotope and transition change is
load-bearing: an `171Yb/88Sr` value cannot be appended as a third
`171Yb/87Sr` row, compared under the existing two-row diagnostic, or converted
using an external recommended-frequency value without creating a derived row
with different covariance semantics.

The candidate therefore cannot satisfy the current Atomic reopen condition.
Its independence does not cure the species mismatch.

## Verdict

`BLOCKED_NO_INDEPENDENT_SOURCE` for the required `171Yb/87Sr` source role.

This verdict does not reject the publication or question its measurement. It
means that the one candidate scouted here is not an admissible independent row
for the repository's existing neutral `171Yb/87Sr` axis. No source-artifact or
row-curation task is authorized from this scout.

## Stop Conditions

- Do not relabel the `171Yb/88Sr` ratio as `171Yb/87Sr`.
- Do not derive an `87Sr` ratio by combining this source with an external
  recommended-frequency value.
- Do not combine its uncertainty budget with the Beloy/Nemitz diagnostic.
- Do not ingest values, run metrics, fit drift, or create `RESULT`, `PRED`,
  `CLAIM`, or `KNOW` artifacts.
- Do not present institutional independence as species compatibility.

## Future Route

Keep the campaign monitor-only until a primary post-2021 `171Yb/87Sr`
publication is found with a distinct clock/network lineage and recoverable
uncertainty semantics, or until a maintainer approves a separate multi-species
harmonization contract. Such a contract would be a different benchmark axis
and must not silently modify the current reopen condition.

## Output Routing

| Destination | Action |
|---|---|
| Source readiness | Candidate assessed; required role remains blocked |
| Atomic rows and manifest | No change |
| Existing Beloy/Nemitz memory | Unchanged |
| Gate A / Gate B | Not attempted / not applicable |
| Result, prediction, claim, knowledge | No impact |
