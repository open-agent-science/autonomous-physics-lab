# Thought-Experiment Consistency

## Goal

Formalize classical thought experiments as deterministic consistency scenarios.
Instead of fitting formulas to data, this campaign asks whether a candidate
derivation respects explicit assumptions, invariants, and known limits.

## Orientation Note for New Contributors

This campaign is **planning-first**. There are no executable benchmarks yet.
Safe contributions right now are planning, scoping, and orientation work —
not implementation.

### Safe contribution scope

- write or improve planning notes for individual scenarios;
- add assumption inventories, invariant lists, or known-limit tables;
- improve cross-links between this campaign and related APL docs;
- scope one scenario at a time as a narrow planning artifact;
- add wording that keeps scenario descriptions falsification-first.

### Good first-step patterns

- read the existing suite design at
  [Thought-Experiment Consistency Suite](../notes/thought-experiment-consistency-suite.md);
- pick one scenario from the candidate list (light clock, simultaneity,
  twin paradox, or Einstein elevator) and write a short planning note for it;
- add explicit assumption, invariant, and known-limit fields to an existing
  scenario description;
- open a task proposal if you see a planning gap with no existing task.

### What not to claim or implement yet

- do not implement an executable validator or benchmark runner for this campaign;
- do not write result artifacts or claim verdicts without a canonical experiment;
- do not imply General Relativity support — v1 scope is inertial-frame scenarios only;
- do not describe planning notes as completed theoretical verification;
- do not open a PR that generates result files under `results/` for this campaign.

The first executable benchmark for this track does not exist yet. Implementation
tasks will follow only after a stable single-scenario contract has been reviewed
and accepted by the maintainer.

## Why It Matters

This campaign broadens APL beyond approximation benchmarking:

- it tests invariant-preserving reasoning rather than curve fitting;
- it creates a path for analytical falsification tasks;
- it is a natural home for relativity-style consistency checks;
- it forces assumptions to be stated explicitly instead of hidden in prose.

If implemented well, this track can show that APL handles both numerical
benchmarks and structured theoretical consistency work.

## Current Results

This campaign is moving from planning-only toward its first executable
single-scenario benchmark:

- `TASK-0014` created the main suite design and is already `DONE`.
- The planning note defines candidate scenarios including the light clock,
  relativity of simultaneity, twin paradox, and Einstein elevator.
- `TASK-0028` is `DONE` and produced the reviewed light-clock planning artifact
  at [Light-Clock Consistency Check](../notes/light-clock-consistency-check.md).
- `TASK-0847` is the next bounded implementation task: implement only the
  TE-001 light-clock benchmark and a wrong-candidate regression before any
  broader thought-experiment suite work.
- No canonical experiment, no executable validator, and no result artifacts
  exist yet.

Current campaign state in one sentence:
The scenario inventory and light-clock contract exist, but the executable
consistency machinery does not.

Start here:

- [Thought-Experiment Consistency Suite](../notes/thought-experiment-consistency-suite.md)
- TASK-0847 after the task queue PR lands

## Open Questions

- Which scenario should become the first executable benchmark: light clock,
  simultaneity, twin paradox, or elevator?
- How should scenario-level verdicts map onto existing APL result artifacts?
- What tolerance policy is appropriate for analytical checks reduced to
  numerical evaluation?
- How should acceleration-heavy scenarios be separated from the simpler
  inertial-frame cases in the first implementation?
- Which cases should be marked `RANGE_LIMITED` or `UNDEFINED` instead of simply
  pass/fail?

## Recommended Tasks

- `TASK-0847` — implement the TE-001 light-clock consistency benchmark from the
  reviewed planning note.
- future planning or implementation tasks must isolate one scenario at a time.
- broader suite implementation waits until the first scenario contract has an
  executable benchmark and review outcome.

## Recommended Contributor Types

- contributors comfortable with classical relativity;
- formalization-focused benchmark designers;
- numerical validation contributors who can translate invariants into tests;
- documentation contributors who can keep scope and assumptions explicit.

## What Not To Claim

- Do not say APL already runs thought-experiment benchmarks.
- Do not imply General Relativity support; v1 scope is narrower.
- Do not describe these scenarios as empirical validation.
- Do not hide assumptions such as inertial frames, `v < c`, or idealized
  turnaround.
- Do not collapse planning notes into a claim of completed theoretical
  verification.

## Visualization Ideas

- scenario matrix showing assumptions, invariants, and known limits;
- mermaid flow from assumptions -> exact relation -> checks -> verdict;
- worldline sketch for the twin-paradox benchmark;
- light-clock geometry panel for the first executable scenario;
- roadmap from suite plan -> single-scenario plan -> implementation -> result.
