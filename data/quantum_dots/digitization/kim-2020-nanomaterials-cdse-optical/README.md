# Kim 2020 CdSe Figure 3a extraction blocker

Task: `TASK-1052`

This package records the real-value extraction attempt for Kim et al. 2020,
"Influence of Size and Shape Anisotropy on Optical Properties of CdSe Quantum
Dots" (doi:10.3390/nano10081589). The source PDF and derived figure raster are
not committed.

`extraction_ledger.yaml` contains the repeated source pins, four text-stated
HRTEM size summaries, two independent WebPlotDigitizer 4.8 sessions, eight
diagnostic peak pairs, the repeatability calculation, and the final blocker.

The two sessions agree within the frozen coordinate tolerances. They do not
satisfy the frozen calibration contract because Figure 3a prints no numeric
y-axis ticks. The panel-frame normalization is diagnostic only, all eight
optical observations remain excluded, and no `qd-*.yaml` row is authorized.

Replay requires fetching the version-of-record PDF at the locator and SHA-256
recorded in the ledger, extracting PDF page 5 image objects 35 and 36, and
appending them top-to-bottom. The WPD sessions used that stitched raster; the
documented origin-preserving Figure 3a crop is a checksum cross-check. Do not
commit the PDF, embedded JPEGs, stitched figure, or crop.
