# Materials Property Residuals

## Goal

Prepare a high-throughput APL scientific campaign around residuals of bulk
material properties (formation energy, band gap, elastic moduli, and similar)
predicted from composition and structure, using pinned public-database
snapshots, conservative baselines, residual maps, and holdout discipline.

The target is **not** materials discovery, property prediction for design, or a
new materials-science law. The target is a disciplined benchmark surface where
standard property baselines and compact agent-proposed variants can be compared
against source-pinned database rows with units, provenance (computed vs
measured), and selection effects kept visible.

The campaign is chosen because materials property databases (JARVIS-DFT,
Materials Project, OQMD, AFLOW, and similar) expose many rows and many property
axes, so they can generate a large number of bounded, parallel-safe tasks for
many agents — but only after a source-first scaffold keeps provenance and
overclaim resistance in place.

## Current Status

**Scaffold-only.** This page and the campaign profile
(`campaign_profiles/materials-property-residuals.yaml`) define scope, admissible
source classes, schema expectations, baseline/holdout/residual-map task types,
and guardrails. There is **no** pinned source snapshot, dataset, schema, loader,
baseline, claim, prediction registry entry, `RESULT-*`, or public artifact yet.
No live materials-database data has been fetched or ingested.

## Admissible Source Classes

A future source-manifest task may consider, with per-source license and version
verification before any ingestion:

- **Open computed-property databases** — JARVIS-DFT, Materials Project, OQMD,
  AFLOW (DFT-computed formation energies, band gaps, elastic tensors). Each row
  must carry the DFT functional and the database version.
- **Curated experimental compilations** — measured band gaps, formation
  enthalpies, or elastic moduli with explicit primary-source citation.
- **Reference/model-only entries** — descriptors or model outputs, admissible
  only as explicitly excluded context, never as measured rows.

Computed and measured properties are separate residual axes and must never be
merged under one metric.

## Allowed Task Types (in sequence)

1. **Source-manifest task** — register admissible sources, license, version, and
   checksum policy; no values ingested.
2. **Pinned snapshot policy task** — define a deterministic, version-pinned,
   checksum-recorded snapshot acquisition path (no live fetch inside agent
   tasks).
3. **Schema task** — define the materials row schema (property kind, units,
   structure/composition semantics, computed-vs-measured provenance, inclusion
   status).
4. **Baseline task** — a conservative per-class/per-descriptor baseline on a
   pinned snapshot, reported per property kind and per provenance axis.
5. **Holdout/no-peek protocol task** — material-family, structure-prototype,
   property-range, and source-date splits.
6. **Residual-map task** — per-property residual/failure maps with null-baseline
   comparison and explicit negative/inconclusive results.

Each task must keep property kinds and computed-vs-measured provenance separate
and must not promote a claim.

## Guardrails

Allowed current work:

- source-manifest and license/provenance review;
- schema and snapshot-policy planning;
- baseline, holdout, and residual-map planning;
- result-promotion scorecards that decide benchmark/public wording without
  promoting a materials claim.

Not allowed yet:

- live materials-database fetching inside agent tasks before a pinned snapshot
  policy exists;
- real material-property claims or broad materials-discovery wording;
- material selection, synthesis, device-fabrication, or biomedical claims or
  guidance of any kind;
- mixing computed and measured properties, or different property kinds, under
  one residual metric;
- autonomous correction search before a frozen baseline and pinned snapshot
  exist;
- public-facing article work before a reviewed residual map exists.

Future source-artifact, snapshot, schema, and residual-map tasks should follow
the [Fresh-Data Intake Protocol](../fresh-data-intake-protocol.md) so source
snapshots, extraction gates, row classes, baseline readiness, and benchmark
readiness stay separate.

## What Not To Claim

- Do not say APL discovered a new material or a material-design law.
- Do not say property residuals imply a new materials-science theory.
- Do not say the campaign supports material selection, synthesis, device
  fabrication, or biomedical applications.
- Do not provide synthesis recipes, chemical-handling, or fabrication guidance.
- Do not blur formation energy, band gap, and elastic-property residuals under
  one metric, or mix computed and measured provenance.

## Recommended Next Tasks

These are recommendations only; this scaffold creates no canonical tasks beyond
itself. Each would be a separate maintainer-approved task or proposal:

1. **Pinned materials source snapshot plan** — pick one license-clean, version
   pinnable database (JARVIS-DFT is a strong first candidate), define the
   checksum and retrieval policy, and name the first property kind and material
   scope. No ingestion.
2. **Materials row schema** — define fields, units, structure semantics, and the
   computed-vs-measured provenance separation.
3. **First conservative baseline + holdout protocol** — only after a pinned
   snapshot and schema exist.

## Why It Matters

Materials property databases combine many rows, many property axes, recognizable
baselines, and natural holdouts (material family, structure prototype, property
range, source date). A clean failure map showing where simple property baselines
break is a useful scientific artifact and an accessible public story, even if no
agent finds a better model — provided provenance discipline is kept from the
start. This scaffold exists so that discipline is in place before any data lands.
