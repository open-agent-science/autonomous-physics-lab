# Stellar M-L Route 2 Promotion-Readiness Scorecard (TASK-0753)

**Task:** `TASK-0753`
**Campaign:** Textbook Formula Audit (Stellar mass-luminosity)
**Scores:** `TASK-0740` / `AGENT-RUN-0070` Route 2 `SANDBOX_PASS`
**Verdict:** `NOT_YET_GATE_A_READY` (promising; one controlled wave away from a
first RESULT candidate)

## What The Route 2 Benchmark Established

Frozen alpha `L = (M/M_sun)^3.5` over the `0.5-2.0 M_sun` primary range, scored
against a per-mass-band train-median null on a checksum-pinned DEBCat snapshot
with a frozen system-level holdout:

| Lane | Rows | Formula MAE (dex) | Beats null |
| --- | ---: | ---: | --- |
| validation | 103 | 0.316 | yes |
| holdout | 132 | 0.347 | yes (null 0.445; margin 0.098 dex) |

Strengths toward promotion: deterministic + reproducible (committed extractor +
benchmark runner + source checksum), predeclared null, frozen holdout, beats the
null out-of-sample, storage/redistribution boundary preserved, conservative
framing (no universal claim).

## Gate A Readiness Checklist

| Criterion | State |
| --- | --- |
| Reproducible, deterministic computation | ✅ committed scripts + pinned checksum |
| Predeclared null / control | ✅ per-mass-band train-median null |
| Frozen holdout, out-of-sample win | ✅ validation + holdout beat the null |
| Source provenance + redistribution boundary | ✅ Route 2 (extractor + samples; full table local-only) |
| **Confounder control (evolutionary stage)** | ❌ main-sequence rows have much smaller residuals than evolved; unknown-stage is a large subset, not controlled |
| **Margin robustness (split-sensitivity / multiple controls)** | ❌ a single 0.098 dex holdout margin; no seeded split-sensitivity or shuffle controls yet (Materials-style) |
| **Baseline adequacy (vs the textbook piecewise M-L)** | ❌ only the single-alpha 3.5 route; the actual textbook piecewise-bin baseline was not run |
| Gate A RESULT packaging | ❌ not attempted |

## Verdict And Why

`NOT_YET_GATE_A_READY`. The benchmark is real sandbox evidence, but `M^3.5` is a
**main-sequence** relation, and the run mixes evolved and unknown-stage systems.
The report itself flags stage sensitivity as the strongest caution. A first
RESULT candidate must not inherit that confounder, and a single 0.098 dex margin
needs the same control discipline Materials applied (null controls +
split-sensitivity) before promotion.

## Ordered Path To A First RESULT Candidate

Each step is a bounded, parallel-safe lane on the Stellar write surface.

1. **Stage-controlled re-score.** Restrict the primary benchmark to
   `main_sequence_compatible` rows (and report `evolved` / `unknown` separately as
   diagnostics), so the M-L test is not confounded by evolution. Re-check the
   holdout margin under that restriction.
2. **Control + split-sensitivity audit.** Add deterministic null/shuffle controls
   and seeded split-sensitivity (as MD-0001 received), to confirm the margin is
   durable rather than a single-split artifact.
3. **Baseline-adequacy decision.** Decide whether to compare against the older
   piecewise textbook-bin M-L baseline (the campaign's named target) before
   declaring the single-alpha result.
4. **Gate A packaging.** Only after 1-3, package a `RESULT-*` candidate with the
   stage-controlled, control-audited evidence and route it through
   `docs/result-promotion-protocol.md`.

## Do Not Launch

- Do not promote a `RESULT-*` from the current mixed-stage SANDBOX_PASS.
- Do not state a universal stellar mass-luminosity relation or a stellar-evolution
  claim.
- Do not commit raw `debs.dat` or the full normalized rows; keep Route 2.
- Do not choose the stage restriction or baseline after inspecting residual
  rankings; declare it first (no-peek).

## Output-Routing Summary

- **Task verdict:** `not_applicable` (promotion-readiness scorecard).
- **Benchmark-readiness verdict:** `NOT_YET_GATE_A_READY`.
- **Canonical destination:** this scorecard; `TASK-0753` → `REVIEW_READY`.
- **Review tier:** `none`; no `RESULT-*` or `PRED-*` created.
- **Gate A status:** not attempted (blocked on stage control + control audit).
- **Gate B status:** not applicable.
- **Claim impact:** no claim change.
- **Knowledge impact:** campaign routing only.
- **Limitations / blockers:** scores only committed Route 2 evidence; the
  stage-controlled re-score (step 1) is the single highest-leverage next lane and
  is not run here.
