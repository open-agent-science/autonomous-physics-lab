# Nuclear Do-Not-Repeat Diagnostic Lanes

- Task: `TASK-0642`
- Campaign: Nuclear Mass Surface
- Mode: planning-only negative-result memory map
- Purpose: a compact go/no-go map so future agents do not rerun exhausted
  Nuclear lanes, while keeping genuinely new source-gated work open

## Scope

This map consolidates the negative, diagnostic-only, and source-blocked Nuclear
lanes into explicit do-not-repeat boundaries, and lists the allowed next lanes
separately. It reviews committed campaign memory only. It does **not** run new
metrics, add predictions, create claims, or promote results.

## How to use this map

Before opening any Nuclear hypothesis/feature lane, check it against the
do-not-repeat and diagnostic-only tables below. A lane is reopenable only if it
is materially disjoint from every exhausted lane **and** it clears the controls
of the [TASK-0448 controls-first gauntlet](../notes/nuclear-controls-first-hypothesis-gauntlet.md)
under a new baseline or a larger curated training slice. Source-gated work
(reveal scouting, prediction readiness, result preflight) follows the allowed
lanes table.

## Do-not-repeat lanes (negative / control-dominated / falsified)

| Lane / feature family | Evidence | State | Why blocked |
| --- | --- | --- | --- |
| `LOCAL-CURVATURE-001` no-leakage prototype | TASK-0394 | `FALSIFIED` | Regresses full-known MAE (+0.0196 MeV), loses to strongest no-leakage control, subset win-rate 0.000. |
| NMD-0002 / NMD-0003 broad factory slates | TASK-0507, TASK-0517 (AGENT-RUN-0052/0053) | `NEGATIVE_CONTROL_DOMINATED` | 0 shortlisted across 72 candidates; top apparent gains rejected by matched random-slice controls. Do not rerun the same slate on the same contract. |
| NMD-0002 uncertainty perturbation | TASK-0518 | `INCONCLUSIVE` | Perturbation stability of the same 11 rows is not independent evidence. |
| Mid-mass / isotope-chain gap features | TASK-0286 | `NEGATIVE` | All executed candidates regress the primary holdout or remain null. |
| Pairing-asymmetry interaction / coupling | TASK-0474, TASK-0594 | `NEGATIVE_CONTROL_DOMINATED` | Regresses validation/full-known; loses to best control. |
| Magic-parity boundary control | TASK-0475 | `NEGATIVE` | Regresses the frozen full-known baseline; not a shell-specific near-miss. |
| Magic-distance interaction | TASK-0451 | `CONTROL_DOMINATED` | Small gain matched by a same-degree random control; fails survival margin. |
| Neutron-rich boundary transfer | TASK-0450 | `NEGATIVE` | Regresses primary holdout and full-known; opposing residual signs in sparse rows. |
| Isotope-chain leave-family-out / transfer | TASK-0476, TASK-0595 | `MIXED_CHAIN_LOCAL` / `NEGATIVE` | Improves some chains, regresses a comparable or larger number; blocks broad transfer wording. |
| Residual-free high-error cluster taxonomy | TASK-0449 | `INCONCLUSIVE` | Training slice too sparse for per-cluster leave-one-out; do not repeat the same taxonomy. |
| `coulomb_surface_interaction` bounded sprint | TASK-0584 | `INCONCLUSIVE_CONTROL_DOMINATED` | Survival margin not cleared under the frozen stratified gate. |
| Odd-even shell interaction; deformation proxy; measured/extrapolated boundary | TASK-0365 | `STOP` | Preserved negative/control sandbox memory only. |
| First broad-surface NMD-0003 baseline refit | TASK-0531 | `INCONCLUSIVE` | Train/full-surface MAE improves but validation-holdout regresses; not a promotable baseline. |

## Diagnostic-only lanes (preserved as sandbox diagnostic; not for re-audit or promotion)

| Lane | Evidence | State | Boundary |
| --- | --- | --- | --- |
| Shell-axis family | TASK-0333 (after TASK-0310/0315/0316/0317/0320/0321) | `DIAGNOSTIC_ONLY` | Keep as sandbox diagnostic; do not add more retrospective shell-axis audits or registry expansion without a maintainer-approved source-gated task. |
| F2 finer taxonomy / component ablation | TASK-0613, TASK-0625 | `COMPONENT_DIAGNOSTIC_ONLY` | Best single component `magic_n_near` (+0.0748 MeV) but no variant clears the 0.25 MeV survival margin. Packaged as the diagnostic RESULT-0018 (TASK-0633). Do not repeat the ablation. |
| NMD-0003 factory negative-result | TASK-0569, TASK-0639 | `GATE_A_BLOCKED` | Keep as negative/control memory; not packageable as a single scoped RESULT (multi-run, rerun forbidden, no promotable candidate). |

## Source-blocked lanes (blocked by data provenance, not by formulas)

| Lane | Evidence | State | Unblock condition |
| --- | --- | --- | --- |
| Prediction reveal scoring | TASK-0585, TASK-0640 | `BLOCKED_SOURCE_NOT_PINNED` | A checksum-pinned source postdating the 2026-05-20 registry freeze that passes the no-peek source gate. |
| NMD-0002 11-row training expansion | TASK-0479 | `BLOCKED_FOR_SOURCE_SAFE_EXPANSION` | A committed source-grade broader measured-row training table; the `post_ame2020_holdout` surface must stay holdout, not training. |

## Allowed next Nuclear lanes (not exhausted)

These remain open and are not blocked by the tables above:

1. **Result-publication preflight** for diagnostic/negative memory (route to a
   scoped `AGENT_PUBLISHED` RESULT only when a single deterministic artifact and
   permitted replay exist, as F2 did in RESULT-0018; otherwise preserve a Gate A
   blocker).
2. **Reveal-source scouting** for post-AME2020 / post-freeze sources —
   readiness only, no scoring (see
   [nuclear-post-ame2020-reveal-source-scout.md](nuclear-post-ame2020-reveal-source-scout.md)).
3. **Prediction reveal-readiness inventory** of frozen `PRED-*` entries (no
   scoring, no value inspection).
4. **A maintainer-approved new source-gated hypothesis family** that is
   materially disjoint from every do-not-repeat lane, run through the
   controls-first gauntlet, and only after a new baseline or a larger curated
   training slice changes the contract.

## Stop conditions preserved

- Do not rerun completed factory/sprint candidate slates on the current
  baseline/split contract.
- Do not run reveal scoring without a pinned post-freeze no-peek source.
- Do not treat diagnostic-only lanes (shell-axis, F2) as promotion candidates or
  re-audit them.
- Do not present any lane as a nuclear mass law or a surviving no-leakage
  candidate.
- Do not add predictions, claims, knowledge, or result artifacts from this map.

## Output routing

- Task verdict: `not_applicable` (negative-result memory map).
- Canonical destination:
  `docs/reviews/nuclear-do-not-repeat-diagnostic-lanes.md`.
- Review tier: `none`.
- Gate A status: not attempted; no `RESULT-*` or `PRED-*` artifact.
- Gate B status: not applicable.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result artifact impact: no `results/` artifacts modified.
- Limitations / blockers: this is a consolidation of committed campaign memory,
  not a new audit; lane states are inherited from the cited tasks and may be
  revised only by a maintainer-approved source-gated task.
