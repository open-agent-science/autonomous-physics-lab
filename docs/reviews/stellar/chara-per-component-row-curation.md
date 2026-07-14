# TASK-1040: CHARA per-component row curation

## Scope

This task re-pins the six TASK-0989 article artifacts, checks the named HD
284163 supplement surface, and attempts a bounded per-component extract for
exactly the thirteen TASK-1025 candidates. It admits only same-component
dynamical mass and bolometric luminosity pairs. No split, fit, residual,
metric, RESULT, PRED, CLAIM, or KNOW artifact was created or changed.

The normalized surface is
[chara_component_rows.yaml](../../../data/textbook_formula_audit/stellar_ml/chara_component_rows.yaml).

## Frozen identity and source checks

- The TASK-1025 alias ledger SHA-256 remains
  `9ba15da828381841914b7e848f2d9e9235aa7237d6ecf513a795dfa6b2ec8613`.
- The frozen DEBCat component surface SHA-256 remains
  `7e8fe4a2359f53f7fd7c80cdba5f56dc024fa45f985879d3faecb8bc8398db08`.
- All six article PDF byte counts and SHA-256 pins reproduce TASK-0989.
- The named OUP artifact `stad3803_supplemental_file.zip` could not be
  checksum-pinned from the publisher surface. No supplement value was used.
- Re-running the normalized identifier intersection on all thirteen candidate
  identifiers found zero DEBCat whole-system intersections.

The article and supplement bytes remain outside the repository. CHARA III is
used only as a bounded factual extract under its AAS rights boundary. CHARA IV
and the Hyades articles are CC BY 4.0 and retain attribution. The committed
surface and its non-vendored posture are registered in `data/DATA_LICENSES.yaml`.

## Curation result

| Source | Candidates | Admitted | Rows | Decision |
| --- | ---: | ---: | ---: | --- |
| CHARA III, Table 8 | 2 | 2 | 4 | Unambiguous mass, radius, temperature, and component mapping; luminosity is derived with Stefan-Boltzmann. |
| CHARA IV, Table 3 | 4 | 4 | 8 | Published dynamical masses and bolometric luminosities are paired by the paper columns. |
| Hyades six, Table 19 | 6 | 0 | 0 | The source provides masses and V/H/K absolute magnitudes, not a reviewed bolometric conversion. |
| HD 284163 | 1 | 0 | 0 | The supplement is not checksum-pinned and no admissible same-component bolometric luminosity pair was found. |

The admitted surface contains 12 rows for 6 systems. Each row records source,
definitions, units, uncertainty treatment, component mapping, morphology,
multiplicity, environment group, and stage flag. The four CHARA III
luminosities use `L/Lsun = (R/Rsun)^2 (Teff/5772 K)^4`; their uncertainties
propagate the published radius and temperature errors assuming independence.
No conversion was attempted from V/H/K magnitudes.

## Verdict

**`SOURCE_LIMITED`.** Six systems are ready as a source-curated component
surface, but the requested thirteen-system surface is incomplete because seven
systems lack a reviewed bolometric luminosity route and one of those seven also
has an unpinned named supplement. This is a source-readiness result only, not
evidence that a mass-luminosity relation transfers to CHARA systems.

## Limitations and routing

- A later task may pin the HD 284163 supplement and propose a reviewed
  bolometric conversion for the Hyades sources. It must not silently fill these
  exclusions.
- The Melotte 25 dependence rule from TASK-1041 remains unchanged. That group
  is not an independent holdout against the frozen DEBCat development surface.
- No row was assigned to train or holdout, and no formula was scored.
- Gate A and Gate B are not attempted. Claim and knowledge impact is none.
