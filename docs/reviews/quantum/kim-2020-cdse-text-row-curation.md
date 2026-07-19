# TASK-1070: Kim-2020 CdSe text-row curation

## Verdict

**`TEXT_ROWS_CURATED_NO_SCORE`.** The frozen TASK-1064 paragraph mapping is
represented as exactly eight included observations: four absorption peaks in
`qd-0005` and four source-described fluorescence peaks, canonically named
`emission_peak_eV`, in `qd-0006`.

## Source and method

- DOI: `10.3390/nano10081589` (CC BY 4.0).
- PDF SHA-256: `2dab8a6b4db18af88f7175ac0773747fe1aeb15d88f951a4a8536cdc2dd73edb`.
- Europe PMC JATS SHA-256: `6642fed609ad6540b61ca856d293d2b469c5ed7be9323479c9b76b023f668244`.
- Locator: Section 3, PDF page 4 of 8, paragraph immediately before Figure 3.
- Method: direct transcription of the four ordered particle sizes, four
  absorption peaks, and four fluorescence peaks frozen by TASK-1064.

Every row records its source-local sample ID, PDF digest, locator,
`text_stated_summary` provenance, 0.01 eV printed precision, 0.005 eV rounding
floor, and `instrument_uncertainty: not_reported`. The fluorescence wording is
preserved while the schema axis remains `emission_peak_eV`.

## Boundaries

The text-stated 2.5 nm CdSe-1 size is retained as printed. It is not averaged
with or replaced by the separate 2.7 nm HRTEM summary in TASK-1052. Morphology
remains `unknown_non_spherical`; no equivalent spherical diameter is inferred.
The TASK-1052 figure coordinates remain excluded under its unchanged
`UNCERTAINTY_BLOCKED` verdict and were not used to admit these rows.

## Output routing

- Canonical destination: `data/quantum_dots/qd-0005-kim-2020-cdse-absorption.yaml`
  and `data/quantum_dots/qd-0006-kim-2020-cdse-emission.yaml`.
- Gate A / Gate B: not attempted; this is source-row curation, not a result.
- Claim impact: none.
- Knowledge impact: none.
- Publication blocker: any benchmark requires a separately frozen task with a
  split, eligible controls, and treatment of rounding and missing instrument
  uncertainty. These eight rows alone do not establish a confinement law.
