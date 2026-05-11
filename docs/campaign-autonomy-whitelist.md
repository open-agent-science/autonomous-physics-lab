# Campaign Autonomy Whitelist

## Purpose

This file defines which scientific campaigns may use the first autonomous
research loop.

The whitelist is intentionally narrow. It protects APL from turning exploratory
agent output into unreviewed claims.

## Current Status

| Campaign profile | Autonomy status | Allowed use |
| --- | --- | --- |
| `pendulum-formula-falsification` | `WHITELISTED_PILOT` | First autonomous pilot campaign |
| `dimensional-analysis-validator` | `WHITELISTED_LIMITED` | Validator curation and sandbox classification proposals |
| `nuclear-mass-surface` | `WHITELISTED_LIMITED` | Sandbox-only residual pilots are allowed against the frozen baseline, pinned slice, and reviewed holdout protocol |
| `particle-mass-relations` | `GUARDRAIL_ONLY` | Falsification-first proposal work only |
| Muon g-2 formula search | `EXCLUDED` | Stress-test framing only, no autonomous sandbox research lane |
| Hubble tension empirical formulas | `EXCLUDED` | Not in first autonomy whitelist |
| Broad constants derivation | `EXCLUDED` | Not in first autonomy whitelist |

## Whitelisted Pilot

### Pendulum Formula Falsification

Pendulum is the first pilot because:

- an exact elliptic-integral reference exists;
- benchmark ranges and known failure modes are already documented;
- strong candidates can be tested against deterministic residual metrics;
- failed candidates still produce useful scientific memory;
- claim ceilings are clear and range-aware.

Allowed autonomous work:

- propose one candidate family;
- compare against exact pendulum reference data;
- report residual metrics and large-angle failure modes;
- prepare a reviewable follow-up PR.

Forbidden autonomous work:

- claiming exactness;
- claiming validity outside the configured range;
- changing canonical results;
- promoting a candidate into knowledge.

## Limited Validator Campaign

### Dimensional Analysis Validator

Dimensional analysis is allowed for limited sandbox proposals because it is a
classification benchmark with explicit expected verdicts.

Allowed autonomous work:

- propose challenge-set entries;
- classify formulas as sandbox examples;
- identify ambiguous `SUSPICIOUS` or `KNOWN_LIMIT_FAIL` cases;
- recommend future benchmark rebaseline tasks.

Forbidden autonomous work:

- silently changing the frozen MVP benchmark scope;
- reporting live curation metrics as canonical result metrics;
- treating dimensional consistency as full physical correctness.

## Guardrail-Only Campaign

### Particle-Mass Relations

Particle-mass relations remain high-risk because numerical coincidences can be
misleading. Autonomous work may only strengthen falsification, provenance,
baseline, or limitation surfaces.

Allowed autonomous work:

- draft falsification-first proposals;
- audit data provenance and scheme or scale assumptions;
- define null baselines or complexity penalties;
- record failed candidates as negative sandbox memory.

Forbidden autonomous work:

- open-ended relation search;
- explanatory language about mass generation;
- broad cross-family generalization;
- claim promotion from fit quality;
- dataset changes without source and scheme review.

## Limited Nuclear-Mass Campaign

### Nuclear Mass Surface

Nuclear mass surface work is now allowed for limited sandbox autonomy because
the repository has the minimum benchmark stack in place:

- pinned dataset loader and field semantics;
- first baseline residual benchmark;
- reviewed holdout protocol;
- explicit subset and uncertainty policy.

Allowed autonomous work:

- propose compact residual-correction families against the frozen `RESULT-0015`
  baseline on `NMD-0002`;
- execute at most a small sandbox batch with explicit rejection triage;
- preserve negative controls and holdout regressions as first-class evidence;
- package results under `hypothesis_proposals/`, `experiment_proposals/`,
  `agent_runs/`, tests, and review docs only.

Forbidden autonomous work:

- claim promotion or canonical `RESULT-*` updates;
- broad nuclear-theory language or universal-mass-formula framing;
- dataset mutation without pinned provenance policy;
- comparisons to advanced nuclear models before a reviewed follow-up task asks
  for them.

## Explicit Exclusions

Muon g-2, Hubble tension, and broad constants-derivation work are outside the
first autonomous research whitelist.

Muon g-2 may remain a guarded empirical formula-search stress test. It must not
be presented as a public success story or autonomous flagship target.

These exclusions may change only through a future reviewed task that adds a
campaign profile, quality gate, and maintainer-approved scope.
