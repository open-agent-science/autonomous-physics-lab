# HD 284163 CHARA Supplement Source Gate

Task: `TASK-1076`

## Verdict

`LUMINOSITY_SEMANTICS_BLOCKED`

The named publisher supplement is now identity-pinned and readable, and the
inner-pair component mapping is unambiguous. The gate still stops because the
source provides no direct bolometric luminosities and does not provide the
complete measured radius and effective-temperature inputs required by the
already reviewed Stefan-Boltzmann route. No extension rows are admitted.

## Inputs And Method

The audit used only the named article and its linked publisher supplement:

- Guillermo Torres et al., "Orbits and dynamical masses for the active Hyades
  multiple system HD 284163", *Monthly Notices of the Royal Astronomical
  Society* 527 (2024), 8907-8920,
  DOI `10.1093/mnras/stad3803`;
- the Oxford Academic article page at
  `https://academic.oup.com/mnras/article/527/3/8907/7469483`;
- the `sup1` attachment linked by that page, without searching for substitute
  mirrors or later catalog values.

The publisher HTML was inspected first to establish the article identity,
license statement, and exact attachment link. Only after that pin was recorded
was the ZIP opened locally. ZIP bytes and extracted member bytes remained
outside git. The audit compared the source fields against the existing CHARA
admission rule: same-component dynamical mass plus either direct bolometric
luminosity or a measured radius and uncertainty together with effective
temperature and uncertainty.

No APL residual, score, split, fitted parameter, or `RESULT-0031` output was
used to decide admissibility.

## Exact Supplement Identity

| Field | Pinned value |
| --- | --- |
| Publisher | Oxford University Press for the Royal Astronomical Society |
| Article DOI | `10.1093/mnras/stad3803` |
| Article publication date | `2023-12-11` |
| Article corrected/typeset date | `2023-12-22` |
| Stable attachment locator | `https://oup.silverchair-cdn.com/oup/backfile/Content_public/Journal/mnras/527/3/10.1093_mnras_stad3803/1/stad3803_supplemental_file.zip` |
| Publisher attachment name | `stad3803_supplemental_file.zip` |
| Retrieval date | `2026-07-23` |
| Media type | `application/zip` |
| ZIP bytes | `3906` |
| ZIP SHA-256 | `ea1d86d52c4c5b1c870e61d9bf2b95fbe85e5ce8c122ace375e745b8cfa52275` |
| ZIP member count | `1` |
| Member | `table4.ascii` |
| Member bytes | `12765` |
| Member SHA-256 | `eb21bfe8fb102951843384dd16bd6f158ef48f9a8411463968e45ae1fa19dd89` |
| ZIP integrity | passed |

The sole member is the machine-readable form of article Table 4. Its columns
are observation time, light-travel-time correction, year, radial velocities
and uncertainties for Aa, Ab, and B, inner and outer phase, and instrument
code. It contains no mass, radius, effective-temperature, or luminosity
column.

## Rights And Reuse Boundary

The article page states that the article is Open Access under CC BY 4.0 and
requires citation of the original work. The supplement is served as the
article's online supplementary material, but the ZIP has no standalone license
file or embedded reuse statement. This task therefore records the exact
publisher locator and checksums and uses only bounded factual inspection.

The raw HTML, ZIP, and `table4.ascii` bytes are not committed or relicensed.
This review does not claim a separate redistribution permission for the raw
supplement. A later task seeking to vendor those bytes would need an explicit
rights decision even though the associated article is CC BY 4.0.

## Component Mapping

The source hierarchy and labels are internally consistent:

| Source component | Role | Prospective extension mapping | Decision |
| --- | --- | --- | --- |
| `HD 284163 Aa` | primary of the 2.39-day inner pair | component `A` | identity clear |
| `HD 284163 Ab` | secondary of the 2.39-day inner pair | component `B` | identity clear |
| `HD 284163 B` | outer tertiary | none | outside the bounded two-row extension |
| `HD 284163 C` | distant fourth component candidate | none | outside the named inner-pair surface |

Article Table 5 reports same-component dynamical masses with uncertainties for
Aa and Ab. Component identity is therefore not the blocker.

## Bolometric-Luminosity Gate

The luminosity gate fails for four independent source reasons:

1. The supplement is a radial-velocity table only.
2. The article's empirical mass-luminosity discussion uses deconvolved
   visual-band absolute magnitudes and H/K-band flux ratios, not bolometric
   luminosities.
3. The interferometric analysis states that the stars are unresolved. The
   fixed angular diameters used in fitting were estimated from preliminary
   masses and model-predicted radii; they are not measured radii admissible for
   a Stefan-Boltzmann derivation.
4. The spectroscopic discussion gives an interpolated effective temperature
   and uncertainty for Aa, but adopts the Ab template temperature without a
   reported uncertainty. Neither inner component has the required measured
   radius and radius uncertainty in this source.

Intrinsic variability and spot modulation also affect the reported
band-limited brightness, so a post hoc bolometric conversion would introduce
an additional unreviewed uncertainty model. Band magnitudes, synthetic
spectral interpolation, and stellar-evolution-model radii cannot be substituted
for the frozen direct-or-Stefan-Boltzmann admission rule.

## Stop Conditions

The following task stop conditions fired:

- band-limited luminosity only;
- missing measured radii and radius uncertainties;
- incomplete effective-temperature uncertainty semantics for Ab;
- model-predicted radii are not measurement inputs.

The supplement identity, article identity, and inner-pair component mapping no
longer block the route. The decisive blocker is luminosity semantics.

## Limitations

- This audit is scoped to the named article and linked supplement. It does not
  search other catalogs for substitute radii or spectral-energy-distribution
  luminosities.
- It does not decide whether a future independently pinned source could supply
  admissible bolometric luminosities for HD 284163.
- It does not assess the tertiary as a separate row candidate.
- Source readability and CC BY article status do not make the raw publisher
  attachment part of the APL repository license.

## Output Routing

- Canonical destination: this source-adjudication note.
- Source readiness: blocked on bolometric-luminosity semantics.
- Extension artifact: not created; admitted row count is `0`.
- Review tier: maintainer review through task closeout.
- Gate A: not attempted.
- Gate B: not attempted.
- `RESULT-0031`: unchanged.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: a separately authorized source task would need
  same-component bolometric luminosities or complete measured
  Stefan-Boltzmann inputs with uncertainty semantics.
