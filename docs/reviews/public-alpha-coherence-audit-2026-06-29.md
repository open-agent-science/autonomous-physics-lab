# Public-Alpha Coherence Audit — 2026-06-29

## Scope

This architecture/support pass checked the public-alpha documentation surface
after the v0.2 public opening signoff and the first post-opening PR activity.

The goal was coherence, not promotion:

- align public-facing docs with the fact that the repository is already public;
- remove stale pre-opening or pre-transfer wording;
- refresh one stale campaign summary line that could mislead new readers;
- avoid creating a new dashboard, generated state surface, or live task cache.

## Inputs

- `docs/reviews/v0.2-public-alpha-opening-signoff-2026-06-28.md`
- `docs/public-release-gates.md`
- `docs/release-checklist.md`
- `docs/status.md`
- `docs/roadmap.md`
- `docs/publication-roadmap.md`
- `docs/releases/v0.2-public-alpha.md`
- `docs/v0.2-launch-pack.md`
- `README.md`
- live GitHub PR metadata for #1288, #1287, and #1285

## Findings

### F1 — Opening state is recorded, but some docs still sounded pre-opening

The release gates and checklist now record the public-opening SHA and branch
protection state. Several higher-level docs still described the opening as a
future visibility decision or referred to the repository as a candidate rather
than a live public-alpha surface.

Action taken:

- `docs/status.md` now says `v0.2-public-alpha live — soft-launch stabilization`.
- `docs/roadmap.md`, `docs/publication-roadmap.md`,
  `docs/releases/v0.2-public-alpha.md`, and `docs/v0.2-launch-pack.md` now
  distinguish completed public visibility from future release tag, DOI, and
  broad-announcement decisions.

### F2 — Quantum summary drifted behind the campaign state

The README still said direct measurement rows were the main Quantum blocker.
That was true earlier, but the current state is sharper: six direct Almeida InP
rows and a source-scoped baseline exist, while transfer-source and
baseline-readiness gates remain.

Action taken:

- README Quantum line now reflects the source-scoped baseline and transfer gate.
- `docs/status.md` now records the same public-facing boundary and notes that
  the failed effective-mass transfer check is preserved as bounded negative
  memory.

### F3 — Live PR state changed since the external stabilization note

Live GitHub metadata showed:

- PR #1288, post-public opening signoff, is merged.
- PR #1287, Quantum effective-mass transfer negative memory, is merged.
- PR #1285, Exoplanet Chen-Kipping published-relation audit, merged during the
  same maintainer review sweep before this coherence PR was closed.

Action taken:

- This pass updates docs only for merged/default-branch state that changes the
  public-alpha coherence wording.
- PR #1285 is intentionally not promoted into the high-level public result
  narrative here; it remains a separately routed, control-sensitive audit
  artifact.

## Deferred

- No `first-public-agent-cycle` artifact was added. The repository already has
  normal PR/task memory for the first post-opening work, and adding a new static
  summary before the cycle is complete would create another maintained surface.
- No GitHub issue templates, labels, pinned issues, release tags, or branch
  protection settings were changed. Those are separate maintainer-gated
  repository-operations decisions.
- No external article or non-repository launch planning was committed.

## Verdict

`PUBLIC_ALPHA_COHERENCE_PATCH_APPLIED`

The public-alpha docs are now better aligned with the current repository state:
public visibility is live, release/tag/DOI decisions remain separately gated,
and the Quantum campaign summary no longer hides the source-scoped baseline that
already exists.

## Output Routing

- Task verdict: `not_applicable`
- Canonical destination: documentation/review note only
- Review tier: `none`
- Gate A status: not applicable
- Gate B status: not applicable
- Claim impact: no claim change
- Knowledge impact: no knowledge change
- Result artifact impact: no `RESULT`, `PRED`, `CLAIM`, `KNOW`, source-row, or
  metric artifact changed
- Limitations: this is a coherence pass, not a release signoff or PR merge
  decision
