import json
from pathlib import Path

from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.registry import load_agent, load_claim, load_experiment, load_hypothesis, load_result, load_task
from physics_lab.registry.repository import validate_repository
from physics_lab.engines.critic import classify_model_score
from physics_lab.engines.formula_discovery import fit_all_models
from physics_lab.engines.scoring import ModelScore, compute_error_metrics
from physics_lab.engines.simulation import exact_pendulum_period_ratio, generate_pendulum_dataset
from physics_lab.workflows.runner import run_pendulum_experiment


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
    assert (
        scores["model_x_x2"].mean_relative_error
        < scores["model_theta2"].mean_relative_error
    )


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


def test_runner_generates_report_and_metrics(tmp_path) -> None:
    experiment_path = tmp_path / "EXP-0001-pendulum-formula-discovery.yaml"
    hypothesis_path = tmp_path / "HYP-0001-pendulum-correction.yaml"
    result_dir = tmp_path / "results"
    report_path = tmp_path / "report.md"
    config_path = tmp_path / "pendulum.yaml"
    experiment_path.write_text(
        "\n".join(
            [
                'id: "EXP-0001"',
                'title: "Pendulum Formula Discovery"',
                'domain: "classical_mechanics"',
                'status: "PLANNED"',
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
                'outputs:',
                f'  report_path: "{report_path}"',
                f'  result_dir: "{result_dir}"',
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
                'status: "FORMALIZED"',
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
                'verdict: "Pending numerical validation."',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    config_path.write_text(
        "\n".join(
            [
                f"experiment_path: {experiment_path}",
                f"hypothesis_path: {hypothesis_path}",
                "train_fraction: 0.7",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    outcome = run_pendulum_experiment(config_path)

    assert outcome.best_model_id
    assert report_path.exists()
    metrics_path = result_dir / "metrics.json"
    assert metrics_path.exists()
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert payload["experiment_id"] == "EXP-0001"
    assert payload["scores"]
    load_result(metrics_path)


def test_runner_resolves_experiment_outputs_from_repo_root(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    examples_dir = repo_root / "examples"
    experiments_dir = repo_root / "experiments"
    hypotheses_dir = repo_root / "hypotheses"
    examples_dir.mkdir(parents=True)
    experiments_dir.mkdir()
    hypotheses_dir.mkdir()
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
                'status: "PLANNED"',
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
                'outputs:',
                '  report_path: "examples/reports/pendulum_formula_discovery.md"',
                '  result_dir: "results/EXP-0001"',
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
                'status: "FORMALIZED"',
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
                'verdict: "Pending numerical validation."',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    config_path.write_text(
        "\n".join(
            [
                f"experiment_path: {experiment_path}",
                f"hypothesis_path: {hypothesis_path}",
                "train_fraction: 0.7",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    outcome = run_pendulum_experiment(config_path)

    assert outcome.artifacts.report_path == repo_root / "examples" / "reports" / "pendulum_formula_discovery.md"
    assert outcome.artifacts.metrics_path == repo_root / "results" / "EXP-0001" / "metrics.json"
    assert outcome.artifacts.report_path.exists()
    assert outcome.artifacts.metrics_path.exists()


def test_cli_run_smoke() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["run", "examples/pendulum.yaml"])

    assert result.exit_code == 0
    assert "Completed: Pendulum Formula Discovery" in result.stdout


def test_registry_files_validate_against_schemas() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    load_claim(repo_root / "claims" / "CLAIM-0001-pendulum-period-amplitude.md")
    load_hypothesis(repo_root / "hypotheses" / "HYP-0001-pendulum-correction.yaml")
    load_experiment(repo_root / "experiments" / "EXP-0001-pendulum-formula-discovery.yaml")
    load_task(repo_root / "tasks" / "TASK-0001-fit-better-pendulum-model.yaml")
    load_agent(repo_root / "agents" / "example-agent.yaml")


def test_cli_validate_hypothesis_smoke() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["validate", "hypotheses/HYP-0001-pendulum-correction.yaml"])

    assert result.exit_code == 0
    assert "Validated hypotheses/HYP-0001-pendulum-correction.yaml as hypothesis." in result.stdout


def test_validate_repository_smoke() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    summary = validate_repository(repo_root)

    assert summary.counts["claims"] == 1
    assert summary.counts["hypotheses"] == 1
    assert summary.counts["experiments"] == 1
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
    runner = CliRunner()
    result = runner.invoke(app, ["validate-repo", "."])

    assert result.exit_code == 0
    assert "Validated repository:" in result.stdout
    assert "- hypotheses: 1" in result.stdout
