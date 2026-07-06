# ThermoML 80-Row Bounded-Extract Maintainer Decision Packet

- Task: `TASK-0940`
- Campaign: `thermophysical-property-residuals`
- Mode: planning-only source-rights decision
- Review date: 2026-07-06
- Recommendation: `APPROVE_BOUNDED_FACTS_ROUTE`

## Decision Scope

This packet converts the `TASK-0895` verdict
`NEEDS_MAINTAINER_SOURCE_DECISION` into an exact repository decision. It
does not fetch the ThermoML archive, inspect new values, extract rows, run
Joback metrics, or change `RESULT-0026`.

The decision is limited to normal boiling temperature (`Tb`) and a maximum
public fixture of 80 curated factual rows: ten rows in each of the eight
families already represented by the committed 40-row fixture. It does not
authorize a normalized ThermoML corpus, another property, or an open-ended
extraction.

## Frozen Evidence

| Surface | Committed evidence |
| --- | --- |
| Provider | NIST Thermodynamics Research Center |
| Product | NIST TRC ThermoML Archive |
| DOI | `10.18434/mds2-2422` |
| Product version | `1.2.6` |
| Archive | `ThermoML.v2020-09-30.tgz` |
| Archive size | `189433115` bytes |
| Archive SHA-256 | `231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2` |
| Verification | Local checksum match recorded by `TASK-0851` |
| Current fixture | 40 rows, five rows in each of eight families |
| Current fixture SHA-256 | `c96b33b60fc07ef78b71a188cb931bff34d443549f0517ce198b0f5049ccdc7c` |
| Current result | `RESULT-0026`, `VALID_IN_RANGE`, unchanged |

The existing families are acids, esters/lactones, ketones,
alcohols/phenols, ethers, halocarbons, aromatic hydrocarbons, and
alkanes/cycloalkanes.

## Rights Determination

This is a repository-policy determination, not legal advice.

1. **May the source be accessed for local analysis?** Yes. The committed
   manifest records `local_analysis_allowed: yes`.
2. **May the upstream bytes be redistributed?** No. The archive and extracted
   XML/JSON trees are held by NIST with journal-publisher permission and are
   outside the repository license.
3. **May a bounded curated facts extract be published?** Yes, conditionally.
   The committed manifest and `data/DATA_LICENSES.yaml` state that numerical
   facts are extractable with attribution while source bytes are not
   re-hosted. Repository precedent also distinguishes individual measured
   facts from a source article or database artifact.

The proposed route remains bounded because it:

- fixes an 80-row ceiling before extraction;
- permits only ten rows from each already approved family;
- carries compound identity, selected source DOI/member, uncertainty, and
  archive attribution on every row;
- uses deterministic value-blind selection rather than copying a source
  table or exposing an open-ended query;
- commits neither source files nor a general normalized mirror.

On the committed evidence, this satisfies APL's facts-basis route for a
limited factual extract. It does not establish permission to redistribute the
archive, article tables, XML/JSON members, figures, or a substantial portion
of the database.

## Options

| Option | Decision | Consequence |
| --- | --- | --- |
| A | Approve bounded public extract | Permit one deterministic 80-row `Tb` fixture under the frozen contract. Recommended. |
| B | Approve local-only expansion | Permit local parsing and analysis, but commit no new value-bearing rows. |
| C | Defer or stop expansion | Keep the committed 40-row fixture as the campaign ceiling. |
| D | Request external permission | Keep the campaign metadata-only until NIST/TRC or the relevant rightsholders provide written clarification. |

## Recommended Decision

Recommend **Option A: approve the bounded public factual extract**.

The recommendation is narrow: it relies on the repository's existing
facts-basis policy, the already committed 40-row precedent, the unchanged
eight-family taxonomy, full attribution, and a hard 80-row ceiling. It does
not rely on a claim that the archive itself has an unrestricted open-data
license.

If the maintainer does not accept that distinction, Option B is the safe
fallback. Option D is appropriate only if the maintainer requires explicit
rightsholder permission beyond the repository's existing facts-basis policy.

## Exact Maintainer Selection

Select exactly one:

- [ ] **YES — Option A.** Approve one public, attributed, maximum 80-row
  `Tb` factual fixture under the frozen `TASK-0895` contract.
- [ ] **NO PUBLIC ROWS — Option B.** Approve local-only extraction and
  analysis; publish only code, metadata, hashes, and aggregate counts.
- [ ] **NO EXPANSION — Option C.** Retain the current 40-row fixture and stop
  the expansion lane.
- [ ] **DEFER — Option D.** Request external permission before any additional
  extraction.

These boxes are intentionally left for the maintainer. This task recommends a
route but does not exercise maintainer authority.

## Artifact Permission Matrix

| Artifact or action | Option A | Option B | Option C | Option D |
| --- | --- | --- | --- | --- |
| Source locator, DOI, version, size, checksum | commit | commit | retain | retain |
| Archive bytes | never commit | never commit | never commit | never commit |
| Extracted XML/JSON tree or source members | never commit | never commit | never commit | never commit |
| Extraction and validation code | commit | commit | no new work | permission-support only |
| Local normalized candidate table | temporary only | temporary only | do not create | do not create |
| New normalized factual rows | commit, maximum 80 total | never commit | never commit | never commit |
| Aggregate candidate/exclusion counts | commit | commit | optional blocker memory | permission metadata only |
| Source manifest update | required | required | optional decision record | required if rights change |
| `data/DATA_LICENSES.yaml` declaration | required for the new fixture path | metadata/local-only declaration | no new dataset entry | update only after evidence |
| Schema and deterministic regeneration tests | required | required for code/metadata outputs | none | none |
| Joback benchmark metrics | prohibited in extraction task | local-only in a later task if authorized | no run | no run |
| `RESULT-0026` modification | prohibited | prohibited | prohibited | prohibited |

Under Option A, a future extraction PR may commit only APL-authored curated
rows and their provenance. It must not commit copied table layout, article
text, source XML/JSON structure, publisher files, or archive bytes.

## Future Task Shapes

### Option A: Public Bounded Fixture

Queue one value-blind source-curation task to:

1. use only the locally held, checksum-matching version 1.2.6 archive;
2. apply the frozen identity, uncertainty, duplicate, conflict, family, and
   Joback-coverage rules from `TASK-0895`;
3. freeze candidate counts and identities before any metric is run;
4. select ten molecular-weight-quantile representatives per family;
5. commit no more than 80 rows, a fixture checksum, provenance, a
   `DATA_LICENSES.yaml` declaration, and deterministic tests;
6. stop without running metrics or editing `RESULT-0026`.

A separate benchmark task may be proposed only after that fixture is merged
and frozen.

### Option B: Local-Only Expansion

Queue one local-analysis task that may commit extractor code, schema tests,
source hashes, aggregate counts, and exclusion summaries. It must not commit
identities paired with measured values, normalized rows, candidate tables, or
archive members.

### Options C Or D

Do not queue extraction. Record the stop decision. Under Option D, reopen only
after a durable permission artifact identifies the rightsholder, scope,
allowed outputs, and attribution terms.

## Stop Conditions

Stop before extraction or publication if any of these conditions holds:

1. archive filename, size, or SHA-256 differs from the frozen source;
2. the selected maintainer option is absent or ambiguous;
3. source access occurs through a live agent fetch rather than the approved
   local snapshot;
4. the output would exceed 80 rows or add a ninth family or another property;
5. fewer than ten admissible non-conflict representatives exist in any family;
6. selection depends on Joback error, benchmark residuals, or post-score
   knowledge;
7. identity, uncertainty, source DOI/member, duplicate, or conflict metadata
   cannot be preserved;
8. archive bytes, extracted trees, source table layout, figures, or article
   text would enter Git;
9. the proposed output resembles a substantial normalized corpus;
10. `DATA_LICENSES.yaml`, attribution, provenance, regeneration tests, or
    fixture checksum are missing.

## Coordination Note

Open PR #1400 proposes maintainer Decision Day clause D2-2: if this packet
confirms a facts-basis route, the extraction lane is pre-approved; otherwise
the campaign stays metadata-only. That PR is not merged at the time of this
packet, so this document does not treat the clause as canonical task input.
If D2-2 merges unchanged, this packet supplies the requested facts-basis
confirmation, while execution still requires a separate source-curation task.

## Output Routing

- Task verdict: `not_applicable`; this is a source-rights decision packet,
  not a scientific test.
- Decision recommendation: `APPROVE_BOUNDED_FACTS_ROUTE`.
- Canonical destination:
  `docs/reviews/thermoml-80-row-bounded-extract-maintainer-decision-packet.md`.
- Review tier: `none`.
- Gate A: not attempted; no RESULT or PRED artifact is produced.
- Gate B: not applicable.
- Data impact: no archive bytes, source members, values, or rows added.
- Benchmark impact: no metric or fit run; `RESULT-0026` unchanged.
- Claim impact: none.
- Knowledge impact: none.
- Remaining authority: maintainer selects or records the applicable option;
  extraction remains a separate task.

## Limitations

- The analysis uses committed repository evidence only and performs no live
  license, terms-of-service, or rightsholder check.
- The facts-basis route is repository engineering policy, not legal advice.
- The 80-row candidate set does not yet exist and may fail family-count,
  identity, uncertainty, conflict, or Joback-coverage gates.
- No conclusion is made about whether an 80-row benchmark would reproduce
  `RESULT-0026`.
