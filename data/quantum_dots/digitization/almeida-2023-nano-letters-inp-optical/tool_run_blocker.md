# TASK-0755 Tool-Run Blocker

- Task: `TASK-0755`
- Source ID: `almeida-2023-nano-letters-inp-optical`
- Status: `DIGITIZATION_BLOCKED_SOURCE_RASTER_UNAVAILABLE`

## Summary

`TASK-0755` could not run a WebPlotDigitizer-class extraction because the exact
Almeida Figure 1b / SI Figure S2b raster, source page, or reusable
WebPlotDigitizer export was not available in the committed package or in the
accessible workspace.

No axis calibration, extracted point file, uncertainty ledger, or
`qd-almeida-2023-inp-optical.yaml` dataset was created. The deterministic
`E1s` optical-energy anchors recorded in `README.md` remain source evidence
only; they are not direct measurement rows without a digitized size axis.

## Required To Unblock

Provide one replayable input:

- the exact maintainer-supplied Almeida Figure 1b / SI Figure S2b raster or
  source page in a local checksum-verifiable form; or
- a WebPlotDigitizer-class export for the exact figure, including axis
  calibration anchors, extracted point coordinates, tool/version metadata, and
  per-point uncertainty notes.

Until then, `TASK-0293` and `TASK-0225` remain blocked.

