from pathlib import Path

from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.registry import (
    load_claim,
    load_experiment,
    load_hypothesis,
    load_knowledge,
    load_result,
)
from physics_lab.workflows.runner import run_experiment_with_output


def test_run_particle_mass_reproduction_with_output(tmp_path) -> None:
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = tmp_path / "apl-koide"

    outcome = run_experiment_with_output(
        repo_root / "examples" / "koide_charged_lepton.yaml",
        output_dir=output_dir,
    )

    run_dir = output_dir / "EXP-0004" / "RUN-0004"
    result_path = run_dir / "result.yaml"
    result_payload = load_result(result_path)

    assert outcome.result_id == "RESULT-0005"
    assert outcome.run_id == "RUN-0004"
    assert outcome.best_model_id is None
    assert outcome.artifacts.result_path == result_path
    assert outcome.artifacts.metrics_path == run_dir / "metrics.json"
    assert (run_dir / "inputs" / "dataset.yaml").exists()
    assert result_payload["comparison_summary"][0]["target_id"] == "target_koide_q"
    assert result_payload["best_verdict"] == "VALID"
    assert result_payload["uncertainty_summary"]["within_combined_uncertainty"] is True

    report_text = (run_dir / "report.md").read_text(encoding="utf-8")
    assert "Charged-Lepton Koide Reproduction" in report_text
    assert "reproduction benchmark, not an explanation claim" in report_text


def test_cli_run_koide_reproduction_smoke(tmp_path) -> None:
    runner = CliRunner()
    output_dir = tmp_path / "apl-koide-cli"

    result = runner.invoke(
        app,
        ["run", "examples/koide_charged_lepton.yaml", "--output-dir", str(output_dir)],
    )

    assert result.exit_code == 0, result.output
    assert "Completed: Charged-Lepton Koide Reproduction" in result.stdout
    assert "Primary comparison: Koide Q target" in result.stdout
    assert "Observed Q:" in result.stdout
    assert "Relative difference vs 2/3:" in result.stdout
    assert "Best model:" not in result.stdout


def test_repository_loads_koide_registry_memory() -> None:
    repo_root = Path(__file__).resolve().parent.parent

    load_claim(repo_root / "claims" / "CLAIM-0003-koide-charged-lepton-reproduction.md")
    load_experiment(repo_root / "experiments" / "EXP-0004-koide-charged-lepton-reproduction.yaml")
    load_hypothesis(repo_root / "hypotheses" / "HYP-0004-koide-charged-lepton-reproduction.yaml")
    load_knowledge(repo_root / "knowledge" / "particle_physics" / "koide_relation.md")
