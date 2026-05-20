# Quantum Direct-Measurement Absorption Seed Investigation

**Task:** TASK-0291
**Status:** review (no qd-*.yaml seed produced; task is REVIEW_READY pending maintainer-led `BLOCKED` closeout)
**Inputs reviewed:**

- `data/quantum_dots/source_manifest.yaml`
- `data/quantum_dots/qd-0001-yu-2003-absorption.yaml`
- `docs/reviews/quantum-size-row-level-data-readiness-for-baseline.md`
- `docs/reviews/quantum-direct-measurement-source-triage.md`
- `docs/reviews/quantum-size-yu-2003-row-level-seed-review.md`
- `docs/quantum-direct-measurement-digitization-protocol.md`
- `data/quantum_dots/digitization/README.md`
- `physics_lab/schemas/quantum_dot_size_effect.schema.json`
- `tasks/TASK-0291-curate-quantum-direct-measurement-absorption-seed.yaml`
- Yu, W. W.; Qu, L.; Guo, W.; Peng, X. *Chem. Mater.* **2003**, *15*, 2854–2860,
  DOI [10.1021/cm034081k](https://doi.org/10.1021/cm034081k), full PDF
  accessed via the publicly mirrored copy at
  [`https://www.ocf.berkeley.edu/~paulpeng/docs/cds_references/optical/yu_cm_2003.pdf`](https://www.ocf.berkeley.edu/~paulpeng/docs/cds_references/optical/yu_cm_2003.pdf).

## Scope

This note records a first-attempt investigation by an LLM-only curator
against the source triaged as the top first-attempt candidate for TASK-0291
(Yu 2003 cadmium-chalcogenide absorption). It does not produce a row-level
`qd-*.yaml` dataset file, does not modify `qd-0001`, does not touch
`source_manifest.yaml`, and does not unblock TASK-0225 or TASK-0293.

The purpose of the investigation is to confirm or falsify the TASK-0298
expectation that Yu 2003 exposes direct-measurement (diameter, first-exciton
absorption peak) rows usable for a measurement-grade dataset seed.

## Method

1. Re-read the source-manifest entry for `yu-2003-cm-absorption` and the
   TASK-0298 triage classification (likely_direct_measurement *and*
   calibration_derived, extractable form table_values; figure_points
   fallback).
2. Located a publicly accessible PDF mirror of Yu 2003 via web search.
3. Fetched the PDF and read it end-to-end, paying particular attention to:
   - any printed table of (diameter, absorption peak wavelength) values;
   - Figure 2 (sizing curves for CdTe, CdSe, CdS) and its provenance;
   - the published empirical polynomial fits (D as a function of λ);
   - the paper's own treatment of measurement uncertainty.
4. Compared what the paper actually exposes to the TASK-0291 requirement
   that rows be "direct table values, digitised figure points, or
   independently reviewed TEM + spectroscopy observations, not values
   generated from a published sizing polynomial or calibration curve."
5. Re-checked the merged TASK-0306 digitisation protocol and the committed
   `data/quantum_dots/digitization/` surface. The protocol defines the
   artifact shape, but the repository still contains no per-source
   axis-calibration or extracted-point artifact that would support direct
   Yu 2003 Figure 2 rows.

## Findings

### F1. No tabulated (diameter, absorption peak) values in Yu 2003

The paper does not include a numerical table that lists discrete
(material, diameter, λ_first_exciton) triples. The closed-form output of
the paper is the set of empirical polynomial fits printed in the text:

- CdTe: `D = 9.8127e-7·λ³ − 1.7147e-3·λ² + 1.0064·λ − 194.84`
- CdSe: `D = 1.6122e-9·λ⁴ − 2.6575e-6·λ³ + 1.6242e-3·λ² − 0.4277·λ + 41.57`
- CdS:  `D = −6.6521e-8·λ³ + 1.9557e-4·λ² − 9.2352e-2·λ + 13.29`

The paper explicitly notes that these polynomials were added at a reviewer's
request: *"Upon the suggestion of a reviewer of the first version of the
manuscript, the empirical fitting functions of the curves shown in Figure 2
are provided as follows."*

These polynomials are exactly the surface that `qd-0001-yu-2003-absorption.yaml`
already exposes. They are calibration-derived per the TASK-0283 readiness
review and are not direct measurements.

### F2. Figure 2 is the only direct-measurement surface in Yu 2003

The discrete TEM (and XRD for very small clusters) measurements live only
as scatter-plot points on Figure 2. The paper records:

- *"The data shown in Figure 2 were all originally determined by TEM
  measurements, except the very small CdSe and CdS nanoclusters which were
  examined by XRD."*
- *"For CdTe, the sizes of the nanocrystals were mostly determined by us,
  as related information is scarce in the literature."*
- *"For CdSe nanocrystals, there is a rich literature published by several
  groups, and all those literature values are included in Figure 2."*
- *"For CdS nanocrystals, values of small sizes are mostly from Vossmeyer
  et al. and the big ones are largely based on our own results."*

So Figure 2 has mixed provenance:

- **CdTe** — predominantly original Yu et al. measurements;
- **CdSe** — Yu et al. plus Peng 1998, Murray 1993, Soloviev 2000 (and other
  cited group results);
- **CdS** — Yu et al. plus Vossmeyer 1994 for the small-size cluster regime.

A curator extracting rows from Figure 2 must split each row by primary
provenance and not attribute every point to Yu 2003.

### F3. Stated paper-internal uncertainty on direct points

The paper records its own uncertainty budget for the ε values on Figure 4
and notes the analogous size-error sources for Figure 2:

- TEM edge accuracy: *"the edge of a nanocrystal determined by TEM can be
  accurate only to approximately one lattice plane"*;
- Sample size distribution: *"around 5–10% standard deviation"*;
- Combined error: *"will likely bring about 20–30%, or ±10–15%, standard
  deviation"*.

This is the floor uncertainty even with an ideal extraction; any additional
digitisation error from reading a scatter plot stacks on top of it.

### F4. LLM-only digitisation is below the precision floor

An LLM-only agent without a figure-digitisation tool can read Figure 2
points only as eyeball approximations. Realistic per-point precision for
that mode is roughly ±0.3–0.5 nm in diameter and ±5–10 nm in wavelength.
Combined with the paper's own ±10–15% uncertainty, the resulting rows would
have *worse* effective precision than the calibration-evaluated values that
`qd-0001` already exposes.

Producing such rows would not satisfy the TASK-0291 intent. The task
explicitly distinguishes direct values from calibration-curve evaluations
*to improve* the readiness gate, not just to relabel the provenance metadata.

### F5. Alternative source surfaces are gated by external paper access

The cited prior literature surfaces that supply discrete Figure 2 points —
Vossmeyer 1994 (CdS small cluster regime), Soloviev 2000 (CdSe small
cluster regime via XRD), Murray 1993 (CdSe size series), and Peng 1998
(CdSe size series) — would in principle be the right primary tables to
curate, but each requires its own source-manifest review pass and its own
PDF access. None of those sources is currently in
`data/quantum_dots/source_manifest.yaml`.

### F6. TASK-0306 defines the path but does not supply the evidence

`docs/quantum-direct-measurement-digitization-protocol.md` now defines the
WebPlotDigitizer-class workflow required for figure-derived rows, including
axis calibration, per-point extracted coordinates, uncertainty, source
attribution, and a lightweight artifact layout under
`data/quantum_dots/digitization/<source_id>/`.

The current repository has only the digitisation README. It has no
`yu-2003-cm-absorption` artifact directory, no `axis_calibration.csv`, no
`extracted_points.csv`, and no reviewed primary-source table values. That
means TASK-0306 satisfies the protocol-definition prerequisite, but it does
not satisfy TASK-0291's evidence prerequisite for committing a `qd-0003`
direct-absorption seed.

## What This Investigation Did Not Do

- It did not edit `data/quantum_dots/qd-0001-yu-2003-absorption.yaml`.
- It did not add a new `qd-0003*.yaml` file, even as a placeholder.
- It did not register any new source in `source_manifest.yaml`.
- It did not redistribute tables or figures from Yu 2003 or any other
  publication.
- It did not promote any claim, knowledge entry, or canonical result.
- It did not unblock TASK-0225 or TASK-0293.

## Decision

This PR sets TASK-0291 to `REVIEW_READY` so the maintainer can review the
investigation. No `qd-0003` dataset is produced in this pass because doing so
would require either a committed digitisation artifact, primary-source table
values, maintainer-provided rows, or an explicit waiver. The intended
post-merge closeout status is `BLOCKED`
(not `DONE`), held until at least one of the unblock paths recorded in the
task file is satisfied:

- (a) WebPlotDigitizer-class workflow over Yu 2003 Figure 2 with per-point
  uncertainty, source attribution (Yu 2003 original vs cited prior
  literature), and material labels, committed alongside the seed file;
- (b) maintainer or human curator with access to primary source tables in
  Vossmeyer 1994, Soloviev 2000, Murray 1993, or Peng 1998 (plus
  corresponding `source_manifest.yaml` entries);
- (c) maintainer-provided table values for at least 6 direct-measurement
  (material, diameter, absorption peak) rows with documented provenance
  and uncertainty;
- (d) maintainer waiver explicitly permitting figure-digitised rows from
  Yu 2003 with relaxed precision constraints, recorded in the seed file's
  `notes` and the campaign page.

This is a deliberate negative result. It is recorded so a follow-up
curator does not repeat the same investigation against the same source
without one of the four unblock conditions in place.

## Limitations

- This pass did not run WebPlotDigitizer or an equivalent figure-digitisation
  tool and did not add any digitisation artifact.
- The investigation relied on the publicly mirrored PDF at the URL above;
  if that mirror diverges from the official ACS-published version, the
  finding about absent tables should be re-verified against the canonical
  version of record.
- The investigation does not estimate how many direct rows a full
  WebPlotDigitizer pass would produce; it only confirms that a non-tool
  agent cannot meet the precision floor.
- No conclusion is drawn here about TASK-0292 (band-edge seed against
  Jasieniak 2011); that source has a different table/figure structure and
  requires its own investigation under TASK-0292.
- No comment is offered about whether Moreels 2009 PbS could be re-curated
  as a direct seed; the TASK-0298 triage already records that source as a
  secondary candidate, and a separate investigation would be needed.

## Verdict

`INCONCLUSIVE` for the row-level seed (no rows curated); `VALID` as a
documented negative result that explicitly defines the unblock path for
TASK-0291.
