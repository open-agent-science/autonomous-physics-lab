# NMS-008 — Pinned Nuclear Dataset Import Checklist

**Microtask:** `NMS-008`
**Campaign:** `nuclear-mass-surface`
**Type:** `source-checklist`
**Status:** REVIEW_NEEDED
**Date:** 2026-05-11

---

## Purpose

This note records a minimum review checklist for any future pinned nuclear-mass
dataset import beyond the current `NMD-0002` measured slice.

The goal is not to block later dataset work with bureaucracy. The goal is to
make source provenance, field semantics, and redistribution assumptions visible
before a broader surface is used for baseline or holdout comparisons.

---

## Checklist

### 1. Source release identity must be explicit

Record the exact source name and edition, not just "AME-style data" or a
general website reference.

Minimum expected fields:
- source title or table name;
- edition or release label;
- upstream publisher or steward;
- access date.

Why it matters:
- later reviewers need to know whether two imports came from the same release;
- time-split or post-baseline updates cannot be audited if the source version is
  vague.

### 2. Extraction method must be reviewable

Record how the committed dataset was produced from the upstream source.

Minimum expected fields:
- raw file name or table identifier;
- extraction script or manual curation note;
- row-selection rule;
- any dropped columns or transformed fields.

Why it matters:
- a pinned file is only reproducible if reviewers can understand how it was
  assembled;
- hidden filtering creates avoidable cherry-picking risk.

### 3. Checksum scope must be named, not implied

Store a checksum and describe exactly what bytes it covers.

Minimum expected fields:
- checksum algorithm;
- checksum value;
- checksum scope description such as raw table, committed YAML payload, or
  normalized export with the checksum field excluded.

Why it matters:
- a checksum without scope is weak evidence;
- reviewers need to distinguish raw-source integrity from committed-slice
  integrity.

### 4. Measured versus extrapolated semantics must remain explicit

The import must preserve whether each entry is measured, extrapolated, or
unspecified in the source layer.

Minimum expected fields:
- explicit `evaluation` value per entry or a justified dataset-level policy;
- any source flag mapping used to derive that value;
- a note when the upstream source does not cleanly separate categories.

Why it matters:
- silent mixing weakens holdout interpretation;
- measured-only and mixed-surface benchmarks answer different questions.

### 5. Field units and value shape must be declared

The import must say which primary value shape it stores and in what units.

Minimum expected fields:
- whether the dataset stores `atomic_mass_u`, `mass_excess_keV`, or both;
- uncertainty fields and their units;
- any mass-to-binding-energy conversion path delegated to deterministic code.

Why it matters:
- later residual comparisons become fragile if units are reconstructed from
  memory;
- handwritten derived fields invite drift across tasks.

### 6. Derived targets must stay reproducible

If the dataset supports binding-energy or residual-target workflows, the import
should document which values are raw inputs and which are derived later.

Minimum expected fields:
- raw-source fields retained in the committed dataset;
- code path used for derived conversions;
- statement that derived targets are not handwritten into the source file unless
  there is a strong review reason.

Why it matters:
- this keeps baseline residual definitions reviewable;
- it reduces the chance of hard-to-audit secondary numbers entering the
  benchmark surface.

### 7. Redistribution and license notes must be attached

Record any known reuse or redistribution constraints for the upstream table.

Minimum expected fields:
- redistribution note or license pointer;
- any local packaging constraint;
- whether the committed file is a raw mirror, a reduced slice, or a normalized
  representation.

Why it matters:
- source discipline includes legal and packaging clarity;
- later public-release work should not have to reconstruct whether a dataset can
  be shipped as committed repository memory.

---

## Minimum Acceptance Rule

A future dataset import should not be considered review-ready unless it can
answer all seven checklist items above in committed repository artifacts.

This does not mean every import must be large or permanent. A small measured
slice is still acceptable if its source identity, checksum scope, semantics,
and redistribution posture are explicit.

---

## Limitation

This checklist does not prove that a dataset is scientifically sufficient for a
benchmark. It only defines the minimum provenance and semantics surface needed
before reviewers can trust that later residual or holdout work is anchored to a
stable input layer.

---

## Novelty Check

Checked against:
- `microtask_runs/`
- `docs/notes/`
- `data/nuclear_masses/README.md`
- `docs/campaigns/nuclear-mass-surface.md`

Result:
- no existing note was dedicated to a compact import-review checklist for source
  version, checksum scope, field semantics, and redistribution posture together;
- existing nuclear notes already cover holdout rationale and campaign scope, but
  not this specific import checklist surface.
