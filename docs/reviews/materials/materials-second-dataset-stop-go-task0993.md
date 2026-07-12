# Materials second-dataset stop/go packet

- Task: `TASK-0993`
- Domain: Materials Property Residuals
- Mode: planning and source curation only
- Decision date: `2026-07-12`

## Scope

MD-0002 v0.1.0 is externally published, checksum-verified, and must remain
byte-stable. This packet decides whether a distinct source-pinned dataset lane
is worth preparing; it does not fetch data, create rows, re-run metrics, or
change MD-0002, RESULT-0021, or any claim.

## Candidate comparison

| Direction | Source availability and reuse | Row-count plausibility | Benchmark target | Leakage risk | Public value | Decision |
| --- | --- | --- | --- | --- | --- | --- |
| OQMD v1.8 source-manifest preflight | The [OQMD download page](https://www.oqmd.org/download/) identifies a February 2026 versioned release, a 21.1 GB dump, and CC BY 4.0 data. The full dump is too large for direct repository intake. | A bounded, source-pinned slice is plausible only after field semantics and extraction policy are reviewed; no row count is authorized here. | A separate computed-property benchmark, with formation-energy semantics checked before any task is queued. | OQMD and Materials Project may share structures, references, or derived provenance; deduplication and disjoint holdout rules are mandatory. | High: an independently versioned, openly licensed computed-data surface can test whether the MD-0002 observations are source-specific. | Advance to source-manifest work. |
| MD-0001 evidence card | Already committed, source-pinned, and documented as computed DFT memory. It is not a new independent dataset surface. | Fixed small pilot; no widening or rebuild is justified. | Context for the known formation-energy and split-fragility limits only. | Reusing it as a new benchmark would repeat the same source and holdout context. | Moderate as review context; low as new evidence. | Keep as memory, do not reopen a leaderboard. |
| AFLOW source lane | The [AFLOW Aflux documentation](https://aflow.org/documentation/) exposes metadata queries but limits data use to scientific, academic, and non-commercial purposes. | Large catalog, but no bounded slice is authorized while reuse limits remain incompatible with a general public dataset route. | None until source rights are resolved. | Cross-database structure and calculation overlap would require a dedicated audit. | Low under the current reuse posture. | Do not open this lane now. |

## Decision

**Recommendation: `OPEN_SOURCE_TASK`.**

Open one narrow OQMD v1.8 source-manifest task. The task must be limited to
source readiness, not acquisition: pin the versioned release locator, record
the CC BY 4.0 attribution and checksum/retrieval policy, verify available field
and unit semantics, define a bounded row-cap proposal, and specify an
MD-0002/OQMD overlap and no-peek plan. It must not download the 21.1 GB dump,
extract rows, construct a dataset, or run a benchmark.

The recommendation is conditional. If exact property semantics, a legal
checksum path, or a defensible overlap screen cannot be specified from source
metadata, the future task must return `HOLD_MATERIALS_DATASET_EXPANSION` rather
than substitute a live fetch or an unpinned export.

## Guardrails for the future task

- Keep all rows explicitly computed or explicitly measured; never merge those
  provenance classes under one metric.
- Keep property axes separate and confirm calculation-method semantics before
  selecting a target axis.
- Require stable source identifiers plus conservative composition/structure
  overlap screening against MD-0002 before any benchmark split is designed.
- Do not treat cross-source agreement, if later observed, as a materials-design
  result or material-discovery claim.
- Preserve MD-0001 as evidence memory only; do not repackage it as an
  independent second dataset.

## Output routing

- Task verdict: `OPEN_SOURCE_TASK`.
- Canonical destination: `docs/reviews/materials/` decision packet.
- Review tier: none.
- Gate A / Gate B: not attempted.
- Data/result/claim/knowledge mutation: none.
- Publication blocker: an OQMD source-manifest and overlap/no-peek decision are
  required before any acquisition or benchmark task.
