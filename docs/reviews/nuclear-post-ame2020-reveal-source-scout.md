# Nuclear post-AME2020 reveal source candidate scout

- Task: `TASK-0640`
- Campaign: `nuclear_mass_surface`
- Protocol class: value-free source-candidate scout (source-class taxonomy)
- Status: no target values fetched, copied, transcribed, inspected, or scored

## Scope

This review scouts **candidate source classes** for a future reveal of the
frozen nuclear-mass prediction registry, one layer earlier than a concrete
source manifest. It maps where a post-freeze measured-mass source could come
from, classifies each class by admissibility posture, and records no-peek
compatibility and checksum/archive feasibility per class.

It extends, and does not repeat, the concrete-source scout in
[`nuclear-post-ame2020-reveal-source-manifest-scout.md`](nuclear-post-ame2020-reveal-source-manifest-scout.md)
(`TASK-0585`), which examined three named sources and landed
`BLOCKED_SOURCE_NOT_PINNED`. The goal here is a reusable classification map so
that whenever a post-freeze source appears, its admissibility lane is already
defined.

This task uses metadata-level evidence only: source-class titles, issuing
bodies, version/date semantics, citation posture, locators, reuse notes,
checksum feasibility, and value-semantics risk. It does **not** fetch source
tables, inspect target rows, record measured mass values, update `PRED-*`
entries, run reveal metrics, or create result, claim, prediction, or knowledge
artifacts.

Use it with:

- [Nuclear Prediction Reveal Protocol](../nuclear-prediction-reveal-protocol.md)
- [Nuclear Reveal Source Readiness Checklist](../nuclear-reveal-source-readiness-checklist.md)
- [Fresh-Data Readiness Matrix](../fresh-data-readiness-matrix.md)
- [Prediction Registry Policy](../prediction-registry-policy.md)

## Registry timing boundary

The frozen prospective entries (`PRED-0063` through `PRED-0068` and the broader
registry) are registered at `2026-05-20T00:00:00Z`. A prospective reveal source
must be demonstrably available to the project **only after** that freeze, or the
comparison must be downgraded to a retrospective diagnostic. This scout was run
on `2026-06-06`, roughly two weeks after the freeze.

No live fetch was performed. This scout reasons at the source-class level from
general provenance knowledge; it does **not** assert that any specific
post-freeze article or release now exists. Confirming a concrete post-freeze
source is the job of a later network-enabled manifest task, and only after the
no-peek gate is satisfied.

## Candidate source classes

Classification labels (per task contract): `admissible`,
`needs_maintainer_access`, `license_blocked`, `date_version_ambiguous`,
`not_relevant`. No class is classified `admissible` today because none has a
pinnable artifact that postdates the freeze.

### Class A — Next official AME / NUBASE evaluation

- Source class: `official_evaluation`.
- Issuing body: Atomic Mass Data Center (AMDC); Chinese Physics C.
- Locator: `https://amdc.impcas.ac.cn/web/masseval.html`; future-edition DOI.
- Version/date semantics: discrete, clearly dated editions (AME2020, NUBASE2020,
  and a future AMEnext). Each edition carries row-level measured vs
  extrapolated/systematics flags.
- Citation posture: strong; citable DOI and stable distribution file
  (`mass.mas`-style).
- No-peek compatibility: **excellent in principle** — a future edition with a
  release date after `2026-05-20` and immutable distribution would give a clean
  predate check and measured/non-measured separation.
- Checksum/archive feasibility: feasible (`committed_copy` or
  `external_archive_with_checksum` of the pinned `.mas` file).
- Classification: `date_version_ambiguous` (not-yet-released). The current
  AME2020/NUBASE2020 editions predate the freeze and are baseline/format
  references only. This is the **ideal** future source but is unavailable today.

### Class B — Primary peer-reviewed mass-measurement tables (Penning trap / storage ring)

- Source class: `peer_reviewed_table` (primary measurement).
- Issuing bodies / facilities: Penning-trap groups such as ISOLTRAP
  (CERN-ISOLDE), JYFLTRAP (Jyväskylä), TITAN (TRIUMF), LEBIT (FRIB/MSU),
  SHIPTRAP (GSI), and FSU; storage-ring programs at GSI ESR and IMP CSRe.
- Locator: per-article journal DOI (PRL/PRC/PLB) plus arXiv preprint surface.
- Version/date semantics: fixed publication date per article, giving a clean
  per-source predate check against the freeze.
- Citation posture: strong (refereed primary literature).
- No-peek compatibility: **good per article**, but requires per-nuclide
  verification that each measured nuclide was absent from AME2020/`NMD-0003`
  training and matches a registered `PRED-*` target, before any inspection of
  values.
- Checksum/archive feasibility: a curated table of measured rows with DOIs could
  be normalized and checksummed; values live in article tables/PDFs, so an
  extraction + `normalized_artifact_checksum` step is required. Raw full text is
  often paywalled.
- Classification: `needs_maintainer_access` (mixed open arXiv / paywalled
  journal) and admissible-in-principle once a qualifying post-`2026-05-20`
  article is confirmed. This is the **most realistic near-term** post-freeze
  lane, conditional on such an article existing.

### Class C — Collaboration / facility / agency data releases

- Source class: `collaboration_release`.
- Issuing bodies: FRIB, GSI/FAIR, IMP Lanzhou data portals; IAEA Nuclear Data
  Services; NNDC.
- Locator: facility data portals and agency services.
- Version/date semantics: often rolling or version-tagged; an immutable,
  date-stamped snapshot is not guaranteed.
- Citation posture: moderate to strong depending on release.
- No-peek compatibility: depends on an explicit, immutable release date and
  measured-row flags; rolling portals make the predate proof fragile.
- Checksum/archive feasibility: feasible only for an explicitly versioned,
  archivable release; not for an interactive query surface.
- Classification: `date_version_ambiguous` (and possibly
  `needs_maintainer_access`). Usable only if a specific versioned release
  postdates the freeze with measured flags.

### Class D — Evaluated rolling databases (ENSDF / NNDC / interactive AMDC tables)

- Source class: `archive_copy` / evaluated-database derivative.
- Issuing bodies: NNDC (ENSDF), AMDC interactive tables.
- Version/date semantics: continuously updated; no immutable per-row
  availability date.
- Citation posture: strong as evaluations, but row-level provenance and timing
  are not cleanly separable.
- No-peek compatibility: **poor** — cannot prove a specific row postdates the
  freeze, and evaluated rows blend measured, extrapolated, and model-derived
  values.
- Checksum/archive feasibility: a snapshot could be checksummed, but the timing
  proof fails.
- Classification: `date_version_ambiguous` / not cleanly no-peek. Not usable for
  prospective reveal without per-row primary-source provenance.

### Class E — Secondary compilations / survey papers

- Source class: `secondary_compilation`.
- Example surface: the 2025 post-AME2020 new-mass survey already logged by
  `TASK-0585` (`https://arxiv.org/abs/2505.09914`,
  `https://doi.org/10.1007/s41365-025-01821-1`), compiling masses for 296
  nuclides from 40 references published 2021–2024.
- Version/date semantics: predates the `2026-05-20` freeze; aggregates
  pre-freeze measurements.
- Citation posture: citable, but secondary and mixed-provenance.
- No-peek compatibility: fails the predate check; secondary provenance prevents
  measured-only guarantees.
- Checksum/archive feasibility: a PDF/package could be pinned, but it is not a
  measured-only reveal table.
- Classification: `not_relevant` for prospective reveal. Usable only as a
  bibliography map for future primary-source scouting, and only without
  inspecting target-row values.

### Class F — Informal / low-provenance sources (theses, proceedings, unrefereed)

- Source class: not a recognized reveal source class.
- Citation posture: insufficient for a reveal gate.
- Classification: `not_relevant`. Excluded regardless of timing.

## Class summary

| Class | Source class | No-peek | Checksum/archive | Classification |
| --- | --- | --- | --- | --- |
| A | Next AME/NUBASE edition | excellent (if post-freeze) | feasible | `date_version_ambiguous` (not yet released) |
| B | Primary Penning-trap/storage-ring tables | good per article | feasible w/ extraction | `needs_maintainer_access` |
| C | Collaboration/agency releases | conditional | conditional | `date_version_ambiguous` |
| D | Evaluated rolling databases | poor | timing proof fails | `date_version_ambiguous` |
| E | Secondary compilations | fails predate | not measured-only | `not_relevant` |
| F | Informal/low-provenance | n/a | n/a | `not_relevant` |

## Readiness decision

`BLOCKED_SOURCE_NOT_PINNED`

No candidate class yields an `admissible`, pinnable artifact today. No class
simultaneously (1) postdates the `2026-05-20T00:00:00Z` freeze, (2) has an exact
immutable locator or accepted archive policy, (3) can be checksummed before
scoring, (4) separates measured from non-measured rows, and (5) can be reviewed
without exposing target-row values. This matches and extends the `TASK-0585`
finding.

## Recommended follow-up

Per the task contract (at most one follow-up source-artifact package task, or
preserve a source blocker), this scout **preserves the source blocker** rather
than opening a follow-up package task now: creating a package task would be
premature while no qualifying post-freeze artifact exists.

The single highest-value follow-up, to be opened **only when** a concrete
qualifying source appears, is a Class B package task: pin one post-`2026-05-20`
primary peer-reviewed measurement table as a value-free source manifest (DOIs,
release date, measured-row flags, target-match rules, raw + normalized
checksums), screened against the no-peek audit before any value inspection.
Class A (next AME/NUBASE edition) would supersede Class B as the cleanest source
the moment such an edition is released.

## Stop conditions preserved

- Do not fetch or parse source tables that expose target mass values.
- Do not inspect target rows while deciding source admissibility.
- Do not score partial reveals from a source that predates registration.
- Do not modify frozen `PRED-*` entries.
- Do not promote any claim or result from this scout.

## Output routing

- Task verdict: `INCONCLUSIVE` for reveal readiness.
- Canonical destination:
  `docs/reviews/nuclear-post-ame2020-reveal-source-scout.md`.
- Review tier: `none`.
- Gate A status: not attempted; no `RESULT-*` or `PRED-*` artifact.
- Gate B status: not attempted; no independent replay target.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result artifact impact: no `results/` artifacts modified.
- Limitations / blockers: no live fetch performed; no admissible post-freeze
  source class is pinnable; reveal scoring remains blocked
  (`BLOCKED_SOURCE_NOT_PINNED`). Class B is the most realistic future lane and
  Class A the ideal, both conditional on a post-`2026-05-20` source existing.

## Metadata sources

- AMDC AME2020 distribution page:
  `https://amdc.impcas.ac.cn/web/masseval.html`.
- AME2020 Part II article:
  `https://doi.org/10.1088/1674-1137/abddaf`.
- Qu et al. post-AME2020 new-mass survey preprint:
  `https://arxiv.org/abs/2505.09914`.
- Qu et al. journal DOI:
  `https://doi.org/10.1007/s41365-025-01821-1`.
