# TASK-1025: CHARA identifier and alias audit

**Task:** TASK-1025  
**Date:** 2026-07-13  
**Mode:** identifier metadata only; physical values were not read

## Scope and frozen comparison source

The audit covers the 13 CHARA candidates left after TASK-0989 excluded two known
DEBCat overlaps. Matching is at whole physical-system level, never at component
row level. The frozen DEBCat snapshot is:

- locator: https://astro.keele.ac.uk/jkt/debcat/debs.dat
- snapshot last modified: 2026-05-16 11:14:34 GMT
- retrieval date: 2026-06-16 UTC
- SHA-256: `326902535b4da2fd94f227806ff339247d6df224ef8faea8857703e553b464da`
- route: metadata-only comparison; raw `debs.dat` is not committed

The committed DEBCat manifests were searched only for identifiers and aliases.
No masses, radii, temperatures, luminosities, or other physical values were
inspected or transcribed.

## Identifier resolution

The official SIMBAD identifier endpoint was queried on 2026-07-13 UTC:
`https://simbad.cds.unistra.fr/simbad/sim-id`

| Candidate | Identifier-only aliases returned |
|---|---|
| HD 8374 | HIC 6514; HR 395; Gaia DR2 323159631479218560 |
| HD 24546 | HIC 18453; HR 1210; IRAS 03528+5033; Gaia DR2 250437313946591360; 1RXS J035635.2+504142; IDS 03492+5024 A |
| HD 61859 | HIC 37580; HR 2962 |
| HD 89822 | HIC 50933; HR 4072 |
| HD 109510 | HIC 61415; HR 4791; PPM 129165; Gaia DR1 3947647756222627712; uvby98 100109510; WEB 10931; Gaia DR2 3947647760517933824 |
| HD 191692 | Gaia DR3 4224225924761329792; HIP 99473; PLX 4790; HIC 99473; HR 7710; IDS 20061-0107 A |
| HD 27483 | HIC 20284; HR 1358; IRAS 04180+1344; Gaia DR1 3310615561179780736; [RSP2011] 238; WEB 3879; Gaia DR2 3310615565476268032; AP J04205271+1351521 |
| HD 283882 | HIC 22394; JP11 4917; NAME NC 12 |
| HD 26874 | HIC 19870; JP11 4953; PPM 93374 |
| HD 27149 | Gaia DR1 47620260916592384; [RSP2011] 211; WEB 3827; Gaia DR2 47620265212420096 |
| HD 30676 | HIC 22496; JP11 4919 |
| HD 28545 | IDS 04249+1529 B; JP11 4972 |
| HD 284163 | HIP 19591; Gaia DR3 149767987810042624; WISEA J041156.32+233809.8; HD 284163A; BD+23 635A; SKF 2409A; Gaia DR2 149767987810042624; Cl* Melotte 25 PELS 20; LSPM J0411+2338 |

All 13 lookups returned HTTP 200. Responses were used only for alias identity,
not as physical-data sources.

## DEBCat overlap result

No identifier-only intersection was found between the 13 alias sets and the
committed DEBCat system/holdout identifier manifests. The two known TASK-0989
overlaps remain excluded and are not reintroduced:

- HD 224355 -> V1022 Cas
- HD 185912 -> V1143 Cyg

This is an identifier-audit result. Future row curation must still resolve
hierarchy and component identity separately.

## Decision

**`ALIAS_AUDIT_READY_FOR_ROW_CURATION`**

All 13 candidates have resolved identifier metadata and no identifier-only match
to the frozen DEBCat manifests. A later row task must preserve whole systems, pin
source versions, and perform value-bearing work under a separate no-peek review.
This packet contains no stellar values, rows, fits, metrics, RESULT, CLAIM,
PREDICTION, or KNOWLEDGE artifact.
