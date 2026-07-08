# FRB Catalog 1 Pre-T Exposure Feature Surface

- Task: `TASK-0963`
- Domain: radio transients astrophysics
- Construction date: `2026-07-08`
- Fixed epoch: `T = 2019-07-02`
- Verdict: `PRE_T_EXPOSURE_FEATURE_SURFACE_CONSTRUCTED`

## Scope

This note records the deterministic construction of the first FRB campaign
pre-T exposure feature surface from the checksum-pinned Catalog 1 interval
exposure pair. The output is the compact derived fixture
`data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml`.

The construction does not read repeater labels, fit a model, select a model,
register a prediction, create a result, or change any claim or knowledge
artifact. Raw Catalog 1 NPZ bytes and the Catalog 2 CSV remain local,
untracked inputs only.

## Inputs Verified

The helper verified the already pinned local source identities before parsing:

| Input | Expected bytes | SHA-256 |
| --- | ---: | --- |
| Catalog 2 CSV | `4057396` | `5108ada779d279a2547d9f9e73ae25bfdd40d8496d6ba7255ec29c6629057a48` |
| Catalog 1 upper-transit NPZ | `186745827` | `088a0617104e5400dc12a8bcaf12621f3c61e82cab3eadc3f842cd6da7018536` |
| Catalog 1 lower-transit NPZ | `12800403` | `e8cc1a47b916fc5cb89f6df3ea0f07d57d5b2a1b22262e9ead57937100b5966a` |

The NPZ files were downloaded to `/private/tmp/apl-frb-task0963/` and were not
committed.

## Construction Rule

The source cohort is limited to Catalog-1-flagged Catalog 2 rows satisfying:

- `excluded_flag == "0"`;
- first finite detection MJD (`mjd_inf`, falling back to `mjd_400`) is at or
  before `58666.0`;
- finite `ra` and `dec`;
- non-empty `tns_name`.

The helper intentionally reads only these Catalog 2 columns:

- `tns_name`;
- `ra`;
- `dec`;
- `mjd_inf`;
- `mjd_400`;
- `excluded_flag`;
- `catalog1_flag`.

It does not read `repeater_name`, Catalog 2 full-window `exp_up` / `exp_low`,
morphology columns, or later source-association fields. The fixture uses
`source_id = tns_name` only, so no late repeater grouping is used as a feature.

For each source position, the helper computes the HEALPix `RING` pixel at
`NSIDE=4096`, reads the Catalog 1 upper/lower interval exposure counts at that
pixel, converts by the gate's frozen rule:

```text
E_hours = 4 * exposure_count / 3600
score_pre_t = log1p(E_upper_hours + E_lower_hours)
```

## Output Summary

| Field | Value |
| --- | ---: |
| Feature rows | `479` |
| Nonzero upper exposure rows | `462` |
| Nonzero lower exposure rows | `117` |
| Nonzero total exposure rows | `465` |
| Zero total exposure rows | `14` |
| Feature table SHA-256 | `3e564bc58452b34db133b72d1177bd99eb7fc8ac76036641edb9aa513a65d139` |

## Reproducibility Command

```bash
python3 scripts/run_frb_catalog1_pre_t_exposure_surface.py \
  --download-dir /private/tmp/apl-frb-task0963 \
  --output data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml \
  --generated-at-utc 2026-07-08T00:00:00Z
```

Use an untracked download directory. Do not stage the downloaded CSV or NPZ
files.

## Limitations

- The feature surface is valid only for the single approved epoch
  `2019-07-02`; arbitrary `T` values remain unsupported.
- The source identifier is the pre-label TNS name. Later repeater grouping and
  label reveal remain future-stage artifacts.
- This is an exposure-only feature surface, not a repeater model, not a
  prediction registry entry, and not an FRB population claim.
- The helper implements HEALPix RING indexing locally to avoid adding a runtime
  dependency; future independent replay may cross-check pixel indices with
  `healpy` if desired.
- The output is a compact derived fixture. It is not a substitute for the
  Catalog 1 exposure maps or Catalog 2 CSV.

## Output Routing

- Task verdict: `not_applicable`; construction verdict is
  `PRE_T_EXPOSURE_FEATURE_SURFACE_CONSTRUCTED`.
- Canonical destination:
  `data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml` and
  this review note.
- Review tier: none.
- Gate A / Gate B: not applicable.
- Dataset impact: one derived pre-T exposure feature fixture.
- Result / PRED impact: none.
- Claim impact: none.
- Knowledge impact: none.
- Next stage: `TASK-0964` may start only after this task's PR is merged, per
  the task's sequencing rule.
