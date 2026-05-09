# Blind Holdout Benchmark Protocol

## Purpose

This protocol defines a lightweight repository-native path for blind holdout or
sealed-target benchmark evaluation.

The goal is to separate model construction from target reveal. It helps future
campaigns produce stronger evidence than post hoc fitting without pretending
that existing benchmark results already used a blind protocol.

This protocol applies to future work. It does not rewrite old results.

## When To Use It

Use this protocol when a task, proposal, or microtask asks a contributor to:

- fit or select a formula from training data;
- tune a model family before evaluating hidden or withheld cases;
- compare a candidate against a baseline where post hoc target matching would
  weaken the evidence;
- run a benchmark that should preserve a clear before/after reveal record.

Do not use it for every small documentation task. The protocol is most useful
when the result could otherwise be confused with a target-aware fit.

## Roles

| Role | Responsibility |
| --- | --- |
| Contributor or agent | Creates the pre-reveal package, runs allowed training checks, and stops before target reveal. |
| Maintainer | Freezes the pre-reveal package, controls or records reveal, and decides whether the result may become canonical evidence. |
| Reviewer | Checks that the reveal did not alter pre-reveal assumptions, code, thresholds, or baselines. |

One person may play more than one role in a small private-alpha task, but the
artifacts must still make the roles auditable.

## Required Artifacts

### Pre-Reveal Package

Freeze these before any holdout target is inspected:

- task id or proposal id;
- hypothesis or candidate family;
- training data or public reference data;
- excluded holdout target description;
- exact code path and command to run;
- model-selection rule;
- baseline or null model;
- pass/fail threshold;
- expected limitations and failure modes;
- allowed output directory.

The pre-reveal package may be a task file, proposal file, note, or dedicated
benchmark manifest. It must be committed or attached to the PR before reveal.

### Reveal Record

Record the reveal step separately:

- timestamp or PR event where reveal occurred;
- who performed or approved reveal;
- revealed target file, dataset slice, or sealed value;
- command used after reveal;
- metrics and verdict;
- whether any pre-reveal artifact changed after reveal.

If a correction is needed after reveal, do not silently edit the pre-reveal
package. Add a reviewed correction note and keep the original visible.

### Result Package

A canonical result package may be created only after maintainer review. It
should include:

- pre-reveal package reference;
- reveal record reference;
- metrics on train/validation and holdout slices;
- baseline comparison;
- limitations;
- verdict;
- statement that the result is holdout-style, not universal proof.

## Workflow

1. Create or reference a canonical task.
2. Draft the pre-reveal package.
3. Run only training, validation, or public-reference checks.
4. Commit or otherwise freeze the pre-reveal package.
5. Maintainer records approval to reveal.
6. Run the reveal command exactly as recorded, or record deviations.
7. Store reveal metrics and limitations.
8. Request maintainer review before any canonical result or claim update.

## Checklist

Before reveal:

- [ ] Candidate family is frozen.
- [ ] Baseline is frozen.
- [ ] Pass/fail threshold is frozen.
- [ ] Holdout target is named without exposing its answer.
- [ ] Code path and command are frozen.
- [ ] Limitations and expected failure modes are written down.

After reveal:

- [ ] Reveal record identifies who approved or performed reveal.
- [ ] Metrics include holdout performance and baseline comparison.
- [ ] Any post-reveal deviation is explicit.
- [ ] Result wording stays scoped to the holdout benchmark.
- [ ] Claim promotion, if any, is deferred to the normal claim-promotion path.

## Application Patterns

### Formula Search

Use training data to select a candidate family and coefficients. Freeze the
selection rule and baseline before evaluating the holdout range or held-out
target.

Example:

- train on lower-amplitude oscillator periods;
- freeze the formula and threshold;
- reveal higher-amplitude holdout periods;
- report where the approximation breaks down.

### Dataset Benchmark

Use a public subset for development and a withheld subset for evaluation.
Freeze unit conventions, parser behavior, and allowed normalizations before
the withheld subset is revealed.

### Microtask Attempts

For repeatable microtask queues, the holdout package can be small:

- one note naming the candidate and training references;
- one frozen command;
- one reveal note with metrics and limitations.

Small does not mean informal. The before/after boundary must still be visible.

## What This Protocol Does Not Do

- It does not promote a hypothesis to knowledge.
- It does not create a claim by itself.
- It does not make a result stronger than its dataset, range, or assumptions.
- It does not replace repository validation, maintainer review, or canonical
  result schemas.

## Relationship To Existing Results

Existing results remain valid within their recorded scope. Do not retroactively
describe them as blind holdout results unless their artifacts already contain a
pre-reveal package and reveal record.

Future work may use this protocol to produce stronger evidence, especially for
new formula-search benchmarks and nonlinear mechanics tasks.
