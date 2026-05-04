# Thought-Experiment Consistency

## Goal

Formalize classical thought experiments as deterministic consistency scenarios.
Instead of fitting formulas to data, this campaign asks whether a candidate
derivation respects explicit assumptions, invariants, and known limits.

## Why It Matters

This campaign broadens APL beyond approximation benchmarking:

- it tests invariant-preserving reasoning rather than curve fitting;
- it creates a path for analytical falsification tasks;
- it is a natural home for relativity-style consistency checks;
- it forces assumptions to be stated explicitly instead of hidden in prose.

If implemented well, this track can show that APL handles both numerical
benchmarks and structured theoretical consistency work.

## Current Results

This campaign is still planning-oriented:

- `TASK-0014` created the main suite design and is already `DONE`.
- The planning note defines candidate scenarios including the light clock,
  relativity of simultaneity, twin paradox, and Einstein elevator.
- `TASK-0028` is `READY` and scopes the light-clock case into a smaller
  follow-up planning artifact.
- No canonical experiment, no executable validator, and no result artifacts
  exist yet.

Current campaign state in one sentence:

The scenario inventory exists, but the executable consistency machinery does
not.

Start here:

- [Thought-Experiment Consistency Suite](../notes/thought-experiment-consistency-suite.md)
- [TASK-0028](../../tasks/TASK-0028-light-clock-consistency-check-planning.yaml)

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

- `TASK-0028` — plan the light-clock consistency check as a narrow next step.
- future planning tasks that isolate one scenario at a time before
  implementation.
- future implementation tasks only after the first scenario contract is stable.

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
