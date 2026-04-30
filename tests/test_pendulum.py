import json
from pathlib import Path

from typer.testing import CliRunner

from physics_lab.cli import app
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
from physics_lab.workflows.runner import run_pendulum_experiment


def _write_task_file(directory: Path, task_id: str = "TASK-0001") -> Path:
    path = directory / f"{task_id}-temp.yaml"
    path.write_text(
        "\n".join(
            [
                f'id: "{task_id}"',
                'title: "Task"',
                'type: "formula_discovery"',
                'status: "OPEN"',
                'difficulty: "medium"',
                'priority: "high"',
                "input:",
                '  hypothesis_id: "HYP-0001"',
                '  experiment_id: "EXP-0001"',
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
    assert dimensional_check.status == "PASS"
    assert small_angle_window_check.status == "PASS"
    assert small_angle_curvature_check.status == "PASS"
    assert large_angle_window_check.status == "PASS"
    assert separatrix_check.metrics["gate"] is False
    assert asymptotic_check.metrics["gate"] is False


def test_symbolic_dimension_check_is_active_for_pendulum_models() -> None:
    assert symbolic_validation_available() is True
    result = validate_pendulum_model_dimensions("model_x_x2")

    assert result.status == "PASS"
    assert result.metrics["auxiliary_definition_count"] == 1


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
    knowledge_update_path = run_dir / "knowledge_update.md"

    assert outcome.result_id == "RESULT-0001"
    assert outcome.run_id == "RUN-0001"
    assert result_path.exists()
    assert report_path.exists()
    assert metrics_path.exists()
    assert claim_update_path.exists()
    assert knowledge_update_path.exists()

    result_payload = load_result(result_path)
    metrics_payload = json.loads(metrics_path.read_text(encoding="utf-8"))

    assert result_payload["result_id"] == "RESULT-0001"
    assert result_payload["run_id"] == "RUN-0001"
    assert result_payload["experiment_id"] == "EXP-0001"
    assert result_payload["task_id"] == "TASK-0001"
    assert result_payload["best_verdict"] == "VALID_IN_RANGE"
    assert result_payload["code_reference"] == "physics_lab/workflows/runner.py"
    assert result_payload["limitations"]
    assert result_payload["engine_version"]
    assert result_payload["generated_at"]
    assert result_payload["command"]
    assert result_payload["input_file_hashes"]["config"]["sha256"]
    assert result_payload["input_file_hashes"]["task"]["sha256"]
    assert result_payload["verification"]["checks"]
    assert result_payload["artifacts"]["report"].endswith("report.md")
    assert result_payload["git_commit"] is None

    assert metrics_payload["result_id"] == "RESULT-0001"
    assert metrics_payload["run_id"] == "RUN-0001"
    assert metrics_payload["verification"]["checks"]

    assert "Proposed Update for CLAIM-0001" in claim_update_path.read_text(encoding="utf-8")
    assert "Proposed Update for KNOW-0001" in knowledge_update_path.read_text(encoding="utf-8")
    assert "## Verification" in report_path.read_text(encoding="utf-8")


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
    assert outcome.artifacts.knowledge_update_path == repo_root / "results" / "EXP-0001" / "RUN-0001" / "knowledge_update.md"


def test_cli_run_smoke() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["run", "examples/pendulum.yaml"])

    assert result.exit_code == 0
    assert "Completed: Pendulum Formula Discovery" in result.stdout
    assert "Result:" in result.stdout
    assert "Claim update:" in result.stdout
    assert "Knowledge update:" in result.stdout


def test_registry_files_validate_against_schemas() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    load_claim(repo_root / "claims" / "CLAIM-0001-pendulum-period-amplitude.md")
    load_example_config(repo_root / "examples" / "pendulum.yaml")
    load_hypothesis(repo_root / "hypotheses" / "HYP-0001-pendulum-correction.yaml")
    load_experiment(repo_root / "experiments" / "EXP-0001-pendulum-formula-discovery.yaml")
    load_knowledge(repo_root / "knowledge" / "classical_mechanics" / "pendulum.md")
    load_task(repo_root / "tasks" / "TASK-0001-fit-better-pendulum-model.yaml")
    load_agent(repo_root / "agents" / "example-agent.yaml")


def test_cli_validate_hypothesis_smoke() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "hypotheses/HYP-0001-pendulum-correction.yaml"])

    assert result.exit_code == 0
    assert "Validated hypotheses/HYP-0001-pendulum-correction.yaml as hypothesis." in result.stdout


def test_cli_validate_result_smoke() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    run_pendulum_experiment(repo_root / "examples" / "pendulum.yaml")
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "results/EXP-0001/RUN-0001/result.yaml"])

    assert result.exit_code == 0
    assert "Validated results/EXP-0001/RUN-0001/result.yaml as result." in result.stdout


def test_validate_repository_smoke() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    run_pendulum_experiment(repo_root / "examples" / "pendulum.yaml")
    summary = validate_repository(repo_root)

    assert summary.counts["claims"] == 1
    assert summary.counts["examples"] == 1
    assert summary.counts["hypotheses"] == 1
    assert summary.counts["experiments"] == 1
    assert summary.counts["knowledge"] == 1
    assert summary.counts["tasks"] == 1
    assert summary.counts["agents"] == 1
    assert summary.counts["results"] >= 1


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


def test_cli_validate_repo_smoke() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    run_pendulum_experiment(repo_root / "examples" / "pendulum.yaml")
    runner = CliRunner()
    result = runner.invoke(app, ["validate-repo", "."])

    assert result.exit_code == 0
    assert "Validated repository:" in result.stdout
    assert "- examples: 1" in result.stdout
    assert "- hypotheses: 1" in result.stdout
    assert "- knowledge: 1" in result.stdout
