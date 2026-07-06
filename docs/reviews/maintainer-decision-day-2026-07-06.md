# Maintainer Decision Day — 2026-07-06 (Decision Day #2)

- Recorded by: gladunrv (maintainer), interactive session with the Scientific
  Campaign Director agent (Claude Code), 2026-07-06.
- Task: TASK-0943.
- Context: the 2026-07-06 six-dimension strategic audit (multi-agent) plus two
  independent agent reviews of that audit converged on the same execution
  order: validation integrity -> external prediction anchor -> decision
  throughput -> public vitrine -> new artifact wave. The maintainer decided
  the eight open forks below in one session (recommended options were
  presented with alternatives; all decisions are the maintainer's).
- Non-claims: this memo changes no RESULT, PRED, CLAIM, or KNOW artifact and
  makes no scientific claim. All executions flow through the queued tasks
  under normal gates.

## Decisions

### D2-1 FRB Catalog-1 single-epoch route — CONDITIONAL GO (schema gate only)

The TASK-0934 scout returned TIME_INDEXED_SOURCE_AMBIGUOUS with exactly one
leakage-safe official route: the CHIME Catalog-1 interval-bounded exposure map
pair at the single epoch T=2019-07-02, with unresolved cross-catalog
semantics caveats (window start 2018-08-28 vs 2018-09-04, 4 s vs 12 s
resolution, pipeline era).

Decision: accept the route conditionally, as a checksum/schema feasibility
gate only — not a campaign activation. The gate (TASK-0947) must formally fix
all five of: (1) source identity as of T, (2) exposure/sensitivity strictly
up to T, (3) no post-T leakage into any frozen surface, (4) repeat-label
reveal strictly after T, (5) the exact scoring rule. Full campaign activation
(exposure construction, model freeze, PRED registration) is a separate
maintainer decision after the gate passes. If the gate cannot fix the five
conditions, the July steering target is retired honestly rather than slipped.

### D2-2 ThermoML bounded 80-row extract — CONDITIONAL GO via TASK-0940

Decision: TASK-0940 (decision packet) proceeds as queued. Pre-approval is
recorded now: if the packet confirms a facts-basis redistribution route for
the bounded 80-row extract (precedent: the post-AME2020 holdout entry in
`data/DATA_LICENSES.yaml`), the extraction lane is approved automatically and
the extraction task may be queued without a second maintainer decision. If
the packet cannot confirm the rights basis, the campaign stays
metadata-only and the expansion lane closes.

### D2-3 Atomic Yb/Sr — KEEP_MONITOR_ONLY ratified as terminal

Decision: the TASK-0938 go/no-go contract verdict KEEP_MONITOR_ONLY is
ratified as the terminal state of the line. Zero further seeded tasks
(scouts, memos, cards) until an external independent source satisfying the
contract's reactivation triggers appears. The ~50 existing atomic-* review
memos stand as anti-rediscovery memory.

### D2-4 Muon g-2 — park CLAIM-0008 as stress-test memory

Decision: park the line. CLAIM-0008 moves to a non-active stress-test/
calibration-memory role following the TASK-0927 claim-role precedent; the
muon g-2 knowledge entry is updated to a parked, honest status. No hardening
tasks are scheduled. Reopen requires a new external result or an explicit
maintainer decision. Execution: TASK-0950.

### D2-5 TASK-0305 — GO (source manifest approved)

Decision: the TASK-0307 source manifest is approved. TASK-0305 (nuclear
shell-axis mini-wave reveal scoring) is unblocked to READY after ~7 weeks;
all its prerequisites (TASK-0303/0304/0307) were already DONE.

### D2-6 Board hygiene batch — approved in full

1. TASK-0827 -> SUPERSEDED: the Decision Day #1 D10 refinement (2026-07-02)
   made the seen-holdout unblock path permanently unreachable, and the live
   path already executed via TASK-0929 (contract) + TASK-0933 (tier-1
   point-only freeze). A high-priority BLOCKED card that can never unblock
   misleads the board.
2. TASK-0925: blocker text rewritten — the TASK-0929 clause is resolved
   (DONE 2026-07-05); the lane remains blocked only on interval/uncertainty
   calibration repair and the FRB flagship execution window.
3. Drifted proposals backlinked: `20260610-roman-fullrepo-pr-ci-visibility`
   -> TASK-0697 (DONE), `20260610-roman-promotion-lane-throughput` ->
   TASK-0716 (DONE). Both were implemented without the backlink being
   recorded; adjudicating them again would waste a decision slot.

### D2-7 Stale proposal adjudication

- `20260503-roman-pytest-conftest-fixtures` -> ACCEPTED, canonical task
  TASK-0951 (cheap test-quality infrastructure).
- `20260520-roman-differentiable-eft-residuals` -> REJECTED: broad new
  science scaffold from the pre-consolidation era; contradicts the current
  strategy (consolidation, no new broad searches).
- `20260520-roman-symmetry-discovery-validator` -> REJECTED: same reason,
  plus the proposal's own noted overclaim risk.

### D2-8 Next external artifact — software DOI v0.2 + PRED anchor capsule

Decision: the next externally visible artifacts are (a) the software DOI for
the v0.2 codebase state minted from the existing `.zenodo.json` + a GitHub
Release, and (b) the PRED-0069..0072 anchor capsule (D2 execution below). The
second dataset DOI is explicitly deferred: it will be decided after the
TASK-0940 ThermoML packet lands (or when MD-0001 release readiness is
assessed) — it is a planned artifact, not an opportunistic one.

## Ratified engineering refinements

### R1 Validation independence (execution: TASK-0944, highest priority)

- New metadata axis inside `validation_record` of result artifacts:
  `validation_independence: independent | same_owner_different_account |
  same_account_different_tool | maintainer_self`, plus optional free-text
  `validation_independence_note`, plus a documented `replays:` list so
  multiple replayers (including external researchers, via PR) can accumulate
  per result.
- Independence is counted at the level of humans, not accounts: multiple
  accounts or tools of the same person never combine into `independent`.
  Additional same-owner replays raise reproducibility confidence only.
- Applies to ALL 10 AGENT_VALIDATED results, including RESULT-0017 and
  RESULT-0018, which are annotated `independent` — the field is a
  classification, not a confession.
- Public wording (ratified): "AGENT_VALIDATED means replayed;
  validation_independence records whether the replay was performed by an
  independent contributor, the same owner, or the same account/tool path."
- Review-tier documentation and the public dashboard wording are updated in
  the same task. Numeric results, verdicts, review_tier values, and history
  are not changed.

### R2 Nuclear freeze rule (clarified wording)

1. Interval-bearing freezes stay blocked until calibration repair.
2. The already-approved tier-1 point-only freeze (TASK-0929 Option A,
   TASK-0933) remains valid as caveated point forecasts.
3. No repeat point-only freeze without a new maintainer decision.
4. The external timestamp anchor (TASK-0945) is added now.

### R3 Zenodo MD-0002 tone

The validation-independence clarification for the published record
(10.5281/zenodo.21207072) is applied as a calm classification note via
Zenodo metadata edit — same DOI, no new version (the dataset payload did not
change), and it is not framed as a correction or erratum.

### R4 Gate B lane routing

- Validation tasks that require independence are reserved for an eligible
  identity at seed time (requirements + `can_be_done_by`), so an ineligible
  lane cannot execute-and-block (the TASK-0941 lesson).
- RESULT-0027's Gate B validation must NOT be executed by akutenyov (he is
  its publisher); its repackage + formal Gate B belongs to the gladunrv lane.
- A packaging-time Gate A check that `command` is Gate-B-replayable
  (SAFE_RESULT_COMMANDS) is committed follow-up tooling for the next wave,
  so no future RESULT is born unreplayable.

## Queued execution lanes

| Task | Lane | Priority |
| --- | --- | --- |
| TASK-0944 | validation_independence policy + annotation of all 10 results + docs/dashboard + Zenodo note pack | high |
| TASK-0945 | PRED-0069..0072 external anchor: annotated tag, GitHub Release, Zenodo capsule pack, record-back | high |
| TASK-0946 | Nuclear reveal-source watch (AME/NUBASE-class post-2026-07-05, flagged trap/ring subsets) | medium |
| TASK-0947 | FRB C1-pair checksum/schema gate @ T=2019-07-02 — reserved: akutenyov | high |
| TASK-0948 | RESULT-0020 Gate B independent replay — reserved: akutenyov, non-Claude tool | high |
| TASK-0949 | RESULT-0025 point-only Gate B replay with recorded identity — reserved: akutenyov | medium |
| TASK-0950 | Muon g-2 park execution (claim role + knowledge status) | low |
| TASK-0951 | Shared pytest fixtures (accepted proposal) | low |

## Standing constraints reaffirmed

- No large new task wave until REVIEW_READY < 8 and this batch is consumed.
- No DOU/Medium or broader promotion before TASK-0944 (integrity) and
  TASK-0945 (anchor) land.
- No new broad formula searches; consolidation remains the strategy.
