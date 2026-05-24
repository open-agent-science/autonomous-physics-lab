# Anomaly Registry

## Goal

Define a guarded, machine-readable planning surface for experimental
anomalies and cross-observable tensions before APL attempts any joint fit.

The goal is not to explain the Hubble tension, muon g-2, W mass, constants,
or mass-relation topics. The goal is to make sure that if those topics are
ever evaluated, they arrive through source admissibility, frozen holdouts,
correlation handling, null-model comparison, and negative-result reporting.

## Current Status

Planning scaffold only.

`TASK-0308` defines:

- anomaly registry schema: [`data/anomalies/anomaly.schema.json`](../../data/anomalies/anomaly.schema.json);
- admissibility and joint-likelihood contract: [Anomaly Registry Admissibility](../notes/anomaly-registry-admissibility.md);
- campaign boundary and WATCHLIST posture: this page.

No anomaly rows exist. No fit has been run. No claim, result, or knowledge
entry is promoted.

## What The Registry Is For

A future anomaly registry entry should capture:

- exact observable id and domain;
- central value, unit, scheme, and uncertainty semantics;
- primary source references;
- covariance or correlation references;
- tension estimate with method and baseline model;
- frozen value and freeze timestamp;
- later measurements excluded from candidate fitting;
- limitation notes and admissibility status.

That structure is useful because cross-observable topics are easy to
overclaim. A registry-first workflow forces every future evaluator to state
what was known, what was frozen, what correlations are known, and what
counts as a negative result.

## Allowed Future Work

Allowed next steps, only after maintainer assignment:

- add empty templates or validators for anomaly entries;
- review one candidate source class without adding rows;
- create a toy synthetic likelihood harness with fabricated values only;
- define a task-specific null-model comparison protocol;
- write a negative-result preservation checklist.

## Not Allowed Yet

Do not:

- add Hubble, muon g-2, W-mass, neutron-lifetime, lithium, or other anomaly
  rows in this task;
- run a joint anomaly fit;
- rank anomalies by significance from secondary summaries;
- fit broad physical constants or mass relations;
- use discovery, explanation, or breakthrough framing;
- promote any anomaly topic out of WATCHLIST without a new maintainer task.

## Source Policy Summary

Admissible source classes:

- primary collaboration release;
- peer-reviewed measurement;
- canonical evaluation;
- archived primary dataset.

Disallowed as sole sources:

- review articles or secondary summaries;
- news posts, social media, informal plots, or slide decks without archival
  backing;
- LLM-recalled values;
- values with ambiguous units, schemes, or uncertainty semantics.

## Relationship To Existing APL Memory

The anomaly registry complements existing memory:

- Prediction registry preserves before/after forecast boundaries.
- Negative-results registry preserves failed hypotheses and falsifications.
- Claim files remain maintainer-reviewed summaries of evidence.

An anomaly entry is not a prediction, not a result, and not a claim.

## WATCHLIST Topics

These remain WATCHLIST:

- Hubble tension;
- muon g-2 follow-up;
- W-mass tension;
- broad physical-constants derivation;
- broad mass-relation searches.

This campaign page is the guardrail that prevents those topics from becoming
direct formula-search work without a source and evaluation contract.

## Recommended Next Task Shape

The safest follow-up is not a real anomaly entry. It is a schema validator or
a synthetic-only likelihood dry-run that exercises parameter penalties,
correlation-blocked entries, and negative-result reporting without using real
anomaly data.

## What Not To Claim

- Do not say APL can solve multiple anomalies.
- Do not imply unrelated tensions share a cause.
- Do not treat a smaller summed residual as evidence of new physics without
  parameter penalties and null-model comparison.
- Do not turn WATCHLIST topics into active research by citing this page.
