# Gaia DR4 Same-Component Luminosity Semantics Gate

- Task: `TASK-1098`
- Claim ledger: <https://github.com/open-agent-science/autonomous-physics-lab/issues/1670>
- Campaign: textbook formula audit, Stellar M-L lane
- Review date and official-source access date: `2026-07-24`
- Mode: value-blind official-metadata review
- Verdict: **`STOP_SOURCE_LEVEL_ONLY`**

## Decision

The pinned official Gaia DR4 draft data model does not supply two bolometric
component luminosities that can be paired with the two component masses in
`nss_masses`. It defines `m1` and `m2` as primary and secondary masses, but
the relevant FLAME luminosity fields are explicitly the luminosity of "the
star" represented by the source-level `ap_xp` or `ap_rvs` row. The draft does
not define `lum1`/`lum2`, primary/secondary FLAME luminosities, or another
documented mapping from one source-level FLAME luminosity to both NSS
components.

The only component-labelled photometric ratio in `nss_masses`, `fluxratio`, is
the secondary-to-primary flux ratio in the Gaia G band. It is not a bolometric
luminosity ratio. The draft also says that some tested flux ratios are chosen
using isochrone consistency. Neither route is an independently justified,
value-blind bolometric decomposition for this benchmark.

Therefore the current official schema cannot bind each direct dynamical
component mass to the bolometric luminosity of that same component. The route
is parked until a named official Gaia schema or documentation revision changes
that specific semantic boundary. This decision does not query or assess
whether any eligible Gaia DR4 systems exist.

## Pinned Official Artifact

The official prerelease bytes were retrieved only to inspect metadata. They
were not committed.

| Property | Pinned identity |
| --- | --- |
| Official landing page | <https://www.cosmos.esa.int/web/gaia/dr4-prerelease> |
| Official ZIP | <https://anonftp.cosmos.esa.int/pub/GAIA_PUBLIC_DATA/Gaia_DR4/dr4-prerelease/gaia-dr4-prerelease-draft-data-model_2026-06-26.zip> |
| Artifact identity | `gaia-dr4-prerelease-draft-data-model_2026-06-26.zip` |
| Artifact status | Draft Gaia DR4 data model, prereleased June 2026 |
| Access date | `2026-07-24` |
| ZIP size | `2840832` bytes |
| ZIP SHA-256 | `d807eae98acbeec0a0af2ce6a5d7d352298df6f270a1f13207cc8d1becf42c66` |
| Inner PDF | `gaia-dr4-prerelease-draft-data-model.pdf` |
| PDF SHA-256 | `8c33055c122eb3f5ef6ac64e8624e6c11a1e261f6fa4108c635296b52feeb043` |
| Archive model identity | `gaia.cu9.archive 21.7.branch`, revision `SB-21.7.0-RC-r0` |
| Direct-delivery identity | `gaia.cu9.directdelivery 21.6.branch`, revision `SB-21.6.0-RC-r0` |
| License instructions | <https://www.cosmos.esa.int/web/gaia-users/license> |

The retrieved ZIP identity, byte count, and both checksums exactly reproduce
the pin recorded by `TASK-1029`. No newer official data-model identity was
substituted in this task. Gaia DR4 remains a future release, and this draft
identity is not represented as a final schema.

## Relevant Official Field Semantics

### Component mass surface: `nss_masses`

`nss_masses` is described as the table of masses derived from NSS solutions
with orbital parameters (pinned PDF page 744). Each row has one `source_id`;
the component identity is expressed by the mass columns rather than by two
component source rows.

| Field | Official draft meaning | Unit / uncertainty semantics | Gate treatment |
| --- | --- | --- | --- |
| `source_id` | Unique source identifier | Identifier, not a component label | Joins source-level products only; does not create two luminosity components |
| `solution_id` | Processing-solution provenance identifier | Numeric provenance identifier | Required provenance context, not a scientific component mapping |
| `m1` | Mass of the primary component | Solar masses | Candidate primary mass only when provenance is direct |
| `m1_lower`, `m1_upper` | 16th and 84th percentiles of primary mass | Solar masses; central 68% interval | Candidate uncertainty bounds |
| `m2` | Mass of the secondary component | Solar masses | Candidate secondary mass only when present and provenance is direct |
| `m2_lower`, `m2_upper` | 16th and 84th percentiles of secondary mass | Solar masses; central 68% interval | Candidate uncertainty bounds |
| `combination_method` | Combination of NSS solution types used to derive the row | Enum-like string assembled from the documented solution families | Must be pinned before any future value access |
| `m1_ref` | Origin of the primary mass estimate | Blank means NSS directly estimates both masses; documented alternatives include `FLAME`, `IsocLum`, `LowMass`, `WD`, `Multiple`, and `MultipleLower` | Only a blank/direct route could satisfy the direct-mass requirement; model-dependent alternatives are inadmissible |
| `fluxratio` | Secondary-to-primary Gaia G-band flux ratio, `F2/F1` | Dimensionless; when derived, bounds are carried by `fluxratio_lower` and `fluxratio_upper` | Not a bolometric luminosity ratio |
| `correlations` | Correlation vector ordered as `m1`, `m2`, `fluxratio` | Float array | Relevant to a future uncertainty contract, but does not supply component luminosities |

The draft summary marks the combined astrometric/spectroscopic SB2 and
eclipsing/spectroscopic SB2 families as capable of constraining both component
masses. The documented names include `ASTROSPECTROSB2` / `ORBITAL_SB2` and
`ECLIPSINGSPECTROSB2` / `ECLIPSING_SB2`. Other combinations can require an
assumed or model-derived primary mass, supply only a bound, or estimate only
one component. Because the luminosity side fails, this task does not promote
any solution enum into a complete reveal route.

The field definitions and combination provenance above are on pinned PDF
pages 745-749. Page 747 states that an empty `m1_ref` means the NSS solution
directly estimates both masses; documented non-empty alternatives include
`FLAME`, `IsocLum`, `LowMass`, `WD`, `Multiple`, and `MultipleLower`.

### Source luminosity surfaces: `ap_xp` and `ap_rvs`

| Table / field | Official draft meaning | Unit / uncertainty semantics | Gate treatment |
| --- | --- | --- | --- |
| `ap_xp.lum_flame` | Luminosity of the star from FLAME using G-band magnitude, extinction, distance, and a bolometric correction | Solar luminosities; median (50th percentile), with `lum_flame_lower` and `lum_flame_upper` at the 16th and 84th percentiles | Source/star-level quantity; not primary- or secondary-labelled |
| `ap_rvs.lum_flame_spec` | Luminosity of the star from FLAME using G-band magnitude, extinction, parallax, and a bolometric correction based on GSP-Spec parameters | Solar luminosities; median (50th percentile), with `lum_flame_spec_lower` and `lum_flame_spec_upper` at the 16th and 84th percentiles | Source/star-level quantity; not primary- or secondary-labelled |
| `ap_xp.lum_flame_model` | Model luminosity corresponding to FLAME mass/age inference | Solar luminosities; 16th/50th/84th percentile fields | Model-dependent and inadmissible as reveal truth |
| `ap_rvs.lum_flame_model_spec` | Model luminosity corresponding to FLAME mass/age inference using GSP-Spec inputs | Solar luminosities; 16th/50th/84th percentile fields | Model-dependent and inadmissible as reveal truth |

The singular "luminosity of the star" definition and the one-row
`source_id` join do not document which component, if either, a FLAME value
represents for an unresolved binary. Joining `nss_masses.source_id` to an
`ap_*` row therefore yields one source-level luminosity beside two labelled
masses; it does not yield `(m1, L1)` and `(m2, L2)`.

The `ap_rvs` table and `lum_flame_spec` definitions are on pinned PDF pages
300 and 314-315. The `ap_xp` table and `lum_flame` definitions are on pages
366 and 388-389.

## Quantity Boundaries

The following quantities remain distinct:

- `m1` and `m2`: component masses;
- `lum_flame` and `lum_flame_spec`: source/star-level bolometric luminosity
  estimates;
- `lum_flame_model` and `lum_flame_model_spec`: model-dependent luminosities;
- `fluxratio`: a Gaia G-band flux ratio;
- G-band absolute magnitude or a bolometric correction: neither is itself a
  component bolometric luminosity.

No admissible transformation is frozen. In particular:

1. one FLAME luminosity must not be copied to both components;
2. one FLAME luminosity must not be assigned to either component without an
   official component identity;
3. the G-band `fluxratio` must not be treated as `L2/L1`;
4. a color-, temperature-, radius-, isochrone-, or outcome-fitted
   decomposition must not be introduced after values are visible;
5. FLAME/model mass or model luminosity must not replace direct dynamical
   mass and same-component observational luminosity.

## Stop Conditions And Reopen Trigger

This pass stops with `STOP_SOURCE_LEVEL_ONLY` because the pinned schema exposes
only source-level bolometric luminosity for the relevant join.

Do not repeat the gate against this same `2026-06-26` draft. Reopen only when
an official Gaia artifact with a distinct version, date, checksum, or final
documentation identity changes at least one of the following:

- defines primary and secondary bolometric luminosities with units and
  uncertainty fields;
- defines an official, component-identified mapping from each `nss_masses`
  component to its same-component bolometric luminosity;
- defines a value-blind bolometric decomposition with documented inputs,
  uncertainty propagation, and component identity.

A change to release timing, row counts, archive availability, or unrelated
field names is not a reopen trigger. If a future route requires inspecting
target values to choose the mapping, it remains stopped.

## No-Value Attestation

This task inspected only official ESA/Gaia release metadata and the pinned
draft data-model definitions. It made:

- zero Gaia Archive row queries;
- zero target or source-count queries;
- zero inspections of source identities, masses, luminosities, temperatures,
  radii, flux ratios, or outcomes;
- zero row downloads or snippets;
- zero fits, decompositions, eligibility counts, predictions, or scores.

The temporary official ZIP/PDF bytes used for metadata inspection were kept
outside the committed artifact set and removed before publication of this
note.

## Method, Metrics, Limitations, And Verdict

- Input references: `TASK-1029`, the two committed Gaia readiness notes,
  `RESULT-0022`, and the official pinned ESA/Gaia draft data model above.
- Method: checksum reproduction plus a targeted, value-blind comparison of
  mass, luminosity, provenance, unit, uncertainty, and component-identity
  definitions.
- Code reference: none; this is a documentation-only metadata gate.
- Deterministic metrics: official artifacts checked `2`; ZIP checksum matches
  `1/1`; PDF checksum matches `1/1`; Gaia data rows queried `0`; admissible
  same-component luminosity pairs documented `0`.
- Limitations: the source is a prerelease draft rather than the final DR4 data
  model; the task does not establish whether the final schema will add a valid
  route, whether eligible systems exist, or whether any future reveal would
  support the stellar relation.
- Verdict: **`STOP_SOURCE_LEVEL_ONLY`**.

Metadata compatibility does not validate the stellar relation, predict Gaia
outcomes, establish a broad mass-luminosity relation, or show that an eligible
DR4 sample exists.

## Output Routing

- Canonical destination:
  `docs/reviews/stellar/gaia-dr4-component-luminosity-gate-2026-07-24.md`
- Review tier: none; planning-only official-metadata gate
- Gate A: not applicable / not attempted
- Gate B: not applicable / not attempted
- Prediction impact: none; no `PRED-*` registered or scored
- Result impact: none; `RESULT-0022` unchanged
- Claim impact: none
- Knowledge impact: none
- Publication blocker: the pinned Gaia DR4 draft provides no documented
  same-component bolometric luminosity route
- Follow-on route: park the Gaia component-luminosity lane until the named
  official-schema reopen trigger is met; do not unlock a functional-freeze or
  reveal-scoring task

## Official Sources

- ESA/Gaia, Gaia DR4 prerelease:
  <https://www.cosmos.esa.int/web/gaia/dr4-prerelease>
- ESA/Gaia, pinned draft data-model ZIP:
  <https://anonftp.cosmos.esa.int/pub/GAIA_PUBLIC_DATA/Gaia_DR4/dr4-prerelease/gaia-dr4-prerelease-draft-data-model_2026-06-26.zip>
- ESA/Gaia, Gaia DR4 landing page:
  <https://www.cosmos.esa.int/web/gaia/data-release-4>
- ESA/Gaia, Gaia DR4 content overview:
  <https://www.cosmos.esa.int/web/gaia/dr4>
- ESA/Gaia user license instructions:
  <https://www.cosmos.esa.int/web/gaia-users/license>

## Repository Inputs

- `tasks/TASK-1029-gaia-dr4-stellar-transfer-freeze-readiness.yaml`
- `docs/reviews/stellar/gaia-dr4-freeze-readiness.md`
- `docs/reviews/gaia-dr4-stellar-ml-reveal-contract-scout.md`
- `results/EXP-0015/RUN-0001/result.yaml`
- `docs/notes/stellar-ml-campaign-promotion-gate.md`
