# Quantum Almeida Raster/Export Row-Readiness Gate (TASK-0797)

**Verdict:** `DIGITIZATION_PROVIDED__ROWS_EXTRACTABLE__PENDING_REVIEWER_REPLAY`

The single blocker that `TASK-0755` / `TASK-0797` preserved — the missing exact
Almeida size-axis raster or replayable export — is resolved. A maintainer-
supplied version-of-record figure asset is now available locally, and the size
axis has been digitized by a deterministic, replayable extractor. Direct InP
`(size, E1s)` rows are now extractable. They are **not yet curated** as canonical
`qd-*.yaml` rows: the extraction tier is `deterministic_figure_extraction` and
requires independent reviewer replay first.

## Artifact provenance

- Source: Almeida et al., *Size-Dependent Optical Properties of InP Colloidal
  Quantum Dots*, Nano Letters 2023, 23 (18), 8697-8703.
- DOI `10.1021/acs.nanolett.3c02630`; license **CC-BY 4.0** version-of-record
  (PMC `PMC10540257`, zero embargo; confirmed TASK-0741).
- Figure: Figure 2b — `E1s vs Edge Length (x10 A)` and `E1s vs Volume (nm^3)`,
  *This work* filled-triangle markers (six samples, lambda1s 460-620 nm).
- Asset locator: `https://pubs.acs.org/cms/10.1021/acs.nanolett.3c02630/asset/images/large/nl3c02630_0001.jpeg`
- Asset SHA-256 `3b7a37c9c5b0377f0101288f91ea4a4ae27294ab3670c6b9489224969e68e2ce`
  (not vendored — checksum + locator only).

## What was produced

- `scripts/extract_almeida_sizing.py` — deterministic extractor (axis-tick
  calibration + filled-marker centroiding; no LLM coordinates, no formula
  substitution; SHA-gated, byte-reproducible).
- `data/quantum_dots/digitization/almeida-2023-nano-letters-inp-optical/axis_calibration.csv`
- `data/quantum_dots/digitization/almeida-2023-nano-letters-inp-optical/extracted_points.csv`
- `data/quantum_dots/digitization/almeida-2023-nano-letters-inp-optical/notes.md`
  (method, provenance, QC, reviewer-replay command, no-claim scope).

## Extracted size axis (Edge Length panel = primary)

| lambda1s (nm) | E1s (eV, known) | L (nm) | +/- (nm) | core_px |
| --- | --- | --- | --- | --- |
| 460 | 2.695 | 1.50 | 0.18 | 13 |
| 480 | 2.583 | 1.99 | 0.27 | 19 |
| 510 | 2.431 | 2.54 | 0.49 | 14 |
| 550 | 2.254 | 2.76 | 0.40 | 10 |
| 580 | 2.138 | 3.13 | 0.09 | 12 |
| 620 | 2.000 | 4.10 | 0.46 | 2 (flagged) |

Volume panel extracted in parallel (secondary; mid-range markers overlap with
wide error bars — see `extracted_points.csv`).

## Cross-checks (passed)

- Smallest dot L = 1.50 nm matches the README text anchor exactly.
- L monotonic with E1s; cross-panel `V ~ 0.118 L^3` consistent.
- Measured vs known E1s agree to <= 0.01 eV; points on the published fit within
  <= 0.10 eV scatter.

## Limitations / readiness

- `>= 6` direct InP rows are extractable, satisfying the row-count floor, **but**
  one edge-length point (lambda620 / E1s 2.0) and one volume point have low
  solid-core pixels due to overlap with an *Xu et al.* open marker; flagged
  `included_flag_review`.
- Tier is `deterministic_figure_extraction`; **reviewer replay is required**
  before curating canonical `qd-almeida-2023-inp-optical.yaml` rows.
- No baseline metric, model fit, or claim is produced here.

## Output routing

- Task verdict: source-to-row readiness gate cleared (digitization provided).
- Canonical destination: `data/quantum_dots/digitization/.../` (source curation).
- Review tier: none (source artifact); extraction tier
  `deterministic_figure_extraction`, `reviewer_replay_required: true`.
- Claim / knowledge impact: none.
- Next steps (separate task / PR): (1) independent reviewer replay of the
  extractor (byte match); (2) curate `qd-almeida-2023-inp-optical.yaml` with
  explicit edge-length size semantics + `DATA_LICENSES.yaml` CC-BY entry;
  (3) rerun the `TASK-0293` row-level readiness gate, which unblocks
  `TASK-0225` / `TASK-0226` / `TASK-0276`.
- Blockers remaining: independent replay + row curation (above). The
  source-raster blocker is cleared.
