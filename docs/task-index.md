# Task Index

This document is a compact inventory of all canonical tasks in the repository.
It is intended to help contributors find a suitable task without scanning every
task file manually.

> **Maintenance note:** This index is generated from `tasks/TASK-*.yaml` files.
> When task status changes, update the corresponding `tasks/TASK-XXXX-*.yaml`
> file and regenerate this index.

## First-Contributor Suitability

A task is marked **Yes** in the "First contributor?" column when it meets all
of these criteria:

- status is `READY`;
- difficulty is `low`;
- type is documentation, reference, planning, or safety review;
- no dependency on canonical result artifacts or shared benchmark outputs.

---

## Full Task Inventory

| ID | Title | Type | Status | Priority | Difficulty | First contributor? |
|----|-------|------|--------|----------|------------|--------------------|
| TASK-0001 | Fit better pendulum model | formula_discovery | DONE | high | medium | No |
| TASK-0002 | Verify damped oscillator regimes | regime_verification | DONE | high | medium | No |
| TASK-0003 | Theory-aware pendulum near separatrix | verifier_extension | DONE | high | high | No |
| TASK-0004 | Strengthen claim promotion policy | evidence_policy | DONE | high | medium | No |
| TASK-0005 | Add artifact hash drift validation | repository_validation | DONE | medium | medium | No |
| TASK-0006 | Establish agent task board and operating model | agent_workflow | DONE | high | medium | No |
| TASK-0007 | Strict validation fail-on-warnings | repository_validation | DONE | high | low | No |
| TASK-0008 | Machine-readable review metadata | knowledge_update | DONE | medium | medium | No |
| TASK-0009 | Plan diffusion scaling benchmark | benchmark_planning | REJECTED | high | medium | No |
| TASK-0010 | Pendulum hypothesis gauntlet (100 candidates) | formula_discovery | DONE | high | high | No |
| TASK-0011 | Audit numerical vs model error | numerical_audit | DONE | high | medium | No |
| TASK-0012 | Private multi-agent contributor dry run | agent_workflow | READY | high | medium | No |
| TASK-0013 | Plan particle mass relation falsifier | benchmark_planning | DONE | high | medium | No |
| TASK-0014 | Plan thought experiment consistency suite | benchmark_planning | DONE | high | medium | No |
| TASK-0015 | Plan diffusion scaling benchmark | benchmark_planning | REVIEW_READY | high | medium | No |
| TASK-0016 | Plan electromagnetic invariance mini-benchmark | benchmark_planning | PROPOSED | medium | medium | No |
| TASK-0017 | Create dimensional analysis challenge set | benchmark_planning | REVIEW_READY | high | medium | No |
| TASK-0018 | Support planning-only task inputs | repository_validation | DONE | high | medium | No |
| TASK-0019 | Standardize agent task protocol | agent_workflow | DONE | high | medium | No |
| TASK-0020 | Add pytest-timeout and CI safeguards | repository_validation | REVIEW_READY | medium | low | No |
| TASK-0021 | Add AI agent attribution policy | agent_workflow | REVIEW_READY | medium | low | No |
| TASK-0022 | Add PR review bundle script | agent_workflow | DONE | medium | low | No |
| TASK-0023 | Create first contributor runbook | contributor_experience | DONE | high | low | No |
| TASK-0024 | Create task index table | documentation | READY | medium | low | **Yes** |
| TASK-0025 | Create result artifacts index | documentation | READY | medium | low | **Yes** |
| TASK-0026 | Add 10 more dimensional-analysis challenge items | physics_dataset_extension | READY | high | low | **Yes** |
| TASK-0027 | Create units and physical constants reference | physics_reference | READY | medium | low | **Yes** |
| TASK-0028 | Plan light-clock thought experiment consistency check | thought_experiment_planning | READY | high | low | **Yes** |
| TASK-0029 | Audit project language for overclaim risk | scientific_safety_review | REVIEW_READY | high | low | No |
| TASK-0030 | Record first friend contributor dry run | contributor_pilot | READY | medium | low | **Yes** |
| TASK-0031 | Add beginner-friendly contributor task set | agent_workflow | DONE | high | low | No |
| TASK-0032 | Build public scientific result package for Pendulum Gauntlet 100 | release_preparation | DONE | high | medium | No |
| TASK-0033 | Standardize contributor-agent identity format | agent_workflow | DONE | high | low | No |
| TASK-0034 | Add maintainer review agent and task closeout protocol | maintainer_workflow | DONE | high | medium | No |
| TASK-0035 | Refactor maintainer review checks into smaller modules | code_quality_refactor | REVIEW_READY | medium | medium | No |
| TASK-0036 | Create particle mass dataset scaffold | scientific_dataset | REVIEW_READY | high | medium | No |
| TASK-0037 | Reproduce Koide charged-lepton relation | relation_reproduction | REVIEW_READY | high | medium | No |
| TASK-0038 | Reproduce historical tau-mass holdout prediction | historical_prediction_benchmark | READY | high | medium | No |
| TASK-0039 | Design Koide-like triplet search with baselines | benchmark_planning | REVIEW_READY | high | medium | No |
| TASK-0040 | Build particle mass relation falsifier MVP | scientific_falsification | PROPOSED | high | high | No |
| TASK-0041 | Design complexity penalty for mass-relation formulas | scoring_design | REVIEW_READY | medium | medium | No |
| TASK-0042 | Add numerology guardrails for particle mass relation work | scientific_safety_review | DONE | high | medium | No |
| TASK-0043 | Add task proposal protocol and id allocation rules | maintainer_workflow | DONE | high | medium | No |
| TASK-0044 | Sync active board and reduce conflict surface | maintainer_workflow | DONE | high | medium | No |
| TASK-0047 | Reduce closeout PR conflicts around active board sync | maintainer_workflow | READY | high | medium | No |
| TASK-0048 | Add schema support for particle-mass reproduction benchmarks | schema_extension | REVIEW_READY | high | high | No |

---

## Ready Tasks Summary

Tasks currently available to pick up:

| ID | Title | Priority | Difficulty | First contributor? |
|----|-------|----------|------------|--------------------|
| TASK-0012 | Private multi-agent contributor dry run | high | medium | No |
| TASK-0024 | Create task index table | medium | low | **Yes** |
| TASK-0025 | Create result artifacts index | medium | low | **Yes** |
| TASK-0026 | Add 10 more dimensional-analysis challenge items | high | low | **Yes** |
| TASK-0027 | Create units and physical constants reference | medium | low | **Yes** |
| TASK-0028 | Plan light-clock thought experiment consistency check | high | low | **Yes** |
| TASK-0030 | Record first friend contributor dry run | medium | low | **Yes** |
| TASK-0038 | Reproduce historical tau-mass holdout prediction | high | medium | No |
| TASK-0047 | Reduce closeout PR conflicts around active board sync | high | medium | No |
