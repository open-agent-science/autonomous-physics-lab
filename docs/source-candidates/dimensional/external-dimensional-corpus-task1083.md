# External Dimensional Corpus Source Scout

Task: `TASK-1083`
Scope: source admissibility only
Review date: 2026-07-23

## Verdict

`LABEL_SEMANTICS_BLOCKED`

No candidate is selected. The five-source slate contains useful equation,
unit, and answer-key resources, but none exposes an independently authored
item-level target compatible with the prospective
`VALID` / `INVALID` / `INCONCLUSIVE` relation-classification interface.

No formulas, labels, publisher files, dataset rows, or source bytes were
copied. The APL validator was not run, no item-level APL predictions or
historical answers were inspected, and no benchmark score was produced.

## Admission Gate

A route must clear every condition before a later curation task may copy or
transform item content:

1. A stable source identity, explicit provenance, and a version or immutable
   retrieval route are available.
2. At least 80 formula relations, or a defensible pre-extraction route to that
   count, include complete variable-dimension declarations.
3. An independently authored answer key maps each relation to dimensional
   agreement. A collection containing only accepted physical equations is not
   a useful dimensional classifier benchmark because an always-`VALID`
   baseline would be sufficient.
4. At least five physics domains can be identified without deriving domain or
   answer labels from APL output.
5. SI and natural-unit conventions are explicit enough to apply the scope in
   the
   [external curator interface](../../dimensional-validator-external-curator-interface.md).
6. Reuse terms cover the intended artifact. A software license is not assumed
   to license third-party textbook, examination, or dataset content.

The ambiguity-rate denominator is zero for this scout because zero items were
admitted. Candidate ambiguity is therefore recorded as `not measurable`, not
as zero ambiguity. A later route may report a rate only after an independently
labelled, rights-cleared package is frozen.

## Candidate Ledger

| Candidate | Stable identity and scale | Formula / dimension schema | Independent label semantics | Coverage and unit scope | Rights posture | Duplicate / ambiguity risk | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Feynman Symbolic Regression Database (FSReD) | [AI Feynman article](https://doi.org/10.1126/sciadv.aay2631), [MIT dataset page](https://space.mit.edu/home/tegmark/aifeynman.html), and code commit [`a05bc4a`](https://github.com/SJ001/AI-Feynman/commit/a05bc4a5be23d6eb3e1d0b2f7eb1ab5b78a920ad). The article describes 100 primary mysteries plus 20 bonus mysteries. | Each mystery has a target equation, numerical table, and unit vectors over metre, second, kilogram, kelvin, and volt. This is close to the needed source schema, but it is not a complete APL SI declaration and requires special review of derived-unit and natural-unit conventions. | The equations are independent answer keys for symbolic regression, but they are accepted equations only. There are no independently labelled dimensionally invalid or inconclusive relations. Creating mutations would make APL the label author. | The paper intentionally samples broad Feynman-Lectures physics and clears the count floor, with mechanics, electromagnetism, quantum physics, and other topics. Five-domain mapping remains metadata work, not a blocker by itself. | The code repository is MIT. The article is CC BY-NC 4.0, while the dataset page says the database is freely downloadable but does not expose a versioned dataset license or checksum. Treat corpus bytes as locator-only pending a rights decision. | Very high family overlap with AI Feynman, PMLB, and SRBench derivatives; a separate blinded structural-overlap review would be mandatory. Ambiguity rate: not measurable because no class-labelled rows exist. | Reject: best structural match, but one-class answer semantics cannot exercise dimensional classification. |
| VerityMath Unit Consistency Programs | [OpenReview paper](https://openreview.net/forum?id=S9utaRXaZt) and official repository commit [`7af1b73`](https://github.com/vernontoh/VerityMath/commit/7af1b7333ca78b3a05835b65ca9b5c8f02832fbd). The paper reports 4,480 generated UCPs from GSM8K. | Word problems are paired with executable programs containing quantity-unit declarations and unit assertions. They are not single symbolic physics relations with complete variable-to-SI-dimension declarations. | The repository documents GPT-generated programs and a separate generated yes/no classification task. Those labels answer whether a word problem needs a unit check, not whether a supplied relation is dimensionally valid. | The inherited GSM8K surface is grade-school arithmetic rather than five physics domains. Everyday units and counts do not define a natural-unit policy. | The repository has no detected license and no release. GSM8K provenance would also need to be carried through any derivative package. No redistribution route is admitted. | High template and source overlap within GSM8K-derived corpora. Program-generation failures make a dimensional ambiguity rate unavailable without a new audit. | Reject: wrong target semantics, wrong domain surface, and unresolved reuse terms. |
| UnitMath over SciTab | [OpenReview submission `OG8sFxeNHv`](https://openreview.net/forum?id=OG8sFxeNHv), revision dated 2025-10-20 with a CC BY 4.0 paper and supplementary archive. | The system evaluates natural-language claims against scientific tables and performs numeric extraction, conversions, tolerance matching, and some dimensional refusal checks. The underlying rows are table claims, not standalone formula relations with declared variable dimensions. | SciTab entailment labels and UnitMath stress checks concern table-claim verification. They do not provide the prospective dimensional labels, and the source does not establish 80 independently labelled physics formula relations. | Scientific tables are multidisciplinary; the source does not establish five physics domains or a consistent SI-versus-natural-unit boundary for eligible formula rows. | The paper is CC BY 4.0. The supplementary archive and inherited SciTab content require an artifact-level license review before any redistribution; this scout keeps them locator-only. | Claims may repeat source-table facts and derived unit-rescaling variants. The eligible-item denominator and ambiguity rate are not measurable from source metadata. | Reject: unit-aware verification is adjacent, but the item and label contracts are different. |
| OlympiadBench | [ACL 2024 paper](https://doi.org/10.18653/v1/2024.acl-long.211), official repository commit [`ba5b26a`](https://github.com/OpenBMB/OlympiadBench/commit/ba5b26a7e2849940b598a9159c1190daa2b9175f), and [dataset card](https://huggingface.co/datasets/Hothan/OlympiadBench). The project reports 8,476 mathematics and physics problems. | Rows provide question, solution, final answer, optional answer unit, answer type, and subfield. They do not provide one relation plus complete dimensions for every variable. | Official numerical or proof answers are independent, but correctness of a solved problem is not a dimensional-consistency label. Deriving relation labels from solutions would be new curation. | Physics partitions are large enough to investigate, but the published schema does not establish five usable dimensional domains or an SI-only boundary. Competition physics may mix SI, non-SI, and convention-dependent notation. | The GitHub repository identifies MIT while the hosted dataset card identifies Apache-2.0. The corpus was OCR-curated from olympiad and examination PDFs, so those top-level licenses do not by themselves resolve upstream problem rights. Locator-only at most. | The authors report deduplication, but public competition problems still carry contamination and formula-family overlap risk. Dimensional ambiguity rate is not available. | Reject: answer keys exist, but neither the schema nor the answers label dimensional agreement; upstream rights also need adjudication. |
| OpenStax University Physics, Volumes 1-3 | [Volume 1 canonical record](https://openstax.org/details/university-physics-volume-1), published 2016, ISBN 978-1-947172-20-3, representing the three-volume calculus-based sequence. | The books contain equations, worked checks, and an explicit dimensional-analysis section, but not a machine-readable relation / variable-dimension / class-label schema. | A small number of exercises explicitly ask about dimensional consistency. The broader equation inventory is reviewed textbook content but does not independently label each equation for this classification task. | The three volumes span mechanics, waves, thermodynamics, electromagnetism, optics, and modern physics. The explicit dimensional-question subset has no defensible route to 80 items without APL-authored extraction and labels. SI is central, while non-SI examples and modern-physics conventions would require filtering. | Current OpenStax pages state CC BY-NC-SA 4.0 terms and prohibit ingestion into generative-AI offerings without permission. No content was ingested or copied; any future use needs an explicit maintainer rights decision and attribution plan. | Standard textbook equations are likely to overlap many educational and APL formula families. Ambiguity rate is not measurable without prohibited item curation. | Reject: broad domain coverage, but insufficient independently labelled dimensional items and restrictive reuse conditions. |

## Why The Closest Route Still Stops

FSReD is the only candidate that simultaneously clears the nominal count,
physics breadth, equation-answer, and unit-metadata gates. It nevertheless
cannot support a meaningful classification benchmark as published:

- every released target is an accepted equation;
- no independent `INVALID` controls are supplied;
- no independent `INCONCLUSIVE` boundary cases are supplied;
- manufacturing malformed variants would transfer label authorship to APL;
- scoring such a package would reward a constant `VALID` predictor.

The route therefore cannot be repaired by a schema adapter. It needs a
different independently labelled source, not a later transformation of the
same equations.

## Retrieval And Checksum Plan

No bytes are fetched by this task. If a future source clears label semantics,
use the following bounded acquisition policy:

| Candidate | Immutable or version pin | Future checksum action | Permitted posture now |
| --- | --- | --- | --- |
| FSReD | Article DOI plus exact named archive from the MIT page and repository commit `a05bc4a5be23d6eb3e1d0b2f7eb1ab5b78a920ad` | Record final URL, retrieval timestamp, byte length, and SHA-256 for every archive before extraction. | Locator-only; dataset rights and label semantics unresolved. |
| VerityMath | Repository commit `7af1b7333ca78b3a05835b65ca9b5c8f02832fbd` | If rights are granted, checksum a GitHub commit archive and each separately retrieved annotation artifact. | Metadata only; no repository license. |
| UnitMath | OpenReview forum id, paper revision date, and exact supplementary-archive URL | Pin the OpenReview revision, then record archive byte length and SHA-256; separately identify inherited SciTab bytes and license. | Locator-only pending contained-artifact review. |
| OlympiadBench | ACL DOI plus repository commit `ba5b26a7e2849940b598a9159c1190daa2b9175f` and an exact hosted-dataset revision | Record independent hashes for the repository archive and hosted dataset snapshot; retain source partition identifiers. | Locator-only pending upstream-rights and license-mismatch review. |
| OpenStax | Canonical book record, ISBN, volume, edition/revision identity, and exact PDF URL | Record the displayed license/revision with retrieval time, then checksum each volume only after permission review. | Citation locator only; no content ingestion or redistribution. |

## Required Schema Gap

The future package must provide these independently sourced fields before APL
execution:

```text
external_item_id
relation
variable_dimensions_si
label: VALID | INVALID | INCONCLUSIVE
physics_domain
dimensional_rationale
source_locator
source_version
reuse_classification
unit_scope
```

None of the five candidates publishes that complete contract. FSReD supplies
the first three fields for accepted equations but not a non-trivial label
surface. OlympiadBench and VerityMath supply independent answers to different
questions. UnitMath supplies table-claim labels. OpenStax supplies reviewed
instructional prose and answers but no corpus-level schema.

## Stop Rule And Follow-Up Boundary

Do not open a curation, adapter, mutation, overlap, or scoring task for these
five candidates under the current interface. Reconsider only when a new
primary source exposes:

- at least 80 relations with independent item-level dimensional labels;
- at least one non-trivial negative or boundary stratum;
- complete variable dimensions;
- five physics domains;
- stable version and explicit dataset reuse terms.

A source with only valid equations may still be useful for symbolic regression
or formula discovery, but it is not the external dimensional-classification
route requested here.

## Limitations

This was a source-metadata audit, not a row audit. Candidate item counts were
used only where the primary project or paper states them. No ambiguity
percentage, usable-row count, class balance, or overlap count is inferred from
uninspected data. Current web license statements can change, so a future
acquisition must repeat the rights check against the exact pinned artifact.

## Output Routing

- Canonical destination: this source-candidate adjudication.
- Selected source manifest: none.
- Dataset impact: none; no formulas, labels, or source bytes were added.
- Review tier: none; no `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*` artifact
  is produced.
- Gate A / Gate B: not attempted and not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: no candidate provides an independently authored,
  non-trivial dimensional-class label surface with the required schema,
  coverage, versioning, and rights.

This source verdict does not validate, invalidate, or measure the APL
dimensional engine.
