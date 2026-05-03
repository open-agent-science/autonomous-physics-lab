# Overclaim Language Audit

Task: `TASK-0029`  
Status: draft audit note for maintainer review

## Purpose

This audit checks repository wording for overclaim risk before broader
contributor activity and any future public release work.

The goal is not to weaken real evidence. The goal is to keep public-facing and
maintainer-facing wording aligned with what the repository actually supports.

## Search Scope

Searched:

- `README.md`
- `docs/`
- `results/`

Wording categories reviewed:

- high-certainty wording
- release-state wording
- scope-expanding wording
- beyond-evidence explanatory framing

## High-Level Verdict

Current wording is mostly disciplined.

Most flagged matches are acceptable because they refer to:

- exact analytical references or exact linear benchmark assumptions;
- internal verdict vocabulary such as `VALID` and `PARTIALLY_VALID`;
- explicit scope-limiting rules already present elsewhere in the repository.

The main risk is not scientific fraud language inside result artifacts. The
main risk is narrative drift in public-facing drafts and repository-level
positioning text.

## Main Findings

### 1. README overstates current public status

File:

- `README.md`

Observed risk:

- wording that frames the repository as already public
- wording that overstates the current release state

Why this is risky:

- the repository is still in `v0.1-private-alpha`;
- that wording can be read as a statement about current release state rather
  than long-term intent.

Safer wording:

- verification-first engine for testing physics ideas
- version-controlled scientific memory

Action taken in this task:

- updated `README.md` to remove the current-state `public` framing from the
  core one-line description.

### 2. Public-alpha drafts read as already released

Files:

- `docs/announcement-v0.1-public-alpha.md`
- `docs/releases/v0.1-public-alpha.md`

Observed risk:

- wording that reads as if the launch already happened
- wording that sounds like finalized release language instead of prepared drafts

Why this is risky:

- these documents are drafts or prepared notes, but the wording reads as a
  completed release event;
- that can blur the gate between private-alpha readiness and actual public
  release.

Safer wording:

- draft wording for a future release announcement
- prepared release notes for a future public launch
- launch-state language only after an explicit release decision

Action taken in this task:

- updated both files to make future-release status explicit.

### 3. Status note implied a public-alpha state more strongly than intended

File:

- `docs/status.md`

Observed risk:

- wording that implies a stronger public-release state than intended
- wording that can read broader than configured benchmark scope

Why this is risky:

- the repository is still private;
- broader-than-scope wording may be scientifically clear in context, but a more
  range-explicit phrase is harder to misread in public-facing reuse.

Safer wording:

- the prepared release package is stable for two slices
- not supported beyond the configured range

Action taken in this task:

- updated `docs/status.md` to keep release-state and scope-state wording more
  precise.

## Acceptable Matches That Should Stay

These patterns appeared often and are appropriate:

- `exact` when referring to the elliptic-integral pendulum reference;
- `exact` when referring to exact linear damped-oscillator solutions;
- `VALID` as internal verdict vocabulary;
- explicit scope-limiting guardrails already used in result packages and policy
  docs.

These are not overclaiming problems by themselves.

## Replacement Guidance

Prefer:

- `validated to tolerance`
- `validated in the configured range`
- `supported in scope`
- `range-limited evidence`
- `benchmark result`
- `reproduction result`
- `future public alpha`
- `prepared release notes`

Avoid unless the evidence truly supports it:

- certainty wording beyond verified scope
- launch-state wording that outruns the release gates
- explanatory framing that suggests a breakthrough rather than a bounded result
- absolute-equivalence wording without symbolic proof

## No-Claim Reminder

Current pendulum evidence supports a reproducible, range-aware benchmark
result. It does not support:

- symbolic exactness;
- unrestricted scope claims;
- explanatory breakthrough framing;
- broad beyond-scope explanatory conclusions.

## Follow-Up Recommendation

Before any public post or release decision:

1. rerun this audit on `README.md`, `docs/results/`, and announcement drafts;
2. keep the phrase "top leaderboard candidate" instead of implying the lowest
   raw residual overall;
3. keep Koide-track wording in reproduction / falsification language rather
   than breakthrough-style explanatory framing.
