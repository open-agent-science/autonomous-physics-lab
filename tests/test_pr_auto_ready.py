from __future__ import annotations

from pathlib import Path

import yaml

from physics_lab.registry.pr_auto_ready import (
    AUTO_READY_CHECK_NAME,
    AUTO_READY_LABEL,
    AUTO_READY_WORKFLOW_NAME,
    AutoReadyPrState,
    auto_ready_decision,
    parse_pr_view_payload,
    pr_number_from_event,
    run_auto_ready,
)
from physics_lab.registry.pr_finish_gate import (
    CheckState,
    FinishGateReport,
    classify_ci_gate,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
AUTO_READY_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "auto-ready-when-green.yml"


def test_pr_number_from_event_supports_pull_request_and_workflow_run() -> None:
    assert pr_number_from_event({"pull_request": {"number": 1476}}) == 1476
    assert (
        pr_number_from_event({"workflow_run": {"pull_requests": [{"number": "1477"}]}})
        == 1477
    )
    assert pr_number_from_event({"workflow_run": {"pull_requests": []}}) is None


def test_parse_pr_view_payload_normalizes_labels_and_state() -> None:
    state = parse_pr_view_payload(
        {
            "number": 42,
            "labels": [{"name": AUTO_READY_LABEL}, {"name": "other"}],
            "isDraft": True,
            "state": "open",
            "isCrossRepository": False,
        }
    )

    assert state.number == 42
    assert state.labels == (AUTO_READY_LABEL, "other")
    assert state.is_draft is True
    assert state.state == "OPEN"
    assert state.is_cross_repository is False


def test_auto_ready_decision_requires_label_draft_open_same_repo() -> None:
    eligible = AutoReadyPrState(
        number=42,
        labels=(AUTO_READY_LABEL,),
        is_draft=True,
        state="OPEN",
        is_cross_repository=False,
    )
    assert auto_ready_decision(eligible).eligible

    missing_label = AutoReadyPrState(
        number=42,
        labels=(),
        is_draft=True,
        state="OPEN",
        is_cross_repository=False,
    )
    assert auto_ready_decision(missing_label).reason == (
        f"Missing opt-in label `{AUTO_READY_LABEL}`."
    )

    fork_pr = AutoReadyPrState(
        number=42,
        labels=(AUTO_READY_LABEL,),
        is_draft=True,
        state="OPEN",
        is_cross_repository=True,
    )
    assert auto_ready_decision(fork_pr).reason == "Auto-ready is limited to same-repository PRs."

    already_ready = AutoReadyPrState(
        number=42,
        labels=(AUTO_READY_LABEL,),
        is_draft=False,
        state="OPEN",
        is_cross_repository=False,
    )
    assert auto_ready_decision(already_ready).reason == "PR is already ready for review."


def test_classify_ci_gate_ignores_auto_ready_pending_self_check() -> None:
    primary = CheckState(
        name="Python fast tests (3.12)",
        bucket="pass",
        state="SUCCESS",
        link="",
        workflow="CI",
    )
    auto_ready = CheckState(
        name=AUTO_READY_CHECK_NAME,
        bucket="pending",
        state="IN_PROGRESS",
        link="",
        workflow=AUTO_READY_WORKFLOW_NAME,
    )

    gate = classify_ci_gate(
        (primary, auto_ready),
        ignored_check_names=(AUTO_READY_CHECK_NAME,),
        ignored_workflows=(AUTO_READY_WORKFLOW_NAME,),
    )

    assert gate.status == "pass"
    assert gate.checks == (primary,)


def test_run_auto_ready_invokes_finish_gate_with_self_check_ignored(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, tuple[str, ...]] = {}

    def fake_load_pr_state(root: Path, pr_number: int, *, gh_path: str | None = None):
        del root, gh_path
        return AutoReadyPrState(
            number=pr_number,
            labels=(AUTO_READY_LABEL,),
            is_draft=True,
            state="OPEN",
            is_cross_repository=False,
        )

    def fake_finish_pr(
        root: Path,
        pr_number: int,
        *,
        dry_run: bool = False,
        gh_path: str | None = None,
        ignored_check_names: tuple[str, ...] = (),
        ignored_workflows: tuple[str, ...] = (),
        validation_timeout_seconds: int = 300,
    ) -> FinishGateReport:
        del root, gh_path, validation_timeout_seconds
        captured["ignored_check_names"] = ignored_check_names
        captured["ignored_workflows"] = ignored_workflows
        assert pr_number == 42
        assert dry_run is True
        return FinishGateReport(
            status="ready_dry_run",
            review_verdict="MERGE_OK",
            ci_status="pass",
            ready_transition="dry_run",
            next_safe_command="gh pr ready 42",
            review_output="Verdict: MERGE_OK\n",
            check_failures=(),
            check_pending=(),
        )

    monkeypatch.setattr("physics_lab.registry.pr_auto_ready.load_pr_state", fake_load_pr_state)
    monkeypatch.setattr("physics_lab.registry.pr_auto_ready.finish_pr", fake_finish_pr)

    result = run_auto_ready(
        tmp_path,
        {"pull_request": {"number": 42}},
        dry_run=True,
    )

    assert result.status == "ready_dry_run"
    assert AUTO_READY_CHECK_NAME in captured["ignored_check_names"]
    assert AUTO_READY_WORKFLOW_NAME in captured["ignored_workflows"]


def test_auto_ready_workflow_is_opt_in_and_uses_trusted_finish_gate() -> None:
    workflow_text = AUTO_READY_WORKFLOW.read_text(encoding="utf-8")
    workflow = yaml.safe_load(workflow_text)

    assert workflow["name"] == AUTO_READY_WORKFLOW_NAME
    assert "Keep this value aligned with the top-level `name:` in ci.yml" in workflow_text
    assert workflow["on"]["workflow_run"]["workflows"] == ["CI"]
    assert workflow["on"]["pull_request_target"]["types"] == ["labeled", "reopened"]
    assert workflow["permissions"]["contents"] == "read"
    assert workflow["permissions"]["pull-requests"] == "write"

    job = workflow["jobs"]["auto-ready"]
    job_if = job["if"]
    assert "github.event.workflow_run.pull_requests[0].number != null" in job_if
    assert "github.event.label.name == 'apl:auto-ready-when-green'" in job_if
    assert "github.event.pull_request.draft == true" in job_if
    assert "github.event.pull_request.head.repo.full_name == github.repository" in job_if
    assert "contains(github.event.pull_request.labels.*.name, 'apl:auto-ready-when-green')" in job_if
    assert job["runs-on"] == "ubuntu-latest"

    steps = job["steps"]
    checkout = steps[0]
    finish_gate = steps[-1]
    assert checkout["with"]["ref"] == "${{ github.event.repository.default_branch }}"
    assert finish_gate["env"]["GH_TOKEN"] == "${{ github.token }}"
    assert "scripts/apl_auto_ready_pr.py" in finish_gate["run"]
    assert "--event-path \"$GITHUB_EVENT_PATH\"" in finish_gate["run"]
