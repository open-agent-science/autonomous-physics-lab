# FRB Catalog 2 Temporal Split And Exposure-Only Baseline

Task: `TASK-0852`
Domain: Radio transients astrophysics
Mode: source pinning + version-locked split specification + exposure-only baseline gate
Verdict: `SPLIT_AND_EXPOSURE_BASELINE_READY`
Run date: `2026-06-28`

## Scope And Non-Goals

This task advances the FRB repeater selection-effect audit by one bounded step.
It pins the public CHIME/FRB Catalog 2 CSV locator and checksum, records a
version-locked no-leakage temporal split specification, and freezes an
aggregate exposure-only baseline gate that later morphology models must beat
out-of-sample.

It does not vendor the upstream catalog bytes, fit a morphology model, create a
PRED, create a RESULT artifact, promote a claim, or scaffold the full FRB
campaign.

Inputs reviewed:

- [frb-chime-source-readiness-temporal-split-scout.md](frb-chime-source-readiness-temporal-split-scout.md)
- [frb-chime-access-reverify-readiness.md](frb-chime-access-reverify-readiness.md)
- [../published-source-dataset-standard.md](../published-source-dataset-standard.md)
- [../blind-holdout-benchmark-protocol.md](../blind-holdout-benchmark-protocol.md)
- [../../tasks/TASK-0852-frb-catalog2-temporal-split-and-exposure-baseline.yaml](../../tasks/TASK-0852-frb-catalog2-temporal-split-and-exposure-baseline.yaml)

Committed outputs:

- [../../data/radio_transients/frb_catalog2_source_manifest.yaml](../../data/radio_transients/frb_catalog2_source_manifest.yaml)
- [../../data/radio_transients/frb_catalog2_temporal_split_exposure_baseline.yaml](../../data/radio_transients/frb_catalog2_temporal_split_exposure_baseline.yaml)
- [../../scripts/run_frb_catalog2_exposure_baseline.py](../../scripts/run_frb_catalog2_exposure_baseline.py)

## 1. Pinned Public Source Locator

The public CANFAR storage listing now resolves for the maintainer-confirmed
vault path:

```text
https://www.canfar.net/storage/vault/list/AstroDataCitationDOI/CISTI.CANFAR/25.0066/data/table
```

The table directory lists:

```text
chimefrbcat2.csv   3.87 MB   /AstroDataCitationDOI/CISTI.CANFAR/25.0066/data/table/chimefrbcat2.csv
chimefrbcat2.fits  7.27 MB
chimefrbcat2.json 10.45 MB
chimefrbcat2.npy  22.94 MB
```

The CSV file was fetched to `C:/tmp/chimefrbcat2.csv` only, then verified and
left out of the repository. The pinned source metadata is:

```text
VOSpace URI: vos://cadc.nrc.ca~vault/AstroDataCitationDOI/CISTI.CANFAR/25.0066/data/table/chimefrbcat2.csv
Storage endpoint: https://cadc-west-01.canfar.net/vault/files/AstroDataCitationDOI/CISTI.CANFAR/25.0066/data/table/chimefrbcat2.csv
Bytes: 4057396
SHA-256: 5108ada779d279a2547d9f9e73ae25bfdd40d8496d6ba7255ec29c6629057a48
HTTP Digest header: md5=6OhFih4Hv5kP3BS/UaygSA==
Last-Modified: Mon, 05 Jan 2026 23:16:21 GMT
```

Replay command:

```powershell
C:\Users\sviti\Documents\APL\.venv\Scripts\python.exe scripts\run_frb_catalog2_exposure_baseline.py --download-csv C:/tmp/chimefrbcat2.csv --csv C:/tmp/chimefrbcat2.csv --output-dir data/radio_transients
```

Rights boundary: the vault files are public-readable and the source is citable,
but the DataCite `rightsList` is still empty. Under the APL published-source
standard, this PR is metadata-only: it commits locator, checksum, attribution,
and aggregate metrics, but not upstream catalog rows or exposure-map bytes.
Bulk derived-row publication remains unapproved without a maintainer-recorded
license or permission decision.

## 2. Version-Locked Temporal Split

Date-locking alone is not sufficient. A one-table filter such as "take Catalog
2 rows before T as features and after T as labels" leaks future information,
because Catalog 2 reprocesses earlier bursts and source associations with a
later analysis framework. That can leak post-T morphology, source grouping,
exposure accumulation, and repeater classification into the pre-T view.

The frozen split spec in
[../../data/radio_transients/frb_catalog2_temporal_split_exposure_baseline.yaml](../../data/radio_transients/frb_catalog2_temporal_split_exposure_baseline.yaml)
therefore requires:

- a pre-T feature version that contains only information available at T;
- a strictly later catalog version or reveal record for repeat/no-repeat labels;
- first-detection time defined as minimum finite `mjd_inf`, falling back to
  `mjd_400`, over bursts assigned to a source;
- T-truncated exposure for any predictive split, not full-window exposure
  summaries;
- source-association and repeater-classification changes between versions
  treated as outcomes, not pre-T inputs.

This is a split specification, not a morphology benchmark. The future pilot must
still construct the T-truncated pre-T view before scoring any predictive model.

## 3. Exposure-Only Baseline Gate

The baseline uses no morphology features. It groups population-eligible rows by
source, where source id is `repeater_name` for repeaters and `tns_name` for
apparent one-offs. It keeps rows with `excluded_flag == '0'`, requires finite
`exp_up` and `exp_low`, and scores each source as:

```text
score = log1p(max(exp_up + exp_low) over population-eligible bursts for the source)
```

The label is whether the source has non-empty `repeater_name` in Catalog 2
population-eligible rows. This is deliberately an exposure gate, not a final
predictive split, because it uses full-window Catalog 2 exposure summaries.

Aggregate counts from the verified CSV:

| Quantity | Value |
| --- | ---: |
| Raw burst rows | 5045 |
| Population-eligible burst rows (`excluded_flag == '0'`) | 4636 |
| Source rows with finite exposure | 3338 |
| Repeater sources with finite exposure | 81 |
| Non-repeater sources with finite exposure | 3257 |

Exposure calibration by source-level exposure quintile:

| Quintile | Sources | Exposure range | Repeater sources | Observed repeat rate |
| --- | ---: | ---: | ---: | ---: |
| 1 | 667 | 0.292131 - 81.969372 | 11 | 0.016492 |
| 2 | 668 | 81.978250 - 102.151598 | 15 | 0.022455 |
| 3 | 667 | 102.288104 - 139.455247 | 15 | 0.022489 |
| 4 | 668 | 139.540545 - 448.059002 | 16 | 0.023952 |
| 5 | 668 | 449.047941 - 18611.498000 | 24 | 0.035928 |

The exposure-only signal is weak but in the expected direction:

- top/bottom quintile repeat-rate ratio: `2.178511`;
- rank AUC for `log1p(exposure)`: `0.581459875596`;
- one-feature logistic standardized coefficient: `0.306021899652`;
- odds ratio per 1 SD log-exposure: `1.358012046214`.

This is enough to freeze the exposure-only baseline gate: any future morphology
model must beat this out-of-sample on the version-locked split before morphology
evidence is interpreted. It is not enough to claim a morphology signal.

## 4. Verdict

`SPLIT_AND_EXPOSURE_BASELINE_READY`.

The source locator and checksum are pinned, raw data is not vendored, the
version-lock requirement is explicit, and the exposure-only baseline has a
positive aggregate calibration check. The task remains bounded: it produces a
source-readiness and baseline-gate artifact, not a morphology model, PRED,
RESULT, claim, or campaign scaffold.

## Output-Routing Summary

- Task verdict: `SPLIT_AND_EXPOSURE_BASELINE_READY`.
- Canonical destination: metadata-only source manifest,
  version-locked temporal split spec, aggregate exposure-only baseline artifact,
  and this review note.
- Review tier: `none`. Gate A: not applicable. Gate B: not applicable.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result/PRED impact: no `results/` artifact and no `prediction_registry/`
  entry.
- Data boundary: public-readable source; no upstream catalog bytes or bulk rows
  committed because redistribution rights are not explicit.
- Main blocker for next task: construct a T-truncated, version-locked pre-T
  exposure view before any morphology benchmark or prospective PRED is allowed.