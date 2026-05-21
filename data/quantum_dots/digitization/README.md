# Quantum-Dot Figure-Digitisation Artifacts

This directory stores per-source figure-digitisation artifacts produced
under the workflow defined in
[`docs/quantum-direct-measurement-digitization-protocol.md`](../../../docs/quantum-direct-measurement-digitization-protocol.md).

## Purpose

A figure-derived `qd-*.yaml` row is acceptable only when it points to a
deterministic digitisation artifact stored under this directory. An LLM
visual estimate, a polynomial-derived value, or a recalled-from-training
value is not acceptable provenance.

## Layout

Each source that ships figure-derived rows gets a subdirectory keyed by
its `source_id` from
[`../source_manifest.yaml`](../source_manifest.yaml):

```
data/quantum_dots/digitization/<source_id>/
  README.md            # short note describing the figure and panel
  axis_calibration.csv # axis anchor points and units
  extracted_points.csv # (point_id, raw_x, raw_y, material, primary_source_id, ...)
  notes.md             # extraction notes, tool version, reviewer attribution
```

The layout is intentionally minimal. A formal JSON schema may be added
once more than one source ships figure-derived rows.

## What Belongs Here

- Per-point CSV exports from a WebPlotDigitizer-class digitisation pass.
- Axis-calibration anchor points with their pixel-or-printed coordinates.
- A short notes file recording the tool version, the figure reference,
  the reviewer attribution, and any exclusions made during extraction.

## What Does Not Belong Here

- Raw figure images or original PDF pages from publications.
- Full-resolution rasterisations of copyrighted figures.
- Cropped, redistributed, or screenshot assets that bypass the
  source's redistribution terms.
- Polynomial-derived values disguised as digitised points.
- LLM-eyeballed "approximate" coordinates without a digitisation tool.

The digitisation artifact must let a reviewer re-run the same extraction
against the publicly available source, not stand in for that source.

## Status

This directory currently contains one blocker package and no row-producing
digitisation artifact:

- `jasieniak-2011-acs-nano-band-edge/README.md` records the TASK-0325
  access/evidence blocker for the Jasieniak 2011 band-edge source path.

The first row-producing artifact must still add source-specific
`axis_calibration.csv`, `extracted_points.csv`, and extraction notes before
any `qd-*.yaml` row may claim figure-derived provenance pointing into this
directory.
