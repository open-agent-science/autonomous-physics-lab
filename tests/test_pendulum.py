import json
from pathlib import Path

from typer.testing import CliRunner

from physics_lab.cli import app
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
    repo_root = Path(__file__).resolve().parent.parent
    report_path = tmp_path / "report.md"
    metrics_path = tmp_path / "metrics.json"
    config_path = tmp_path / "pendulum.yaml"
    config_path.write_text(
        "\n".join(
            [
                f"experiment_path: {repo_root / 'experiments' / 'EXP-0001-pendulum-formula-discovery.yaml'}",
                f"hypothesis_path: {repo_root / 'hypotheses' / 'HYP-0001-pendulum-correction.yaml'}",
                f"report_path: {report_path}",
                f"metrics_path: {metrics_path}",
                "train_fraction: 0.7",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    outcome = run_pendulum_experiment(config_path)

    assert outcome.best_model_id
    assert report_path.exists()
    assert metrics_path.exists()
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    assert payload["experiment_id"] == "EXP-0001"
    assert payload["scores"]


def test_cli_run_smoke() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["run", "examples/pendulum.yaml"])

    assert result.exit_code == 0
    assert "Completed: Pendulum Formula Discovery" in result.stdout
