# FRB Reveal-Source Admissibility Contract

- Task: `TASK-0995`
- Verdict: `REVEAL_CONTRACT_READY`
- Mode: planning-only, label-blind reveal-source contract
- Frozen target source: `data/radio_transients/frb_sealed_prediction_registration_pack.yaml`

## No-Label Statement

This contract does not fetch a later catalog, open a later label surface, read
repeat status, inspect `repeater_name`, score frozen ranks, register a `PRED-*`
entry, create a result, or change any claim or knowledge artifact. It defines
the future manifest and reveal rules only.

Explicit guard: it does not read repeat status before the future reveal
manifest is frozen.

Explicit guard: it does not register a `PRED-*` entry.

The frozen prediction inputs remain the TASK-0964 score surface and the
TASK-0965 staged pack:

- target count: `479`;
- frozen score rule: `score_pre_t = log1p(E_upper_hours + E_lower_hours)`;
- fixed split epoch: `T=2019-07-02`;
- target key: pre-label `source_id` / TNS name;
- pack SHA-256:
  `0b64202b9bf8ccd37bf23bd4304e374bc10baf17f09498ad5635725eccca75e5`;
- target payload SHA-256:
  `b4b26d63b53866644332a7ffb325db30ba5f9ec5ced90833e9a4dc4d393ae2bf`.

## Admissible Reveal-Source Classes

| Source class | Admissible if | Required pins before label read |
| --- | --- | --- |
| Official CHIME/FRB catalog snapshot | The snapshot is a specific released table or archive artifact from CHIME/FRB, CADC/CANFAR, or an official companion data release; it has a release/publication date after `T`; it has enough source identity and repeat-evidence fields to label the 479 frozen targets without changing their scores. | Version, release/publication date, locator, byte size, SHA-256, citation, license/reuse note, and parser command. |
| Official CHIME/FRB repeat-source or source-association table | The table is an official released artifact that explicitly records source grouping and repeat evidence timing; it is checksumable or has an immutable archive reference. | Version, locator, checksum or immutable record id, source-id fields, repeat-evidence time fields, row-count, and license/reuse note. |
| Maintainer-approved external reveal record set | The records are citable public sources such as CHIME papers, ATels, TNS pages, or collaboration notices; each positive label has a publication timestamp strictly after `T`; the set is frozen as a manifest before scoring. | Per-record locator, access timestamp, archive snapshot when available, record checksum or immutable citation, extracted source id, and evidence timestamp. |

## Inadmissible Reveal-Source Classes

| Source class | Why it stops reveal |
| --- | --- |
| Live web search results, mutable web tables, or notebook screenshots | They are not immutable, checksum-pinned source artifacts. |
| Any source opened before the manifest freezes label columns and checksums | It violates the no-peek boundary for this reveal lane. |
| Catalog 2 full-window exposure, morphology, or completeness fields as prediction inputs | Those are forbidden post-T feature channels; reveal may read labels only, not alter scores. |
| Private communications or unarchived local notes | They are not independently reviewable. |
| Sources without publication/release date or reuse/license posture | Timing and rights cannot be audited. |
| Rows where repeat evidence is only before or at `T` | They do not reveal post-T repeater evidence for this split and must be excluded or escalated. |

## Required Future Manifest Fields

A future reveal task must freeze a manifest with these fields before reading
target labels or computing scores:

- `manifest_id`, `task_id`, `prepared_at_utc`, and maintainer approval record;
- accepted source class and reason it is admissible;
- source title, version, issuing body, publication/release date, and citation;
- source locator, access timestamp, byte size, SHA-256, and archive route;
- license/reuse note and whether raw bytes may be committed;
- parser/normalizer command, code reference, and normalized artifact checksum;
- raw row count, normalized row count, and source-id field names;
- repeat-label field names and repeat-evidence timestamp field names;
- frozen registry/pack commit, pack SHA-256, target count, and target payload SHA-256;
- deterministic source-id matching policy and alias table path, if any;
- duplicate, missing-row, ambiguous-row, and pre-T-repeat handling policy;
- allowed label-status enum and allowed metrics;
- no-peek attestation naming who froze the manifest before label inspection.

If any required field is absent or ambiguous, the reveal task must stop at
source readiness and return an explicit blocker rather than scoring.

## Source-ID Matching Policy

The frozen target key is the pre-label TNS-style `source_id` from the TASK-0963
feature surface. Matching must proceed in this order:

1. Exact source id match after whitespace trimming only.
2. Case-normalized exact match, preserving the original frozen id in output.
3. Maintainer-approved alias-table match, where every alias row records the
   frozen `source_id`, reveal-source id, source field, source row locator, and
   justification.

Forbidden matching shortcuts:

- using `repeater_name` as a pre-T feature or to rewrite frozen target ids;
- fuzzy matching by sky position after labels are visible;
- merging two frozen targets because a later source-association table groups
  them, unless a maintainer-approved alias table records the change before
  scoring;
- dropping a target silently because it is absent from the reveal source.

## Row-Loss, Duplicate, And Ambiguity Handling

Future comparison outputs must use this label-status enum:

- `POSITIVE_POST_T_REPEAT`: admissible repeat evidence exists and at least one
  repeat-evidence timestamp is strictly after `T=2019-07-02`.
- `NO_POST_T_REPEAT_EVIDENCE_AS_OF_SOURCE`: the source has an admissible row for
  the target but no admissible post-T repeat evidence as of the source version.
  This is a source-state label, not a permanent non-repeater claim.
- `UNREVEALED_MISSING`: the frozen target is absent from the pinned source.
  Missing rows are excluded from scored metrics and counted separately.
- `AMBIGUOUS_STOP`: duplicate, conflicting, or insufficient rows prevent safe
  labeling. The target is excluded from scored metrics unless a maintainer
  resolves it in a separate note.
- `PRE_T_REPEAT_EXCLUDED`: repeat evidence is present only before or at `T`.
  This does not count as a post-T reveal positive.

Duplicates must be resolved before scoring. If duplicate rows agree exactly on
source id and repeat-evidence semantics, they may collapse to one label with a
recorded duplicate count. If they disagree, the target becomes
`AMBIGUOUS_STOP`.

## Frozen Comparison Outputs And Comparators

The future reveal task may write only these comparison outputs:

- source manifest;
- no-peek attestation;
- eligibility table with one row per frozen target;
- comparison table over eligible revealed targets only;
- review note with metrics, limitations, and negative/null outcomes preserved.

The TASK-0964 scoring rule must not change. No feature may be refit, retuned,
or added after labels are visible.

Explicit guard: No feature may be refit, retuned, or added after labels are visible.

Allowed score columns:

- selected score: `log1p(E_upper_hours + E_lower_hours)`;
- frozen comparator: `log1p(E_upper_hours)`;
- frozen comparator: `log1p(E_lower_hours)`;
- frozen null comparator: `0.0`.

Allowed metrics, computed only after manifest freeze:

- revealed target count by label-status enum;
- rank AUC for selected score vs binary post-T repeat label, with tie handling
  documented;
- average precision for selected score;
- top-k positive counts for `k in {10, 25, 50}`;
- the same metrics for the frozen comparator scores and constant null.

No metric may be described as FRB predictive success unless a separate
maintainer-reviewed reveal result says so. Negative, null, partial, or
inconclusive outcomes remain valid outputs.

## Stop Conditions

Stop before scoring if:

1. the reveal source lacks a checksum, immutable archive reference, release
   date, or license/reuse note;
2. label columns or repeat-evidence timestamps were read before the manifest
   froze;
3. the source does not support post-T repeat evidence semantics;
4. target matching requires fuzzy, post-label, or unreviewed source-association
   decisions;
5. missing or ambiguous rows exceed the maintainer-approved reveal policy;
6. any score, rank, target set, or TASK-0964 formula would need to change;
7. an executor proposes claim, knowledge, discovery, or population wording
   before a reviewed reveal result.

## Output Routing

- Canonical destination: this reveal-source contract note.
- Review tier: source-readiness contract only; future reveal requires
  maintainer-approved source manifest.
- Gate A status: not applicable.
- Gate B status: not applicable.
- Prediction impact: none; no registry entry is written or scored.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: future reveal remains blocked until a checksum-pinned
  admissible source manifest exists and is approved before label inspection.
