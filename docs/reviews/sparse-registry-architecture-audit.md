# Sparse Registry Architecture Audit

Date: 2026-06-03
Task: `TASK-0558`

## Verdict

Do not delete these registries in one broad cleanup PR. They are small, but
they preserve early scientific-memory decisions and a few deterministic
examples. The useful cleanup is to classify them explicitly and stop treating
all three as equal active registry surfaces.

| Surface | Current role | Decision | Rationale |
| --- | --- | --- | --- |
| `constants_verification/` | Legacy worked example | Keep for history; no new entries by default | `CV-0001` is definitionally true and useful as an early format example, but it is not a current campaign lane. Future constants work should use Textbook Formula Audit, source/dataset standards, or canonical results rather than expanding this root registry. |
| `hypothesis_register/` | Legacy pilot registry | Keep for history; no new `HRE-*` entries | It duplicates concepts now covered by `hypothesis_proposals/`, `hypotheses/`, `results/`, and `claims/`. Its existing entries are useful historical memory, especially the rejected neutrino Koide and formalized anharmonic examples, but new hypotheses should not route here. |
| `approximation_probes/` | Small retained deterministic probe track | Retain as active-but-narrow | Unlike the other two, it has live deterministic code and tests in `physics_lab/engines/approximation_probes.py` and `tests/test_approximation_probes.py`. It can support Textbook Formula Audit style exact-reference probes, but should not become a broad root-level registry without a campaign need. |

## Dependency Inventory

`constants_verification/`

- Artifact: `constants_verification/CV-0001-fine-structure-constant.yaml`
- Schema: `physics_lab/schemas/constant_verification.schema.json`
- Schema inference: `physics_lab/registry/validation.py`
- Docs: `docs/notes/physical-constants-verification-track.md`
- Current code/tests: no dedicated loader or test path was found in the main repository validation index.

`hypothesis_register/`

- Artifacts: `hypothesis_register/HRE-0001` through `HRE-0005`
- Schema: `physics_lab/schemas/hypothesis_register_entry.schema.json`
- Schema inference: `physics_lab/registry/validation.py`
- Docs: `docs/notes/hypothesis-register-protocol.md`,
  `docs/reviews/hypothesis-register-pilot-01.md`,
  `docs/drafts/anharmonic-period-experiment-plan.md`
- Current code/tests: no dedicated repository loader in `physics_lab/registry/repository.py`; the surface is mostly historical/documentary.

`approximation_probes/`

- Artifact: `approximation_probes/AP-0001-small-angle-pendulum.yaml`
- Schema: `physics_lab/schemas/approximation_probe.schema.json`
- Schema inference: `physics_lab/registry/validation.py`
- Code: `physics_lab/engines/approximation_probes.py`
- Tests: `tests/test_approximation_probes.py`
- Docs: `docs/notes/approximation-breakdown-probes-track.md`,
  `docs/notes/pff-008-large-angle-breakdown-probe.md`

## Recommended Follow-Ups

1. Leave paths stable until a broader registry migration has tests for loader,
   validator, docs-link, snapshot, and agent-instruction compatibility.
2. Route future hypothesis ideas to `hypothesis_proposals/` or canonical
   `hypotheses/`, not `hypothesis_register/`.
3. Route future constants examples through Textbook Formula Audit, source
   artifacts, reusable datasets, or canonical `results/` when they produce
   reviewable evidence.
4. Keep `approximation_probes/` only for deterministic exact-reference
   breakdown probes with code and tests; do not expand it into a catch-all
   formula-audit registry.
5. If a later cleanup wants fewer root directories, migrate these paths only
   through a compatibility PR that updates `validation.py`, docs, tests, and
   historical links together.

## Claim Impact

No scientific claim is added or promoted. This audit classifies repository
surfaces and preserves existing artifacts as historical or narrow deterministic
memory.
