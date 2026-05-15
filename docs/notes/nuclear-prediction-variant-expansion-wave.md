# Nuclear Prediction Variant Expansion Wave

## Purpose

This note defines the shared contract for the next Nuclear Mass Surface
prediction-registry wave after `PRED-0001` through `PRED-0020`.

The goal is scalable parallel testing preparation: agents should add bounded
prospective prediction variants that can be compared later when future
maintainer-reviewed measurements are available.

These tasks are not proposal-only. Each agent should execute the variant,
calculate the registered values, validate the entry, and open a reviewable PR.

## Agent Contract

Each lane agent should:

1. Choose two bounded model/control variants inside the lane scope.
2. Freeze the model formula, coefficients, target set, source state, and reveal
   conditions before any later measurement comparison.
3. Compute `mass_excess_mev` deterministically.
4. Register exactly two `PRED-XXXX.yaml` entries unless the maintainer approves
   a larger batch.
5. Add a short review note that explains the model choice, deterministic
   calculation path, target batch, and limitations.
6. Add or update tests so the registered entries are checked before reveal.
7. Run repository validation and leave the entries as prospective forecasts,
   not claims.

## Factory Follow-Up

`TASK-0249` should automate the repetitive inner loop behind future waves. The
desired workflow is:

1. An agent or maintainer defines bounded model families and target batches in
   a YAML config.
2. A deterministic script expands those families into many candidate forecasts.
3. The script computes `mass_excess_mev`, sensitivity metadata, and draft
   review summaries without live external fetching.
4. An AI agent reviews leakage, complexity, redundancy, and scientific value.
5. Only a small selected subset is committed as reviewed `PRED-XXXX` entries.

This keeps AI agents in the scientific-curation loop while moving arithmetic,
coefficient grids, and draft generation into reproducible code.

After the initial factory lands, use the factory-wave tasks instead of adding
large raw registry batches directly:

| Task | Purpose |
| --- | --- |
| `TASK-0250` | Generate and review the first 30-80 candidate factory slate |
| `TASK-0251` | Register only the selected slate subset as `PRED-0041+` after review |
| `TASK-0252` | Extend the factory to shell, magic-number, and neutron-excess feature terms |
| `TASK-0253` | Add deterministic slate ranking / redundancy review |
| `TASK-0254` | Add reusable target-batch library for future factory configs |

## Pre-Reveal Validation

Agents can test entries before reveal by checking:

- schema validity;
- `A = Z + N`;
- no live external fetching;
- targets absent from committed measured/holdout datasets at registration time;
- deterministic recomputation of prediction values when code is added;
- explicit no-claim / no-result / no-knowledge-promotion wording;
- stable reveal conditions and no-peek rule.

Agents cannot currently test predictive success against future measurements.
That comparison requires a later reveal task and future reviewed data.

## Numbering Policy

Suggested `PRED` ranges are coordination hints, not scientific semantics.

If parallel branches collide on prediction ids, renumber the affected branch
before review or merge. The final merged repository must still contain unique
`PRED-XXXX` filenames and `prediction_id` values.

## Lane Map

| Task | Suggested outputs | Lane |
| --- | --- | --- |
| `TASK-0228` | `PRED-0021`, `PRED-0022` | smooth semi-empirical controls |
| `TASK-0229` | `PRED-0023`, `PRED-0024` | pairing / odd-even variants |
| `TASK-0230` | `PRED-0025`, `PRED-0026` | shell / magic-number bounded variants |
| `TASK-0231` | `PRED-0027`, `PRED-0028` | neutron-excess / asymmetry variants |
| `TASK-0232` | `PRED-0029`, `PRED-0030` | isotope-chain extrapolation variants |
| `TASK-0233` | `PRED-0031`, `PRED-0032` | mass-region stratified variants |
| `TASK-0234` | `PRED-0033`, `PRED-0034` | negative-control variants |
| `TASK-0235` | `PRED-0035`, `PRED-0036` | uncertainty / ensemble-style controls |
| `TASK-0236` | `PRED-0037`, `PRED-0038` | agent-designed minimal-complexity variants |
| `TASK-0237` | `PRED-0039`, `PRED-0040` | adversarial / null stress variants |

## Guardrails

- Do not fetch live external measurements during registration.
- Do not reveal or compare against future data in these tasks.
- Do not promote claims, canonical results, accepted knowledge, or discovery
  wording.
- Do not modify existing `PRED-0001` through `PRED-0020` entries except in a
  separate maintainer-approved correction task.
- Do not use failed sandbox candidates as promoted models; they may only appear
  as clearly labeled controls or negative tests when the lane permits it.
