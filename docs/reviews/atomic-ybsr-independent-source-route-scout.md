# Atomic Yb/Sr Independent Source Route Scout

Task: `TASK-0889`
Campaign: `atomic-clock-residuals`
Mode: planning-only source-readiness scout (value-blind)
Route scouted: NIST Yb optical-lattice-clock absolute-frequency / Yb-Sr-Hg
ratio surface associated with McGrew et al. 2018 (NIST), distinct from the
already-adjudicated Beloy/Nemitz/Pizzocaro paths
Verdict: `NEEDS_MAINTAINER_SOURCE_DECISION`
Review date: 2026-06-29

## Scope

This scout checks exactly **one** candidate independent absolute Yb/Sr source
route against the Atomic reopen condition recorded in the
[Yb/Sr source-limited consistency memory card](atomic-yb-sr-source-limited-consistency-memory-card.md):
a finer-precision independent absolute Yb/Sr source row that does not let the
Nemitz uncertainty dominate, or a maintainer-approved aggregation route.

The candidate deliberately differs from the three paths that the campaign has
already adjudicated:

- Beloy 2021 / BACON and Nemitz 2016 / RIKEN are the two committed rows behind
  the source-limited two-row diagnostic; rerunning them is explicitly
  out of bounds.
- Pizzocaro 2020 / INRIM VLBI was scouted in the
  [reopen source-route scout](atomic-ybsr-reopen-source-route-scout.md)
  (`AGGREGATION_CONTRACT_NEEDED`) and re-confirmed diagnostic-only in the
  [aggregation and observable-harmonization contract](atomic-pizzocaro-aggregation-observable-harmonization-contract.md)
  (`REMAINS_DIAGNOSTIC_ONLY`).

The candidate scouted here is the **NIST Yb optical-lattice-clock source family
associated with McGrew et al. 2018**, which the
[second-source fallback triage](atomic-second-source-fallback-triage.md) ranked
(rank 3) as a primary direct-ratio candidate that carries a Yb-Sr-Hg ratio
surface, and which the
[direct-ratio source-artifact review](atomic-clock-direct-ratio-source-artifact-review.md)
named as an alternative single-source candidate that would each need its own
source-artifact review.

This scout uses committed repository evidence plus general, value-blind
knowledge of the precision-metrology literature. It does **not** fetch live
sources, transcribe or ingest any frequency-ratio value, add or edit rows,
aggregate windows, rerun Beloy/Nemitz/Pizzocaro metrics, fit any drift, or
create `RESULT`, `PRED`, `CLAIM`, or `KNOW` artifacts. No constants-variation
or drift wording is asserted anywhere in this note.

## Candidate Identity And Locator

| Field | Value (locator-level only, value-blind) |
| --- | --- |
| Candidate route | NIST Yb optical-lattice-clock absolute-frequency / Yb-Sr-Hg ratio surface (McGrew et al. 2018) |
| Reporting group / lab | NIST (with the contemporaneous NIST/JILA optical-clock comparison network) |
| Publication of record | McGrew et al., *Nature* 564, 87 (2018), "Atomic clock performance enabling geodesy below the centimetre level" |
| DOI (locator, not a value) | 10.1038/s41586-018-0738-2 |
| Preprint locator class | arXiv preprint exists; locator must be confirmed and pinned by a separate source-artifact task |
| Species pair of interest | ¹⁷¹Yb (lattice clock) vs ⁸⁷Sr (lattice clock) — the load-bearing Yb/Sr axis |
| Source class (intended) | `direct_frequency_ratio_measurement` (per `source_manifest_template.yaml` row class `direct_frequency_ratio_measurement`) **only if** a primary, source-pinned absolute Yb/Sr ratio surface is recoverable; otherwise `evaluation_or_review_summary` |

## Source-Readiness Assessment

The assessment below maps the candidate against the
[source-manifest template](../../data/atomic_clocks/source_manifest_template.yaml)
`direct_frequency_ratio_measurement` requirements and the
[atomic-clock row schema](../../data/atomic_clocks/schema.md) `direct_measurement`
fields.

| Readiness dimension | Candidate state (value-blind) | Decision |
| --- | --- | --- |
| Identity / locator | Publication of record and DOI are recoverable as facts; preprint locator and checksum/archive plan are not pinned in this repository. | needs source-artifact task |
| Source class / row type | Intended `direct_frequency_ratio_measurement` → `direct_measurement`. Whether the source publishes a **primary absolute ¹⁷¹Yb/⁸⁷Sr ratio** as a first-class row (versus an absolute ¹⁷¹Yb frequency vs SI second plus a separately reported ratio surface) is **not established** from committed evidence. | undetermined; gates row class |
| License / reuse posture | Nature publication of record is not redistributable here (same posture as Beloy/Nemitz). arXiv preprint, if present, is arXiv nonexclusive-distrib; that is a license-review decision, not an automatic third-party redistribution grant (same posture recorded for Lange/PTB). Metadata and locators are committable as facts. | metadata-only until maintainer license review |
| Uncertainty semantics | A primary NIST optical-clock paper is expected to expose total / statistical / systematic budgets, but the **exact decomposition for an absolute Yb/Sr ratio** (versus an absolute Yb frequency) is not transcribed or confirmed here. Must be recovered field-by-field before any row. | undetermined; gates ingestion |
| Covariance / correlation visibility | This is the load-bearing risk. The NIST Yb source shares the NIST/JILA optical-clock comparison network, combs, and reference infrastructure with the **NIST + JILA + NIST BACON 2018 campaign behind Beloy 2021 / BACON (ACR-0001)**. A Yb/Sr ratio derived from, or sharing systematics with, that same network is **not independent** of the load-bearing Beloy row. Independence vs Beloy must be demonstrated, not assumed. | independence not demonstrated; high risk |
| Version-drift risk | Preprint vs version-of-record vs any erratum/supplement must be compared before row publication (the standing `SOURCE_ARTIFACT_VERSION_DRIFT` stop condition). | medium; standard source-curation work |
| Admissible value-bearing row curation | Not admissible now. Blocked on (a) confirming a primary absolute Yb/Sr ratio surface exists, (b) demonstrating independence from the Beloy/BACON NIST/JILA network, and (c) the standard locator/license/uncertainty gates. | blocked pending decision |

## Stop-Condition Check

Against the `global_stop_conditions` in the
[source-manifest template](../../data/atomic_clocks/source_manifest_template.yaml)
and the [fallback triage](atomic-second-source-fallback-triage.md) stop list:

- Not a review summary by intent, **but** it is not yet confirmed to publish a
  primary absolute Yb/Sr ratio row rather than an absolute Yb-frequency surface
  combined with separately reported ratios. If only the latter is recoverable,
  the route collapses toward `review_summary` semantics and stops.
- Combination rules are not hidden in principle, but the **shared-systematic /
  network-overlap question with Beloy/BACON is exactly the
  `source_mentions_covariance_or_shared_systematics_without_recoverable_notes`
  risk** and must be resolved before any row.
- Uncertainty semantics are plausibly present but not yet recovered.
- No private-access barrier is known beyond the ordinary
  non-redistributable publication-of-record posture; the candidate does **not**
  require agent-unavailable private access to scout at metadata level.

No single stop condition fires hard enough to force an immediate `BLOCKED`
(unlike a pure review summary or a private-access-only source), but two
conditions — primary-absolute-ratio confirmation and Beloy-network independence —
are unresolved and are decisive. This is why the verdict is
`NEEDS_MAINTAINER_SOURCE_DECISION` rather than `READY` or `BLOCKED`.

## Verdict

`NEEDS_MAINTAINER_SOURCE_DECISION`.

The route is plausible and genuinely distinct from Beloy/Nemitz/Pizzocaro, and
it is the strongest remaining candidate that could in principle supply a finer
independent absolute Yb/Sr surface. It is **not** `READY`: a value-bearing row
cannot be curated until two source-defining questions are answered, and one of
them (independence from the Beloy/BACON NIST/JILA network) is a scientific
admissibility decision, not ordinary curation. It is **not** `BLOCKED` outright,
because the source is public, not a review summary by intent, and scoutable at
metadata level without private access.

The maintainer-or-source decision needed, exactly:

1. Confirm whether the McGrew 2018 NIST source publishes a **primary,
   source-pinned absolute ¹⁷¹Yb/⁸⁷Sr frequency ratio** as a first-class row
   (with its own uncertainty budget), or only an absolute ¹⁷¹Yb frequency
   together with a separately reported ratio surface. Only the former is a
   candidate `direct_measurement` Yb/Sr row.
2. Decide whether a NIST Yb/Sr ratio sharing the NIST/JILA optical-clock
   comparison network, combs, and references with the Beloy 2021 / BACON
   campaign (`ACR-0001`) can count as an **independent** source for the Atomic
   reopen condition, or whether the shared network makes it a correlated
   surface that cannot reduce the two-row / source-limited blocker.

If both answers are favorable, the route clears to ordinary source-curation
work; if either is unfavorable, the route is `BLOCKED` and the campaign should
fall back to the next ranked candidate in the
[fallback triage](atomic-second-source-fallback-triage.md).

## Next Row-Curation Task Shape (Conditional, Not Authorized Here)

Only if the maintainer decision above is favorable on **both** points, the next
task is an ordinary single-source source-artifact + readiness task, not a
benchmark task. Its shape:

- **Type:** `scientific_source_curation`, `mode: source_artifact_pinning`
  (metadata-only first; no value ingestion in the same step).
- **Goal:** pin the McGrew 2018 NIST source artifact under
  `data/atomic_clocks/source_artifacts/`, with locator, DOI, retrieval date,
  license note, and checksum/archive plan, following the
  [source-acquisition lane](../source-acquisition-lane.md).
- **Required evidence to recover before any row:** primary absolute Yb/Sr ratio
  surface confirmation; total/statistical/systematic uncertainty decomposition;
  explicit shared-systematic / network-overlap notes vs Beloy/BACON; campaign
  epoch window; preprint-vs-version-of-record drift check.
- **Stop conditions:** the standing `SOURCE_ARTIFACT_VERSION_DRIFT`, any
  unrecoverable covariance/shared-systematic note, any mixing of a direct ratio
  with a derived constants-variation constraint, and any attempt to assign a
  benchmark holdout role before the source gate passes.
- **Explicitly out of scope for that task:** Yb/Sr metric runs, drift fitting,
  cross-source comparison, and any `RESULT`/`PRED`/`CLAIM`/`KNOW` artifact.

The independence question (point 2) must be decided **before** the row is given
any `cross_source_reference` or `cross_source_target` holdout role, because a
correlated source cannot serve as an independent cross-check of the Beloy row.

## Output Routing

- Task verdict: `NEEDS_MAINTAINER_SOURCE_DECISION` (source-readiness scout; no
  metric, no result, no prediction).
- Canonical destination:
  `docs/reviews/atomic-ybsr-independent-source-route-scout.md`.
- Review tier: `none`.
- Gate A status: not attempted; no `RESULT`/`PRED` artifact produced.
- Gate B status: not applicable.
- Claim impact: none; no claim created or changed.
- Knowledge impact: none; no knowledge entry created or changed.
- Result / dataset impact: none; no value ingested, no row, covariance, source
  manifest, claim, or knowledge file edited.
- Source-readiness impact: one independent absolute Yb/Sr candidate route
  (McGrew 2018 / NIST) scouted value-blind; it is distinct from
  Beloy/Nemitz/Pizzocaro and remains gated on a primary-absolute-ratio
  confirmation and a Beloy-network independence decision.
- Publication blocker: no admissible third absolute Yb/Sr row exists; the route
  cannot reduce the two-row / Nemitz-dominated blocker until the two
  maintainer/source decisions above are resolved.

## Limitations

- This scout evaluated exactly one route, as required; it is not a broad
  literature search for all candidate Yb/Sr sources.
- It used committed repository evidence plus value-blind general knowledge of the
  precision-metrology literature. It did **not** inspect live publisher pages,
  PDFs, supplements, or current archive state, and it transcribed no value.
- The McGrew 2018 absolute-ratio surface determination and the Beloy-network
  independence determination are stated as open questions, not as confirmed
  facts; both are owned by a future maintainer-scoped source-artifact task.
- Nothing here authorizes row curation, source pinning, metric runs, aggregation,
  drift fitting, or any claim/knowledge/result promotion. Constants-variation
  and drift framing are out of scope and are not asserted.
