# Review Summary — RESULT-0021 (Materials MD-0002 formation-energy benchmark)

**Proposed review tier:** AGENT_PUBLISHED · **Proposed verdict:** VALID_IN_RANGE (frozen-scope)

## What this is

An agent-published benchmark result: on the checksum-pinned, holdout-frozen MD-0002
stable ternary-oxide slice, an exact cation-pair mean baseline reaches holdout
formation-energy MAE 0.200606 eV/atom vs 0.506092 eV/atom for the global-median null
(60.4% lower), robust to seeded re-splits and shuffle controls.

## Gate A self-check (all True)

- deterministic_run — `replay_materials_md0002_result.py --check` → GATE_A_REPLAY PASS (tol 1e-6)
- verification_block_populated — 6 PASS checks with metrics
- input_hashes_recorded — config/experiment/hypothesis/task sha256 pinned
- limitations_listed — 5 scope/provenance limitations
- engine_version_and_commit_pinned — engine 0.1.0, git_commit `0e23e2b6…`
- schema_validation_passes — validated against result.schema.json
- no_protected_artifact_rewrite — no CLAIM/KNOW promotion proposed
- no_forbidden_overclaim_wording — benchmark framing only; no discovery/universal-law wording
- dataset_provenance_valid — MD-0002 CC BY 4.0, DATA_LICENSES-declared, computed DFT, no live fetch

## What is explicitly NOT claimed

- No materials-discovery, design, or universal formation-energy law.
- No CLAIM or KNOW promotion (maintainer-gated; none proposed here).
- Verdict bounded to the frozen 362-row MD-0002 slice; computed-DFT residuals only.

## Suggested maintainer follow-up

Confirm the AGENT_PUBLISHED tier and the scope-limited VALID_IN_RANGE verdict; decide
separately (out of scope here) whether any claim/knowledge surface should be opened.
