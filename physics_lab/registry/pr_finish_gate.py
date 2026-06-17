"""Finish-gate helper for PR review, CI, and ready transition."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any

from physics_lab.registry.maintainer_review import DEFAULT_REVIEW_VALIDATION_TIMEOUT_SECONDS
from physics_lab.registry.pr_capability import find_gh_path
from physics_lab.registry.review_git import CommandResult, run_command


REVIEW_VERDICT_PATTERN = re.compile(r"^Verdict:\s*(?P<verdict>[A-Z_]+)\s*$", re.MULTILINE)
ACTION_RUN_PATTERN = re.compile(r"/actions/runs/(?P<run_id>[0-9]+)")
PASS_BUCKETS = frozenset({"pass", "skipping"})
FAIL_BUCKETS = frozenset({"fail", "cancel"})
PENDING_BUCKETS = frozenset({"pending"})


@dataclass(frozen=True)
class CheckState:
    """Normalized GitHub PR check state."""

    name: str
    bucket: str
    state: str
    link: str
    workflow: str = ""

    @property
    def inspection_command(self) -> str:
        """Return a deterministic next command for inspecting this check."""
        match = ACTION_RUN_PATTERN.search(self.link)
        if match is not None:
            return f"gh run view {match.group('run_id')} --log-failed"
        return "gh pr checks <pr-number> --json name,state,bucket,link"


@dataclass(frozen=True)
class CiGate:
    """Aggregated CI gate state."""

    status: str
    checks: tuple[CheckState, ...]
    failures: tuple[CheckState, ...]
    pending: tuple[CheckState, ...]
    raw_error: str = ""


@dataclass(frozen=True)
class FinishGateReport:
    """Result of trying to finish a pull request."""

    status: str
    review_verdict: str
    ci_status: str
    ready_transition: str
    next_safe_command: str
    review_output: str
    check_failures: tuple[CheckState, ...]
    check_pending: tuple[CheckState, ...]
    ready_output: str = ""
    error: str = ""

    @property
    def ok(self) -> bool:
        """Return whether the PR was marked ready or would be marked ready."""
        return self.status in {"ready_marked", "ready_dry_run"}


def parse_review_verdict(review_output: str) -> str:
    """Extract the maintainer review verdict from apl_review_pr output."""
    match = REVIEW_VERDICT_PATTERN.search(review_output)
    if match is None:
        return "UNKNOWN"
    return match.group("verdict")


def _workflow_name(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("name") or "")
    return str(value or "")


def parse_checks_payload(payload: str) -> tuple[CheckState, ...]:
    """Parse `gh pr checks --json` output into normalized check rows."""
    rows = json.loads(payload)
    if not isinstance(rows, list):
        raise ValueError("Expected a list from gh pr checks JSON output.")
    checks: list[CheckState] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        checks.append(
            CheckState(
                name=str(row.get("name") or "").strip() or "<unnamed check>",
                bucket=str(row.get("bucket") or "").strip().lower(),
                state=str(row.get("state") or "").strip(),
                link=str(row.get("link") or row.get("detailsUrl") or "").strip(),
                workflow=_workflow_name(row.get("workflow")),
            )
        )
    return tuple(checks)


def classify_ci_gate(checks: tuple[CheckState, ...]) -> CiGate:
    """Classify checks as pass, fail, pending, or unknown."""
    failures = tuple(check for check in checks if check.bucket in FAIL_BUCKETS)
    pending = tuple(check for check in checks if check.bucket in PENDING_BUCKETS)
    unknown = tuple(
        check
        for check in checks
        if check.bucket not in PASS_BUCKETS | FAIL_BUCKETS | PENDING_BUCKETS
    )
    if failures:
        status = "fail"
    elif pending:
        status = "pending"
    elif unknown or not checks:
        status = "unknown"
    else:
        status = "pass"
    return CiGate(status=status, checks=checks, failures=failures, pending=pending)


def load_ci_gate(root: Path, pr_number: int, *, gh_path: str | None = None) -> CiGate:
    """Load and classify GitHub PR checks through gh."""
    resolved_gh_path = gh_path or find_gh_path()
    if resolved_gh_path is None:
        return CiGate(
            status="unknown",
            checks=(),
            failures=(),
            pending=(),
            raw_error="GitHub CLI `gh` is not installed or discoverable.",
        )
    result = run_command(
        [
            resolved_gh_path,
            "pr",
            "checks",
            str(pr_number),
            "--json",
            "name,state,bucket,link,workflow",
        ],
        cwd=root,
        timeout=60,
    )
    if result.returncode != 0:
        return CiGate(
            status="unknown",
            checks=(),
            failures=(),
            pending=(),
            raw_error=(result.stderr or result.stdout).strip(),
        )
    try:
        checks = parse_checks_payload(result.stdout)
    except (json.JSONDecodeError, ValueError) as exc:
        return CiGate(
            status="unknown",
            checks=(),
            failures=(),
            pending=(),
            raw_error=str(exc),
        )
    return classify_ci_gate(checks)


def run_review_gate(
    root: Path,
    pr_number: int,
    *,
    validation_timeout_seconds: int = DEFAULT_REVIEW_VALIDATION_TIMEOUT_SECONDS,
) -> CommandResult:
    """Run the canonical PR review helper through the active Python runtime."""
    return run_command(
        [
            sys.executable,
            str(root / "scripts" / "apl_review_pr.py"),
            "--pr",
            str(pr_number),
            "--validation-timeout-seconds",
            str(validation_timeout_seconds),
        ],
        cwd=root,
        timeout=900,
    )


def mark_ready(root: Path, pr_number: int, *, gh_path: str | None = None) -> CommandResult:
    """Mark a PR ready for review through gh."""
    resolved_gh_path = gh_path or find_gh_path()
    if resolved_gh_path is None:
        return CommandResult(
            returncode=127,
            stdout="",
            stderr="GitHub CLI `gh` is not installed or discoverable.",
        )
    return run_command(
        [resolved_gh_path, "pr", "ready", str(pr_number)],
        cwd=root,
        timeout=60,
    )


def finish_pr(
    root: Path,
    pr_number: int,
    *,
    dry_run: bool = False,
    gh_path: str | None = None,
    validation_timeout_seconds: int = DEFAULT_REVIEW_VALIDATION_TIMEOUT_SECONDS,
) -> FinishGateReport:
    """Run review and CI gates, then mark the PR ready when both pass."""
    review_result = run_review_gate(
        root,
        pr_number,
        validation_timeout_seconds=validation_timeout_seconds,
    )
    review_output = (review_result.stdout or "") + (review_result.stderr or "")
    review_verdict = parse_review_verdict(review_output)
    if review_result.returncode != 0 or review_verdict != "MERGE_OK":
        return FinishGateReport(
            status="blocked",
            review_verdict=review_verdict,
            ci_status="not_checked",
            ready_transition="not_attempted",
            next_safe_command=f"python3 scripts/apl_review_pr.py --pr {pr_number}",
            review_output=review_output,
            check_failures=(),
            check_pending=(),
            error="Review gate did not return MERGE_OK.",
        )

    ci_gate = load_ci_gate(root, pr_number, gh_path=gh_path)
    if ci_gate.status == "fail":
        failing = ci_gate.failures[0]
        return FinishGateReport(
            status="blocked",
            review_verdict=review_verdict,
            ci_status=ci_gate.status,
            ready_transition="not_attempted",
            next_safe_command=failing.inspection_command,
            review_output=review_output,
            check_failures=ci_gate.failures,
            check_pending=ci_gate.pending,
            error=f"CI check failed: {failing.name}.",
        )
    if ci_gate.status == "pending":
        return FinishGateReport(
            status="blocked",
            review_verdict=review_verdict,
            ci_status=ci_gate.status,
            ready_transition="not_attempted",
            next_safe_command=f"gh pr checks {pr_number} --watch",
            review_output=review_output,
            check_failures=ci_gate.failures,
            check_pending=ci_gate.pending,
            error="CI checks are still pending.",
        )
    if ci_gate.status != "pass":
        return FinishGateReport(
            status="blocked",
            review_verdict=review_verdict,
            ci_status=ci_gate.status,
            ready_transition="not_attempted",
            next_safe_command=f"gh pr checks {pr_number} --json name,state,bucket,link",
            review_output=review_output,
            check_failures=ci_gate.failures,
            check_pending=ci_gate.pending,
            error=ci_gate.raw_error or "CI status is unknown.",
        )

    if dry_run:
        return FinishGateReport(
            status="ready_dry_run",
            review_verdict=review_verdict,
            ci_status=ci_gate.status,
            ready_transition="dry_run",
            next_safe_command=f"gh pr ready {pr_number}",
            review_output=review_output,
            check_failures=(),
            check_pending=(),
        )

    ready_result = mark_ready(root, pr_number, gh_path=gh_path)
    ready_output = (ready_result.stdout or "") + (ready_result.stderr or "")
    if ready_result.returncode != 0:
        return FinishGateReport(
            status="blocked",
            review_verdict=review_verdict,
            ci_status=ci_gate.status,
            ready_transition="failed",
            next_safe_command=f"gh pr ready {pr_number}",
            review_output=review_output,
            check_failures=(),
            check_pending=(),
            ready_output=ready_output,
            error="Ready transition command failed.",
        )
    return FinishGateReport(
        status="ready_marked",
        review_verdict=review_verdict,
        ci_status=ci_gate.status,
        ready_transition="completed",
        next_safe_command="none",
        review_output=review_output,
        check_failures=(),
        check_pending=(),
        ready_output=ready_output,
    )


def render_finish_gate_report(report: FinishGateReport, *, pr_number: int) -> str:
    """Render a maintainer-facing finish gate report."""
    lines = [
        f"PR: {pr_number}",
        f"Status: {report.status}",
        f"Review verdict: {report.review_verdict}",
        f"CI status: {report.ci_status}",
        f"Ready transition: {report.ready_transition}",
    ]
    if report.check_failures:
        lines.append("Failing checks:")
        for check in report.check_failures:
            lines.append(f"- {check.name}")
            if check.link:
                lines.append(f"  URL: {check.link}")
            lines.append(f"  Inspect: {check.inspection_command}")
    if report.check_pending:
        lines.append("Pending checks:")
        for check in report.check_pending:
            lines.append(f"- {check.name}")
            if check.link:
                lines.append(f"  URL: {check.link}")
    if report.error:
        lines.append(f"Blocker: {report.error}")
    if report.next_safe_command != "none":
        lines.append(f"Next safe command: {report.next_safe_command}")
    if report.ready_output.strip():
        lines.append("Ready command output:")
        lines.append(report.ready_output.strip())
    return "\n".join(lines)
