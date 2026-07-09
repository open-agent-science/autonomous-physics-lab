"""Opt-in auto-ready policy for draft pull requests."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from physics_lab.registry.pr_capability import find_gh_path
from physics_lab.registry.pr_finish_gate import FinishGateReport, finish_pr
from physics_lab.registry.review_git import run_command


AUTO_READY_LABEL = "apl:auto-ready-when-green"
AUTO_READY_WORKFLOW_NAME = "Auto Ready When Green"
AUTO_READY_CHECK_NAME = "Auto-ready finish gate"
AUTO_READY_IGNORED_CHECK_NAMES = (
    AUTO_READY_CHECK_NAME,
    AUTO_READY_WORKFLOW_NAME,
    f"{AUTO_READY_WORKFLOW_NAME} / {AUTO_READY_CHECK_NAME}",
)
AUTO_READY_IGNORED_WORKFLOWS = (AUTO_READY_WORKFLOW_NAME,)
PR_VIEW_FIELDS = "number,isDraft,state,labels,isCrossRepository"


@dataclass(frozen=True)
class AutoReadyPrState:
    """Normalized PR state needed before running the finish gate."""

    number: int
    labels: tuple[str, ...]
    is_draft: bool
    state: str
    is_cross_repository: bool


@dataclass(frozen=True)
class AutoReadyDecision:
    """Decision for whether the auto-ready finish gate may run."""

    status: str
    reason: str

    @property
    def eligible(self) -> bool:
        return self.status == "eligible"


@dataclass(frozen=True)
class AutoReadyRunResult:
    """Rendered outcome for one auto-ready event."""

    status: str
    reason: str
    pr_number: int | None
    finish_report: FinishGateReport | None = None

    @property
    def ok(self) -> bool:
        """Return whether the workflow itself should pass."""
        return self.status != "error"


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def pr_number_from_event(payload: dict[str, Any]) -> int | None:
    """Extract a pull request number from supported GitHub event payloads."""
    pull_request = payload.get("pull_request")
    if isinstance(pull_request, dict):
        number = _int_or_none(pull_request.get("number"))
        if number is not None:
            return number

    workflow_run = payload.get("workflow_run")
    if isinstance(workflow_run, dict):
        pull_requests = workflow_run.get("pull_requests") or []
        if isinstance(pull_requests, list):
            for row in pull_requests:
                if not isinstance(row, dict):
                    continue
                number = _int_or_none(row.get("number"))
                if number is not None:
                    return number
    return None


def _label_names(labels: Any) -> tuple[str, ...]:
    if not isinstance(labels, list):
        return ()
    names: list[str] = []
    for item in labels:
        if isinstance(item, dict):
            name = str(item.get("name") or "").strip()
        else:
            name = str(item or "").strip()
        if name:
            names.append(name)
    return tuple(names)


def parse_pr_view_payload(payload: dict[str, Any]) -> AutoReadyPrState:
    """Normalize `gh pr view --json` output for auto-ready decisions."""
    number = _int_or_none(payload.get("number"))
    if number is None:
        raise ValueError("PR view payload is missing a numeric pull request number.")
    return AutoReadyPrState(
        number=number,
        labels=_label_names(payload.get("labels")),
        is_draft=bool(payload.get("isDraft")),
        state=str(payload.get("state") or "").strip().upper(),
        is_cross_repository=bool(payload.get("isCrossRepository")),
    )


def auto_ready_decision(
    pr_state: AutoReadyPrState,
    *,
    label: str = AUTO_READY_LABEL,
) -> AutoReadyDecision:
    """Return whether a PR is eligible for automatic ready transition."""
    if pr_state.state != "OPEN":
        return AutoReadyDecision("skipped", f"PR state is {pr_state.state or 'unknown'}.")
    if pr_state.is_cross_repository:
        return AutoReadyDecision("skipped", "Auto-ready is limited to same-repository PRs.")
    if not pr_state.is_draft:
        return AutoReadyDecision("skipped", "PR is already ready for review.")

    wanted = label.casefold()
    labels = {item.casefold() for item in pr_state.labels}
    if wanted not in labels:
        return AutoReadyDecision("skipped", f"Missing opt-in label `{label}`.")
    return AutoReadyDecision("eligible", f"Opt-in label `{label}` is present.")


def load_pr_state(
    root: Path,
    pr_number: int,
    *,
    gh_path: str | None = None,
) -> AutoReadyPrState:
    """Load normalized PR state through GitHub CLI."""
    resolved_gh_path = gh_path or find_gh_path()
    if resolved_gh_path is None:
        raise RuntimeError("GitHub CLI `gh` is not installed or discoverable.")
    result = run_command(
        [resolved_gh_path, "pr", "view", str(pr_number), "--json", PR_VIEW_FIELDS],
        cwd=root,
        timeout=60,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout).strip()
        raise RuntimeError(message or f"Could not load PR #{pr_number} metadata.")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not parse PR #{pr_number} metadata JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected mapping metadata for PR #{pr_number}.")
    return parse_pr_view_payload(payload)


def run_auto_ready(
    root: Path,
    event_payload: dict[str, Any],
    *,
    pr_number: int | None = None,
    label: str = AUTO_READY_LABEL,
    dry_run: bool = False,
    gh_path: str | None = None,
    ignored_check_names: tuple[str, ...] = (),
    ignored_workflows: tuple[str, ...] = (),
    validation_timeout_seconds: int = 300,
) -> AutoReadyRunResult:
    """Run the auto-ready gate when the event and PR state opt in."""
    resolved_pr_number = pr_number if pr_number is not None else pr_number_from_event(event_payload)
    if resolved_pr_number is None:
        return AutoReadyRunResult("skipped", "No pull request number found in event.", None)

    try:
        pr_state = load_pr_state(root, resolved_pr_number, gh_path=gh_path)
    except RuntimeError as exc:
        return AutoReadyRunResult("error", str(exc), resolved_pr_number)

    decision = auto_ready_decision(pr_state, label=label)
    if not decision.eligible:
        return AutoReadyRunResult(decision.status, decision.reason, resolved_pr_number)

    finish_report = finish_pr(
        root,
        resolved_pr_number,
        dry_run=dry_run,
        gh_path=gh_path,
        ignored_check_names=tuple(AUTO_READY_IGNORED_CHECK_NAMES) + tuple(ignored_check_names),
        ignored_workflows=tuple(AUTO_READY_IGNORED_WORKFLOWS) + tuple(ignored_workflows),
        validation_timeout_seconds=validation_timeout_seconds,
    )
    status = finish_report.status if finish_report.ok else "blocked"
    reason = finish_report.error or decision.reason
    return AutoReadyRunResult(status, reason, resolved_pr_number, finish_report)


def render_auto_ready_result(result: AutoReadyRunResult) -> str:
    """Render an auto-ready event result for GitHub Actions logs."""
    from physics_lab.registry.pr_finish_gate import render_finish_gate_report

    lines = [
        f"Auto-ready status: {result.status}",
        f"PR: {result.pr_number if result.pr_number is not None else 'none'}",
        f"Reason: {result.reason}",
    ]
    if result.finish_report is not None and result.pr_number is not None:
        lines.append("")
        lines.append(render_finish_gate_report(result.finish_report, pr_number=result.pr_number))
    return "\n".join(lines)
