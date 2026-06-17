# Review Summary — RESULT-0022 (Stellar M-L DEBCat controlled benchmark)

**Proposed review tier:** AGENT_PUBLISHED · **Proposed verdict:** VALID_IN_RANGE (frozen-scope)

## What this is

An agent-published controlled benchmark: on the CC-BY-4.0, holdout-frozen DEBCat
main-sequence slice (0.5–2.0 Msun; train 102 / holdout 65), the textbook single
exponent α=3.5 beats the per-mass-band null (0.184954 vs 0.331817 dex) but is
inadequate as the sole baseline — a train-fitted α̂=4.526 (0.119925 dex) and the
piecewise α=4.0 (0.137608 dex) are better by 0.065 / 0.047 dex (> 0.04 dex
split-noise reference). Positive in 5/5 seeded splits; beats all shuffle controls.

## Gate A self-check (all True)

- deterministic_run — `replay_stellar_ml_result.py --check` → GATE_A_REPLAY PASS (tol 1e-6)
- verification_block_populated — 8 PASS checks with metrics
- input_hashes_recorded — config/experiment/hypothesis/task sha256 pinned
- limitations_listed — 5 scope/provenance limitations (incl. stale seed-flag note)
- engine_version_and_commit_pinned — engine 0.1.0, git_commit `0e23e2b6…`
- schema_validation_passes — validated against result.schema.json
- no_protected_artifact_rewrite — no CLAIM/KNOW promotion proposed
- no_forbidden_overclaim_wording — controlled-benchmark framing; α=3.5 not called falsified; no universal-law wording
- dataset_provenance_valid — DEBCat CC BY 4.0 (Southworth grant, TASK-0763), DATA_LICENSES-declared, direct dynamical masses, no live fetch

## What is explicitly NOT claimed

- No universal mass-luminosity law, stellar-evolution, or application-domain claim.
- α=3.5 is NOT falsified as a textbook relation; it is inadequate as the *sole frozen baseline* on this slice.
- No CLAIM or KNOW promotion (maintainer-gated; none proposed here).
- Verdict bounded to the frozen main-sequence 0.5–2.0 Msun slice.

## Maintainer follow-up flagged

The committed DEBCat dataset header carries seed-stage advisory flags
(`benchmark_allowed: false`, `sandbox_only: true`) authored in the TASK-0708 seed,
now superseded by TASK-0763 (CC BY publication) and the merged TASK-0759/0762
benchmark audits. A separate task should reconcile the extractor + header; this
result PR does not mutate the published dataset.
