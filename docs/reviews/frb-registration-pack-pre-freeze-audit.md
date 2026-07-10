# FRB Sealed-Registration Pack — Pre-Freeze Independent Audit

- Task: `TASK-0984`
- Verdict: `FREEZE_PACK_NEEDS_REPAIR`
- Audited pack: `data/radio_transients/frb_sealed_prediction_registration_pack.yaml`
  (`FRB-PRET-PRED-REGPACK-0001`, SHA-256 `0839eba264f312752a82161ea184a4ee3f94f94cf4198fe9e0b591f52bd36f6d`)
- Method: four independent audit lenses (checksum consistency; no-label/pre-T
  boundary; frozen scoring-rule fidelity; registry-entry schema dry-run and
  reveal-condition clarity), each instructed to refute the pack adversarially.
- Executor independence: this audit lane did not author the TASK-0963/0964/0965
  chain.

## Boundary Statement

This audit wrote no `prediction_registry/` file, read no repeat/repeater
labels, fetched no external source, and created no tag, release, archive,
result, claim, or success wording. The schema dry-run used a scratch copy of
the staged payload outside the repository tree.

## 1. Checksum Consistency — PASS

All 46 recorded checksum/size assertions reproduce exactly (raw SHA-256):

| Artifact | Bytes | SHA-256 (recomputed = recorded) |
| --- | ---: | --- |
| registration pack | 189,435 | `0839eba264f312752a82161ea184a4ee3f94f94cf4198fe9e0b591f52bd36f6d` |
| decision stub | 2,181 | `e11ceb7e54cdaa86e3b42e79d352f7d2fbdabca239bcf0da4c7fb2363818bc5e` |
| model surface | 46,200 | `978049b9c7360091f812ee451dae36a5ca81ccea403725a61b36c01a42f562ab` |
| selection contract | 4,253 | `5d3db1fceaafa88a0fd7c68b2c6987e96fa6cf0cd82a3a156cd5be35275ca7df` |
| feature surface | 177,389 | `8fc57714013a62b51710d48402e23b76eb8f7fa79c17b4e6b0875f06d3374b26` |

Derived digests all reproduce with
`sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))`:
`per_source_scores_sha256`, `feature_table_sha256`, the four
`score_vector_sha256` pins, `draft_entry_targets_sha256`
(`b4b26d63b53866644332a7ffb325db30ba5f9ec5ced90833e9a4dc4d393ae2bf`), and
`draft_entry_sha256` (`ad8d4224864293ce314ac189fbea41224f336eeeac50d2ad95d15148d1663567`).
The TASK-0994 dry-run capsule rebuilds byte-identically (610,063 bytes,
`fb0343894b26211b1b0c38723f79d2009a9840e51986bd25a87b823e30a5487f`). The
pinned freeze commit `3d1da6d0a627` exists. Target count, rank range 1..479,
and target-id uniqueness all verify.

Advisories (no repair required, record only): the two builder scripts use
different byte-normalization in `sha256_file` (CRLF-normalized vs raw; equal
today because no pinned file contains CR bytes); the pack's
`external_anchor_plan.capsule_manifest` lists 9 members while the TASK-0994
dry-run capsule packages 11 (the final post-approval capsule must state which
list governs); the pack review note renders two scores with `%.12g` textual
truncation (display-only).

## 2. No-Label / Pre-T Boundary — PASS

Complete field census of the staged entry and all 479 target rows: identity
keys, pre-T exposure hours, derived score/rank, and metadata only. No
repeat/repeater, morphology, Catalog-2 full-window, association, or post-T
field is present. `label_columns_read` and `source_association_columns_read`
are both empty; max first-detection MJD in the cohort is 58665.93866 < T
(58666.0 / 2019-07-02); T is recorded consistently across artifacts.

Advisories: `pre_t_detection_count_for_source_id` (feature surface; >1 on
38/479 rows) is a repeat-adjacent multiplicity signal whose semantics are
undocumented — it does not enter the frozen score or the staged entry, but
future surfaces should document or drop it; the feature surface's
`columns_intentionally_not_read` list is incomplete relative to its own
forbidden-features list (safe due to the explicit 7-column read allowlist);
the model surface does not restate the split epoch it depends on (inherited
via the SHA-pinned contract); the pre-T construction physically opened the
uncommitted Catalog-2 CSV under a declared column allowlist — process-level
residual risk, honestly declared in the artifacts.

## 3. Frozen Scoring-Rule Fidelity — PASS

Recomputing from full-precision counts via the declared rule
(`round(log1p(4*(E_upper_counts+E_lower_counts)/3600), 12)`) reproduces all
479 recorded scores exactly; the payload target set equals the feature-surface
and model-surface sets with zero additions/drops/renames; ranks are exactly
1..479, consistent with `sort(-score, source_id asc)`; all 10 tie groups
(32 rows) are genuine ties with identical underlying count totals.

Advisories: recomputing from the stored 12-dp hour columns (instead of counts)
differs by 1 ulp at the 12th decimal on 4 rows (max abs 5.1e-13, inside the
freeze script's declared tolerance 1.1e-12, cannot change any rank) — no
frozen artifact states that the canonical recompute path is from counts; the
rank tie-break rule lives only in the committed replay script, not in contract
prose.

## 4. Registry Schema Dry-Run + Reveal-Condition Clarity — ISSUES

These are the findings that set the verdict. None of them touches the
scientific content; all sit in the registration/validation machinery.

- **D1 (schema-invalid registration):** the staged payload fails the generic
  `prediction` schema on exactly two fields — `uncertainty_semantics` is a
  mapping but the schema requires a string, and
  `review_tier: MAINTAINER_REVIEW_REQUIRED` is not in the schema enum. Both
  are emitted by `scripts/prepare_frb_pred_registration_pack.py`. Registered
  as staged, `PRED-0001.yaml` would be schema-invalid; with the two fields
  fixed it validates cleanly (verified in the dry-run).
- **D2 (wrong-schema routing):** `physics_lab/registry/validation.py` infers
  kind `nuclear_mass_prediction` for any path under `prediction_registry/`,
  so validating the FRB entry would run it against the nuclear schema
  (16 spurious errors). No path-based route to the generic `prediction`
  schema exists.
- **D3 (CI blind spot):** `physics_lab/registry/repository.py` covers only
  `prediction_registry/nuclear_masses/*.yaml`, so `validate-repo --strict`
  would never schema-check the registered FRB entry — the same blind spot
  already hides `prediction_registry/exoplanet_mass_radius/PRED-0001.yaml`.
- **D4 (no placeholder guard):** the generic schema cannot stop an accidental
  registration that still contains
  `SET_BY_MAINTAINER_PREDICTION_FREEZE_DECISION` /
  `SET_TO_APPROVED_FREEZE_COMMIT` (format not enforced by the loader; commit
  field only `minLength: 1`), unlike the nuclear schema's explicit regexes.
- **D5 (reveal-clarity gap):** the staged entry does not reference the
  TASK-0995 reveal-source admissibility contract, and
  `partial_reveal_allowed: true` is undefined in the entry — a future reveal
  executor reading only the registered PRED could score a hand-picked target
  subset without violating anything written in the entry.

Advisories: the entry's `comparison_source_class` wording admits two source
classes while the TASK-0995 contract defines three; `PRED-0001` is ambiguous
across three registry subdirectories without a path qualifier;
`freeze_tier: point_score_only` is free-form vocabulary under the generic
schema.

## Required Repairs (exact, bounded)

- **R1 — pack payload repair (successor of TASK-0965, regenerate via
  `scripts/prepare_frb_pred_registration_pack.py`):** make
  `uncertainty_semantics` a string (fold the note into it); set `review_tier`
  to a schema-valid value decided by the maintainer at freeze time; add an
  explicit reference to
  `docs/reviews/frb-reveal-source-admissibility-contract.md` (and its stop
  conditions / label-status enum) to the entry's reveal fields; either define
  `partial_reveal_allowed` semantics in the entry or set it to `false`; align
  `comparison_source_class` with the contract's three admissible classes.
  Because the payload changes, re-pin `draft_entry_sha256` /
  `draft_entry_targets_sha256` (targets digest should be unchanged) and
  refresh the TASK-0994 capsule pins through a reviewed successor (the capsule
  test is an intentional tripwire and will fail until refreshed).
- **R2 — registry validation repair (separate tooling task):** route
  `prediction_registry/<domain>/` paths to their intended schemas (generic
  `prediction` for radio_transients and exoplanet_mass_radius), extend the
  repository validation patterns so `validate-repo --strict` covers all
  registry subdirectories, and add placeholder-rejecting regexes (timestamp,
  40-hex commit) to the generic prediction schema mirroring the nuclear one.
- **R3 — record-only advisories:** capsule member-list governance note,
  canonical score-recompute path (from counts), tie-break prose, builder
  hash-recipe unification, `pre_t_detection_count_for_source_id` semantics.

## Recommendation To The Maintainer

Hold the Class 2 `prediction_freeze` approval until R1 and R2 land (both are
bounded, one focused session each). The scientific content of the pack is
sound and byte-reproducible; approving before the repairs would anchor a
registration that the repository's own validation cannot check and that a
future reveal could interpret loosely.

## Output Routing

- Task verdict: `FREEZE_PACK_NEEDS_REPAIR`
- Canonical destination: this audit note (`docs/reviews/`)
- Review tier: `none` (pre-freeze audit; no tiered artifact produced)
- Gate A status: not applicable
- Gate B status: not applicable
- Prediction impact: none — no registry entry written; freeze remains blocked
  pending repairs and the maintainer decision
- Claim impact: none
- Knowledge impact: none
- Publication blocker: R1 (pack payload repair + re-pin + capsule refresh) and
  R2 (registry validation routing/coverage/placeholder guards) before any
  Class 2 approval
