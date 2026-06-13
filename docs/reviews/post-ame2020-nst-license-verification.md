# Post-AME2020 NST Article Licence Verification

**Task:** `TASK-0734`
**Source:** Qu, Chen, Pan, Yu & Zhang 2025, *Benchmarking nuclear energy density
functionals with new mass data*, Nuclear Science and Techniques **36**, 231
(`doi:10.1007/s41365-025-01821-1`; Springer).
**Dataset:** `data/nuclear_masses/post_ame2020_holdout.yaml` (post-AME2020 mass
holdout rows; registry id `post-ame2020-nst-holdout`).
**Verdict:** `RESTRICTIVE_ARTICLE_LICENCE_FACTS_BASIS_RETAINED` — pending status
resolved; no Creative Commons licence found.

## Why this was pending

`TASK-0733` declared every committed third-party dataset's redistribution basis
in `data/DATA_LICENSES.yaml`. This entry was the only one left at
`license_verification_pending`: the committed values are individual published
mass facts with citation and the raw article is not vendored, but the article's
reuse licence had not been authoritatively recorded.

## Verification

Crossref metadata for `doi:10.1007/s41365-025-01821-1` (queried 2026-06-13)
records two licence entries (`content-version` `tdm` and `vor`), **both** pointing
to the Springer text-and-data-mining policy
(`https://www.springernature.com/gp/researchers/text-and-data-mining`). **No
Creative Commons licence URL is present.** This is the signature of a Springer
subscription / non-open-access article: the version-of-record licence is the TDM
policy, not CC BY. (The Springer article landing page itself is behind an
authentication redirect and could not be read directly; Crossref is the
authoritative machine-readable per-article licence source used here.)

Contrast: AME2020 (`ame2020-nuclear-masses`) is genuinely CC BY 3.0 (Chinese
Physics C open access). The NST article is **not** open for general
redistribution.

## Resolution

The pending status is resolved to a **verified restrictive** basis. The repo does
not rely on an open licence for this source; it relies on a facts basis:

- Committed values are **individual measured nuclear mass values** — scientific
  facts, not copyrightable expression — curated with full citation to the source.
- The raw article, PDF, and JATS/HTML payload are **not vendored**
  (`raw_artifact_vendored: false`).
- The registry entry now records the Crossref evidence and removes the pending
  marker.

This is the posture `TASK-0734` anticipated for a restrictive article licence
("preserve the facts-plus-citation posture").

## Residual consideration (for maintainer awareness)

The holdout commits a few hundred mass values extracted from one non-open-access
paper's results tables. Reproducing measured values with citation is standard,
well-grounded scientific practice (facts are not copyrightable), and a single
paper's results table is far less database-like than a curated catalogue, so the
launch risk is **low**. If a maintainer nonetheless wants the most conservative
posture, options are: (a) keep as-is on the facts basis (recommended); (b) reduce
the committed set or seek author/publisher permission, analogous to the DEBCat
sample-only treatment (`TASK-0708`). Changing the committed holdout set is out of
scope for `TASK-0734` (it is scoped to licence/provenance metadata) and would
need its own task because the holdout feeds nuclear validation splits
(`TASK-0196`).

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `not_applicable` (publication-hardening metadata task);
  decision `RESTRICTIVE_ARTICLE_LICENCE_FACTS_BASIS_RETAINED`.
- **Canonical destination:** `data/DATA_LICENSES.yaml` entry update + this note.
  No data rows, results, predictions, claims, or knowledge change.
- **Review tier:** `none`. **Gate A / Gate B:** not applicable.
- **Limitations / blockers:** Springer article landing page not directly
  readable (auth redirect); licence basis established from Crossref metadata. No
  Creative Commons licence exists for this article; committed data rests on a
  facts-plus-citation basis, not an open licence.
