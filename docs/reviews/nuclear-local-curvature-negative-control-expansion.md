# Nuclear local-curvature negative-control expansion review

**Task:** `TASK-0397`  
**Agent run:** `AGENT-RUN-0041`  
**Predecessor:** `TASK-0351` / `AGENT-RUN-0031`

## Scope

This review expands the local-curvature negative-control panel with chain-shuffled, mass-number-only, magic-distance-only, smooth-window, neighbor-availability, and near-null neighborhood controls. It keeps metric definitions aligned with the predecessor local-curvature lane.

## Headline Result

- Lane verdict: `PARTIALLY_VALID`.
- Control explanation verdict: `NOT_EXPLAINED_BY_TESTED_CONTROLS`.
- Best candidate: `LOCAL-CURVATURE-001`.
- Strongest control: `LOCAL-NEGCTRL-006`.
- Control-minus-candidate margin: +0.544296 MeV.

## Candidate vs Strongest Control

| Candidate | Strongest control | Margin | Subset win-rate |
| --- | --- | ---: | ---: |
| `LOCAL-CURVATURE-001` | `LOCAL-NEGCTRL-006` | +0.544296 | 0.684 |
| `LOCAL-CURVATURE-002` | `LOCAL-NEGCTRL-006` | -0.179776 | 0.368 |
| `LOCAL-CURVATURE-003` | `LOCAL-NEGCTRL-006` | -1.766016 | 0.000 |

## Limitations

- The audit is retrospective and uses committed full-known residual context.
- The controls are deterministic but not exhaustive.
- No live data, reveal scoring, registry entry, canonical result, claim, or knowledge update is produced.

## Verdict

`PARTIALLY_VALID`
