# Nuclear Shell-Axis Post-Audit Decision

**Task:** `TASK-0333`  
**Evidence class:** sandbox-only retrospective decision synthesis  
**Recommended lane status:** `DIAGNOSTIC_ONLY`

## Scope

This review synthesizes the completed post-`TASK-0310` shell-axis audit wave
and recommends whether the lane should continue as a source-gated reveal
candidate, be narrowed, be paused, or remain diagnostic-only.

Inputs are committed review artifacts only:

- `docs/reviews/nuclear-shell-axis-validity-domain-after-0310.md`
- `docs/reviews/nuclear-shell-axis-coefficient-stability-audit.md`
- `docs/reviews/nuclear-shell-axis-specificity-controls.md`
- `docs/reviews/nuclear-shell-axis-magic-asymmetry-audit.md`
- `docs/reviews/nuclear-shell-axis-light-regression-audit.md`
- `docs/reviews/nuclear-shell-axis-isotope-chain-transfer-audit.md`
- `docs/reviews/nuclear-shell-axis-neutron-rich-tail-audit.md`
- `TASK-0324`

`TASK-0324` is `DONE` in the current task board, so no maintainer waiver is
needed for this synthesis.

This task does not fetch data, add prediction registry entries, score
`PRED-0063` through `PRED-0068`, edit canonical result artifacts, promote
claims, or update knowledge files.

## Evidence Surface Summary

| Surface | Verdict | Support status | Regression status | Blocker status |
| --- | --- | --- | --- | --- |
| Validity domain after `TASK-0310` | `BOUNDED_DOMAIN_MAP` | Aggregate retrospective support appears around near-magic, magic-N, mid-mass, neutron-rich, measured/extrapolated comparison, and sparse repeat-chain-neighbor subsets. | Light `A<50` regresses for all three primary shell-axis candidates; some sparse subsets are diagnostic only. | Not promotion-ready; source-gated reveal scoring remains blocked. |
| Coefficient stability | `FRAGILE` | Leave-one-out fits preserve small full-known and holdout improvements. | Exhaustive 8-of-11 resampling produces coefficient sign flips and some full-known or holdout regressions. | Blocks broad robustness wording, registry expansion, and claim promotion. |
| Specificity controls | `SHELL_SPECIFIC_BUT_BOUNDED` | The strongest shell-axis candidate beats the tested smooth-A, asymmetry, mass-region, baseline, and deterministic random controls on full-known and holdout MAE. | Smooth-A and neutron-excess controls are not inert, so the shell-axis interpretation remains bounded. | Keeps shell-axis alive only as sandbox evidence. |
| Magic-axis asymmetry | `NEUTRON_DOMINANT_BUT_SPARSE` | Primary candidates improve magic-N more than magic-Z under the audit margin. | Magic-N, magic-Z, and double-magic panels are sparse, with double-magic diagnostic only. | Directional note only; not enough for reveal or claim wording. |
| Light-nuclei regression | `WARNING_ZONE` | Some matched non-light behavior improves for the first two primary candidates. | All three primary shell-axis candidates regress light `A<50`; 15 of 24 light rows regress for each candidate. | Light nuclei must remain outside support wording. |
| Isotope-chain transfer | `MIXED_CHAIN_LOCAL` | Best shell-axis candidate improves 21 interpretable chains. | Best shell-axis candidate regresses 20 interpretable chains; candidate-level transfer rates are below half. | Blocks broad chain-transfer wording. |
| Neutron-rich tail | `OUTLIER_DIAGNOSTIC` | Neutron-rich high-error tail improves for all three primary candidates and survives removing the largest one or two baseline-error rows. | Matched non-neutron-rich high-error controls also improve, sometimes more than the neutron-rich tail. | Not a neutron-rich-specific support claim. |

## Decision

The lane should be kept as `DIAGNOSTIC_ONLY`.

Rationale:

- the shell-axis family has repeatable retrospective support on some aggregate
  and subset panels;
- the support is stronger than the tested simple non-shell controls on the
  main aggregate surfaces;
- coefficient stability is fragile under deterministic smaller resamples;
- light `A<50` is a persistent warning zone;
- isotope-chain transfer is mixed at the chain level;
- neutron-rich tail behavior is better read as high-error diagnostic behavior
  than as neutron-rich-specific support;
- the post-registration source gate for any real reveal comparison is still
  unresolved.

`NARROW_DOMAIN_ONLY` is too strong because the apparent domain still depends
on fragile coefficients and mixed chain-local behavior. `SOURCE_GATED_REVEAL_REVIEW`
is premature because the source/readiness blocker remains active and the
audit wave does not justify scoring frozen prospective entries. `PAUSE_SHELL_AXIS`
would discard useful diagnostic evidence that should remain visible for future
review and negative-control context.

## Additional Audit Recommendation

No additional retrospective shell-axis audits are recommended now.

The completed audit wave already covers the main decision surfaces: aggregate
domain, coefficient fragility, specificity controls, magic-axis direction,
light-nuclei regression, isotope-chain transfer, and neutron-rich high-error
tail behavior. More retrospective slicing would likely add review churn
without unlocking a clearer decision.

Future shell-axis work should be limited to maintainer-approved source-gated
review tasks or narrowly scoped explanation tasks for known negative panels.
Those should not add registry entries, score `PRED-0063` through `PRED-0068`,
or promote claims unless a later task explicitly authorizes that scope.

## Task-State Recommendations

- Keep `TASK-0305` blocked until a reviewed post-registration source manifest
  and no-peek reveal boundary exist.
- Do not create new shell-axis prediction registry entries from the current
  retrospective evidence.
- Do not mark any shell-axis evidence as canonical result or claim support.
- Preserve `TASK-0316`, `TASK-0320`, `TASK-0323`, and `TASK-0324` as required
  limitations in any future shell-axis evidence package.

No unrelated task statuses are changed by this synthesis.

## Verdict

`DIAGNOSTIC_ONLY`

The shell-axis lane remains useful as sandbox-only diagnostic evidence and a
negative-control-rich review surface, but the post-audit record does not
support further retrospective expansion, claim promotion, registry expansion,
or source-gated reveal scoring at this stage.
