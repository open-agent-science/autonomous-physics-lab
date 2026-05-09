from pathlib import Path
import shutil
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
    claim_patch_text = (
        tmp_path / "apl-results" / "EXP-0002" / "RUN-0001" / "claim_update.patch.md"
    ).read_text(encoding="utf-8")
    assert "## Target Knowledge Note" in knowledge_update_text
    assert "## Suggested Linked Objects Update" in knowledge_update_text
    assert "## Proposed Diff" in claim_patch_text
    assert (tmp_path / "apl-results" / "EXP-0002" / "RUN-0001" / "review_summary.md").exists()
    assert (tmp_path / "apl-results" / "EXP-0002" / "RUN-0001" / "review_metadata.yaml").exists()
    assert result_payload["artifacts"]["review_metadata"].endswith("review_metadata.yaml")


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
    assert "Claim patch:" in result.stdout
    assert "Review summary:" in result.stdout
    assert "Review metadata:" in result.stdout


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
    strict_snapshots: bool = False,
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
    (repo_root / "results" / "EXP-0001" / "RUN-0001" / "claim_update.patch.md").write_text("claim patch\n", encoding="utf-8")
    (repo_root / "results" / "EXP-0001" / "RUN-0001" / "knowledge_update.md").write_text("knowledge\n", encoding="utf-8")
    (repo_root / "results" / "EXP-0001" / "RUN-0001" / "knowledge_update.patch.md").write_text("knowledge patch\n", encoding="utf-8")
    (repo_root / "results" / "EXP-0001" / "RUN-0001" / "review_summary.md").write_text("summary\n", encoding="utf-8")
    (repo_root / "results" / "EXP-0001" / "RUN-0001" / "review_metadata.yaml").write_text(
        textwrap.dedent("""\
            schema_version: '1'
            artifact_type: review_metadata
            result_id: RESULT-0001
            run_id: RUN-0001
            experiment_id: EXP-0001
            claim_id: CLAIM-0001
            knowledge_id: KNOW-0001
            generated_at: '2026-04-30T00:00:00+00:00'
            proposed_claim_status: PARTIALLY_SUPPORTED
            required_human_review: true
            evidence_basis:
            - RESULT-0001
            claim_target_file: claims/CLAIM-0001-pendulum-period-amplitude.md
            knowledge_target_file: knowledge/classical_mechanics/pendulum.md
            patch_artifacts:
              claim_patch: results/EXP-0001/RUN-0001/claim_update.patch.md
              knowledge_patch: results/EXP-0001/RUN-0001/knowledge_update.patch.md
              review_summary: results/EXP-0001/RUN-0001/review_summary.md
            """),
        encoding="utf-8",
    )

    config_input = repo_root / "examples" / "temp.yaml"
    experiment_input = repo_root / "experiments" / "EXP-0001-temp.yaml"
    hypothesis_input = repo_root / "hypotheses" / "HYP-0001-temp.yaml"
    task_input = repo_root / "tasks" / "TASK-0001-temp.yaml"
    if strict_snapshots:
        inputs_dir = repo_root / "results" / "EXP-0001" / "RUN-0001" / "inputs"
        inputs_dir.mkdir(parents=True, exist_ok=True)
        config_input = inputs_dir / "config.yaml"
        experiment_input = inputs_dir / "experiment.yaml"
        hypothesis_input = inputs_dir / "hypothesis.yaml"
        task_input = inputs_dir / "task.yaml"
        config_input.write_text((repo_root / "examples" / "temp.yaml").read_text(encoding="utf-8"), encoding="utf-8")
        experiment_input.write_text((repo_root / "experiments" / "EXP-0001-temp.yaml").read_text(encoding="utf-8"), encoding="utf-8")
        hypothesis_input.write_text((repo_root / "hypotheses" / "HYP-0001-temp.yaml").read_text(encoding="utf-8"), encoding="utf-8")
        task_input.write_text((repo_root / "tasks" / "TASK-0001-temp.yaml").read_text(encoding="utf-8"), encoding="utf-8")

    config_hash = hash_file(config_input, repo_root)["sha256"]
    experiment_hash = hash_file(experiment_input, repo_root)["sha256"]
    hypothesis_hash = hash_file(hypothesis_input, repo_root)["sha256"]
    task_hash = hash_file(task_input, repo_root)["sha256"]
    config_input_path = config_input.relative_to(repo_root).as_posix()
    experiment_input_path = experiment_input.relative_to(repo_root).as_posix()
    hypothesis_input_path = hypothesis_input.relative_to(repo_root).as_posix()
    task_input_path = task_input.relative_to(repo_root).as_posix()

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
              config: {{path: {config_input_path}, sha256: "{overrides.get('config', config_hash)}"}}
              experiment: {{path: {experiment_input_path}, sha256: "{overrides.get('experiment', experiment_hash)}"}}
              hypothesis: {{path: {hypothesis_input_path}, sha256: "{overrides.get('hypothesis', hypothesis_hash)}"}}
              task: {{path: {task_input_path}, sha256: "{overrides.get('task', task_hash)}"}}
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
              claim_update_patch: results/EXP-0001/RUN-0001/claim_update.patch.md
              knowledge_update: results/EXP-0001/RUN-0001/knowledge_update.md
              knowledge_update_patch: results/EXP-0001/RUN-0001/knowledge_update.patch.md
              review_summary: results/EXP-0001/RUN-0001/review_summary.md
              review_metadata: results/EXP-0001/RUN-0001/review_metadata.yaml
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


def test_validate_repository_rejects_duplicate_canonical_result_ids(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    _write_minimal_repository_fixture(
        repo_root,
        claim_scope="Valid only within the tested range for this temporary benchmark.",
        claim_body="Claim body with explicit in-scope wording.",
    )

    duplicate_run_dir = repo_root / "results" / "EXP-0001" / "RUN-0002"
    shutil.copytree(repo_root / "results" / "EXP-0001" / "RUN-0001", duplicate_run_dir)

    try:
        validate_repository(repo_root)
    except ValueError as exc:
        assert "Duplicate canonical result id RESULT-0001" in str(exc)
    else:
        raise AssertionError("Expected duplicate result id validation to fail")


def test_repository_accepts_crlf_text_snapshot_with_same_content(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    _write_minimal_repository_fixture(
        repo_root,
        claim_scope="Valid only within the tested range for this temporary benchmark.",
        claim_body="Claim body with explicit in-scope wording.",
        strict_snapshots=True,
    )

    config_path = repo_root / "results" / "EXP-0001" / "RUN-0001" / "inputs" / "config.yaml"
    config_text = config_path.read_text(encoding="utf-8")
    with config_path.open("w", encoding="utf-8", newline="\r\n") as handle:
        handle.write(config_text)

    summary = validate_repository(repo_root)

    assert summary.root == repo_root.resolve()


def test_hash_file_preserves_binary_line_ending_bytes(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    first = repo_root / "blob_a.bin"
    second = repo_root / "blob_b.bin"
    first.write_bytes(b"a\r\nb\r\n")
    second.write_bytes(b"a\nb\n")

    first_hash = hash_file(first, repo_root)["sha256"]
    second_hash = hash_file(second, repo_root)["sha256"]

    assert first_hash != second_hash


def test_validate_repository_strict_smoke() -> None:
    repo_root = Path(__file__).resolve().parent.parent

    summary = validate_repository(repo_root, strict=True)

    assert summary.strict is True
    assert summary.error_count == 0
    assert summary.warning_count == 0
    assert summary.info_count >= 1


def test_cli_validate_repo_strict_fail_on_warnings(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    _write_minimal_repository_fixture(
        repo_root,
        claim_scope="Valid only within the tested range for this temporary benchmark.",
        claim_body="Claim body with explicit in-scope wording.",
        strict_snapshots=True,
    )
    orphan_run_dir = repo_root / "results" / "EXP-0001" / "RUN-9999"
    orphan_run_dir.mkdir(parents=True, exist_ok=True)
    (orphan_run_dir / "report.md").write_text("report\n", encoding="utf-8")
    (orphan_run_dir / "metrics.json").write_text("{}", encoding="utf-8")
    (orphan_run_dir / "claim_update.md").write_text("claim\n", encoding="utf-8")
    (orphan_run_dir / "claim_update.patch.md").write_text("claim patch\n", encoding="utf-8")
    (orphan_run_dir / "knowledge_update.md").write_text("knowledge\n", encoding="utf-8")
    (orphan_run_dir / "knowledge_update.patch.md").write_text("knowledge patch\n", encoding="utf-8")
    (orphan_run_dir / "review_summary.md").write_text("summary\n", encoding="utf-8")
    (orphan_run_dir / "review_metadata.yaml").write_text(
        textwrap.dedent("""\
            schema_version: '1'
            artifact_type: review_metadata
            result_id: RESULT-9999
            run_id: RUN-9999
            experiment_id: EXP-0001
            claim_id: CLAIM-0001
            knowledge_id: KNOW-0001
            generated_at: '2026-04-30T00:00:01+00:00'
            proposed_claim_status: PARTIALLY_SUPPORTED
            required_human_review: true
            evidence_basis:
            - RESULT-9999
            claim_target_file: claims/CLAIM-0001-pendulum-period-amplitude.md
            knowledge_target_file: knowledge/classical_mechanics/pendulum.md
            patch_artifacts:
              claim_patch: results/EXP-0001/RUN-9999/claim_update.patch.md
              knowledge_patch: results/EXP-0001/RUN-9999/knowledge_update.patch.md
              review_summary: results/EXP-0001/RUN-9999/review_summary.md
            """),
        encoding="utf-8",
    )
    inputs_dir = orphan_run_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    for name in ("config.yaml", "experiment.yaml", "hypothesis.yaml", "task.yaml"):
        (inputs_dir / name).write_text(
            (repo_root / "results" / "EXP-0001" / "RUN-0001" / "inputs" / name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    config_hash = hash_file(inputs_dir / "config.yaml", repo_root)["sha256"]
    experiment_hash = hash_file(inputs_dir / "experiment.yaml", repo_root)["sha256"]
    hypothesis_hash = hash_file(inputs_dir / "hypothesis.yaml", repo_root)["sha256"]
    task_hash = hash_file(inputs_dir / "task.yaml", repo_root)["sha256"]
    (orphan_run_dir / "result.yaml").write_text(
        textwrap.dedent(
            f"""\
            result_id: RESULT-9999
            run_id: RUN-9999
            experiment_id: EXP-0001
            title: Orphan Result
            hypothesis_id: HYP-0001
            task_id: TASK-0001
            code_reference: tests/test_damped_oscillator.py
            limitations:
              - temp
            engine_version: 0.1.0
            generated_at: "2026-04-30T00:00:01+00:00"
            git_commit: null
            command: temp
            input_file_hashes:
              config: {{path: results/EXP-0001/RUN-9999/inputs/config.yaml, sha256: "{config_hash}"}}
              experiment: {{path: results/EXP-0001/RUN-9999/inputs/experiment.yaml, sha256: "{experiment_hash}"}}
              hypothesis: {{path: results/EXP-0001/RUN-9999/inputs/hypothesis.yaml, sha256: "{hypothesis_hash}"}}
              task: {{path: results/EXP-0001/RUN-9999/inputs/task.yaml, sha256: "{task_hash}"}}
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
              report: results/EXP-0001/RUN-9999/report.md
              metrics: results/EXP-0001/RUN-9999/metrics.json
              claim_update: results/EXP-0001/RUN-9999/claim_update.md
              claim_update_patch: results/EXP-0001/RUN-9999/claim_update.patch.md
              knowledge_update: results/EXP-0001/RUN-9999/knowledge_update.md
              knowledge_update_patch: results/EXP-0001/RUN-9999/knowledge_update.patch.md
              review_summary: results/EXP-0001/RUN-9999/review_summary.md
              review_metadata: results/EXP-0001/RUN-9999/review_metadata.yaml
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

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["validate-repo", str(repo_root), "--strict", "--fail-on-warnings"],
    )

    assert result.exit_code == 1
    assert "orphan_result" in result.stdout


def test_repository_strict_detects_noncanonical_input_snapshots(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    _write_minimal_repository_fixture(
        repo_root,
        claim_scope="Valid only within the tested range for this temporary benchmark.",
        claim_body="Claim body with explicit in-scope wording.",
    )

    summary = validate_repository(repo_root, strict=True)

    assert summary.error_count > 0
    assert any(issue.code == "noncanonical_input_snapshot" for issue in summary.issues)


def test_repository_strict_detects_orphan_result(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    _write_minimal_repository_fixture(
        repo_root,
        claim_scope="Valid only within the tested range for this temporary benchmark.",
        claim_body="Claim body with explicit in-scope wording.",
        strict_snapshots=True,
    )
    orphan_run_dir = repo_root / "results" / "EXP-0001" / "RUN-9999"
    orphan_run_dir.mkdir(parents=True, exist_ok=True)
    (orphan_run_dir / "report.md").write_text("report\n", encoding="utf-8")
    (orphan_run_dir / "metrics.json").write_text("{}", encoding="utf-8")
    (orphan_run_dir / "claim_update.md").write_text("claim\n", encoding="utf-8")
    (orphan_run_dir / "claim_update.patch.md").write_text("claim patch\n", encoding="utf-8")
    (orphan_run_dir / "knowledge_update.md").write_text("knowledge\n", encoding="utf-8")
    (orphan_run_dir / "knowledge_update.patch.md").write_text("knowledge patch\n", encoding="utf-8")
    (orphan_run_dir / "review_summary.md").write_text("summary\n", encoding="utf-8")
    (orphan_run_dir / "review_metadata.yaml").write_text(
        textwrap.dedent("""\
            schema_version: '1'
            artifact_type: review_metadata
            result_id: RESULT-9999
            run_id: RUN-9999
            experiment_id: EXP-0001
            claim_id: CLAIM-0001
            knowledge_id: KNOW-0001
            generated_at: '2026-04-30T00:00:01+00:00'
            proposed_claim_status: PARTIALLY_SUPPORTED
            required_human_review: true
            evidence_basis:
            - RESULT-9999
            claim_target_file: claims/CLAIM-0001-pendulum-period-amplitude.md
            knowledge_target_file: knowledge/classical_mechanics/pendulum.md
            patch_artifacts:
              claim_patch: results/EXP-0001/RUN-9999/claim_update.patch.md
              knowledge_patch: results/EXP-0001/RUN-9999/knowledge_update.patch.md
              review_summary: results/EXP-0001/RUN-9999/review_summary.md
            """),
        encoding="utf-8",
    )
    inputs_dir = orphan_run_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    for name in ("config.yaml", "experiment.yaml", "hypothesis.yaml", "task.yaml"):
        (inputs_dir / name).write_text(
            (repo_root / "results" / "EXP-0001" / "RUN-0001" / "inputs" / name).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    config_hash = hash_file(inputs_dir / "config.yaml", repo_root)["sha256"]
    experiment_hash = hash_file(inputs_dir / "experiment.yaml", repo_root)["sha256"]
    hypothesis_hash = hash_file(inputs_dir / "hypothesis.yaml", repo_root)["sha256"]
    task_hash = hash_file(inputs_dir / "task.yaml", repo_root)["sha256"]
    (orphan_run_dir / "result.yaml").write_text(
        textwrap.dedent(
            f"""\
            result_id: RESULT-9999
            run_id: RUN-9999
            experiment_id: EXP-0001
            title: Orphan Result
            hypothesis_id: HYP-0001
            task_id: TASK-0001
            code_reference: tests/test_damped_oscillator.py
            limitations:
              - temp
            engine_version: 0.1.0
            generated_at: "2026-04-30T00:00:01+00:00"
            git_commit: null
            command: temp
            input_file_hashes:
              config: {{path: results/EXP-0001/RUN-9999/inputs/config.yaml, sha256: "{config_hash}"}}
              experiment: {{path: results/EXP-0001/RUN-9999/inputs/experiment.yaml, sha256: "{experiment_hash}"}}
              hypothesis: {{path: results/EXP-0001/RUN-9999/inputs/hypothesis.yaml, sha256: "{hypothesis_hash}"}}
              task: {{path: results/EXP-0001/RUN-9999/inputs/task.yaml, sha256: "{task_hash}"}}
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
              report: results/EXP-0001/RUN-9999/report.md
              metrics: results/EXP-0001/RUN-9999/metrics.json
              claim_update: results/EXP-0001/RUN-9999/claim_update.md
              claim_update_patch: results/EXP-0001/RUN-9999/claim_update.patch.md
              knowledge_update: results/EXP-0001/RUN-9999/knowledge_update.md
              knowledge_update_patch: results/EXP-0001/RUN-9999/knowledge_update.patch.md
              review_summary: results/EXP-0001/RUN-9999/review_summary.md
              review_metadata: results/EXP-0001/RUN-9999/review_metadata.yaml
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

    summary = validate_repository(repo_root, strict=True)

    assert summary.warning_count > 0
    assert any(issue.code == "orphan_result" for issue in summary.issues)


def test_repository_strict_allows_done_non_result_visualization_and_workflow_tasks(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    _write_minimal_repository_fixture(
        repo_root,
        claim_scope="Valid only within the tested range for this temporary benchmark.",
        claim_body="Claim body with explicit in-scope wording.",
        strict_snapshots=True,
    )
    (repo_root / "tasks" / "TASK-1001-temp.yaml").write_text(
        textwrap.dedent(
            """\
            id: TASK-1001
            title: Temp visualization task
            type: scientific_visualization
            status: DONE
            difficulty: low
            priority: medium
            input:
              mode: planning_only
              related_domain: classical_mechanics
              related_objects: []
              planning_context: Visual summary package
            requirements:
              - static figures
            accepted_outputs:
              - docs/figures/example.png
            can_be_done_by:
              - human
            """
        ),
        encoding="utf-8",
    )
    (repo_root / "tasks" / "TASK-1002-temp.yaml").write_text(
        textwrap.dedent(
            """\
            id: TASK-1002
            title: Temp workflow pilot task
            type: workflow_pilot
            status: DONE
            difficulty: medium
            priority: medium
            input:
              mode: workflow
              related_objects: []
              planning_context: Pilot hypothesis review flow
            requirements:
              - workflow check
            accepted_outputs:
              - docs/reviews/example.md
            can_be_done_by:
              - human
            """
        ),
        encoding="utf-8",
    )
    (repo_root / "tasks" / "TASK-1003-temp.yaml").write_text(
        textwrap.dedent(
            """\
            id: TASK-1003
            title: Temp scientific audit task
            type: scientific_audit
            status: DONE
            difficulty: medium
            priority: medium
            input:
              mode: workflow
              related_objects: []
              planning_context: Audit a canonical replay path
            requirements:
              - diagnose replay drift
            accepted_outputs:
              - docs/notes/audit-example.md
            can_be_done_by:
              - human
            """
        ),
        encoding="utf-8",
    )
    (repo_root / "tasks" / "TASK-1004-temp.yaml").write_text(
        textwrap.dedent(
            """\
            id: TASK-1004
            title: Temp reproducibility task
            type: reproducibility
            status: DONE
            difficulty: medium
            priority: medium
            input:
              mode: workflow
              related_objects: []
              planning_context: Document replay instructions
            requirements:
              - add reproducibility capsule
            accepted_outputs:
              - docs/reproducibility-example.md
            can_be_done_by:
              - human
            """
        ),
        encoding="utf-8",
    )
    (repo_root / "tasks" / "TASK-1005-temp.yaml").write_text(
        textwrap.dedent(
            """\
            id: TASK-1005
            title: Temp validation task
            type: validation
            status: DONE
            difficulty: medium
            priority: medium
            input:
              mode: workflow
              related_objects: []
              planning_context: Harden repository preflight validation
            requirements:
              - add deterministic proposal validation
            accepted_outputs:
              - physics_lab/registry/validation_example.py
            can_be_done_by:
              - human
            """
        ),
        encoding="utf-8",
    )
    (repo_root / "tasks" / "TASK-1006-temp.yaml").write_text(
        textwrap.dedent(
            """\
            id: TASK-1006
            title: Temp autonomous pilot task
            type: autonomous_research_pilot
            status: DONE
            difficulty: high
            priority: high
            input:
              mode: workflow
              related_objects: []
              planning_context: Preserve sandbox-only pilot evidence
            requirements:
              - create one reviewable sandbox run
            accepted_outputs:
              - agent_runs/AGENT-RUN-TEMP/agent_run.yaml
            can_be_done_by:
              - human
            """
        ),
        encoding="utf-8",
    )
    (repo_root / "tasks" / "TASK-1007-temp.yaml").write_text(
        textwrap.dedent(
            """\
            id: TASK-1007
            title: Temp review workflow task
            type: review_workflow
            status: DONE
            difficulty: medium
            priority: medium
            input:
              mode: workflow
              related_objects: []
              planning_context: Package sandbox evidence for maintainer review
            requirements:
              - add review helper output
            accepted_outputs:
              - docs/review-checklists/temp-review-workflow.md
            can_be_done_by:
              - human
            """
        ),
        encoding="utf-8",
    )
    (repo_root / "tasks" / "TASK-1008-temp.yaml").write_text(
        textwrap.dedent(
            """\
            id: TASK-1008
            title: Temp scientific governance task
            type: scientific_governance
            status: DONE
            difficulty: medium
            priority: medium
            input:
              mode: workflow
              related_objects: []
              planning_context: Score current flagship results against a shared rubric
            requirements:
              - define governance rubric
            accepted_outputs:
              - docs/result-quality-rubric.md
            can_be_done_by:
              - human
            """
        ),
        encoding="utf-8",
    )
    (repo_root / "tasks" / "TASK-1009-temp.yaml").write_text(
        textwrap.dedent(
            """\
            id: TASK-1009
            title: Temp benchmark protocol task
            type: benchmark_protocol
            status: DONE
            difficulty: medium
            priority: medium
            input:
              mode: workflow
              related_objects: []
              planning_context: Freeze train and holdout reveal rules for future benchmarks
            requirements:
              - define holdout protocol
            accepted_outputs:
              - docs/blind-holdout-benchmark-protocol.md
            can_be_done_by:
              - human
            """
        ),
        encoding="utf-8",
    )

    summary = validate_repository(repo_root, strict=True)

    assert not any(
        issue.code == "done_task_without_result" and issue.path is not None and issue.path.endswith("TASK-1001-temp.yaml")
        for issue in summary.issues
    )
    assert not any(
        issue.code == "done_task_without_result" and issue.path is not None and issue.path.endswith("TASK-1002-temp.yaml")
        for issue in summary.issues
    )
    assert not any(
        issue.code == "done_task_without_result" and issue.path is not None and issue.path.endswith("TASK-1003-temp.yaml")
        for issue in summary.issues
    )
    assert not any(
        issue.code == "done_task_without_result" and issue.path is not None and issue.path.endswith("TASK-1004-temp.yaml")
        for issue in summary.issues
    )
    assert not any(
        issue.code == "done_task_without_result" and issue.path is not None and issue.path.endswith("TASK-1005-temp.yaml")
        for issue in summary.issues
    )
    assert not any(
        issue.code == "done_task_without_result" and issue.path is not None and issue.path.endswith("TASK-1006-temp.yaml")
        for issue in summary.issues
    )
    assert not any(
        issue.code == "done_task_without_result" and issue.path is not None and issue.path.endswith("TASK-1007-temp.yaml")
        for issue in summary.issues
    )
    assert not any(
        issue.code == "done_task_without_result" and issue.path is not None and issue.path.endswith("TASK-1008-temp.yaml")
        for issue in summary.issues
    )
    assert not any(
        issue.code == "done_task_without_result" and issue.path is not None and issue.path.endswith("TASK-1009-temp.yaml")
        for issue in summary.issues
    )


def test_repository_strict_rejects_malformed_review_metadata(tmp_path) -> None:
    """Strict validation must raise invalid_review_metadata for a structurally invalid file."""
    repo_root = tmp_path / "repo"
    _write_minimal_repository_fixture(
        repo_root,
        claim_scope="Valid only within the tested range for this temporary benchmark.",
        claim_body="Claim body with explicit in-scope wording.",
        strict_snapshots=True,
    )
    # Overwrite the valid review_metadata.yaml with a structurally incomplete one
    # (missing required fields: artifact_type, result_id, claim_id, …)
    (repo_root / "results" / "EXP-0001" / "RUN-0001" / "review_metadata.yaml").write_text(
        "schema_version: '1'\n",
        encoding="utf-8",
    )

    summary = validate_repository(repo_root, strict=True)

    assert summary.error_count > 0
    assert any(issue.code == "invalid_review_metadata" for issue in summary.issues)
