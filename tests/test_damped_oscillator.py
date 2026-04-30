from pathlib import Path
import textwrap
from typing import Optional

from typer.testing import CliRunner

from physics_lab.cli import app
from physics_lab.engines.damped_oscillator import (
    DampedOscillatorParameters,
    classify_damping_regime,
    generate_damped_oscillator_dataset,
)
from physics_lab.registry import load_claim, load_experiment, load_hypothesis, load_knowledge, load_task
from physics_lab.registry.results import load_result
from physics_lab.registry.repository import validate_repository
from physics_lab.workflows.artifacts import hash_file
from physics_lab.workflows.claim_semantics import suggest_claim_status
from physics_lab.workflows.runner import (
    run_damped_oscillator_experiment_with_output,
    run_experiment_with_output,
)


def test_damped_oscillator_regime_classification() -> None:
    underdamped = DampedOscillatorParameters(mass=1.0, damping=0.5, stiffness=4.0, x0=1.0, v0=0.0)
    critical = DampedOscillatorParameters(mass=1.0, damping=4.0, stiffness=4.0, x0=1.0, v0=0.0)
    overdamped = DampedOscillatorParameters(mass=1.0, damping=5.0, stiffness=4.0, x0=1.0, v0=0.0)

    assert classify_damping_regime(underdamped) == "underdamped"
    assert classify_damping_regime(critical) == "critical"
    assert classify_damping_regime(overdamped) == "overdamped"


def test_damped_oscillator_dataset_energy_decays() -> None:
    parameters = DampedOscillatorParameters(
        mass=1.0,
        damping=0.4,
        stiffness=4.0,
        x0=1.0,
        v0=0.0,
    )
    dataset = generate_damped_oscillator_dataset(
        time_start=0.0,
        time_end=10.0,
        sample_count=200,
        parameters=parameters,
    )

    assert dataset.regime == "underdamped"
    assert dataset.energy[0] > dataset.energy[-1]


def test_damped_oscillator_registry_files_validate() -> None:
    load_hypothesis("hypotheses/HYP-0002-damped-oscillator-regimes.yaml")
    load_experiment("experiments/EXP-0002-damped-oscillator-regimes.yaml")
    load_task("tasks/TASK-0002-verify-damped-oscillator-regimes.yaml")
    load_claim("claims/CLAIM-0002-damped-oscillator-regimes.md")
    load_knowledge("knowledge/classical_mechanics/damped_oscillator.md")


def test_damped_oscillator_runner_writes_temp_artifacts(tmp_path) -> None:
    outcome = run_damped_oscillator_experiment_with_output(
        config_path=Path("examples/damped_oscillator.yaml"),
        output_dir=tmp_path / "apl-results",
    )

    result_path = tmp_path / "apl-results" / "EXP-0002" / "RUN-0001" / "result.yaml"
    assert outcome.result_id == "RESULT-0002"
    assert result_path.exists()

    result_payload = load_result(result_path)
    check_names = {check["name"] for check in result_payload["verification"]["checks"]}

    assert result_payload["experiment_id"] == "EXP-0002"
    assert result_payload["best_verdict"] == "VALID_IN_RANGE"
    assert result_payload["verification"]["passed"] is True
    assert {
        "regime_classification",
        "initial_condition_recovery",
        "underdamped_energy_decay",
        "oscillatory_vs_nonoscillatory_behavior",
        "dimensional_consistency",
        "c_to_zero_limit",
        "envelope_decay_rate",
        "critical_damping_boundary",
        "overdamped_asymptotic_behavior",
    } <= check_names
    assert all(check["status"] == "PASS" for check in result_payload["verification"]["checks"])
    knowledge_update_text = (
        tmp_path / "apl-results" / "EXP-0002" / "RUN-0001" / "knowledge_update.md"
    ).read_text(encoding="utf-8")
    assert "## Target Knowledge Note" in knowledge_update_text
    assert "## Suggested Linked Objects Update" in knowledge_update_text


def test_damped_oscillator_dispatch_writes_temp_artifacts(tmp_path) -> None:
    outcome = run_experiment_with_output(
        config_path=Path("examples/damped_oscillator.yaml"),
        output_dir=tmp_path / "apl-results",
    )

    assert outcome.result_id == "RESULT-0002"
    assert outcome.artifacts.result_path == tmp_path / "apl-results" / "EXP-0002" / "RUN-0001" / "result.yaml"


def test_cli_run_damped_oscillator_smoke() -> None:
    runner = CliRunner()
    result = runner.invoke(
        app,
        ["run", "examples/damped_oscillator.yaml", "--output-dir", "/tmp/apl-damped-test"],
    )

    assert result.exit_code == 0
    assert "Completed: Damped Oscillator Regime Verification" in result.stdout
    assert "Result:" in result.stdout


def test_claim_status_suggestion_for_exact_verified_benchmark() -> None:
    suggestion = suggest_claim_status(
        verification_summary={
            "passed": True,
            "checks": [
                {"name": "a", "status": "PASS"},
                {"name": "b", "status": "PASS"},
            ],
        },
        best_verdict="VALID_IN_RANGE",
        range_limited=False,
        exact_verification=True,
    )

    assert suggestion.status == "SUPPORTED"
    assert suggestion.fail_count == 0


def test_claim_status_suggestion_for_range_limited_benchmark() -> None:
    suggestion = suggest_claim_status(
        verification_summary={
            "passed": True,
            "checks": [
                {"name": "a", "status": "PASS"},
                {"name": "b", "status": "PASS"},
            ],
        },
        best_verdict="VALID_IN_RANGE",
        range_limited=True,
        exact_verification=False,
    )

    assert suggestion.status == "PARTIALLY_SUPPORTED"


def _write_minimal_repository_fixture(
    repo_root: Path,
    *,
    claim_scope: str,
    claim_body: str,
    hash_overrides: Optional[dict[str, str]] = None,
) -> None:
    for directory in (
        "agents",
        "claims",
        "experiments",
        "hypotheses",
        "knowledge",
        "results/EXP-0001/RUN-0001",
        "tasks",
        "examples",
    ):
        (repo_root / directory).mkdir(parents=True, exist_ok=True)
    (repo_root / "tests").mkdir(parents=True, exist_ok=True)
    (repo_root / "tests" / "test_damped_oscillator.py").write_text("# temp\n", encoding="utf-8")

    (repo_root / "agents" / "example-agent.yaml").write_text(
        textwrap.dedent(
            """\
            id: agent-example-001
            name: Example Agent
            type: autonomous_agent
            capabilities:
              - formula_discovery
            allowed_tasks:
              - formula_discovery
            constraints:
              - deterministic only
            output_formats:
              - yaml
            """
        ),
        encoding="utf-8",
    )
    (repo_root / "tasks" / "TASK-0001-temp.yaml").write_text(
        textwrap.dedent(
            """\
            id: TASK-0001
            title: Temp Task
            type: formula_discovery
            status: OPEN
            difficulty: medium
            priority: high
            input:
              hypothesis_id: HYP-0001
              experiment_id: EXP-0001
            requirements:
              - deterministic
            accepted_outputs:
              - markdown
            can_be_done_by:
              - human
            """
        ),
        encoding="utf-8",
    )
    (repo_root / "hypotheses" / "HYP-0001-temp.yaml").write_text(
        textwrap.dedent(
            """\
            id: HYP-0001
            title: Temp Hypothesis
            domain: classical_mechanics
            status: TESTING
            hypothesis:
              statement: Temp hypothesis
              formula_candidates:
                - x
            assumptions:
              - deterministic
            variables:
              x:
                unit: "1"
                description: temp
            evidence:
              experiments:
                - EXP-0001
              results:
                - RESULT-0001
            verdict: temp
            """
        ),
        encoding="utf-8",
    )
    (repo_root / "experiments" / "EXP-0001-temp.yaml").write_text(
        textwrap.dedent(
            """\
            id: EXP-0001
            title: Temp Experiment
            domain: classical_mechanics
            status: COMPLETED
            hypothesis_id: HYP-0001
            method:
              type: formula_discovery
              simulator: exact
              fitter: exact
            data:
              amplitude_range_radians:
                start: 0.01
                end: 1.0
              sample_count: 20
            candidate_models:
              - id: model_theta2
                formula: 1 + a*theta^2
            """
        ),
        encoding="utf-8",
    )
    (repo_root / "claims" / "CLAIM-0001-temp.md").write_text(
        textwrap.dedent(
            f"""\
            ---
            id: CLAIM-0001
            title: Temp Claim
            domain: classical_mechanics
            status: SUPPORTED
            hypothesis_id: HYP-0001
            evidence:
              experiments:
                - EXP-0001
              results:
                - RESULT-0001
            scope: {claim_scope}
            ---

            {claim_body}
            """
        ),
        encoding="utf-8",
    )
    (repo_root / "knowledge" / "temp.md").write_text(
        textwrap.dedent(
            """\
            ---
            id: KNOW-0001
            title: Temp
            domain: classical_mechanics
            topic: temp
            linked_objects:
              hypotheses:
                - HYP-0001
              experiments:
                - EXP-0001
              claims:
                - CLAIM-0001
              tasks:
                - TASK-0001
            ---

            Temp knowledge note.
            """
        ),
        encoding="utf-8",
    )
    (repo_root / "examples" / "temp.yaml").write_text(
        textwrap.dedent(
            """\
            experiment_path: ../experiments/EXP-0001-temp.yaml
            hypothesis_path: ../hypotheses/HYP-0001-temp.yaml
            task_id: TASK-0001
            run_id: RUN-0001
            result_id: RESULT-0001
            result_root: ../results/EXP-0001
            train_fraction: 0.7
            """
        ),
        encoding="utf-8",
    )
    (repo_root / "results" / "EXP-0001" / "RUN-0001" / "report.md").write_text("report\n", encoding="utf-8")
    (repo_root / "results" / "EXP-0001" / "RUN-0001" / "metrics.json").write_text("{}", encoding="utf-8")
    (repo_root / "results" / "EXP-0001" / "RUN-0001" / "claim_update.md").write_text("claim\n", encoding="utf-8")
    (repo_root / "results" / "EXP-0001" / "RUN-0001" / "knowledge_update.md").write_text("knowledge\n", encoding="utf-8")

    config_hash = hash_file(repo_root / "examples" / "temp.yaml", repo_root)["sha256"]
    experiment_hash = hash_file(repo_root / "experiments" / "EXP-0001-temp.yaml", repo_root)["sha256"]
    hypothesis_hash = hash_file(repo_root / "hypotheses" / "HYP-0001-temp.yaml", repo_root)["sha256"]
    task_hash = hash_file(repo_root / "tasks" / "TASK-0001-temp.yaml", repo_root)["sha256"]

    overrides = hash_overrides or {}
    (repo_root / "results" / "EXP-0001" / "RUN-0001" / "result.yaml").write_text(
        textwrap.dedent(
            f"""\
            result_id: RESULT-0001
            run_id: RUN-0001
            experiment_id: EXP-0001
            title: Temp Result
            hypothesis_id: HYP-0001
            task_id: TASK-0001
            code_reference: tests/test_damped_oscillator.py
            limitations:
              - temp
            engine_version: 0.1.0
            generated_at: "2026-04-30T00:00:00+00:00"
            git_commit: null
            command: temp
            input_file_hashes:
              config: {{path: examples/temp.yaml, sha256: "{overrides.get('config', config_hash)}"}}
              experiment: {{path: experiments/EXP-0001-temp.yaml, sha256: "{overrides.get('experiment', experiment_hash)}"}}
              hypothesis: {{path: hypotheses/HYP-0001-temp.yaml, sha256: "{overrides.get('hypothesis', hypothesis_hash)}"}}
              task: {{path: tasks/TASK-0001-temp.yaml, sha256: "{overrides.get('task', task_hash)}"}}
            train_range: [0.01, 0.7]
            test_range: [0.71, 1.0]
            best_model_id: model_theta2
            best_verdict: VALID_IN_RANGE
            verification:
              passed: true
              checks:
                - name: small_angle_limit
                  status: PASS
                  details: ok
                  metrics: {{}}
            artifacts:
              report: results/EXP-0001/RUN-0001/report.md
              metrics: results/EXP-0001/RUN-0001/metrics.json
              claim_update: results/EXP-0001/RUN-0001/claim_update.md
              knowledge_update: results/EXP-0001/RUN-0001/knowledge_update.md
            scores:
              - model_id: model_theta2
                formula: 1 + a*theta^2
                coefficients: {{a: 0.0625}}
                complexity_score: 1
                train_metrics: {{mean_relative_error: 0.0, max_relative_error: 0.0}}
                test_metrics: {{mean_relative_error: 0.0, max_relative_error: 0.0}}
                composite_score: 0.001
                verdict: VALID
            """
        ),
        encoding="utf-8",
    )


def test_repository_rejects_supported_claim_without_scope_language(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    _write_minimal_repository_fixture(
        repo_root,
        claim_scope="General statement with no bounded-scope wording.",
        claim_body="Claim body without bounded-scope wording.",
    )

    try:
        validate_repository(repo_root)
    except ValueError as exc:
        assert "range-limited evidence" in str(exc)
    else:
        raise AssertionError("Expected SUPPORTED claim without range language to fail validation")


def test_repository_rejects_result_input_hash_drift(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    _write_minimal_repository_fixture(
        repo_root,
        claim_scope="Valid only within the tested range for this temporary benchmark.",
        claim_body="Claim body with explicit in-scope wording.",
        hash_overrides={"config": "0" * 64},
    )

    try:
        validate_repository(repo_root)
    except ValueError as exc:
        assert "input hash drift" in str(exc)
    else:
        raise AssertionError("Expected result input hash drift to fail validation")
