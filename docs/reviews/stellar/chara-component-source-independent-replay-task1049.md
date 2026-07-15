# TASK-1049: Independent CHARA component-source replay

## Scope and independence

This replay validates the bounded twelve-row CHARA component source surface
created by TASK-1040. The source-curation commit is attributed to contributor
`akutenyov`; this replay is controlled by contributor `gladunrv` using Codex.
The work therefore satisfies the task's different-human-contributor condition.
The active coordination claim is GitHub issue 1576.

No stellar relation was fit or scored. No residual, split, benchmark output,
RESULT, PRED, CLAIM, or KNOW artifact was inspected or changed.

## Independent source pins

All six cited arXiv PDFs were fetched again on 2026-07-15. Their byte counts
and SHA-256 digests reproduce the committed source manifest exactly.

| Source | Bytes | SHA-256 | Replay decision |
| --- | ---: | --- | --- |
| CHARA I, arXiv 1902.05557 | 610985 | `8860e1f9b2c37b13864f71996256177f5ebed98702dc63416b12b4c1d86dc3ae` | Exact pin; no values used. |
| CHARA II, arXiv 1909.09161 | 2922018 | `581debe7ce77da900eb250e418bf020de848a90ef7a8384186ad3381726b62c1` | Exact pin; no values used. |
| CHARA III, arXiv 2005.00546 | 958390 | `1f61a6ddcfefd1225459ea6a3485b2c17ec09870a91dc15025fe531bbeee7b5c` | Exact pin; Table 8 facts replayed. |
| CHARA IV, arXiv 2209.09993 | 1227253 | `bf700038072502164842a92384713f9c030be56cdac9a6e243dd4d4942adfd6b` | Exact pin; Table 3 facts replayed. |
| Hyades six, arXiv 2406.01674 | 1717730 | `c8bc5d92f3cd3386f648a777c6bdbe50c324ca666e56af23a0f13543895229d0` | Exact pin; Table 19 remains band-limited only. |
| HD 284163 article, arXiv 2312.05301 | 2695999 | `b70c76a0eb77f7e2c723471361fbd0b832f4ab9944f52d94be09bdde6d87182f` | Exact pin; article has masses and band magnitudes only. |

The OUP landing page for the named
`stad3803_supplemental_file.zip` returned HTTP 403 in this replay session. The
supplement therefore remains explicitly checksum-unavailable and unused. This
does not alter any admitted row because HD 284163 remains excluded.

## Row-by-row replay

The paper primary maps to component A and the paper secondary maps to component
B in every row. CHARA III Table 8 reports the dynamical masses, radii, and
effective temperatures used for the four derived rows. CHARA IV Table 3 reports
all eight masses and bolometric luminosities directly, with symmetric quoted
uncertainties. Section 4.3 explicitly states that the Table 3 luminosities were
calculated with the Stefan-Boltzmann law; they are not conversions from
band-limited magnitudes.

| Row | Source locator | Mass check | Luminosity check | Mapping and flags | Decision |
| --- | --- | --- | --- | --- | --- |
| HD8374-A | CHARA III Table 8 | `1.636 +/- 0.050 M_sun` | Derived from `1.84 +/- 0.05 R_sun`, `7280 +/- 110 K` | primary to A; SB2 visual binary | PASS |
| HD8374-B | CHARA III Table 8 | `1.587 +/- 0.049 M_sun` | Derived from `1.66 +/- 0.12 R_sun`, `7280 +/- 120 K` | secondary to B; SB2 visual binary | PASS |
| HD24546-A | CHARA III Table 8 | `1.434 +/- 0.014 M_sun` | Derived from `1.67 +/- 0.06 R_sun`, `6790 +/- 120 K` | primary to A; wide sibling recorded | PASS |
| HD24546-B | CHARA III Table 8 | `1.409 +/- 0.014 M_sun` | Derived from `1.60 +/- 0.10 R_sun`, `6770 +/- 90 K` | secondary to B; wide sibling recorded | PASS |
| HD61859-A | CHARA IV Table 3 | `1.629 +/- 0.023 M_sun` | `9.6 +/- 1.3 L_sun`, reported bolometric | primary to A; SB2 visual binary | PASS |
| HD61859-B | CHARA IV Table 3 | `1.443 +/- 0.020 M_sun` | `4.1 +/- 0.5 L_sun`, reported bolometric | secondary to B; SB2 visual binary | PASS |
| HD89822-A | CHARA IV Table 3 | `2.779 +/- 0.153 M_sun` | `101.0 +/- 8.0 L_sun`, reported bolometric | primary to A; SB2 visual binary | PASS |
| HD89822-B | CHARA IV Table 3 | `1.708 +/- 0.094 M_sun` | `9.7 +/- 1.0 L_sun`, reported bolometric | secondary to B; SB2 visual binary | PASS |
| HD109510-A | CHARA IV Table 3 | `1.838 +/- 0.218 M_sun` | `15.6 +/- 1.3 L_sun`, reported bolometric | primary to A; HD 109511 sibling recorded | PASS |
| HD109510-B | CHARA IV Table 3 | `1.541 +/- 0.184 M_sun` | `7.2 +/- 0.9 L_sun`, reported bolometric | secondary to B; HD 109511 sibling recorded | PASS |
| HD191692-A | CHARA IV Table 3 | `3.564 +/- 0.049 M_sun` | `229.8 +/- 22.5 L_sun`, reported bolometric | primary to A; WDS sibling recorded | PASS |
| HD191692-B | CHARA IV Table 3 | `2.739 +/- 0.037 M_sun` | `54.0 +/- 5.8 L_sun`, reported bolometric | secondary to B; WDS sibling recorded | PASS |

The morphology flags agree with the papers' combined double-lined
spectroscopic and visual-orbit analyses. The distant-sibling flags for HD
24546, HD 109510, and HD 191692 agree with the TASK-1025 sibling-component
ledger; the other three admitted systems have no sibling component in that
ledger.

## Derivation replay

The four CHARA III luminosities were recomputed with the frozen relation

`L/L_sun = (R/R_sun)^2 * (T_eff/5772 K)^4`

and independent-error propagation

`sigma_L/L = sqrt((2 sigma_R/R)^2 + (4 sigma_T/T_eff)^2)`.

The maximum absolute luminosity drift is
`4.3231877633331806e-07 L_sun`; the maximum absolute propagated-uncertainty
drift is `1.4513580925967773e-07 L_sun`. Both are below the precision of the
six-decimal committed values and arise only from decimal rounding.

## Identity, grouping, and leakage checks

- The surface contains exactly 12 component rows for six systems, with complete
  A/B pairs.
- Normalized whole-system identifiers have zero intersection with the frozen
  DEBCat component surface.
- Each admitted system maps one-to-one to the corresponding TASK-1041
  provisional singleton. The source surface uses
  `provisional_singleton_HD...` labels while TASK-1041 uses
  `singleton-hd-...`; the partition assignment is equivalent and no Melotte 25
  system is admitted.
- The seven exclusions remain justified: Hyades Table 19 provides only V/H/K
  absolute magnitudes, and HD 284163 has no pinned same-component bolometric
  luminosity route.
- No residual, model score, split assignment, or target-dependent selection was
  read or produced during the replay.

## Rights and redistribution

The committed surface contains normalized factual values only. CHARA III stays
inside its AAS bounded-factual-extract boundary; CHARA IV and the Hyades/HD
284163 open articles retain their recorded attribution and reuse terms. No
publisher PDF, HTML, figure, table image, or supplement byte is committed.
`data/DATA_LICENSES.yaml` already registers the mixed-source surface and the
non-vendored boundary.

## Verdict

**`INDEPENDENT_SOURCE_REPLAY_PASS`.** All twelve admitted rows, source
identities, source locators, units, uncertainty meanings, component mappings,
morphology/multiplicity flags, derivations, identifier checks, grouping
assignments, and redistribution boundaries replay without a contested row or
material numeric drift.

## Output routing

- Canonical destination: this source-validation note and validation metadata
  on `chara_component_rows.yaml`.
- Review tier: none; this task creates no scientific RESULT or PRED artifact.
- Gate A: not attempted. Gate B: not attempted.
- Claim impact: none. Knowledge impact: none.
- Limitation: the HD 284163 supplement remains checksum-unavailable and unused;
  the replay validates only this bounded factual source extract, not a stellar
  relation, population, or universal law.
