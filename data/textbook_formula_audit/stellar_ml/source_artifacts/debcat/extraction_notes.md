# DEBCat Extraction Notes

Task: `TASK-0628`
Source ID: `debcat-detached-eclipsing-binaries`
Extraction status: not started

## Artifact Shape

The source page links a machine-readable ASCII table at:

```text
https://astro.keele.ac.uk/jkt/debcat/debs.dat
```

During TASK-0628 the table was downloaded only to sandbox temp for checksum
verification:

```text
D:\Python\APLab\tmp\TASK-0628\debs.dat
```

That file is value-bearing source data and is not committed.

## Fields To Preserve In A Later Row Task

- physical binary system identifier;
- component role (primary/secondary);
- component mass and mass uncertainty;
- radius and radius uncertainty;
- effective temperature and uncertainty when present;
- luminosity/log-luminosity field semantics if used;
- metallicity and source-reference notes when relevant;
- source reference and catalogue update/version metadata.

## No-Leakage Rules

Any later train/test or holdout split must be by physical binary system before
component-level rows are used. The two components of the same binary must not
appear in different evaluation lanes.

## Non-Goals

This package does not parse the ASCII table, transcribe rows, normalize
columns, compute luminosities, fit mass-luminosity exponents, or run residual
metrics.
