# TASK-1025: CHARA identifier and whole-system alias audit

## Scope and freeze

This audit completes the identifier-complete alias and whole-system de-dup
step required by
[chara-value-blind-source-artifact.md](./chara-value-blind-source-artifact.md)
(TASK-0989) before any CHARA stellar row curation. It audits exactly the
thirteen candidates left after TASK-0989's two explicit DEBCat exclusions
(HD 224355 and HD 185912). The work is identifier-only and value-blind: no
mass, luminosity, radius, temperature, orbit, parallax, residual, or
model-performance value was read, transcribed, normalized, summarized, or
committed, and no metric, fit, RESULT, CLAIM, or knowledge artifact was
created or changed.

Frozen comparison surface (recorded before any matching):

| Property | Value |
| --- | --- |
| Path | `data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml` |
| File SHA-256 | `7e8fe4a2359f53f7fd7c80cdba5f56dc024fa45f985879d3faecb8bc8398db08` |
| Last commit touching file | `c16d97e07f5a8d01b2481c3350b0574871ac0d9c` (2026-06-19) |
| Branch base at audit time | `3eb4d8603901611e5c5caaa513ce95679fd9f237` |
| System identifiers | 373 (from 748 component rows) |
| Exclusion unit | whole physical system |

Only the `system_id` field of each component row was extracted for the
comparison list; value fields were never parsed.

## Alias lookup identity and pinning

All alias and hierarchy evidence comes from pinned SIMBAD TAP responses
(service `https://simbad.cds.unistra.fr/simbad/sim-tap/sync`, `format=text`,
access date `2026-07-13`). For each queried identifier the audit ran one
alias query (all identifiers of the resolved object) and one hierarchy query
(all `h_link` parents/children), with exact ADQL templates recorded in the
committed ledger. Raw response bytes are held in a temporary, uncommitted
cache; each response's SHA-256 is recorded in
[chara_alias_audit_ledger.yaml](../../../data/textbook_formula_audit/stellar_ml/chara_alias_audit_ledger.yaml),
following the same pin-without-vendoring pattern as TASK-0989. A single
additional pinned query recorded each candidate's SIMBAD `main_id` and `oid`
and confirmed one-to-one identity resolution (13 queried identifiers, 13
distinct objects). SIMBAD content used here is limited to object identifiers
and hierarchy links (facts), with CDS acknowledgement recorded in the ledger.

Matching used one recorded deterministic normalization applied to both sides
(strip whitespace/quotes; drop a leading GCVS `V* ` prefix; uppercase; remove
all spaces and underscores). No coordinate-proximity, fuzzy, or value/model
similarity matching was used anywhere.

Positive controls: the two known TASK-0989 overlaps were re-queried through
the identical pipeline and both were detected, so a null result on the
thirteen candidates is not a silent-pipeline artifact.

| Control | Expected DEBCat system | Pipeline result |
| --- | --- | --- |
| HD 224355 | `V1022_Cas` | matched via alias `V* V1022 Cas` — PASS |
| HD 185912 | `V1143_Cyg` | matched via alias `V* V1143 Cyg` — PASS |

## Candidate-by-candidate ledger

Full identifier-complete alias lists, per-response digests, hierarchy links,
and per-candidate reasons are in the committed ledger; this table is the
decision summary. "Siblings checked" are WDS/CCDM co-components of the same
physical system whose own pinned alias sets were also intersected against
DEBCat (whole-system rule).

| Candidate | Paper surface | SIMBAD main_id | GCVS designation | Cluster membership (h_link) | Sibling checked | DEBCat match | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HD 8374 | CHARA III | * 47 And | none | none | — | null | `INDEPENDENT_CANDIDATE` |
| HD 24546 | CHARA III | * 43 Per | none | none | WDS J03566+5042B | null | `INDEPENDENT_CANDIDATE` |
| HD 61859 | CHARA IV | HD 61859 | none | none | — | null | `INDEPENDENT_CANDIDATE` |
| HD 89822 | CHARA IV | V* ET UMa | ET UMa | none | — | null | `INDEPENDENT_CANDIDATE` |
| HD 109510 | CHARA IV | * 24 Com B | none | none | WDS J12351+1823A | null | `INDEPENDENT_CANDIDATE` |
| HD 191692 | CHARA IV | * tet Aql | none | none | WDS J20113-0049B | null | `INDEPENDENT_CANDIDATE` |
| HD 27483 | Hyades six | HD 27483 | none | Melotte 25; Hyades MG | — (pair `** BAS 3` merged into same entry) | null | `INDEPENDENT_CANDIDATE` |
| HD 283882 | Hyades six | V* V808 Tau | V808 Tau | Melotte 25; Hyades MG | WDS J04492+2448B | null | `INDEPENDENT_CANDIDATE` |
| HD 26874 | Hyades six | HD 26874 | none | Melotte 25 | WDS J04157+2049B | null | `INDEPENDENT_CANDIDATE` |
| HD 27149 | Hyades six | V* V1232 Tau | V1232 Tau | Melotte 25; Hyades MG | — | null | `INDEPENDENT_CANDIDATE` |
| HD 30676 | Hyades six | HD 30676 | none | Melotte 25 | — | null | `INDEPENDENT_CANDIDATE` |
| HD 28545 | Hyades six | HD 28545 | none | Melotte 25 | WDS J04306+1542A | null | `INDEPENDENT_CANDIDATE` |
| HD 284163 | MNRAS stad3803 | HD 284163A | V1136 Tau | Melotte 25 | WDS J04119+2338B | null | `INDEPENDENT_CANDIDATE` |

Component-hierarchy notes recorded from pinned responses:

- HD 284163 resolves to the `A` component entry (`WDS J04119+2338A`, close
  pair `Aa,Ab`, `** CHR 14`/`** SKF 2409A`), which also carries the paper's
  aliases `BD+23 635`, `Cl* Melotte 25 PELS 20`, and `V* V1136 Tau`; the
  wider `B` companion entry was separately checked against DEBCat (null).
- HD 109510 is itself the `B` component of `WDS J12351+1823` (`ADS 8600 B`);
  the `A` component entry was separately checked against DEBCat (null).
- HD 28545 is itself the `B` component of `WDS J04306+1542` (`** BUP 62B`);
  the `A` component entry was separately checked against DEBCat (null).
- All thirteen candidates carry `SBC9` spectroscopic-binary identifiers
  except HD 30676, whose binarity is asserted by the paper surface only; this
  is identifier-level context, not a value statement.

Notable identifier corrections this audit makes durable: HD 283882's GCVS
designation is `V808 Tau` (DEBCat's `V1236_Tau` is a different system), and
HD 27149 is `V1232 Tau` (DEBCat's `V1229_Tau` and `V1236_Tau` are different
systems). Neither intersects the frozen DEBCat list.

## Counts and verdict

| Quantity | Value |
| --- | ---: |
| Candidates audited | 13 |
| Identity unresolved or conflicting | 0 |
| Hierarchy-ambiguous identities | 0 |
| Stable DEBCat alias intersections (whole-system) | 0 |
| Sibling component entries additionally checked | 7 |
| Positive controls passed | 2 / 2 |
| Eligible independent systems after audit | 13 |
| Value rows extracted | 0 |
| Metrics or fits run | false |
| Result/claim mutations | 0 |

**Verdict: `ALIAS_AUDIT_READY_FOR_ROW_CURATION`.** All thirteen
post-exclusion CHARA candidates resolve to single, stable SIMBAD identities;
none of their identifier-complete alias sets (nor any checked co-component's
alias set) intersects the frozen 373-system DEBCat surface. The candidates
remain candidates only: this audit does not make them a benchmark, holdout,
or evidence about any mass-luminosity formula.

## Limitations

- SIMBAD is a living database; alias sets are pinned by access date and
  response digest, not by an upstream version number. A future row-curation
  task should re-verify digests only if it needs to re-query.
- The audit trusts SIMBAD's identifier cross-matching. A DEBCat system whose
  committed `system_id` is not linked to a candidate in SIMBAD's `ident`
  table would be missed; this residual risk is shared with TASK-0989 and is
  mitigated by checking all 373 DEBCat spellings against complete alias sets
  (including 2MASS, Gaia DR3, TYC, TIC, HD, HIP, HR, BD forms).
- Seven of thirteen candidates are Melotte 25 (Hyades) members per pinned
  hierarchy links. They are physically distinct systems from every DEBCat
  entry, but they are not statistically independent draws of environment or
  chemistry; the future benchmark-split design must treat cluster membership
  explicitly (including possible cluster overlap with DEBCat systems, which
  this identifier audit does not assess).
- Multiplicity identifiers (WDS/CCDM/SBC9) are recorded as facts; whether a
  wide co-component contaminates published photometry or dynamics is a
  row-curation question, not an identifier question, and remains open.
- The `** BAS 3` pair designation for HD 27483 has no separate component
  entries in SIMBAD, so no sibling entry existed to check; the whole-system
  rule was applied to its single merged entry.

## Bounded future row-curation task shape

Because the verdict is ready, the next bounded task may:

1. re-pin the six TASK-0989 paper artifacts and the supplement bytes for
   HD 284163 (`stad3803_supplemental_file.zip`) before reading any table;
2. extract per-component rows for exactly the thirteen ledger systems,
   recording per-row source location, component mapping against the ledger's
   hierarchy notes, and uncertainty semantics;
3. keep DEBCat leakage closed by re-running this ledger's intersection on
   the extracted row identifiers (fail-closed on any new alias);
4. stop before any benchmark split, M-L scoring, exponent fitting, or
   formula wording — split design and scoring remain separate tasks.

## Output routing

- Task verdict: `not_applicable` (source-readiness audit; the audit-level
  outcome is `ALIAS_AUDIT_READY_FOR_ROW_CURATION`).
- Canonical destination: this review note plus the identifier-only ledger
  under `data/textbook_formula_audit/stellar_ml/`; no `agent_runs/`,
  `results/`, `prediction_registry/`, `claims/`, or `knowledge/` artifact.
- Review tier: none (source-readiness documentation; maintainer closeout is
  `closeout: review` per task YAML).
- Gate A: not attempted (no publishable RESULT/PRED is produced).
- Gate B: not attempted (no replayable metric exists at this stage).
- Claim impact: no claim change.
- Knowledge impact: no knowledge change; the row-curation follow-up remains
  a maintainer decision.
- Publication blockers: none for this audit itself; value extraction stays
  blocked until a maintainer-approved row-curation task exists, and the
  HD 284163 supplement bytes remain unpinned.
