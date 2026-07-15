# TASK-1031 clean official-metadata source scout

## Scope

This note records the clean-session retry required by TASK-1031. It is limited
to source identity, release timing, rights metadata, retrieval identity, and
checksum feasibility. It contains no target list, target-status assessment,
measured values, table content, prediction values, matching, or scores.

## Executor independence record

- Contributor ID: `akutenyov`
- GitHub username: `akutenyov`
- Agent tool/model: Codex / GPT-5
- Session identity: `019ec659-8105-71c3-aecb-1b1258f52b12`
- Session started as a fresh context for TASK-1031.
- Pre-browse attestation was recorded before network access: the executor had
  not seen the TASK-1023 target-bearing snippets, candidate target values,
  PRED-0063..PRED-0068 contents, or target/value-bearing files.
- A local directory name, `.review-temp-1031-long`, appeared during initial
  filesystem inventory. Its contents were not opened.
- The old PR #1560 body, diff, files, review discussion, and branch contents
  were not read or reused.
- During required protocol reading, generic checklist prose exposed a few
  example identifiers, but no values or measured-status information. They were
  not used for queries or matching.
- No target value or target status was exposed during this scout.

## Method and admissibility boundary

The scout used only direct official metadata surfaces:

1. IAEA Nuclear Data Services' Atomic Mass Data Center landing page.
2. The Atomic Mass Data Center's IMP landing page.
3. Direct DOI links exposed by the IAEA page.
4. Crossref registrar records restricted to bibliographic fields:
   title, DOI, publisher, publication date, license URL, record creation time,
   work type, and DOI URL.
5. Date-bounded Crossref metadata checks from 2026-05-21 through 2026-07-16
   using only generic phrases about nuclear or atomic mass measurement.
6. Structured `href` metadata from the IAEA landing page to establish a
   future checksum route without fetching linked files.

The scout did not use general web search, search-result snippets, AI summaries,
cached previews, target-name queries, PDFs, article text, tables, ASCII data
payloads, archive payloads, or target matching. The ANL official mirror returned
HTTP 403 to the automated metadata client and was not used as evidence.

Access timestamp: `2026-07-15T22:15:05Z`.

## Direct official source records

| Source title | Issuing body / source class | Release date | Locator | Rights / reuse metadata | Retrieval and checksum assessment |
| --- | --- | --- | --- | --- | --- |
| The AME 2020 atomic mass evaluation (I). Evaluation of input data, and adjustment procedures | Atomic Mass Data Center; IOP Publishing; `official_evaluation` | 2021-03-01 | DOI `10.1088/1674-1137/abddb0`; IAEA AMDC landing page | Crossref records CC BY 3.0 for the journal article. The IAEA page instructs users to cite the papers. Raw-file redistribution terms are not stated on the landing page. | DOI identity is stable. No payload was fetched. |
| The AME 2020 atomic mass evaluation (II). Tables, graphs and references | Atomic Mass Data Center; IOP Publishing; `official_evaluation` | 2021-03-01 | DOI `10.1088/1674-1137/abddaf`; IAEA AMDC landing page | Crossref records CC BY 3.0 for the journal article. The IAEA page instructs users to cite the papers. Raw-file redistribution terms are not stated on the landing page. | The landing page exposes `https://www-nds.iaea.org/amdc/ame2020/mass_1.mas20.txt`. No payload was fetched and no digest was computed. A later approved task could retrieve the exact locator once and record file size plus SHA-256. |
| The NUBASE2020 evaluation of nuclear physics properties | Atomic Mass Data Center; IOP Publishing; `official_evaluation` | 2021-03-01 | DOI `10.1088/1674-1137/abddae`; IAEA AMDC landing page | Crossref records CC BY 3.0 for the journal article. The IAEA page instructs users to cite the papers. Raw-file redistribution terms are not stated on the landing page. | The landing page exposes a stable-looking ASCII locator, but no payload was fetched and no official digest was displayed. |

Official metadata pages:

- `https://www-nds.iaea.org/amdc/`
- `https://amdc.impcas.ac.cn/`
- `https://doi.org/10.1088/1674-1137/abddb0`
- `https://doi.org/10.1088/1674-1137/abddaf`
- `https://doi.org/10.1088/1674-1137/abddae`

## Timing, rights, and checksum decision

The repository protocol records the relevant freeze on 2026-05-20. Repository
history independently shows the registry wave was added on 2026-05-20. All
three official evaluation records above were released on 2021-03-01 and
therefore predate registration by more than five years.

The date-bounded Crossref registrar checks found no post-freeze record whose
title metadata established an official nuclear-mass measurement or evaluation
source suitable for this reveal surface. Records identifiable from title
metadata as theory, prediction, modeling, or unrelated measurements were not
opened and were not promoted as candidates.

The IAEA route makes future checksum capture technically feasible, but no
checksum was computed because downloading a value-bearing payload is forbidden
in this task. Article-license metadata does not by itself establish
redistribution rights for the linked raw files. These limitations do not
override the earlier timing failure.

A candidate source-manifest scaffold is not created: the official source
identity fails the post-registration timing gate.

## Stop conditions and no-value attestation

The executor would stop immediately on any target value or target-status
exposure. No such exposure occurred. No source payload was downloaded, no
target identifier was queried, no source row was inspected, and no target was
classified as measured or unmeasured. No PRED, RESULT, CLAIM, or KNOW artifact
was modified or created.

## Verdict

`SOURCE_PREDATES_REGISTRATION`

This is the single TASK-1031 source-readiness verdict. It is not a scientific
result and does not authorize a reveal, target matching, or scoring.

## Output routing

- Task verdict: `SOURCE_PREDATES_REGISTRATION`
- Canonical destination: this metadata-only review note
- Review tier: `none`
- Gate A status: not attempted
- Gate B status: not attempted
- Claim impact: no claim change
- Knowledge impact: no knowledge change
- Prediction impact: no prediction mutation
- Result impact: no result artifact
- Publication blocker: no admissible post-registration official source was
  identified; the available official evaluation sources predate registration
- Allowed next step: a future fresh metadata-only scout after a new official
  release, or maintainer review of this timing decision
