# DEBCat Extraction Notes

Task: `TASK-0628` (source package), `TASK-0708` (row extraction)
Source ID: `debcat-detached-eclipsing-binaries`
Extraction status: completed by `TASK-0708` (see extraction ledger below)

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

## Non-Goals (TASK-0628 source package)

The original TASK-0628 source package did not parse the ASCII table, transcribe
rows, normalize columns, compute luminosities, fit mass-luminosity exponents, or
run residual metrics. TASK-0708 performs the row extraction below; it still does
not fit exponents or inspect residuals.

## TASK-0708 Extraction Ledger

- Extraction script: `scripts/extract_debcat_stellar_ml_rows.py`
  (deterministic, cross-platform; raw `debs.dat` is **not** committed).
- Source artifact: `https://astro.keele.ac.uk/jkt/debcat/debs.dat`, fetched to a
  local temp path only and verified byte-for-byte against the pinned checksum
  `326902535b4da2fd94f227806ff339247d6df224ef8faea8857703e553b464da`
  (95297 bytes, 374 system records). The script refuses to curate if the
  checksum drifts.
- Column mapping (`debs.dat` -> normalized row), per component `n` in {1, 2}:
  - `System` -> `system_id`
  - `SpTn` -> `spectral_type`
  - `logMn`, `logMne` -> `log_mass_solar`, `log_mass_solar_unc`
    (`mass_provenance_class: direct_observation`, DEBCat dynamical mass)
  - `logLn`, `logLne` -> `log_luminosity_solar`, `log_luminosity_solar_unc`
    (`luminosity_provenance_class: direct_observation`) when populated
  - fallback when `logLn` is the `-9.99` sentinel: Stefan-Boltzmann from
    `logRn`, `logTn` -> `log_luminosity_solar`
    (`luminosity_provenance_class: derived_luminosity`),
    `log10(L/Lsun) = 2*logR + 4*(logT - log10(5772))`,
    `sigma_logL = sqrt((2*sigma_logR)^2 + (4*sigma_logT)^2)`.
- Missing-value sentinel: `-9.99` (`-9.9900` in the table).
- Luminosity provenance: DEBCat catalogue-reported (Southworth 2015). The
  machine-readable `debs.dat` does not expose per-row primary-literature
  pointers; catalogue-level provenance is recorded and flagged as a limitation
  in `docs/reviews/stellar-ml-debcat-row-package.md`.
- Holdout split: deterministic, value-blind
  `bucket = int(sha256(system_id), 16) % 10` (0-4 train, 5-6 validation,
  7-9 holdout), frozen before any residual inspection. Both components of one
  physical binary always share one lane.
- Results: 373 unique systems (374 records; one ambiguous duplicate id),
  742 admitted component rows (597 direct-luminosity, 145 SB-derived),
  6 excluded (4 ambiguous-duplicate `Gaia_DR3_4658237043035232256`,
  2 `no_admissible_luminosity_path`).
- Publication posture (TASK-0763/TASK-0779): the full normalized rows and
  frozen holdout manifest are committed under explicit CC BY 4.0 permission,
  each with a sibling license marker. The raw `debs.dat` table remains
  uncommitted under the Route 2 checksum-pinned source posture. The
  non-substitutive samples remain only for quick inspection and fixture use.
- Reproduce the full rows locally: fetch
  `debs.dat` with `scripts/fetch_source_artifact.py`, confirm the checksum, then
  `python3 scripts/extract_debcat_stellar_ml_rows.py --debs-dat <path>
  --out-rows <local>/debcat_component_rows.yaml
  --out-manifest <local>/debcat_holdout_manifest.yaml
  --generated-at 2026-06-12T00:00:00Z`.
