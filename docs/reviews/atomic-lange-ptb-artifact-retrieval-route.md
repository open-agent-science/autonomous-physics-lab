# Atomic Lange/PTB Artifact Retrieval Route

**Task:** `TASK-0669`  
**Campaign:** Atomic-Clock Residuals  
**Source ID:** `ACLOCK-SRC-CANDIDATE-2021-LANGE-PTB-YBPLUS`  
**Verdict:** `METADATA_ONLY_UNTIL_MAINTAINER_LICENSE_APPROVAL`

## Scope

This review decides the artifact-retrieval route for the Lange/PTB Yb+ source
candidate after `TASK-0652` pinned its bibliographic metadata. It does not
download files, checksum a PDF, transcribe clock values, add `acr-*.yaml` rows,
fit constants drift, compare sources, or promote claims.

The decision applies only to artifact retrieval and reuse. It does not change
the scientific classification from the preflight: Lange/PTB remains a separate
Yb+ E3/Cs and E3/E2 source family, not a Yb/Sr benchmark unblocker.

## Inputs Reviewed

- `docs/reviews/atomic-lange-ptb-source-artifact-preflight.md`
- `data/atomic_clocks/source_manifest.yaml`
- `docs/fresh-data-intake-protocol.md`
- `docs/campaigns/atomic-clock-residuals.md`
- arXiv license page for `nonexclusive-distrib/1.0`
- arXiv record `2010.06620`

## Source Surfaces

| Surface | Locator | Route decision |
| --- | --- | --- |
| arXiv abstract | `https://arxiv.org/abs/2010.06620` | metadata locator remains committed |
| arXiv PDF | `https://arxiv.org/pdf/2010.06620` | do not commit yet; maintainer license approval required |
| arXiv license | `https://arxiv.org/licenses/nonexclusive-distrib/1.0/license.html` | grants arXiv a non-exclusive distribution license; not treated as a blanket third-party redistribution grant |
| Publication of record | `10.1103/PhysRevLett.126.011102` | DOI/citation only; publisher PDF is not redistributable here |

The arXiv record exposes the submitted and revised versions, journal reference,
related PRL DOI, and PDF/TeX source links. Those locators are stable enough for
metadata-only provenance. They are not enough to commit the PDF without a
license decision because the default arXiv non-exclusive distribution license
is a license to arXiv, not a repository redistribution license.

## Repository Precedent

The Atomic manifest already contains arXiv preprint artifacts for Beloy and
Nemitz with `license_note: arXiv_perpetual_licence_for_committed_preprint`.
Those entries are preserved as historical repository state. `TASK-0669` does
not reinterpret or rewrite them.

For Lange/PTB, the safer current route is:

`metadata-only until maintainer license approval`

This avoids broadening the prior arXiv artifact posture without an explicit
maintainer decision, especially because Lange/PTB is not on the critical Yb/Sr
benchmark unblock path.

## Decision

`METADATA_ONLY_UNTIL_MAINTAINER_LICENSE_APPROVAL`

Do not commit the Lange/PTB arXiv PDF or TeX source in the next task by default.
Keep the existing metadata-only manifest entry and add this review as readiness
evidence. A future task may retrieve and checksum an artifact only if the
maintainer explicitly approves one of these routes:

1. **Repository-copy route:** commit an arXiv PDF copy with a checksum and
   explicit maintainer approval note.
2. **Locator-only route:** keep the source metadata-only forever and require
   future extraction reviews to cite the arXiv locator without committing a
   source file.
3. **External archive route:** use a separate archive or institutional copy
   only if its reuse terms are clearer than the default arXiv license.

Until then, Lange/PTB remains a source candidate, not a source artifact.

## Required Shape If Artifact Commit Is Later Approved

If a later maintainer-approved task chooses the repository-copy route, it should
create:

```text
data/atomic_clocks/source_artifacts/2021-lange-ptb-ybplus/
  README.md
  provenance.yaml
```

The `provenance.yaml` must record at least:

- `source_id: ACLOCK-SRC-CANDIDATE-2021-LANGE-PTB-YBPLUS`
- `task_id` for the retrieval task
- arXiv id and version, preferably `2010.06620v2`
- arXiv abstract URL and PDF URL
- license URI and maintainer approval note
- retrieval date in UTC
- checksum algorithm and SHA-256 digest for every committed file
- checksum scope, for example `arxiv_preprint_pdf`
- publication-of-record DOI and `redistributable_here: false`
- statement that no clock values are transcribed by the artifact task

The source manifest should then change `value_status` only to
`source_artifact_pinned_no_values`; it must not become a value-bearing dataset
entry until a separate extraction and row-curation task passes review.

## Scientific Boundary

Lange/PTB is valuable as an alternate high-precision fresh-data path because it
comes from PTB and covers Yb+ E3/Cs plus E3/E2 quantities. It still does not
carry a Yb/Sr row. Therefore:

- it does not unblock the first Yb/Sr benchmark;
- it should not be compared against Beloy, Nemitz, or Pizzocaro in this task;
- it should not be used for constants-drift fitting;
- it should not produce a result, claim, prediction, or knowledge promotion.

## Output Routing Summary

- Task verdict: `METADATA_ONLY_UNTIL_MAINTAINER_LICENSE_APPROVAL`.
- Canonical destination:
  `docs/reviews/atomic-lange-ptb-artifact-retrieval-route.md` plus a
  metadata-only manifest/campaign-note update.
- Review tier: none.
- Gate A status: not attempted; no result or prediction artifact.
- Gate B status: not applicable.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Dataset impact: no `acr-*.yaml` rows or source files added.
- Publication blocker: maintainer license approval is required before any
  Lange/PTB arXiv artifact is committed.
