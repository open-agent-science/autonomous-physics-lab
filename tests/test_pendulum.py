import json
from pathlib import Path
from typing import Optional

import pytest
from typer.testing import CliRunner

from physics_lab.cli import _latest_result_path, _project_stage, app
from physics_lab.engines.critic import classify_model_score
from physics_lab.engines.formula_discovery import fit_all_models
from physics_lab.engines.scoring import ModelScore, compute_error_metrics
from physics_lab.engines.simulation import exact_pendulum_period_ratio, generate_pendulum_dataset
from physics_lab.engines.symbolic import symbolic_validation_available, validate_pendulum_model_dimensions
from physics_lab.engines.verification import verify_candidate_model
from physics_lab.registry import (
    load_agent,
    load_claim,
    load_example_config,
    load_experiment,
    load_hypothesis,
    load_knowledge,
    load_result,
    load_task,
)
from physics_lab.registry.repository import validate_repository
from physics_lab.registry.task_discovery import find_task_file
from physics_lab.workflows.runner import (
    run_experiment_with_output,
    run_pendulum_experiment,
    run_pendulum_experiment_with_output,
)


def _write_task_file(
    directory: Path,
    task_id: str = "TASK-0001",
    *,
    task_type: str = "formula_discovery",
    input_lines: Optional[list[str]] = None,
) -> Path:
    path = directory / f"{task_id}-temp.yaml"
    task_input_lines = input_lines or [
        "input:",
        '  hypothesis_id: "HYP-0001"',
        '  experiment_id: "EXP-0001"',
    ]
    path.write_text(
        "\n".join(
            [
                f'id: "{task_id}"',
                'title: "Task"',
                f'type: "{task_type}"',
                'status: "OPEN"',
                'difficulty: "medium"',
                'priority: "high"',
                *task_input_lines,
                "requirements:",
                '  - "req"',
                "accepted_outputs:",
                '  - "yaml"',
                "can_be_done_by:",
                '  - "human"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def test_exact_pendulum_period_ratio_matches_small_angle_limit() -> None:
    ratio = exact_pendulum_period_ratio([1.0e-6])[0]
    assert abs(ratio - 1.0) < 1.0e-12


def test_generate_pendulum_dataset_increases_with_amplitude() -> None:
    dataset = generate_pendulum_dataset(0.01, 1.2, 20)
    assert dataset.theta.shape == (20,)
    assert dataset.period_ratio.shape == (20,)
    assert dataset.period_ratio[-1] > dataset.period_ratio[0]


def test_formula_discovery_prefers_two_term_sine_family_on_test_range() -> None:
    dataset = generate_pendulum_dataset(0.01, 1.5707963267948966, 200)
    split_index = 140
    fitted_models = fit_all_models(dataset.theta[:split_index], dataset.period_ratio[:split_index])
    scores = {
        model.candidate.model_id: compute_error_metrics(
            model.predict(dataset.theta[split_index:]),
            dataset.period_ratio[split_index:],
        )
        for model in fitted_models
    }
    assert scores["model_x_x2"].mean_relative_error < scores["model_theta2"].mean_relative_error


def test_load_task_accepts_planning_only_input_mode(tmp_path) -> None:
    task_path = _write_task_file(
        tmp_path,
        task_id="TASK-0100",
        task_type="benchmark_planning",
        input_lines=[
            "input:",
            '  mode: "planning_only"',
            '  related_domain: "particle_physics"',
            "  related_objects: []",
            '  planning_context: "Particle mass relation falsifier planning"',
        ],
    )

    payload = load_task(task_path)

    assert payload["input"]["mode"] == "planning_only"
    assert payload["input"]["related_domain"] == "particle_physics"


def test_load_task_accepts_workflow_input_mode(tmp_path) -> None:
    task_path = _write_task_file(
        tmp_path,
        task_id="TASK-0101",
        task_type="agent_workflow",
        input_lines=[
            "input:",
            '  mode: "workflow"',
            "  related_objects: []",
            '  planning_context: "Private multi-agent contributor dry run"',
        ],
    )

    payload = load_task(task_path)

    assert payload["input"]["mode"] == "workflow"


def test_theory_aware_candidate_improves_separatrix_behavior() -> None:
    dataset = generate_pendulum_dataset(0.01, 1.5707963267948966, 200)
    split_index = 140
    fitted_models = fit_all_models(dataset.theta[:split_index], dataset.period_ratio[:split_index])
    models_by_id = {model.candidate.model_id: model for model in fitted_models}

    baseline_summary = verify_candidate_model(
        models_by_id["model_theta2_theta4"],
        theta_range=(float(dataset.theta[0]), float(dataset.theta[-1])),
    )
    theory_aware_summary = verify_candidate_model(
        models_by_id["model_x_x2_log"],
        theta_range=(float(dataset.theta[0]), float(dataset.theta[-1])),
    )
    baseline_checks = {check.name: check for check in baseline_summary.checks}
    theory_aware_checks = {check.name: check for check in theory_aware_summary.checks}

    assert theory_aware_checks["near_separatrix_extrapolation"].metrics["end_ratio_to_exact"] > baseline_checks[
        "near_separatrix_extrapolation"
    ].metrics["end_ratio_to_exact"]
    assert theory_aware_checks["separatrix_asymptotic_alignment"].metrics["max_relative_error"] < baseline_checks[
        "separatrix_asymptotic_alignment"
    ].metrics["max_relative_error"]
    assert theory_aware_checks["separatrix_log_growth_rate"].metrics["relative_slope_error"] < baseline_checks[
        "separatrix_log_growth_rate"
    ].metrics["relative_slope_error"]


def test_critic_flags_invalid_model_when_errors_are_large() -> None:
    score = ModelScore(
        model_id="bad_model",
        formula="1 + a*theta^2",
        coefficients={"a": 0.0},
        complexity_score=1,
        train_metrics=compute_error_metrics([1.0, 1.0], [1.1, 1.1]),
        test_metrics=compute_error_metrics([1.0, 1.0], [1.2, 1.2]),
        composite_score=0.5,
    )
    assert classify_model_score(score) == "INVALID"


def test_verification_summary_contains_expected_checks() -> None:
    dataset = generate_pendulum_dataset(0.01, 1.5707963267948966, 120)
    fitted_models = fit_all_models(dataset.theta[:80], dataset.period_ratio[:80])
    best_model = fitted_models[1]
    summary = verify_candidate_model(
        best_model,
        theta_range=(float(dataset.theta[0]), float(dataset.theta[-1])),
    )

    check_names = {check.name for check in summary.checks}
    assert {
        "small_angle_limit",
        "small_angle_window_accuracy",
        "small_angle_curvature",
        "large_angle_window_accuracy",
        "near_separatrix_extrapolation",
        "separatrix_asymptotic_alignment",
        "separatrix_log_growth_rate",
        "evenness",
        "monotonicity",
        "dimensional_consistency",
        "known_small_angle_coefficients",
    } <= check_names
    dimensional_check = next(check for check in summary.checks if check.name == "dimensional_consistency")
    small_angle_window_check = next(
        check for check in summary.checks if check.name == "small_angle_window_accuracy"
    )
    small_angle_curvature_check = next(
        check for check in summary.checks if check.name == "small_angle_curvature"
    )
    large_angle_window_check = next(
        check for check in summary.checks if check.name == "large_angle_window_accuracy"
    )
    separatrix_check = next(
        check for check in summary.checks if check.name == "near_separatrix_extrapolation"
    )
    asymptotic_check = next(
        check for check in summary.checks if check.name == "separatrix_asymptotic_alignment"
    )
    log_growth_check = next(
        check for check in summary.checks if check.name == "separatrix_log_growth_rate"
    )
    assert dimensional_check.status == "PASS"
    assert small_angle_window_check.status == "PASS"
    assert small_angle_curvature_check.status == "PASS"
    assert large_angle_window_check.status == "PASS"
    assert separatrix_check.metrics["gate"] is False
    assert asymptotic_check.metrics["gate"] is False
    assert log_growth_check.metrics["gate"] is False


def test_symbolic_dimension_check_is_active_for_pendulum_models() -> None:
    assert symbolic_validation_available() is True
    result = validate_pendulum_model_dimensions("model_x_x2")
    theory_aware_result = validate_pendulum_model_dimensions("model_x_x2_log")

    assert result.status == "PASS"
    assert result.metrics["auxiliary_definition_count"] == 1
    assert theory_aware_result.status == "PASS"
    assert theory_aware_result.metrics["auxiliary_definition_count"] == 2


def test_runner_generates_run_based_artifacts(tmp_path) -> None:
    experiment_path = tmp_path / "EXP-0001-pendulum-formula-discovery.yaml"
    hypothesis_path = tmp_path / "HYP-0001-pendulum-correction.yaml"
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()
    config_path = tmp_path / "pendulum.yaml"
    experiment_path.write_text(
        "\n".join(
            [
                'id: "EXP-0001"',
                'title: "Pendulum Formula Discovery"',
                'domain: "classical_mechanics"',
                'status: "COMPLETED"',
                'hypothesis_id: "HYP-0001"',
                "method:",
                '  type: "formula_discovery"',
                '  simulator: "exact_pendulum_period_ratio"',
                '  fitter: "deterministic_least_squares"',
                "data:",
                "  amplitude_range_radians:",
                "    start: 0.01",
                "    end: 1.5707963267948966",
                "  sample_count: 80",
                "candidate_models:",
                '  - id: "model_theta2"',
                '    formula: "1 + a*theta^2"',
                '  - id: "model_theta2_theta4"',
                '    formula: "1 + a*theta^2 + b*theta^4"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    hypothesis_path.write_text(
        "\n".join(
            [
                'id: "HYP-0001"',
                'title: "Pendulum period correction with amplitude terms"',
                'domain: "classical_mechanics"',
                'status: "TESTING"',
                "hypothesis:",
                '  statement: "The pendulum period ratio can be approximated by low-order amplitude correction formulas."',
                "  formula_candidates:",
                '    - "T/T0 = 1 + a*theta^2"',
                'assumptions:',
                '  - "Ideal mathematical pendulum"',
                'variables:',
                "  theta:",
                '    unit: "radian"',
                '    description: "Initial angular amplitude"',
                "evidence:",
                "  experiments:",
                '    - "EXP-0001"',
                'verdict: "Initial benchmark completed. Low-order approximations are valid only within tested amplitude ranges; near-separatrix diagnostics fail for the current best candidate."',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _write_task_file(tasks_dir)
    config_path.write_text(
        "\n".join(
            [
                f"experiment_path: {experiment_path}",
                f"hypothesis_path: {hypothesis_path}",
                "task_id: TASK-0001",
                "run_id: RUN-0001",
                "result_id: RESULT-0001",
                "result_root: results/EXP-0001",
                "train_fraction: 0.7",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    outcome = run_pendulum_experiment(config_path)

    run_dir = tmp_path / "results" / "EXP-0001" / "RUN-0001"
    result_path = run_dir / "result.yaml"
    report_path = run_dir / "report.md"
    metrics_path = run_dir / "metrics.json"
    claim_update_path = run_dir / "claim_update.md"
    claim_update_patch_path = run_dir / "claim_update.patch.md"
    knowledge_update_path = run_dir / "knowledge_update.md"
    knowledge_update_patch_path = run_dir / "knowledge_update.patch.md"
    review_summary_path = run_dir / "review_summary.md"

    review_metadata_path = run_dir / "review_metadata.yaml"

    assert outcome.result_id == "RESULT-0001"
    assert outcome.run_id == "RUN-0001"
    assert result_path.exists()
    assert report_path.exists()
    assert metrics_path.exists()
    assert claim_update_path.exists()
    assert claim_update_patch_path.exists()
    assert knowledge_update_path.exists()
    assert knowledge_update_patch_path.exists()
    assert review_summary_path.exists()
    assert review_metadata_path.exists()

    result_payload = load_result(result_path)
    metrics_payload = json.loads(metrics_path.read_text(encoding="utf-8"))

    assert result_payload["result_id"] == "RESULT-0001"
    assert result_payload["run_id"] == "RUN-0001"
    assert result_payload["experiment_id"] == "EXP-0001"
    assert result_payload["task_id"] == "TASK-0001"
    assert result_payload["best_verdict"] == "VALID_IN_RANGE"
    assert result_payload["code_reference"] == "physics_lab/workflows/pendulum.py"
    assert result_payload["limitations"]
    assert result_payload["engine_version"]
    assert result_payload["generated_at"]
    assert result_payload["command"]
    assert result_payload["input_file_hashes"]["config"]["sha256"]
    assert result_payload["input_file_hashes"]["task"]["sha256"]
    assert result_payload["verification"]["checks"]
    assert result_payload["artifacts"]["report"].endswith("report.md")
    assert result_payload["artifacts"]["claim_update_patch"].endswith("claim_update.patch.md")
    assert result_payload["artifacts"]["knowledge_update_patch"].endswith("knowledge_update.patch.md")
    assert result_payload["artifacts"]["review_summary"].endswith("review_summary.md")
    assert result_payload["artifacts"]["review_metadata"].endswith("review_metadata.yaml")
    git_commit = result_payload["git_commit"]
    assert git_commit is None or (
        isinstance(git_commit, str)
        and len(git_commit) == 40
        and all(char in "0123456789abcdef" for char in git_commit)
    )

    assert metrics_payload["result_id"] == "RESULT-0001"
    assert metrics_payload["run_id"] == "RUN-0001"
    assert metrics_payload["verification"]["checks"]

    assert "Proposed Update for CLAIM-0001" in claim_update_path.read_text(encoding="utf-8")
    claim_patch_text = claim_update_patch_path.read_text(encoding="utf-8")
    assert "## Proposed Diff" in claim_patch_text
    assert "CLAIM-0001" in claim_patch_text
    knowledge_update_text = knowledge_update_path.read_text(encoding="utf-8")
    knowledge_patch_text = knowledge_update_patch_path.read_text(encoding="utf-8")
    assert "Proposed Update for KNOW-0001" in knowledge_update_text
    assert "## Target Knowledge Note" in knowledge_update_text
    assert "## Suggested Linked Objects Update" in knowledge_update_text
    assert "## Proposed Diff" in knowledge_patch_text
    assert "## Required Maintainer Action" in review_summary_path.read_text(encoding="utf-8")
    assert "## Verification" in report_path.read_text(encoding="utf-8")

    import yaml as _yaml
    review_metadata = _yaml.safe_load(review_metadata_path.read_text(encoding="utf-8"))
    assert review_metadata["schema_version"] == "1"
    assert review_metadata["artifact_type"] == "review_metadata"
    assert review_metadata["result_id"] == "RESULT-0001"
    assert review_metadata["run_id"] == "RUN-0001"
    assert review_metadata["experiment_id"] == "EXP-0001"
    assert review_metadata["claim_id"] == "CLAIM-0001"
    assert review_metadata["knowledge_id"] == "KNOW-0001"
    assert review_metadata["required_human_review"] is True
    assert isinstance(review_metadata["evidence_basis"], list)
    assert len(review_metadata["evidence_basis"]) >= 1
    assert review_metadata["patch_artifacts"]["claim_patch"].endswith("claim_update.patch.md")
    assert review_metadata["patch_artifacts"]["knowledge_patch"].endswith("knowledge_update.patch.md")
    assert review_metadata["patch_artifacts"]["review_summary"].endswith("review_summary.md")


def test_runner_resolves_config_paths_relative_to_config_location(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    examples_dir = repo_root / "examples"
    experiments_dir = repo_root / "experiments"
    hypotheses_dir = repo_root / "hypotheses"
    tasks_dir = repo_root / "tasks"
    examples_dir.mkdir(parents=True)
    experiments_dir.mkdir()
    hypotheses_dir.mkdir()
    tasks_dir.mkdir()
    (repo_root / "pyproject.toml").write_text("[project]\nname='tmp'\nversion='0.0.0'\n", encoding="utf-8")

    config_path = examples_dir / "pendulum.yaml"
    experiment_path = experiments_dir / "EXP-0001-pendulum-formula-discovery.yaml"
    hypothesis_path = hypotheses_dir / "HYP-0001-pendulum-correction.yaml"
    experiment_path.write_text(
        "\n".join(
            [
                'id: "EXP-0001"',
                'title: "Pendulum Formula Discovery"',
                'domain: "classical_mechanics"',
                'status: "COMPLETED"',
                'hypothesis_id: "HYP-0001"',
                "method:",
                '  type: "formula_discovery"',
                '  simulator: "exact_pendulum_period_ratio"',
                '  fitter: "deterministic_least_squares"',
                "data:",
                "  amplitude_range_radians:",
                "    start: 0.01",
                "    end: 1.5707963267948966",
                "  sample_count: 40",
                "candidate_models:",
                '  - id: "model_theta2"',
                '    formula: "1 + a*theta^2"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    hypothesis_path.write_text(
        "\n".join(
            [
                'id: "HYP-0001"',
                'title: "Pendulum period correction with amplitude terms"',
                'domain: "classical_mechanics"',
                'status: "TESTING"',
                "hypothesis:",
                '  statement: "The pendulum period ratio can be approximated by low-order amplitude correction formulas."',
                "  formula_candidates:",
                '    - "T/T0 = 1 + a*theta^2"',
                'assumptions:',
                '  - "Ideal mathematical pendulum"',
                'variables:',
                "  theta:",
                '    unit: "radian"',
                '    description: "Initial angular amplitude"',
                "evidence:",
                "  experiments:",
                '    - "EXP-0001"',
                'verdict: "Initial benchmark completed. Low-order approximations are valid only within tested amplitude ranges; near-separatrix diagnostics fail for the current best candidate."',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _write_task_file(tasks_dir)
    config_path.write_text(
        "\n".join(
            [
                "experiment_path: ../experiments/EXP-0001-pendulum-formula-discovery.yaml",
                "hypothesis_path: ../hypotheses/HYP-0001-pendulum-correction.yaml",
                "task_id: TASK-0001",
                "run_id: RUN-0001",
                "result_id: RESULT-0001",
                "result_root: ../results/EXP-0001",
                "train_fraction: 0.7",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    outcome = run_pendulum_experiment(config_path)

    assert outcome.artifacts.result_path == repo_root / "results" / "EXP-0001" / "RUN-0001" / "result.yaml"
    assert outcome.artifacts.report_path == repo_root / "results" / "EXP-0001" / "RUN-0001" / "report.md"
    assert outcome.artifacts.metrics_path == repo_root / "results" / "EXP-0001" / "RUN-0001" / "metrics.json"
    assert outcome.artifacts.claim_update_path == repo_root / "results" / "EXP-0001" / "RUN-0001" / "claim_update.md"
    assert outcome.artifacts.claim_update_patch_path == repo_root / "results" / "EXP-0001" / "RUN-0001" / "claim_update.patch.md"
    assert outcome.artifacts.knowledge_update_path == repo_root / "results" / "EXP-0001" / "RUN-0001" / "knowledge_update.md"
    assert outcome.artifacts.knowledge_update_patch_path == repo_root / "results" / "EXP-0001" / "RUN-0001" / "knowledge_update.patch.md"
    assert outcome.artifacts.review_summary_path == repo_root / "results" / "EXP-0001" / "RUN-0001" / "review_summary.md"


def test_cli_run_smoke(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["run", "examples/pendulum.yaml", "--output-dir", str(tmp_path / "apl-pendulum-test")],
    )

    assert result.exit_code == 0
    assert "Completed: Pendulum Formula Discovery" in result.stdout
    assert "Result:" in result.stdout
    assert "Claim update:" in result.stdout
    assert "Claim patch:" in result.stdout
    assert "Knowledge update:" in result.stdout
    assert "Knowledge patch:" in result.stdout
    assert "Review summary:" in result.stdout
    assert "Review metadata:" in result.stdout


def test_runner_output_override_writes_outside_repo_results(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    examples_dir = repo_root / "examples"
    experiments_dir = repo_root / "experiments"
    hypotheses_dir = repo_root / "hypotheses"
    tasks_dir = repo_root / "tasks"
    results_dir = repo_root / "results"
    examples_dir.mkdir(parents=True)
    experiments_dir.mkdir()
    hypotheses_dir.mkdir()
    tasks_dir.mkdir()
    results_dir.mkdir()
    (repo_root / "pyproject.toml").write_text("[project]\nname='tmp'\nversion='0.0.0'\n", encoding="utf-8")

    config_path = examples_dir / "pendulum.yaml"
    experiment_path = experiments_dir / "EXP-0001-pendulum-formula-discovery.yaml"
    hypothesis_path = hypotheses_dir / "HYP-0001-pendulum-correction.yaml"
    experiment_path.write_text(
        "\n".join(
            [
                'id: "EXP-0001"',
                'title: "Pendulum Formula Discovery"',
                'domain: "classical_mechanics"',
                'status: "COMPLETED"',
                'hypothesis_id: "HYP-0001"',
                "method:",
                '  type: "formula_discovery"',
                '  simulator: "exact_pendulum_period_ratio"',
                '  fitter: "deterministic_least_squares"',
                "data:",
                "  amplitude_range_radians:",
                "    start: 0.01",
                "    end: 1.5707963267948966",
                "  sample_count: 40",
                "candidate_models:",
                '  - id: "model_theta2"',
                '    formula: "1 + a*theta^2"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    hypothesis_path.write_text(
        "\n".join(
            [
                'id: "HYP-0001"',
                'title: "Pendulum period correction with amplitude terms"',
                'domain: "classical_mechanics"',
                'status: "TESTING"',
                "hypothesis:",
                '  statement: "The pendulum period ratio can be approximated by low-order amplitude correction formulas."',
                "  formula_candidates:",
                '    - "T/T0 = 1 + a*theta^2"',
                'assumptions:',
                '  - "Ideal mathematical pendulum"',
                'variables:',
                "  theta:",
                '    unit: "radian"',
                '    description: "Initial angular amplitude"',
                "evidence:",
                "  experiments:",
                '    - "EXP-0001"',
                "  results:",
                '    - "RESULT-0001"',
                'verdict: "Initial benchmark completed. Low-order approximations are valid only within tested amplitude ranges; near-separatrix diagnostics fail for the current best candidate."',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    _write_task_file(tasks_dir)
    config_path.write_text(
        "\n".join(
            [
                "experiment_path: ../experiments/EXP-0001-pendulum-formula-discovery.yaml",
                "hypothesis_path: ../hypotheses/HYP-0001-pendulum-correction.yaml",
                "task_id: TASK-0001",
                "run_id: RUN-0001",
                "result_id: RESULT-0001",
                "result_root: ../results/EXP-0001",
                "train_fraction: 0.7",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    output_dir = tmp_path / "external-results"
    outcome = run_pendulum_experiment_with_output(config_path, output_dir=output_dir)

    assert outcome.artifacts.result_path == output_dir / "EXP-0001" / "RUN-0001" / "result.yaml"
    assert outcome.artifacts.result_path.exists()
    assert not (repo_root / "results" / "EXP-0001" / "RUN-0001" / "result.yaml").exists()


def test_registry_files_validate_against_schemas() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    load_claim(repo_root / "claims" / "CLAIM-0001-pendulum-period-amplitude.md")
    load_example_config(repo_root / "examples" / "pendulum.yaml")
    load_hypothesis(repo_root / "hypotheses" / "HYP-0001-pendulum-correction.yaml")
    load_experiment(repo_root / "experiments" / "EXP-0001-pendulum-formula-discovery.yaml")
    load_knowledge(repo_root / "knowledge" / "classical_mechanics" / "pendulum.md")
    load_task(find_task_file(repo_root, "TASK-0001"))
    load_agent(repo_root / "tests" / "fixtures" / "example-agent.yaml")


def test_cli_validate_hypothesis_smoke() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "hypotheses/HYP-0001-pendulum-correction.yaml"])

    assert result.exit_code == 0
    assert "Validated hypotheses/HYP-0001-pendulum-correction.yaml as hypothesis." in result.stdout


def test_cli_validate_result_smoke(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    run_pendulum_experiment_with_output(
        repo_root / "examples" / "pendulum.yaml",
        output_dir=tmp_path / "apl-pendulum-validate",
    )
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "results/EXP-0001/RUN-0002/result.yaml"])

    assert result.exit_code == 0
    assert "Validated results/EXP-0001/RUN-0002/result.yaml as result." in result.stdout


@pytest.mark.full_repo
def test_validate_repository_smoke(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    run_pendulum_experiment_with_output(
        repo_root / "examples" / "pendulum.yaml",
        output_dir=tmp_path / "apl-pendulum-repo-validate",
    )
    summary = validate_repository(repo_root)
    # Archive-aware: canonical tasks live flat under tasks/ or in
    # tasks/archive/<bucket>/, so count recursively to match the loader.
    expected_task_count = len(
        [
            path
            for path in (repo_root / "tasks").rglob("TASK-[0-9][0-9][0-9][0-9]-*.yaml")
            if path.name != "TASK-TEMPLATE.yaml"
        ]
    )
    expected_knowledge_count = len(list((repo_root / "knowledge").rglob("*.md")))

    assert summary.counts["claims"] == len(list((repo_root / "claims").glob("CLAIM-*.md")))
    assert summary.counts["examples"] == len(list((repo_root / "examples").glob("*.yaml")))
    assert summary.counts["hypotheses"] == len(list((repo_root / "hypotheses").glob("HYP-*.yaml")))
    assert summary.counts["experiments"] == len(list((repo_root / "experiments").glob("EXP-*.yaml")))
    assert summary.counts["knowledge"] == expected_knowledge_count
    assert summary.counts["tasks"] == expected_task_count
    assert summary.counts["agents"] == len(list((repo_root / "agents").glob("*.yaml")))
    assert summary.counts["results"] == len(list((repo_root / "results").glob("*/*/result.yaml")))


def test_validate_repository_detects_missing_reference(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    for directory in ("agents", "claims", "experiments", "hypotheses", "results", "tasks"):
        (repo_root / directory).mkdir(parents=True, exist_ok=True)

    (repo_root / "hypotheses" / "HYP-0001.yaml").write_text(
        "\n".join(
            [
                'id: "HYP-0001"',
                'title: "Hypothesis"',
                'domain: "test"',
                'status: "FORMALIZED"',
                "hypothesis:",
                '  statement: "Test statement"',
                "  formula_candidates:",
                '    - "x"',
                "assumptions:",
                '  - "Assumption"',
                "variables:",
                "  x:",
                '    unit: "1"',
                '    description: "Variable"',
                "evidence:",
                "  experiments:",
                '    - "EXP-9999"',
                'verdict: "Pending"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    try:
        validate_repository(repo_root)
    except ValueError as exc:
        assert "missing experiment id" in str(exc)
    else:
        raise AssertionError("Expected missing reference validation to fail")


def test_validate_repository_allows_planning_task_without_fake_science_refs(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    for directory in ("agents", "claims", "experiments", "hypotheses", "results", "tasks"):
        (repo_root / directory).mkdir(parents=True, exist_ok=True)

    (repo_root / "tasks" / "TASK-0018-temp.yaml").write_text(
        "\n".join(
            [
                'id: "TASK-0018"',
                'title: "Planning Task"',
                'type: "benchmark_planning"',
                'status: "READY"',
                'difficulty: "medium"',
                'priority: "high"',
                "input:",
                '  mode: "planning_only"',
                '  related_domain: "particle_physics"',
                "  related_objects: []",
                '  planning_context: "Particle mass relation falsifier planning"',
                "requirements:",
                '  - "deterministic"',
                "accepted_outputs:",
                '  - "markdown"',
                "can_be_done_by:",
                '  - "human"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = validate_repository(repo_root)

    assert summary.counts["tasks"] == 1


def test_validate_repository_rejects_duplicate_canonical_task_ids(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    for directory in ("agents", "claims", "experiments", "hypotheses", "results", "tasks"):
        (repo_root / directory).mkdir(parents=True, exist_ok=True)

    task_payload = "\n".join(
        [
            'id: "TASK-0087"',
            'title: "Duplicate Task"',
            'type: "benchmark_planning"',
            'status: "READY"',
            'difficulty: "low"',
            'priority: "high"',
            "input:",
            '  mode: "planning_only"',
            '  related_domain: "task_coordination"',
            "  related_objects: []",
            '  planning_context: "Duplicate task id regression test"',
            "requirements:",
            '  - "stay unique"',
            "accepted_outputs:",
            '  - "canonical task spec"',
            "can_be_done_by:",
            '  - "human"',
        ]
    ) + "\n"

    (repo_root / "tasks" / "TASK-0087-first.yaml").write_text(task_payload, encoding="utf-8")
    (repo_root / "tasks" / "TASK-0087-second.yaml").write_text(task_payload, encoding="utf-8")

    try:
        validate_repository(repo_root)
    except ValueError as exc:
        assert "Duplicate canonical task id TASK-0087" in str(exc)
    else:
        raise AssertionError("Expected duplicate task id validation to fail")


def test_validate_repository_keeps_science_task_references_strict(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    for directory in ("agents", "claims", "experiments", "hypotheses", "results", "tasks"):
        (repo_root / directory).mkdir(parents=True, exist_ok=True)

    (repo_root / "tasks" / "TASK-0001-temp.yaml").write_text(
        "\n".join(
            [
                'id: "TASK-0001"',
                'title: "Science Task"',
                'type: "formula_discovery"',
                'status: "READY"',
                'difficulty: "medium"',
                'priority: "high"',
                "input:",
                '  hypothesis_id: "HYP-9999"',
                '  experiment_id: "EXP-9999"',
                "requirements:",
                '  - "deterministic"',
                "accepted_outputs:",
                '  - "markdown"',
                "can_be_done_by:",
                '  - "human"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    try:
        validate_repository(repo_root)
    except ValueError as exc:
        assert "missing hypothesis_id" in str(exc)
    else:
        raise AssertionError("Expected science task reference validation to fail")


@pytest.mark.full_repo
@pytest.mark.xdist_group("full_repo_smoke")
def test_cli_validate_repo_smoke(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    run_pendulum_experiment_with_output(
        repo_root / "examples" / "pendulum.yaml",
        output_dir=tmp_path / "apl-pendulum-cli-validate-repo",
    )
    summary = validate_repository(repo_root)
    runner = CliRunner()
    result = runner.invoke(app, ["validate-repo", "."])

    assert result.exit_code == 0
    assert "Validated repository:" in result.stdout
    assert f"- examples: {summary.counts['examples']}" in result.stdout
    assert f"- hypotheses: {summary.counts['hypotheses']}" in result.stdout
    assert f"- knowledge: {summary.counts['knowledge']}" in result.stdout


@pytest.mark.full_repo
@pytest.mark.xdist_group("full_repo_smoke")
def test_cli_validate_repo_strict_smoke() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["validate-repo", ".", "--strict"])

    assert result.exit_code == 0
    assert "Strict validation: PASS" in result.stdout
    assert "ERROR" in result.stdout
    assert "INFO" in result.stdout


@pytest.mark.full_repo
@pytest.mark.xdist_group("full_repo_smoke")
def test_cli_status_smoke(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    run_pendulum_experiment_with_output(
        repo_root / "examples" / "pendulum.yaml",
        output_dir=tmp_path / "apl-pendulum-status",
    )
    latest_result_path = _latest_result_path(repo_root)
    assert latest_result_path is not None
    latest_result = load_result(latest_result_path)
    runner = CliRunner()
    result = runner.invoke(app, ["status", "."])

    assert result.exit_code == 0
    assert f"Stage: {_project_stage(repo_root)}" in result.stdout
    assert f"Run id: {latest_result['run_id']}" in result.stdout
    assert "Validation: PASS" in result.stdout
    assert f"Best verdict: {latest_result['best_verdict']}" in result.stdout
    assert "Verification checks:" in result.stdout
    if latest_result.get("comparison_summary"):
        assert "Primary comparison:" in result.stdout
        assert "Uncertainty:" in result.stdout
    else:
        assert "Best model:" in result.stdout


def test_run_dispatches_pendulum_with_output_dir(tmp_path) -> None:
    outcome = run_experiment_with_output(
        Path("examples/pendulum.yaml"),
        output_dir=tmp_path / "apl-results",
    )

    assert outcome.result_id == "RESULT-0003"
    assert outcome.artifacts.result_path == tmp_path / "apl-results" / "EXP-0001" / "RUN-0002" / "result.yaml"


def test_cli_validate_review_metadata_smoke() -> None:
    """CLI validate must correctly identify and validate review_metadata.yaml by filename."""
    runner = CliRunner()
    result = runner.invoke(
        app, ["validate", "results/EXP-0001/RUN-0002/review_metadata.yaml"]
    )

    assert result.exit_code == 0
    assert "review_metadata" in result.stdout


def test_infer_kind_from_path_review_metadata() -> None:
    """infer_kind_from_path must return review_metadata for any review_metadata.yaml path."""
    from physics_lab.registry.validation import infer_kind_from_path

    assert infer_kind_from_path("results/EXP-0001/RUN-0001/review_metadata.yaml") == "review_metadata"
    assert infer_kind_from_path("/absolute/results/EXP-0002/RUN-0001/review_metadata.yaml") == "review_metadata"


def test_gauntlet_produces_100_unique_candidates() -> None:
    from physics_lab.engines.gauntlet import build_gauntlet_candidates, atom_family

    atom_groups, models = build_gauntlet_candidates()

    assert len(models) == 100
    assert len(atom_groups) == 100

    model_ids = [m.model_id for m in models]
    assert len(set(model_ids)) == 100, "All model IDs must be unique"

    for mid in model_ids:
        assert mid.startswith("model_"), f"model_id must match schema pattern: {mid}"
        assert mid == mid.lower(), f"model_id must be lowercase: {mid}"

    families = {atom_family(g) for g in atom_groups}
    assert "theta_poly" in families
    assert "x_poly" in families

    size1 = [g for g in atom_groups if len(g) == 1]
    size2 = [g for g in atom_groups if len(g) == 2]
    size3 = [g for g in atom_groups if len(g) == 3]
    assert len(size1) == 11
    assert len(size2) == 55
    assert len(size3) == 34


def test_gauntlet_legacy_candidate_set_preserves_original_enumeration() -> None:
    from physics_lab.engines.gauntlet import build_gauntlet_candidates

    atom_groups, models = build_gauntlet_candidates(atom_set="legacy_10")

    assert len(models) == 100
    assert len({model.model_id for model in models}) == 100
    assert "model_l0" not in {model.model_id for model in models}

    size1 = [group for group in atom_groups if len(group) == 1]
    size2 = [group for group in atom_groups if len(group) == 2]
    size3 = [group for group in atom_groups if len(group) == 3]
    assert len(size1) == 10
    assert len(size2) == 45
    assert len(size3) == 45


def test_asymptotic_refined_candidate_passes_configured_large_angle_window() -> None:
    from physics_lab.engines.gauntlet import build_asymptotic_refined_candidate
    from physics_lab.engines.formula_discovery import fit_candidate_model
    from physics_lab.engines.scoring import score_model
    from physics_lab.workflows.artifacts import split_dataset

    dataset = generate_pendulum_dataset(0.01, 3.10, 200)
    split_index = split_dataset(sample_count=200, train_fraction=0.7)
    _, candidate = build_asymptotic_refined_candidate()
    fitted_model = fit_candidate_model(
        candidate,
        dataset.theta[:split_index],
        dataset.period_ratio[:split_index],
    )
    score = score_model(
        fitted_model=fitted_model,
        train_theta=dataset.theta[:split_index],
        train_target=dataset.period_ratio[:split_index],
        test_theta=dataset.theta[split_index:],
        test_target=dataset.period_ratio[split_index:],
    )
    verification = verify_candidate_model(
        fitted_model,
        theta_range=(float(dataset.theta[0]), float(dataset.theta[-1])),
    )
    checks = {check.name: check for check in verification.checks}

    assert score.test_metrics.max_relative_error < 5.0e-5
    assert verification.passed is True
    assert checks["large_angle_window_accuracy"].status == "PASS"
    assert checks["separatrix_asymptotic_alignment"].status == "PASS"


def test_gauntlet_candidates_are_numerically_stable() -> None:
    import numpy as np
    from physics_lab.engines.gauntlet import build_gauntlet_candidates

    theta = np.linspace(1e-4, np.pi - 1e-3, 50)
    _, models = build_gauntlet_candidates()
    for model in models:
        features = model.feature_builder(theta)
        assert features.shape == (50, model.complexity_score)
        assert np.all(np.isfinite(features)), f"Non-finite features for {model.model_id}"


def test_gauntlet_run_produces_leaderboard(tmp_path) -> None:
    import json
    experiment_path = tmp_path / "EXP-0001-pendulum-formula-discovery.yaml"
    hypothesis_path = tmp_path / "HYP-0001-pendulum-correction.yaml"
    tasks_dir = tmp_path / "tasks"
    tasks_dir.mkdir()
    config_path = tmp_path / "pendulum_gauntlet.yaml"
    experiment_path.write_text(
        "\n".join([
            'id: "EXP-0001"',
            'title: "Pendulum Formula Discovery"',
            'domain: "classical_mechanics"',
            'status: "COMPLETED"',
            'hypothesis_id: "HYP-0001"',
            "method:",
            '  type: "formula_discovery"',
            '  simulator: "exact_pendulum_period_ratio"',
            '  fitter: "deterministic_least_squares"',
            "data:",
            "  amplitude_range_radians:",
            "    start: 0.01",
            "    end: 1.5707963267948966",
            "  sample_count: 80",
            "candidate_models:",
            '  - id: "model_theta2"',
            '    formula: "1 + a*theta^2"',
        ]) + "\n",
        encoding="utf-8",
    )
    hypothesis_path.write_text(
        "\n".join([
            'id: "HYP-0001"',
            'title: "Pendulum period correction with amplitude terms"',
            'domain: "classical_mechanics"',
            'status: "TESTING"',
            "hypothesis:",
            '  statement: "The pendulum period ratio can be approximated by low-order amplitude correction formulas."',
            "  formula_candidates:",
            '    - "T/T0 = 1 + a*theta^2"',
            "assumptions:",
            '  - "Ideal mathematical pendulum"',
            "variables:",
            "  theta:",
            '    unit: "radian"',
            '    description: "Initial angular amplitude"',
            "evidence:",
            "  experiments:",
            '    - "EXP-0001"',
            'verdict: "Pending"',
        ]) + "\n",
        encoding="utf-8",
    )
    _write_task_file(tasks_dir, task_id="TASK-0010")
    config_path.write_text(
        "\n".join([
            f"experiment_path: {experiment_path}",
            f"hypothesis_path: {hypothesis_path}",
            "task_id: TASK-0010",
            "run_id: RUN-0003",
            "result_id: RESULT-0004",
            "result_root: results/EXP-0001",
            "train_fraction: 0.7",
            "workflow: gauntlet",
        ]) + "\n",
        encoding="utf-8",
    )

    from physics_lab.workflows.gauntlet import run_gauntlet_experiment_with_output

    outcome = run_gauntlet_experiment_with_output(config_path)

    run_dir = tmp_path / "results" / "EXP-0001" / "RUN-0003"
    assert (run_dir / "result.yaml").exists()
    assert (run_dir / "report.md").exists()
    assert (run_dir / "metrics.json").exists()
    assert (run_dir / "leaderboard.json").exists()
    assert (run_dir / "leaderboard.md").exists()
    assert (run_dir / "claim_update.md").exists()
    assert (run_dir / "review_metadata.yaml").exists()

    assert outcome.result_id == "RESULT-0004"
    assert outcome.run_id == "RUN-0003"
    assert len(outcome.scores) == 100

    leaderboard = json.loads((run_dir / "leaderboard.json").read_text(encoding="utf-8"))
    assert leaderboard["total_candidates"] == 100
    assert len(leaderboard["entries"]) == 100
    assert leaderboard["entries"][0]["rank"] == 1

    from physics_lab.registry.results import load_result
    result_payload = load_result(run_dir / "result.yaml")
    assert result_payload["result_id"] == "RESULT-0004"
    assert result_payload["best_verdict"] in ("VALID_IN_RANGE", "PARTIALLY_VALID", "INVALID")
    assert len(result_payload["scores"]) == 100


def test_gauntlet_config_validates_as_example_config() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    load_example_config(repo_root / "examples" / "pendulum_gauntlet.yaml")


def test_canonical_pendulum_gauntlet_replay_preserves_run_0003_invariants(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    outcome = run_experiment_with_output(
        repo_root / "examples" / "pendulum_gauntlet.yaml",
        output_dir=tmp_path / "replay",
    )
    result_payload = load_result(tmp_path / "replay" / "EXP-0001" / "RUN-0003" / "result.yaml")

    assert outcome.best_model_id == "model_t4_x1"
    assert result_payload["best_model_id"] == "model_t4_x1"
    assert result_payload["best_verdict"] == "VALID_IN_RANGE"
    assert result_payload["gauntlet_candidate_set"] == "legacy_10"
    assert len(result_payload["scores"]) == 100


def test_canonical_constrained_gauntlet_replay_preserves_run_0004_invariants(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    outcome = run_experiment_with_output(
        repo_root / "examples" / "pendulum_constrained_gauntlet.yaml",
        output_dir=tmp_path / "replay",
    )
    result_payload = load_result(tmp_path / "replay" / "EXP-0001" / "RUN-0004" / "result.yaml")

    assert outcome.best_model_id == "model_t2_x4_l2"
    assert result_payload["best_model_id"] == "model_t2_x4_l2"
    assert result_payload["best_verdict"] == "OVERFITTED"
    assert result_payload["gauntlet_candidate_set"] == "legacy_10"
    assert len(result_payload["scores"]) == 101


def test_cli_run_gauntlet_smoke(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["run", "examples/pendulum_gauntlet.yaml", "--output-dir", str(tmp_path / "apl-gauntlet-test")],
    )

    assert result.exit_code == 0, result.output
    assert "Completed:" in result.stdout
    assert "Gauntlet" in result.stdout
    assert "Best model:" in result.stdout
    assert "Result:" in result.stdout
    assert "Claim update:" in result.stdout
    assert "Review metadata:" in result.stdout


def test_independent_pendulum_reference_matches_standard_reference_on_run_0003_grid() -> None:
    import numpy as np

    from physics_lab.engines.precision_audit import independent_pendulum_period_ratio
    from physics_lab.engines.simulation import exact_pendulum_period_ratio
    from physics_lab.workflows.artifacts import split_dataset

    theta = np.linspace(0.01, np.pi / 2.0, 200)
    split_index = split_dataset(200, 0.7)
    test_theta = theta[split_index:]

    standard_reference = exact_pendulum_period_ratio(test_theta)
    independent_reference, quadrature_error = independent_pendulum_period_ratio(test_theta)
    relative_error = np.abs(standard_reference - independent_reference) / independent_reference

    assert float(np.mean(relative_error)) < 1.0e-12
    assert float(np.max(relative_error)) < 1.0e-12
    assert float(np.max(quadrature_error)) < 1.0e-10


def test_run_0003_precision_audit_classifies_error_as_model_residual() -> None:
    import json
    import numpy as np

    from physics_lab.engines.precision_audit import audit_gauntlet_run_precision

    metrics_payload = json.loads(
        (
            Path(__file__).resolve().parent.parent
            / "results"
            / "EXP-0001"
            / "RUN-0003"
            / "metrics.json"
        ).read_text(encoding="utf-8")
    )

    audit_payload = audit_gauntlet_run_precision(
        metrics_payload=metrics_payload,
        amplitude_start=0.01,
        amplitude_end=np.pi / 2.0,
        sample_count=200,
        train_fraction=0.7,
        rounded_digits=6,
    )

    assert audit_payload["classification"]["error_source"] == "model_residual"
    assert audit_payload["metrics"]["reference_to_model_mean_error_ratio"] < 1.0e-10
    assert audit_payload["metrics"]["rounding_to_model_mean_error_ratio"] < 0.01
    assert abs(
        audit_payload["metrics"]["model_vs_standard_reference"]["mean_relative_error"]
        - metrics_payload["scores"][0]["test_metrics"]["mean_relative_error"]
    ) < 1.0e-15
