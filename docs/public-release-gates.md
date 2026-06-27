# Public Release Gates

This repository stays private until all gates below are satisfied.

The goal is not to optimize for a fast public launch. The goal is to confirm
that the contributor workflow, branch-based review, reproducible validation,
campaign guidance, and public scientific memory work together without
overclaiming results.

The detailed private validation plan lives in
[private-contributor-validation-plan.md](./private-contributor-validation-plan.md).
Use [private-agent-test-metrics.md](./private-agent-test-metrics.md) and
[private-contributor-scorecard.md](./private-contributor-scorecard.md) to collect
evidence for Gate 2.

## Gate 1 — Technical Stability

All of the following must be true:

- clean git state
- CI green
- `python3 -m physics_lab.cli validate-repo .` green
- `python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings` green
- no local path leaks
- no tracked cache, OS, or agent-local files
- public source/data artifact history has been reviewed and the current
  default-branch scan is clean: no reachable non-redistributable publisher PDFs,
  preprint PDFs, restricted third-party raw datasets, or license-ambiguous
  source payloads remain in the public-launch history

Suggested evidence:

- latest CI run link
- maintainer validation log
- release-time validation signoff artifact
- repository snapshot without local-only files
- Phase B history scan / cleanup signoff or release-gate addendum that records
  scanned refs, candidate removal paths, verification commands, and whether a
  merge-freeze rewrite was required or has already been verified as complete

## Gate 2 — Multi-Agent / Open Agent Network Contributor Pilot

All of the following must be true:

- 3-5 invited contributors or contributor-agent pairs
- 10 or more task-based PRs
- 3 or more scientific sandbox PRs
- 2 or more technical, docs, or test PRs
- 2 or more independent replay or audit PRs
- each PR links to a task
- each PR passes CI
- maintainer review happens before merge
- no direct pushes to `main`
- no automatic claim or knowledge promotion
- agent-published or agent-validated artifacts remain clearly labeled by
  review tier
- no dirty active-board or context sync after merge

Suggested evidence:

- PR list with linked `TASK-*` ids
- validation logs per PR
- short maintainer summary of what worked and what caused friction

## Gate 3 — Measurable Scientific Result And Negative Evidence

At least one public-facing result or benchmark-diagnostic surface must exist.
Examples:

- 100 candidate formulas tested
- failure modes classified
- leaderboard generated
- report explains limitations
- no global or exact discovery claim

At least one clear falsification surface should also remain visible as
first-class evidence rather than being hidden behind successful reproductions
only.

If agent-published or agent-validated artifacts are cited, their review tier
must remain visible. Agent publication is evidence visibility, not maintainer
endorsement of a claim.

Required wording discipline:

- do not claim final physics answers from APL outputs
- do not frame outputs as discovery-level physics beyond exceptional evidence
  and review
- do not say "100% exact" unless symbolic equality is proven
- prefer "validated to tolerance" for numerical agreement

## Gate 4 — Public Narrative

All of the following must be true:

- `README.md` has a result summary
- strategy and status docs describe APL as the first physics proof-of-work for
  Open Agent Science and use the live
  `open-agent-science/autonomous-physics-lab` repository path for current
  contributor entrypoints
- `docs/status.md` and the public science dashboard summarize current campaign
  state without implying discovery-level claims
- an announcement draft exists
- a citation/publication path exists for software and reusable datasets, even
  if DOI minting is deferred until maintainer-approved release
- external reviewer replication guidance has been checked against the current
  public evidence surface
- no final-answer, universal-theory, or discovery-level overclaim
- claims remain review-gated
- guarded stress-test outputs are not presented as flagship public successes

## Gate 5 — Post-Transfer Repository Readiness

The repository has moved to `open-agent-science/autonomous-physics-lab`. Before
opening it publicly, all of the following must remain true:

- CI, self-hosted runner labels, and repository secrets have been checked after
  transfer;
- branch protection is enabled before public opening when the repository plan
  supports private-repository protection; when the current GitHub plan only
  exposes protection for public repositories, the intended `main` protection
  policy is documented before opening and enabled immediately after the
  visibility switch, before external contributor invitations or broad
  announcement;
- clone URLs, contributor docs, release docs, and citation metadata point at the
  Open Agent Science repository where they are live-current rather than
  historical;
- old owner paths are kept only as historical references, redirects, or
  historical review/CI evidence;
- no source artifact, result artifact, or prediction registry entry is rewritten
  merely to match the new organization path.

## Gate 6 — Public Artifact History And Redistribution Boundary

Before the repository is opened publicly, the maintainer must confirm that the
public default branch and its reachable history satisfy the source-artifact
publication policy:

- publisher PDFs, arXiv/preprint PDFs, and other third-party source documents
  are not vendored unless explicit redistribution evidence is recorded;
- committed source/data artifacts either carry machine-readable reuse evidence
  or are limited to metadata, checksum, extractor, and non-substitutive sample
  forms;
- any required history cleanup is performed only after a maintainer-declared
  merge freeze, full blob/path scan, reviewed paths-to-remove list, backup plan,
  and contributor re-clone/rebase instructions;
- no public launch proceeds while known non-redistributable source artifacts
  remain reachable from the public default branch history.

Current status note: `TASK-0858` verified current `origin/main` at
`15a9675b097250be88e0cb3fa7a2e3acd59c8373` and found no reachable `.pdf` blobs
or risky binary/document/archive additions, and the two arXiv PDF paths named by
`TASK-0732` are no longer present in default-branch history. Treat the old
freeze-time rewrite blocker as closed for this cut, subject to a final
exact-SHA release signoff re-running the scan.

## Release Decision

The repository may become public only when all applicable gates are satisfied,
the release-time validation signoff has been reviewed, and a maintainer
explicitly decides that the current docs, task board, and scientific claims are
aligned with the evidence.
