# Quantum Direct-Measurement Digitization Protocol

## Purpose

This protocol defines when and how figure-derived measurement rows may
enter `data/quantum_dots/qd-*.yaml` files in the Quantum Size Effects
campaign.

It exists because the highest-priority direct-measurement source identified
by the TASK-0298 triage (Yu 2003 cadmium-chalcogenide absorption) does not
tabulate its discrete measurements. The investigation under TASK-0291
confirmed that the only closed-form output in Yu 2003 is the empirical
polynomial fit already exposed by `qd-0001`, while the direct TEM/XRD
points live only as scatter-plot points on Figure 2. Other registered
candidate sources (Moreels 2009 PbS absorption; Jasieniak 2011 band-edge)
have similar table-versus-figure tradeoffs.

Without a documented workflow, "direct-measurement" can drift into
"LLM-eyeballed graph point," which is exactly the failure mode that the
TASK-0283 readiness gate is designed to keep out of the dataset.

This protocol is upstream of `TASK-0291`, `TASK-0292`, and any later
campaign source that ships discrete measurement values primarily through
figures rather than tables.

## Scope

The protocol applies to:

- absorption-peak, emission-peak, and bandgap rows derived from a
  publication figure rather than a printed table;
- rows that mix figure-derived and table-derived sources in the same
  `qd-*.yaml` file;
- any new source added to `data/quantum_dots/source_manifest.yaml` whose
  inclusion rationale depends on figure-derived measurements.

It does **not** apply to:

- printed table rows where every value is a primary table entry;
- model-only references such as the Brus 1984 entry already marked
  `excluded` in the source manifest;
- canonical claims, knowledge entries, or result artifacts.

It does not authorise:

- scraping copyrighted figures into the repository;
- redistributing publication PDFs, supporting-information files, or
  full-resolution figure assets;
- fetching live external data from a curation script;
- unblocking `TASK-0225` (the baseline residual benchmark) without
  re-running the TASK-0283 readiness gate;
- adding synthesis protocols, device claims, or biomedical content.

## What Is Not Acceptable

The following are explicitly forbidden as direct-measurement provenance:

1. **LLM visual estimates.** A row whose `(diameter, energy)` values come
   from an LLM agent reading a rendered scatter plot is not acceptable.
   This includes "approximately read from Figure 2", "estimated from the
   figure panel", or any value without a per-point digitisation record.
2. **Memory-derived values.** A row whose values come from "the model
   recalled the table from training data" is not acceptable. Even if the
   recall is plausible, there is no verifiable per-point provenance.
3. **Polynomial-generated values.** A row whose value is the output of a
   published sizing polynomial (for example the Yu 2003 fits used by
   `qd-0001`) evaluated at a chosen size is calibration-derived, not a
   direct measurement.
4. **Implicit table reconstruction.** A row whose value is back-computed
   from a calibration formula plus a chosen TEM-style diameter is also
   calibration-derived.
5. **Aggregate or summary values.** A row that uses a mean, bin centre,
   or fitted curve value at a representative size instead of an original
   discrete point.

A row that fails any of (1)–(5) must not enter `qd-*.yaml` regardless of
how plausible the value looks; the failure mode is provenance, not
accuracy.

## Required Workflow

A figure-derived row may enter `qd-*.yaml` only when produced by the
following workflow.

### Step 1 — Identify and register the source

1. Locate the publication and identify the specific figure that contains
   the discrete (size, property) points.
2. Confirm there is no equivalent printed table in the main text or in
   the publicly available supporting information. If a printed table
   exists, use it instead and skip this protocol.
3. Add or update the `source_manifest.yaml` entry for the source with
   accurate citation metadata, DOI, table or figure reference, license
   note, and `checksum_policy`.
4. Record in the manifest `notes` field that figure-derived rows are
   permitted only via this protocol.

### Step 2 — Run a WebPlotDigitizer-class extraction pass

1. Use a deterministic figure-digitisation tool. Acceptable tools include
   [WebPlotDigitizer](https://automeris.io/WebPlotDigitizer/) and any
   equivalent open-source successor that records axis calibration points
   and per-point coordinates.
2. Calibrate both axes against printed tick marks visible on the figure.
   Record at least four calibration anchors (two per axis where possible)
   so a reviewer can verify the calibration.
3. Select each discrete data point individually. Do not interpolate along
   a fitted curve; do not average overlapping points.
4. Export the digitisation as a per-point artifact containing axis
   calibration, raw extracted (x, y) coordinates, and any extraction-tool
   metadata version. Commit the artifact under
   `data/quantum_dots/digitization/<source_id>/` (see Step 5).
5. The digitisation pass must be runnable by a reviewer with the same
   tool on the same figure. The artifact replaces an LLM eyeball.

### Step 3 — Assign per-point provenance

For each extracted point, record:

- **source_id** — the manifest entry the figure belongs to;
- **source_figure_ref** — the figure number and panel reference;
- **primary_source_id** — the original publication that contributed the
  point. For Yu 2003 Figure 2 this may be Yu 2003 itself for original
  measurements, or Vossmeyer 1994 / Soloviev 2000 / Murray 1993 / Peng
  1998 for cited prior literature. Each primary source must also have a
  manifest entry before its derived rows are committed;
- **axis_calibration_ref** — pointer to the digitisation artifact;
- **extraction_tool** — name and version of the digitisation tool;
- **coordinate_uncertainty** — explicit (Δsize, Δenergy) uncertainty
  combining the digitisation read error and the publication's stated
  measurement uncertainty. For Yu 2003 the floor is roughly ±10–15% per
  the paper's own error budget;
- **material**, **property_kind**, **measurement_type**, and
  **inclusion_status** as already required by the quantum-dot schema.

A point that cannot carry all of the above must be excluded with
`inclusion_status: excluded` and an explicit `exclusion_reason`, not
silently dropped.

### Non-Spherical Size Axes

If a source reports a non-spherical size quantity, do not coerce it into
`diameter_nm` without review. Use the schema axis that preserves the source
quantity (`edge_length_nm` or `volume_nm3`) and record the morphology, such
as `tetrahedral`, before any row can be included.

A reviewed equivalent-diameter route may be used only when the entry stores
`equivalent_diameter_nm` together with `size_conversion`, including the
original source size axis, original source value, source unit, equivalent
axis, and conversion rule. This preserves the source measurement while
allowing later model code to decide whether an equivalent spherical axis is
scientifically appropriate.

### Step 4 — Cross-check against the calibration formula

If the publication also provides a calibration polynomial or sizing
equation (as Yu 2003 does), evaluate the polynomial at the digitised size
for each row and record:

- the formula value;
- the residual `(digitised_energy − formula_energy)` in eV;
- whether the residual lies inside the publication's stated uncertainty
  band.

A row whose residual falls outside the paper's own uncertainty band is a
candidate for review. Do not silently overwrite the digitised value with
the formula value; that would collapse direct rows back into
calibration-derived rows.

### Step 5 — Commit the digitisation artifact

Commit the per-source digitisation artifact under:

```
data/quantum_dots/digitization/<source_id>/
  README.md            # short note describing the figure and panel
  axis_calibration.csv # axis anchor points and units
  extracted_points.csv # (point_id, raw_x, raw_y, material, primary_source_id, ...)
  notes.md             # extraction notes, tool version, reviewer attribution
```

The artifact layout is intentionally lightweight. A schema file is not
required for the first artifact but should be added when more than one
source ships figure-derived rows.

Do not commit raw figure images, original PDF pages, or
non-redistributable assets into the repository. The artifact must be
re-runnable from a publicly accessible source URL.

### Step 6 — Build the `qd-*.yaml` file

The figure-derived `qd-*.yaml` file:

- uses the next available `qd-NNNN` identifier;
- references the digitisation artifact under `data/quantum_dots/digitization/`;
- includes at least 6 rows that pass Steps 2–4;
- separates `absorption_peak_eV`, `emission_peak_eV`, and `bandgap_eV`
  per the existing campaign property-kind separation policy;
- explicitly excludes uncertain rows with `inclusion_status: excluded`;
- carries `notes` that name the figure, the digitisation artifact, the
  primary-source breakdown, and the residual-vs-formula cross-check.

The file should be reviewed against the schema by the same tests that
cover `qd-0001` and `qd-0002`. Update those tests if the schema needs
new optional fields.

## When Figure-Derived Rows Are Acceptable

A figure-derived row is acceptable only when all of the following hold:

- the source has no equivalent printed table in the main text or
  publicly available supporting information;
- a deterministic digitisation tool has been run and the artifact is
  committed;
- per-point provenance fields from Step 3 are recorded for every row;
- the residual-vs-formula cross-check from Step 4 is recorded;
- the file contains at least 6 rows that pass the gate, with explicit
  exclusion of any row that does not.

## When Figure-Derived Rows Are Not Acceptable

A figure-derived row is **not** acceptable, and a curator must escalate
to one of the other unblock paths in `TASK-0291`, when:

- a primary table is available in the same paper or a cited prior
  publication that already has a manifest entry;
- the figure does not contain enough discrete points to reach 6 rows
  after exclusions;
- the publication's stated measurement uncertainty already exceeds the
  benchmark's intended residual scale (typically ~0.05 eV at the
  per-material level);
- the figure mixes measurements from several primary sources that have
  not been independently registered in `source_manifest.yaml`;
- the agent does not have a deterministic digitisation tool available;
  in that case the row-level work must wait for a curator who does.

The last point is the binding case for the TASK-0291 first-attempt
investigation: an LLM-only agent has no access to a WebPlotDigitizer-class
tool, so figure-derived rows from Yu 2003 cannot enter the dataset until
either a human curator runs the workflow or the maintainer accepts an
explicit waiver with relaxed precision.

## Recommendation for TASK-0291

`TASK-0291` should remain `BLOCKED` until at least one of its four
unblock paths is satisfied. This protocol clarifies what unblock path
(a) — the WebPlotDigitizer-class workflow — requires in practice, but it
does not by itself unblock the task because no digitisation artifact is
committed by this PR.

A future curator who runs Steps 1–6 against Yu 2003 Figure 2 may unblock
`TASK-0291` without splitting it. The split into a separate
digitisation-artifact task is recommended only if the curator wants the
artifact reviewed independently of the seed file. In that case the
artifact-only task should be a `READY` micro-task scoped to Step 5 alone,
and `TASK-0291` should depend on its DONE status.

## Recommendation for TASK-0292

`TASK-0292` (direct band-edge seed against Jasieniak 2011) already has a
built-in escape clause permitting a review-only outcome if no
measurement-grade rows can be curated. The Jasieniak 2011 source
combines table values, figure-derived points, and electrochemistry-
derived band-edge measurements; the same workflow applies whenever the
band-edge rows come from a figure rather than a table.

## Relationship To Other Protocols

- `docs/quantum-size-effect-holdout-protocol.md` defines holdout rules
  for the benchmark; this protocol defines provenance rules for the
  rows that feed the benchmark. Holdout splits cannot fix bad
  provenance.
- `docs/reviews/quantum-size-row-level-data-readiness-for-baseline.md`
  remains the gate that determines whether `TASK-0225` can leave
  `BLOCKED`. A figure-derived seed must satisfy that gate the same way
  a table-derived seed does, with additional attention to per-point
  uncertainty.
- `docs/reviews/quantum-direct-measurement-source-triage.md` records
  per-source first-attempt recommendations. This protocol is the
  workflow that triaged sources must satisfy.
- `docs/reviews/quantum-size-direct-absorption-seed-review.md` is the
  TASK-0291 investigation that motivated this protocol.

## Limitations

- The protocol does not estimate how many direct rows a Yu 2003 Figure 2
  digitisation pass would actually yield; it only defines what such a
  pass must produce to be acceptable.
- The protocol does not specify a particular digitisation tool. Any
  WebPlotDigitizer-class tool with axis calibration, per-point export,
  and version metadata satisfies Step 2.
- The protocol intentionally does not relax the TASK-0283 readiness
  gate. A figure-derived seed must clear the same gate as a
  table-derived seed.
- The protocol does not authorise live external data fetches, even when
  a public PDF mirror is available.

## Verdict Vocabulary

When a digitisation pass is reviewed, the per-source review note should
use:

- `VALID` — full Steps 1–6 satisfied; rows enter `qd-*.yaml`.
- `PARTIALLY_VALID` — Steps 1–5 satisfied but fewer than 6 rows survive
  exclusions, or some rows lack a fully-traceable primary source. The
  artifact may be committed but the seed file is not yet usable.
- `INCONCLUSIVE` — Step 2 cannot be performed due to figure quality or
  ambiguous axis calibration. Record what blocked the pass.
- `INVALID` — any of the forbidden cases under "What Is Not Acceptable"
  applies. Do not commit the seed file.
