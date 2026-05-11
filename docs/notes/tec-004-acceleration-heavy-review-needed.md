# TEC-004: REVIEW_NEEDED — Acceleration-Heavy Thought Experiment Assumptions

## Status: REVIEW_NEEDED

This note flags a class of thought experiments that should NOT be simplified too
aggressively without explicit maintainer or reviewer judgment.

## Scenario Class

Any scenario involving:
- Finite acceleration phases (e.g., physical twin-paradox turnaround with
  non-zero acceleration duration)
- Rotating reference frames (e.g., Sagnac effect, Ehrenfest paradox)
- Combinations of non-uniform gravity and motion (equivalence principle edge
  cases beyond the local approximation)

## Unresolved Assumption

In special relativity, an accelerating observer is not globally equivalent to
an inertial one. An agent simplifying an acceleration phase to an instantaneous
velocity change may silently violate consistency in the following ways:

1. **Clock hypothesis:** the assumption that a clock's rate depends only on
   instantaneous velocity (not on acceleration history) is an additional
   postulate within SR, not a theorem. It must be stated explicitly if used.

2. **Rotating frames:** simultaneity cannot be defined globally in a rotating
   frame without coordinate singularities (the Ehrenfest paradox). Simplifying
   a rotating scenario to a linear-motion approximation may remove the
   phenomenon being studied.

## Why Maintainer Judgment Is Needed

The inertial-frame-only SR model used in this campaign is correct and well-
defined for the specified scenarios. Extending it to acceleration-heavy cases
requires either:
- Stating the clock hypothesis as an explicit assumption, or
- Transitioning to a GR-capable formalism.

This scope decision should be made by the maintainer. Agents working
autonomously on this campaign should not extend the model to accelerating frames
without an explicit scope change.

## REVIEW_NEEDED Policy

Any thought experiment involving non-inertial motion beyond the instantaneous-
turnaround idealization should be marked REVIEW_NEEDED in this campaign until
the scope is clarified by a maintainer.
