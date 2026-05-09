from __future__ import annotations

from pathlib import Path

from physics_lab.registry.agent_run_pr import build_agent_run_pr_context


def test_agent_run_pr_context_includes_required_review_sections() -> None:
    repo_root = Path(__file__).resolve().parent.parent

    context = build_agent_run_pr_context(
        repo_root / "agent_runs" / "AGENT-RUN-0001" / "agent_run.yaml",
        root=repo_root,
    )

    assert "# Agent-Run PR Context - AGENT-RUN-0001" in context
    assert "## Hypothesis Summary" in context
    assert "## Experiment Summary" in context
    assert "## Preflight Result" in context
    assert "## Metrics" in context
    assert "## Limitations" in context
    assert "## Rejected Alternatives / Failure Modes" in context
    assert "## Overclaim Audit" in context
    assert "public claim allowed: `False`" in context
    assert "writes canonical result: `False`" in context
    assert "claim promotion allowed: `False`" in context
    assert "retain it as negative or sandbox-only scientific memory" in context


def test_agent_run_pr_context_preserves_negative_sandbox_evidence() -> None:
    repo_root = Path(__file__).resolve().parent.parent

    context = build_agent_run_pr_context(
        "agent_runs/AGENT-RUN-0002/agent_run.yaml",
        root=repo_root,
    )

    assert "AGENT-RUN-0002" in context
    assert "SANDBOX_FAIL" in context
    assert "Negative-control sandbox evidence only." in context
    assert "theta2-only negative-control candidate failed" in context


def test_agent_run_pr_helper_writes_output_file(tmp_path: Path) -> None:
    from scripts.apl_agent_run_pr_helper import main

    repo_root = Path(__file__).resolve().parent.parent
    output_file = tmp_path / "agent-run-pr-context.md"

    exit_code = main(
        [
            "agent_runs/AGENT-RUN-0001/agent_run.yaml",
            "--root",
            str(repo_root),
            "--output-file",
            str(output_file),
        ]
    )

    assert exit_code == 0
    assert output_file.exists()
    assert "Agent-Run PR Context" in output_file.read_text(encoding="utf-8")


def test_agent_run_pr_helper_stdout_smoke() -> None:
    from scripts.apl_agent_run_pr_helper import build_parser

    parser = build_parser()

    args = parser.parse_args(["agent_runs/AGENT-RUN-0001/agent_run.yaml"])

    assert args.agent_run_path == "agent_runs/AGENT-RUN-0001/agent_run.yaml"
