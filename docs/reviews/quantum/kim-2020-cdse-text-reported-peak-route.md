# TASK-1064: Kim-2020 CdSe text-reported optical-peak route

## Verdict

**`GO_TEXT_REPORTED_PEAK_ROUTE`.** All eight required optical peak statements
are directly source-locatable, sample-resolved through the article's ordered
Figure 3(a) size sequence, semantically separated into absorption and
fluorescence quantities, expressed in eV, and compatible with the pinned CC BY
4.0 rights posture.

This is a provenance decision only. It does not admit a measurement row or
change the historical TASK-1052 verdict.

## Exact source locator

- DOI: `10.3390/nano10081589`.
- Version of record: PDF page 4 of 8, Section 3, paragraph immediately after
  Figure 2 and immediately before Figure 3.
- Europe PMC full text: Section 3 paragraph beginning with the Figure 3a
  description, immediately before the Figure 3 block.
- Pinned PDF SHA-256:
  `2dab8a6b4db18af88f7175ac0773747fe1aeb15d88f951a4a8536cdc2dd73edb`.
- Pinned JATS SHA-256:
  `6642fed609ad6540b61ca856d293d2b469c5ed7be9323479c9b76b023f668244`.

The paragraph first gives the ordered Figure 3(a) particle sizes, then the
absorption-peak sequence, then the fluorescence-peak sequence. Sequence
position therefore supplies the sample mapping; agreement with digitized
coordinates is not used.

## Complete text-stated mapping

| Sample | Paragraph size position (nm) | Absorption peak (eV) | Fluorescence peak (eV) |
| --- | ---: | ---: | ---: |
| `CdSe-1` | 2.5 | 2.54 | 2.44 |
| `CdSe-2` | 3.5 | 2.41 | 2.30 |
| `CdSe-3` | 3.7 | 2.31 | 2.18 |
| `CdSe-4` | 4.5 | 2.18 | 2.06 |

Completeness is 4/4 samples and 8/8 axis statements. The optical paragraph's
2.5 nm first position differs from the primary HRTEM summary of 2.7 +/- 0.5 nm
already preserved by TASK-1052. A future extraction must retain both reported
contexts without averaging or silently substituting one for the other.

## Provenance and uncertainty decision

`text_stated_summary` is admissible as a distinct factual provenance class.
It is not `figure_digitized_spectrum_peak`. The source prints peak energies to
0.01 eV, so the future contract records a rounding floor of 0.005 eV. This is
not instrument uncertainty; instrument uncertainty remains `not_reported`.

Absorption and fluorescence remain separate property kinds. Neither may be
relabeled as bandgap. Morphology remains `unknown_non_spherical`; no
equivalent-sphere conversion is allowed.

## Immutable historical boundary

TASK-1043 and TASK-1052 remain unchanged:

- the printed-y-tick requirement is unchanged;
- all eight digitized optical observations remain excluded;
- `UNCERTAINTY_BLOCKED` remains the digitization verdict;
- diagnostic digitized coordinates cannot become primary values;
- digitization agreement may appear only as a labelled non-admission
  cross-check and cannot decide text-route admissibility.

The adjacent machine-readable contract contains zero measurement rows and
predeclares the only permitted future schema.

## Rights, routing, and next action

The pinned version of record is CC BY 4.0. Attributed factual extraction is
rights-compatible; publisher source bytes remain uncommitted under the existing
metadata-only posture.

A new canonical data-curation task may extract exactly eight text-reported
rows, preserve the source locator and rounding floor, and perform no scoring.
This task itself creates no `qd-*.yaml`, split, fit, metric, RESULT, PRED,
CLAIM, or KNOW artifact. Gate A and Gate B are not attempted; claim and
knowledge impact are none.
