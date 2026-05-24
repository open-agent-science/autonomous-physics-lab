# Nuclear extrapolated/measured boundary lane

**Task:** `TASK-0341`
**Agent run:** `AGENT-RUN-0028`
**Evidence class:** sandbox-only retrospective source-status diagnostic
**Verdict:** `INCONCLUSIVE`

## Boundary

This run uses only committed repository rows and row-level source-status metadata. The boundary flag is the AME2020 comparison-column extrapolation marker on post-AME2020 measured rows. It writes no prediction registry entries, canonical results, claims, or knowledge artifacts.

## Source-Status Preflight

- Training measured rows: `11`.
- Post-AME2020 holdout rows: `295`.
- AME2020 measured-comparison rows: `240`.
- AME2020 extrapolated-comparison rows: `55`.
- Measurement-method families: `4`.
- Fit surface: `retrospective_full_known_diagnostic`.
- Preflight note: Usable for retrospective source-status diagnostics; not sufficient for a prospective physical correction because training rows are curated measured-only.

## Candidate And Control Results

| Candidate | Role | Full-known MAE | Holdout | Measured comparison | Extrapolated comparison | Edge | Neutron-rich | Magic region | High-error |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BOUNDARY-001 | executed_boundary_candidate | +0.013552 | +0.014058 | +0.009321 | +0.034726 | +0.027051 | -0.026405 | -0.030830 | -0.176031 |
| BOUNDARY-002 | executed_boundary_candidate | -0.002948 | -0.003058 | -0.001094 | -0.011624 | +0.001408 | -0.005470 | -0.010798 | +0.013567 |
| BOUNDARY-003 | executed_boundary_candidate | -0.012085 | -0.012536 | -0.006552 | -0.038648 | +0.070898 | -0.051573 | -0.037858 | -0.187539 |
| BOUNDARY-CONTROL-001 | measured_only_control | +0.026444 | +0.027430 | +0.033716 | +0.000000 | +0.132783 | -0.322848 | -0.091301 | -0.455785 |
| BOUNDARY-CONTROL-002 | extrapolated_only_control | -0.017957 | -0.018627 | +0.000000 | -0.099907 | +0.129216 | -0.499264 | -0.056297 | -0.142647 |
| BOUNDARY-CONTROL-003 | source_shuffled_control | -0.026839 | -0.027274 | +0.027910 | -0.268077 | +0.047231 | -0.439751 | -0.147353 | -0.491486 |
| BOUNDARY-CONTROL-004 | smooth_a_control | -0.405412 | -0.430186 | -0.463163 | -0.286290 | -0.493181 | +0.154074 | +0.034245 | +0.295519 |

Negative deltas mean lower MAE than the frozen semi-empirical baseline on that subset. Positive deltas are regressions and remain visible.

## Control Gate

| Candidate | Best control | Candidate primary | Best control primary | Beats controls |
| --- | --- | ---: | ---: | --- |
| BOUNDARY-001 | BOUNDARY-CONTROL-004 | +0.013552 | -0.405412 | no |
| BOUNDARY-002 | BOUNDARY-CONTROL-004 | -0.002948 | -0.405412 | no |
| BOUNDARY-003 | BOUNDARY-CONTROL-004 | -0.012085 | -0.405412 | no |

## Interpretation

- Generated boundary candidates: `6`.
- Executed boundary candidates: `3`.
- Executed controls: `4`.
- Best full-known delta: `BOUNDARY-CONTROL-004` (-0.405412 MeV MAE).
- The verdict stays conservative because the source-status terms are fit retrospectively on the committed surface.
- Any positive status signal is data-boundary diagnostic evidence only, not a physical-law or reveal-scoring result.

## Limitations

- The NMD-0002 fit slice is curated measured-only, so source-status terms are retrospective diagnostics, not prospective correction evidence.
- The extrapolated flag describes the AME2020 comparison column for new measured rows, not an extrapolated new measurement.
- Candidate coefficients are fit on the full committed surface and must not be treated as holdout validation.
- Measured/extrapolated and source-shuffled controls are included because status features can track provenance or sample composition.
- No source fetch, canonical result rewrite, PRED entry, claim update, or public-facing physics claim is authorized.
