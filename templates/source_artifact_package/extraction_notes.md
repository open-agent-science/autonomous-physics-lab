# Extraction Notes

## Extraction Scope

Source ID: `replace-with-source-id`

Extraction status: `not_started`

This template records the extraction plan only. It contains no measured values,
row values, digitised points, benchmark metrics, predictions, claims, or
results.

## Source Location

Specify the exact source location before extraction:

- PDF page or table number:
- Supplementary file name:
- Figure panel:
- CSV column names:
- API endpoint and query contract:
- Repository release/tag:

## Method

Choose one:

- `direct_table`
- `manual_transcription`
- `figure_digitisation`
- `api_snapshot`
- `csv_snapshot`
- `calibration_curve_reconstruction`
- `metadata_only`

## Required Per-Row Or Per-Point Fields

- source id;
- source location;
- extraction method;
- extracted by;
- reviewed by;
- unit;
- uncertainty semantics;
- row class;
- inclusion status;
- blocker reason when excluded;
- accepted-for-benchmark flag.

## Figure Digitisation Requirements

For figure-derived points, record:

- source image checksum;
- axis calibration points;
- axis transform;
- digitisation tool and version;
- point-level extraction log;
- precision and rounding limits;
- independent review note.

## API Snapshot Requirements

For API-derived source artifacts, record:

- endpoint;
- query contract;
- retrieval timestamp;
- raw response checksum;
- normalized output checksum;
- live-fetch policy after pinning.

## Reviewer Notes

Template only. Replace this section in a source-specific package.
