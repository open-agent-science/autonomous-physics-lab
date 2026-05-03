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

Risk terms searched:

- `exact`
- `proved`
- `proven`
- `discovered`
- `discovery`
- `valid`
- `global`
- `solved`
- `solve`
- `theory of everything`

## High-Level Verdict

Current wording is mostly disciplined.

Most matches for `exact` and `valid` are acceptable because they refer to:

- exact analytical references or exact linear benchmark assumptions;
- internal verdict vocabulary such as `VALID` and `PARTIALLY_VALID`;
- explicit anti-overclaim rules such as "no global validity claim."

The main risk is not scientific fraud language inside result artifacts. The
main risk is narrative drift in public-facing drafts and repository-level
positioning text.

## Main Findings

### 1. README overstates current public status

File:

- `README.md`

Observed risk:

- "public verification engine for physics ideas"
- "public knowledge base"

Why this is risky:

- the repository is still in `v0.1-private-alpha`;
- "public" can be read as a statement about current release state rather than
  long-term intent.

Safer wording:

- "verification-first engine for testing physics ideas"
- "version-controlled scientific memory"

Action taken in this task:

- updated `README.md` to remove the current-state `public` framing from the
  core one-line description.

### 2. Public-alpha drafts read as already released

Files:

- `docs/announcement-v0.1-public-alpha.md`
- `docs/releases/v0.1-public-alpha.md`

Observed risk:

- "Opened public alpha of Autonomous Physics Lab."
- "First public alpha of Autonomous Physics Lab."

Why this is risky:

- these documents are drafts or prepared notes, but the wording reads as a
  completed release event;
- that can blur the gate between private-alpha readiness and actual public
  release.

Safer wording:

- "Draft wording for a future public alpha announcement"
- "Prepared release notes for a future public alpha"
- "Launching the public alpha..." only after a release decision

Action taken in this task:

- updated both files to make future-release status explicit.

### 3. Status note implied a public-alpha state more strongly than intended

File:

- `docs/status.md`

Observed risk:

- "Public alpha is stable for two slices"
- "globally valid"

Why this is risky:

- the repository is still private;
- "globally valid" is scientifically clear in context, but "supported beyond
  the configured range" is harder to misread in public-facing reuse.

Safer wording:

- "The prepared public-alpha package is stable for two slices"
- "not supported beyond the configured range"

Action taken in this task:

- updated `docs/status.md` to keep release-state and scope-state wording more
  precise.

## Acceptable Matches That Should Stay

These patterns appeared often and are appropriate:

- `exact` when referring to the elliptic-integral pendulum reference;
- `exact` when referring to exact linear damped-oscillator solutions;
- `VALID` as internal verdict vocabulary;
- anti-overclaim guardrails such as "No symbolic exactness claim" and
  "No global validity claim."

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

- `proved`
- `solved physics`
- `discovered new physics`
- `global validity`
- `100% exact`
- `public alpha` when the repository is still private

## No-Claim Reminder

Current pendulum evidence supports a reproducible, range-aware benchmark
result. It does not support:

- symbolic exactness;
- global validity;
- a discovery claim;
- a claim of new physics.

## Follow-Up Recommendation

Before any public post or release decision:

1. rerun this audit on `README.md`, `docs/results/`, and announcement drafts;
2. keep the phrase "top leaderboard candidate" instead of implying the lowest
   raw residual overall;
3. keep Koide-track wording in reproduction / falsification language rather
   than discovery language.
