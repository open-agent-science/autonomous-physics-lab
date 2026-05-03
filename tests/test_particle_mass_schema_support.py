from physics_lab.registry.validation import validate_document


def test_reproduction_example_config_allows_reproduction_workflow_without_train_fraction() -> None:
    payload = {
        "experiment_path": "../experiments/EXP-0003-koide-reproduction.yaml",
        "hypothesis_path": "../hypotheses/HYP-0003-koide-relation.yaml",
        "task_id": "TASK-0037",
        "run_id": "RUN-0004",
        "result_id": "RESULT-0005",
        "result_root": "../results/EXP-0003",
        "workflow": "reproduction",
    }

    assert validate_document(payload, "example_config", "examples/koide.yaml") == payload


def test_non_reproduction_example_config_still_requires_train_fraction() -> None:
    payload = {
        "experiment_path": "../experiments/EXP-0001-pendulum-formula-discovery.yaml",
        "hypothesis_path": "../hypotheses/HYP-0001-pendulum-correction.yaml",
        "task_id": "TASK-0001",
        "run_id": "RUN-0001",
        "result_id": "RESULT-0001",
        "result_root": "../results/EXP-0001",
    }

    try:
        validate_document(payload, "example_config", "examples/pendulum.yaml")
    except ValueError as exc:
        assert "train_fraction" in str(exc)
    else:
        raise AssertionError("Expected fit-style example config to require train_fraction")


def test_reproduction_experiment_schema_accepts_dataset_based_benchmark() -> None:
    payload = {
        "id": "EXP-0003",
        "title": "Charged-Lepton Koide Reproduction",
        "domain": "particle_physics",
        "status": "PLANNED",
        "hypothesis_id": "HYP-0003",
        "method": {
            "type": "dataset_reproduction",
            "simulator": "explicit_dataset_loader",
            "comparator": "target_difference",
        },
        "data": {
            "dataset_path": "data/particle_masses/charged_leptons.yaml",
            "dataset_kind": "particle_mass_dataset",
            "sample_axes": ["particle"],
        },
        "comparison_targets": [
            {
                "id": "target_koide_q",
                "label": "Koide Q target",
                "reference_value": 0.6666666667,
                "unit": None,
            }
        ],
    }

    assert validate_document(payload, "experiment", "experiments/EXP-0003.yaml") == payload


def test_reproduction_result_schema_accepts_comparison_and_uncertainty_summary() -> None:
    payload = {
        "result_id": "RESULT-0005",
        "run_id": "RUN-0004",
        "experiment_id": "EXP-0003",
        "title": "Charged-Lepton Koide Reproduction Result",
        "hypothesis_id": "HYP-0003",
        "task_id": "TASK-0037",
        "code_reference": "physics_lab/workflows/runner.py",
        "limitations": [
            "Charged-lepton scope only.",
            "No explanatory claim follows from reproduction accuracy alone.",
        ],
        "engine_version": "0.1",
        "generated_at": "2026-05-03T12:00:00Z",
        "command": "python3 -m physics_lab.cli run examples/koide.yaml --output-dir /tmp/apl-koide",
        "input_file_hashes": {
            "config": {
                "path": "examples/koide.yaml",
                "sha256": "0" * 64,
            },
            "experiment": {
                "path": "experiments/EXP-0003-koide-reproduction.yaml",
                "sha256": "1" * 64,
            },
            "hypothesis": {
                "path": "hypotheses/HYP-0003-koide-relation.yaml",
                "sha256": "2" * 64,
            },
            "task": {
                "path": "tasks/TASK-0037-reproduce-koide-charged-lepton-relation.yaml",
                "sha256": "3" * 64,
            },
        },
        "git_commit": None,
        "best_verdict": "VALID_IN_RANGE",
        "verification": {
            "passed": True,
            "checks": [
                {
                    "name": "koide_quantity_computed",
                    "status": "PASS",
                    "details": "Computed from explicit charged-lepton pole masses.",
                    "metrics": {
                        "observed_q": 0.666661,
                    },
                }
            ],
        },
        "artifacts": {
            "report": "results/EXP-0003/RUN-0004/report.md",
            "metrics": "results/EXP-0003/RUN-0004/metrics.yaml",
            "claim_update": "results/EXP-0003/RUN-0004/claim_update.md",
            "claim_update_patch": "results/EXP-0003/RUN-0004/claim_update.patch.md",
            "knowledge_update": "results/EXP-0003/RUN-0004/knowledge_update.md",
            "knowledge_update_patch": "results/EXP-0003/RUN-0004/knowledge_update.patch.md",
            "review_summary": "results/EXP-0003/RUN-0004/review_summary.md",
            "review_metadata": "results/EXP-0003/RUN-0004/review_metadata.yaml",
        },
        "comparison_summary": [
            {
                "target_id": "target_koide_q",
                "label": "Koide Q target",
                "reference_value": 0.6666666667,
                "observed_value": 0.666661,
                "unit": None,
                "absolute_difference": 0.0000056667,
                "relative_difference": 0.0000085,
            }
        ],
        "uncertainty_summary": {
            "method": "monte_carlo",
            "observed_uncertainty": 0.0000001,
            "reference_uncertainty": None,
            "combined_uncertainty": 0.0000001,
            "z_score": 56.667,
            "within_combined_uncertainty": False,
            "notes": "Reference value treated as exact benchmark target.",
        },
    }

    assert validate_document(payload, "result", "results/EXP-0003/RUN-0004/result.yaml") == payload
