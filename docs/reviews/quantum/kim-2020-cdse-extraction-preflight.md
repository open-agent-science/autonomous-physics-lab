# TASK-1043: Kim 2020 CdSe extraction preflight

## Scope

This task freezes the extraction rules for the checksum-pinned Kim et al. 2020
CdSe source before any figure is cropped, digitized, or converted into a
measurement row. The machine-readable contract is
[extraction_contract.yaml](../../../data/quantum_dots/source_artifacts/kim-2020-nanomaterials-cdse-optical/extraction_contract.yaml).

No numerical value from the article was transcribed. No `qd-*.yaml` row,
benchmark split, fit, metric, RESULT, PRED, CLAIM, or KNOW artifact was created
or changed.

## Source re-verification

On 2026-07-13 the three TASK-1027 artifacts were fetched again and hashed
without inspecting or retaining their scientific values:

| Artifact | Bytes | SHA-256 | Outcome |
| --- | ---: | --- | --- |
| Version-of-record PDF | 1,368,239 | `2dab8a6b4db18af88f7175ac0773747fe1aeb15d88f951a4a8536cdc2dd73edb` | exact TASK-1027 match |
| Europe PMC JATS | 62,029 | `6642fed609ad6540b61ca856d293d2b469c5ed7be9323479c9b76b023f668244` | exact TASK-1027 match |
| Crossref snapshot | 12,087 | `6b3a36ba7160d7c3d12a54bc64b846ec358d569ee562e778e8ac64eca6526e9c` | exact access-date snapshot match |

The PMC OA service still returns the official `tar.gz` FTP locator. Its HTTPS
form returned 404 and FTP denied the directory change, so no package checksum
is asserted. This does not block the preflight because the VoR PDF, structured
JATS, DOI, and CC BY 4.0 rights posture are already pinned. Publisher bytes
remain uncommitted under the existing `metadata_only` policy.

## Admissible provenance classes

The article-text/Figure 1 caption mean size and dispersion are admissible in a
future task as `text_stated_summary`: exactly one summary for each of
`CdSe-1` through `CdSe-4`, with its exact locator. The reported dispersion is a
size-distribution descriptor, not a standard error, and must keep that label.

Figure 1 histogram digitization is a separate
`figure_digitized_distribution` class. It is excluded from the primary summary
route and must never replace, average with, or silently duplicate the four
text-stated summaries.

Figure 3a absorption and emission spectra are eligible only through a
deterministic, replayable digitization. Figure 3b Stokes-shift/FWHM summaries,
Figure 4 differential-absorption transitions, and Figure 5 model levels remain
separate analysis/model-derived classes and are out of scope here.

## Deterministic Figure 3a contract

- Tool: WebPlotDigitizer-class axis-calibrated export, with the exact
  application version and export format recorded at execution.
- Input: a panel derived from the checksum-pinned VoR; its raster checksum must
  be recorded. The raster is not committed without a maintainer redistribution
  decision.
- Calibration: at least four printed-tick anchors, with at least two per axis;
  store pixel coordinates, printed values/units, and linear/log scale type.
- Native axes are retained. A wavelength-to-energy conversion, if needed, is a
  separate derived field with an explicit constant and formula.
- Each sample and curve role is digitized independently. Absorption and
  emission traces must not be merged.
- Two independent extraction passes are mandatory. Every admitted peak must
  agree within 0.5% of the x-axis span and 1.0% of the y-axis span. Any failure
  returns `UNCERTAINTY_BLOCKED` rather than widening the tolerance after seeing
  values.

Every extracted point must carry sample, source checksum, panel, curve role,
raw pixel coordinates, calibration reference, tool/version, pass/operator,
native coordinates/units, coordinate uncertainty, and inclusion/exclusion
state.

## Axis and morphology safeguards

`absorption_peak_eV`, `emission_peak_eV`, derived Stokes shift, FWHM,
differential-absorption levels, and model-derived levels remain distinct.
None may be relabelled as “bandgap” without a separate reviewed physical
mapping.

Morphology stays `unknown_non_spherical`. The source-reported HRTEM Gaussian
fit diameter is retained under that provenance label; no equivalent-sphere
conversion is authorized. A future row that needs such a conversion returns
`MORPHOLOGY_BLOCKED` until reviewed geometry exists.

## Exact future gate

A complete future sample-level package requires all four sample identities,
four text-stated size summaries, four absorption peaks, and four emission
peaks: 12 atomic observations with 100% sample pairing, source locator,
size-dispersion, and digitization-uncertainty completeness. Fewer rows return
`SOURCE_LIMITED`. Unreported instrument uncertainty must be recorded as
`not_reported`; it must not be invented or replaced by pixel error.

## Verdict

**`EXTRACTION_CONTRACT_READY`.** Source identity and rights are stable, the
allowed provenance classes are separated, Figure 3a has a deterministic
calibration/replay contract, morphology conversion is forbidden, and exact row
and uncertainty gates are frozen before value access.

This verdict authorizes only a separate future extraction task. Gate A and
Gate B are not attempted because this preflight creates no scientific result or
replay artifact.

## Output routing

Contract and review note only. Zero cropped figures, digitized points,
measurement rows, metrics, fits, results, predictions, claims, or knowledge
mutations.
