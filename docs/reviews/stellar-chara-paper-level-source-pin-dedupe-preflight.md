# Stellar CHARA Paper-Level Source Pin And DEBCat De-dup Preflight

- Task: `TASK-0939`
- Campaign: `textbook-formula-audit` / Stellar M-L
- Mode: planning-only, value-blind source readiness
- Review date: 2026-07-06
- Verdict: `PAPER_LEVEL_PIN_READY`

## Scope

This preflight asks whether the CHARA spectroscopic-binary and Hyades-orbit
route can be pinned paper by paper and screened deterministically against the
committed DEBCat systems before any future row curation. It does not fetch or
transcribe mass, luminosity, parallax, radius, temperature, orbit, or
photometry values. It does not run an M-L metric or edit `RESULT-0022` or
`RESULT-0024`.

The decision is about source-artifact readiness only. A positive verdict does
not mean that a benchmark-ready independent dataset exists.

## Evidence Boundary

The preflight inspected publication metadata, primary or author-hosted landing
pages, licence statements, paper titles and target identifiers, the prior
`TASK-0928` scout, and the committed DEBCat identifier surface. No
value-bearing source table was downloaded or committed.

The frozen DEBCat comparison surface is:

- path: `data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml`
- SHA-256: `7e8fe4a2359f53f7fd7c80cdba5f56dc024fa45f985879d3faecb8bc8398db08`
- source snapshot policy: committed normalized rows from the TASK-0763
  permission route; both components share one `system_id`

## Candidate Paper Surfaces

| Surface | Stable locator | Table/source route visible at preflight | Rights posture | Future checksum plan | Preflight role |
| --- | --- | --- | --- | --- | --- |
| CHARA Visual Orbits I, `HD 224355` | DOI `10.3847/1538-3881/ab064d`; arXiv `1902.05557`; CHARA journal index | Article/PDF tables; no stable publisher machine-readable-table URL pinned here | 2019 AAS article states all rights reserved; local inspection only, no byte redistribution | Pin the DOI landing metadata and one author-hosted or arXiv artifact at first licence-clear fetch; record byte count and SHA-256 | Known DEBCat-overlap control |
| CHARA Visual Orbits II, `HD 185912` | DOI `10.3847/1538-3881/ab449d`; arXiv `1909.09161`; CHARA-hosted PDF | Article/PDF tables; no stable publisher machine-readable-table URL pinned here | 2019 AAS article states all rights reserved; local inspection only, no byte redistribution | Same per-paper locator, byte-count, and SHA-256 rule as Paper I | Known DEBCat-overlap control |
| CHARA Visual Orbits III, `HD 8374` and `HD 24546` | DOI `10.3847/1538-3881/ab8f95`; arXiv `2005.00546`; CHARA-hosted PDF | Article tables and primary paper artifact; machine-readable endpoint remains to be verified | 2020 AAS article states all rights reserved; no source-byte vendoring | Pin article/preprint bytes separately; a publisher table, if admitted, receives its own checksum and licence decision | Candidate paper-level source |
| CHARA Visual Orbits IV, four named HD systems | DOI `10.3847/1538-3881/ac9385`; arXiv `2209.09993`; Exeter/NSF public record | Article tables and public repository copy; no aggregate CHARA snapshot | CC BY 4.0 on the article; attribution required | Pin DOI metadata plus the exact admitted repository or publisher artifact; checksum every file independently | Candidate paper-level source |
| CHARA Hyades six-system paper | DOI `10.3847/1538-4357/ad54b2`; arXiv `2406.01674` | Article tables expose identifiers and source metadata; no single reusable aggregate snapshot was found | CC BY 4.0 on the article; attribution required | Pin the version-of-record or admitted preprint and any separate table artifact independently | Candidate cluster-orbit source |
| CHARA Hyades `HD 284163` paper | DOI `10.1093/mnras/stad3803`; arXiv `2312.05301`; Oxford Academic landing page | Article plus explicitly declared online supplementary material | CC BY 4.0; attribution required | Pin article and supplement as separate artifacts with retrieval date, byte count, and SHA-256 | Candidate companion cluster-orbit source |

Primary routing references:

- CHARA publication index:
  `https://chara.gsu.edu/astronomers/journal-articles`
- Papers I-IV:
  `https://arxiv.org/abs/1902.05557`,
  `https://arxiv.org/abs/1909.09161`,
  `https://arxiv.org/abs/2005.00546`, and
  `https://arxiv.org/abs/2209.09993`
- Hyades six-system paper: `https://arxiv.org/abs/2406.01674`
- Hyades `HD 284163` version of record:
  `https://academic.oup.com/mnras/article/527/3/8907/7469483`

The table-route entries above are intentionally conservative. A journal page
showing tables is not treated as a stable machine-readable artifact until a
future task records the exact download locator, licence, retrieval date, byte
count, and checksum.

## Three-Question Rights Decision

| Question | Decision |
| --- | --- |
| May an agent inspect an admitted paper locally? | Yes, subject to the publisher/host access terms. |
| May APL redistribute source bytes? | Only for an artifact with an explicit compatible licence. Papers I-III default to no vendoring; Paper IV and the two Hyades papers carry CC BY 4.0 but still require per-artifact attribution and identity checks. |
| May a later task publish normalized factual rows? | Not authorized here. A separate task must decide per-paper row provenance, citation, table terms, uncertainty semantics, and whether bolometric luminosity is available without importing an M-L relation. |

An arXiv locator does not by itself grant APL a CC BY redistribution right.
Where the version of record is all-rights-reserved, the safe route is locator,
metadata, local checksum, and no committed upstream bytes.

## Known DEBCat Overlap

The title-level HD-number screen is not sufficient because DEBCat commonly
uses variable-star designations. Two load-bearing aliases from the primary
papers demonstrate the problem:

| CHARA paper target | Alias used by committed DEBCat | Committed evidence | Decision |
| --- | --- | --- | --- |
| `HD 224355` | `V1022 Cas` | `DEBCAT-V1022_Cas-C1` and `C2` | Exclude from an independent holdout |
| `HD 185912` | `V1143 Cyg` | `DEBCAT-V1143_Cyg-C1` and `C2` | Exclude from an independent holdout |

A direct search of the remaining title-level HD identifiers found no match in
the committed DEBCat file. That is not evidence of independence: Papers III
and IV and the Hyades systems remain `ALIAS_AUDIT_REQUIRED` until a pinned
cross-identifier ledger is checked.

## Deterministic De-dup Contract

A future source-artifact task must apply this contract before viewing or
curating value-bearing fields:

1. Freeze the committed DEBCat file identity using the path and SHA-256 above.
2. For every candidate physical system, collect identifier metadata only:
   paper name, HD, HIP, HR, GCVS/variable name, Gaia DR3 `source_id` when
   published, cluster identifier, and component hierarchy.
3. Record the primary identifier source and pin any external alias response
   used for the crosswalk with retrieval date and checksum. Do not rely on an
   unrecorded interactive SIMBAD lookup.
4. Normalize case, whitespace, underscores, and punctuation, but never infer
   identity from a similar string alone.
5. Exclude the entire physical system when any stable identifier intersects a
   committed DEBCat system alias. Both or all components receive the same
   exclusion decision.
6. Classify coordinate-only, component-hierarchy, conflicting-alias, or
   unresolved matches as `AMBIGUOUS_OVERLAP` and exclude them from the
   independent lane. This preflight deliberately sets no coordinate radius
   because no coordinate artifact is pinned.
7. Emit a deterministic ledger with candidate paper, candidate system,
   normalized aliases, matched DEBCat `system_id` or null, decision, reason,
   and source-artifact hashes. Sort by DOI then stable system identifier.
8. Compute coverage counts only after the alias ledger is frozen. Do not use
   masses, luminosities, residuals, or model performance to choose which
   systems survive.

This rule treats uncertainty as exclusion, not as permission to call a system
independent.

## Coverage Readiness

The six paper surfaces name fifteen physical systems at paper level. The two
known DEBCat aliases leave at most thirteen candidates before the full alias,
measurement-class, evolutionary-state, luminosity-provenance, and mass-window
gates. This is plausibly enough to justify a small paper-level source-artifact
and de-dup exercise, but it is not enough to assert statistical adequacy.

The future artifact must preserve these boundaries:

- exact `0.5-2.0 M_sun` eligibility remains unknown until an authorized row
  task exists;
- absolute magnitudes in a paper are not automatically the bolometric
  luminosity target used by `RESULT-0022`;
- model-derived masses are inadmissible as truth;
- the CHARA route still does not supply a credible independent high-mass
  surface for `RESULT-0024`;
- a minimum holdout size must be predeclared by a later benchmark contract,
  not selected after values or metrics are seen.

## Verdict

`PAPER_LEVEL_PIN_READY`.

The source family has enough stable paper-level locators, explicit rights
boundaries, and identifier metadata to support a bounded value-blind artifact
task. The known Paper I/II aliases prove that de-duplication is necessary and
also show that the committed DEBCat snapshot can detect real overlap. The
absence of a single CHARA catalogue is no longer a hard blocker because each
paper and supplement can be independently pinned.

This verdict does not authorize rows or a benchmark. The route can still stop
as source-limited if machine-readable table endpoints cannot be pinned, the
alias ledger removes too many systems, bolometric luminosity provenance is
incompatible, or the eligible sample misses a predeclared future size floor.

## Bounded Future Task Shape

A maintainer-authorized follow-up may create a value-blind source-artifact
manifest for the six paper surfaces above. It should:

- pin exact article/table/supplement locators, retrieval dates, byte counts,
  SHA-256 hashes, licences, and citations;
- build the identifier-only alias ledger under the frozen contract above;
- report paper-level and post-de-dup system counts without transcribing
  scientific values;
- return `SOURCE_ARTIFACT_READY`, `SOURCE_LIMITED`, or `BLOCKED`;
- stop before row extraction, luminosity construction, M-L scoring, exponent
  fitting, or artifact promotion.

This task shape is advisory and has no canonical task id. It requires a
maintainer or Scientific Director decision before execution.

## Stop Conditions

- Stop if a paper/table artifact has no stable locator or its byte identity
  cannot be pinned.
- Stop rather than vendoring an all-rights-reserved paper or table.
- Stop if aliases or component hierarchy cannot distinguish a candidate from
  a DEBCat system.
- Stop if luminosity would be reconstructed from an assumed M-L relation.
- Stop if a future task attempts to score the same systems used to tune the
  frozen DEBCat relation as independent evidence.
- Do not use this route to claim a universal stellar mass-luminosity law.

## Output Routing

- Task verdict: `PAPER_LEVEL_PIN_READY`.
- Canonical destination:
  `docs/reviews/stellar-chara-paper-level-source-pin-dedupe-preflight.md`.
- Review tier: none; source-readiness planning only.
- Gate A: not applicable; no RESULT or PRED artifact was created.
- Gate B: not applicable; no benchmark or replay was run.
- Data impact: none; no source values, rows, tables, or upstream bytes were
  committed.
- Metric impact: none; no M-L metric or fit was run.
- Result impact: `RESULT-0022` and `RESULT-0024` unchanged.
- Claim impact: none.
- Knowledge impact: none.
- Remaining blockers: per-paper artifact checksums, complete alias ledger,
  bolometric-luminosity provenance, exact eligibility, and a predeclared
  future holdout-size floor.
