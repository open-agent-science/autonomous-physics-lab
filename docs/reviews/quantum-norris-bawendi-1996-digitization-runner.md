# Quantum Norris-Bawendi 1996 Digitization Runner Preflight

**Task:** `TASK-0563`
**Campaign:** Quantum Size Effects
**Source ID:** `norris-bawendi-1996-prb-cdse-band-edge`
**DOI:** `10.1103/PhysRevB.53.16338`
**Verdict:** `BLOCKED_PENDING_LEGITIMATE_SOURCE_COPY_AND_TOOL_RUN`

## Scope

This task prepares a deterministic digitization-preflight package for the
Norris-Bawendi 1996 CdSe source path. It does not fetch, copy, crop, or commit
publisher source material; it does not run WebPlotDigitizer; it does not add
`qd-*.yaml` rows; and it does not run quantum-size baselines or promote claims.

## Inputs Reviewed

- `docs/source-candidates/quantum/quantum-direct-source-candidate-brief.md`
- `docs/reviews/quantum-norris-bawendi-source-artifact-review.md`
- `docs/reviews/quantum-norris-bawendi-1996-digitization-preflight.md`
- `docs/quantum-direct-measurement-digitization-protocol.md`
- `docs/published-source-dataset-standard.md`
- `docs/source-acquisition-lane.md`
- `data/quantum_dots/source_artifacts/norris-bawendi-1996-prb-cdse-band-edge/README.md`

## Package Added

The package is under:

```text
data/quantum_dots/digitization/norris-bawendi-1996-prb-cdse-band-edge/
```

It contains:

- `README.md` with source locator, blockers, point-state vocabulary, and
  uncertainty rules;
- `axis_calibration_template.csv`;
- `extracted_points_template.csv`;
- `extraction_ledger_template.csv`.

These are templates and blocker metadata only. They contain no extracted
coordinates or measurement values.

## Blocker Decision

The source remains blocked for row curation. The missing conditions are:

- legitimate source copy available to the curator;
- target figure/panel confirmation;
- explicit redistribution decision for any panel/intermediate image;
- WebPlotDigitizer-class tool name and version;
- axis calibration anchors;
- extracted point coordinates;
- per-point uncertainty and inclusion/exclusion state;
- reviewer replay.

The blocker is precise rather than source-disqualifying: Norris-Bawendi remains
the clearest Quantum direct-row unblock path, but the repository still lacks the
deterministic extraction artifact required by the protocol.

## Output Routing Summary

- Task verdict: `BLOCKED_PENDING_LEGITIMATE_SOURCE_COPY_AND_TOOL_RUN`
- Canonical destination:
  `data/quantum_dots/digitization/norris-bawendi-1996-prb-cdse-band-edge/`
  and this review note.
- Review tier: `none`
- Gate A status: not attempted; no result or row dataset was produced.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Dataset impact: no `qd-*.yaml` rows added or changed.
- Benchmark impact: no quantum-size benchmark run.
- Publication blocker: source access, target panel, checksum/redistribution
  decision, deterministic tool run, axis calibration, extracted points, and
  uncertainty semantics are all still missing.

## Next Allowed Step

A human or tool-equipped curator may replace the templates with real
`axis_calibration.csv`, `extracted_points.csv`, `extraction_ledger.csv`, and
`notes.md` only after using a legitimate source copy and recording the
redistribution/checksum posture. A separate row-curation task must still decide
whether enough reviewed points survive to create a `qd-*.yaml` dataset.
