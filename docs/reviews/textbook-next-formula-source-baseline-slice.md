# Textbook Next Formula Source/Baseline Slice

Task: `TASK-0783`
Campaign: `textbook-formula-audit`
Mode: planning-only source/baseline slice selection
Decision: `NEXT_SLICE_SELECTED_SOURCE_CURATION_ONLY`
Selected slice: Wien displacement empirical FIRAS source-curation route
Review date: 2026-06-18

## Scope

This review selects at most one next Textbook Formula Audit slice after the
Stellar M-L Gate A package. It does not fetch live data, pin files, run
empirical metrics, refit a formula, create `RESULT`, `PRED`, `CLAIM`, or `KNOW`
artifacts, or make universal formula claims.

The current highest-priority result path remains Stellar M-L Gate B replay and
DEBCat scope-flag reconciliation. This note only chooses the next
source/baseline slice that should be admitted after that path is no longer the
bottleneck.

## Inputs Reviewed

| Input | Role |
| --- | --- |
| `docs/campaigns/textbook-formula-audit.md` | Campaign guardrails and current Stellar M-L state. |
| `docs/notes/textbook-formula-audit-candidate-list.md` | Ordered candidate slate. |
| `docs/reviews/textbook-wien-displacement-source-baseline-plan.md` | Existing Wien source/baseline plan. |
| `docs/reviews/textbook-stefan-boltzmann-source-baseline-plan.md` | Existing Stefan-Boltzmann source/baseline plan and circularity warnings. |
| `docs/campaigns/textbook-formula-audit/stellar-mass-luminosity-ood-source-baseline-plan.md` | Existing Stellar M-L plan and shared stellar-source context. |
| `results/EXP-0013/RUN-0001/result.yaml` | Gate-B-validated exact-reference software/convention result. |
| `results/EXP-0015/RUN-0001/result.yaml` | Agent-published Stellar M-L empirical result still awaiting Gate B. |
| `docs/result-promotion-protocol.md` | Output routing and no-promotion constraints. |

## Candidate Triage

| Candidate | Decision | Reason |
| --- | --- | --- |
| Stellar M-L | Defer | Already has `RESULT-0022`; next work is Gate B replay and scope-flag cleanup, not a new planning slice. |
| Kleiber allometric scaling | Defer | Candidate list explicitly notes compendium redistribution and license uncertainty. It needs source-license review before a source/baseline slice can be admitted. |
| Wien displacement | Select | Existing source/baseline plan already defines formula convention, row schema, inclusion/exclusion rules, gates, and an empirical FIRAS route with a clear source-artifact blocker. |
| Stefan-Boltzmann empirical stellar slice | Defer | Existing plan warns that many stellar luminosities are circular if derived from the same radius-temperature formula; use only after independent luminosity source curation. |

## Selected Slice

Selected slice: **Wien displacement empirical FIRAS source-curation route**.

The formula is the wavelength-domain Wien displacement relation:

```text
lambda_peak = b / T
```

with frozen constant convention:

```text
b = 2.897771955e-3 m K
```

The next task should be a source-artifact curation task, not a metric task.
It should pin the NASA LAMBDA COBE/FIRAS source files needed to determine
whether a wavelength-domain peak audit is possible. The source route is useful
because it is open, blackbody-like, and already named by the Wien source plan,
but it is still blocked until file provenance and spectral-axis semantics are
frozen.

## Required Source Gate

A future source-curation task must define and pin:

- exact NASA LAMBDA COBE/FIRAS product URLs and retrieval timestamp;
- source license / redistribution posture;
- SHA-256 checksums for any committed or referenced files;
- whether the product reports frequency, wavenumber, wavelength, or a
  convertible spectral axis;
- whether the quantity is spectral radiance/irradiance per wavelength or a
  different domain;
- the temperature context and uncertainty semantics;
- the spectral coverage window and whether `b / T` falls inside it with margin;
- a no-live-fetch replay path from committed source artifacts.

If those fields cannot be pinned without ambiguity, the route must stop with a
source blocker and no audit metrics.

## Row Schema

The future row schema should reuse the Wien source plan minimum fields:

| Field | Required decision before metrics |
| --- | --- |
| `row_id` | Stable source-row identifier. |
| `source_id` | Frozen FIRAS artifact or generated fixture id. |
| `route` | `cobe_firas` for this selected empirical route. |
| `temperature_K` and uncertainty | Source temperature and uncertainty semantics. |
| `lambda_peak_observed_m` and uncertainty | Wavelength-domain peak only; frequency-domain peaks are excluded. |
| `lambda_convention` | Vacuum/air/unknown convention; unknown blocks interpretation. |
| `spectral_axis` | Must be wavelength for benchmark rows. |
| `spectral_quantity` | Must identify per-wavelength spectral radiance/irradiance/exitance. |
| `source_file_sha256` | Required before any metric task. |
| `retrieved_at_utc` | Required before any metric task. |

## Holdout Policy

Because FIRAS is a narrow empirical route, the source-curation task should not
pretend it supplies a broad temperature holdout. Use this policy:

- source-curation task: no holdout metrics; only pin files and determine row
  admissibility;
- later audit task, if admitted: compare any FIRAS row against deterministic
  synthetic exact-reference rows as software controls;
- treat the FIRAS empirical row as a single calibrator slice, not as a broad
  validation set;
- if multiple FIRAS product variants exist, freeze one variant before residuals
  are inspected and treat other variants as sensitivity checks only.

## Verification Gates For Later Audit

No audit runs in this task. A later metric task must predeclare at least these
gates:

1. Dimensional consistency: `b / T` reduces to length.
2. Constant convention: use the wavelength-domain CODATA 2022 constant.
3. Peak-domain gate: frequency-domain, wavenumber-domain, color-temperature, or
   broadband peaks are excluded unless a source-owned wavelength-domain peak is
   pinned.
4. Range gate: predicted peak must sit inside the source spectral window.
5. Uncertainty gate: missing temperature or peak uncertainty yields
   `INCONCLUSIVE`, not a pass/fail claim.
6. Negative control: use the wrong-domain Wien constant or a deliberately wrong
   constant as a deterministic control; never tune `b` from the source.

## Stop Condition

Stop with `NO_AUDIT_METRICS_READY` if source curation cannot prove
wavelength-domain peak semantics, checksums, license posture, temperature
semantics, and spectral coverage. Do not substitute a frequency-domain peak
with `lambda = c / nu`, do not infer a peak from broadband photometry, and do
not treat the existing exact-reference fixture as empirical validation.

## Output Routing

- Task verdict: `NEXT_SLICE_SELECTED_SOURCE_CURATION_ONLY`.
- Canonical destination:
  `docs/reviews/textbook-next-formula-source-baseline-slice.md`.
- Review tier: `none`.
- Gate A status: not attempted.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Source readiness impact: Wien/FIRAS is selected as the next planning/source
  route, but empirical audit metrics remain blocked until source artifacts are
  pinned and domain semantics pass.
- Publication blocker: no empirical dataset snapshot, row checksum, audit
  metric, result artifact, or maintainer-reviewed claim exists.

## No-Claim Wording

Allowed wording:

- "Wien/FIRAS is the next source-curation slice to prepare."
- "The source must prove wavelength-domain peak semantics before metrics."

Forbidden wording:

- "APL validated Wien displacement."
- "APL falsified Wien displacement."
- "FIRAS proves the law universally."
- Any claim about blackbody physics beyond the future slice and source gates.
