"""Helpers for source-of-truth-driven repository snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess

from physics_lab.registry.active_board import STATUS_SECTION_ORDER, load_board_entries
from physics_lab.registry.experiments import load_experiment
from physics_lab.registry.results import load_result


@dataclass(frozen=True)
class SnapshotContext:
    """Canonical git context for a repository snapshot run."""

    invocation_root: Path
    canonical_root: Path
    repo_name: str
    current_branch: str
    head_commit: str
    default_base_ref: str


@dataclass(frozen=True)
class ResultSnapshot:
    """Compact summary of one canonical result artifact."""

    result_id: str
    experiment_id: str
    run_id: str
    task_id: str
    best_verdict: str
    generated_at: str
    path: str
    title: str


def build_snapshot_context(root: Path) -> SnapshotContext:
    """Return canonical repository identity for snapshot output."""
    invocation_root = root.resolve()
    common_dir_raw = _run_git(invocation_root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    common_dir = Path(common_dir_raw).resolve() if common_dir_raw else None
    if common_dir is not None and common_dir.name == ".git":
        canonical_root = common_dir.parent
    else:
        canonical_root_raw = _run_git(invocation_root, "rev-parse", "--show-toplevel")
        canonical_root = Path(canonical_root_raw).resolve() if canonical_root_raw else invocation_root
    current_branch = _run_git(invocation_root, "branch", "--show-current") or "detached"
    head_commit = _run_git(invocation_root, "rev-parse", "--short=12", "HEAD") or "unknown"

    default_base_ref = "origin/main"
    if not _git_ref_exists(invocation_root, default_base_ref):
        current_ref = current_branch if current_branch != "detached" else "HEAD"
        default_base_ref = current_ref

    return SnapshotContext(
        invocation_root=invocation_root,
        canonical_root=canonical_root,
        repo_name=canonical_root.name,
        current_branch=current_branch,
        head_commit=head_commit,
        default_base_ref=default_base_ref,
    )


def render_authority_notes(root: Path) -> str:
    """Return markdown notes describing snapshot authority layers."""
    context = build_snapshot_context(root)
    lines = [
        "### Snapshot Authority",
        "",
        f"- canonical_repo_name: `{context.repo_name}`",
        f"- canonical_repo_root: `{context.canonical_root}`",
        f"- invocation_path: `{context.invocation_root}`",
        f"- current_branch: `{context.current_branch}`",
        f"- head_commit: `{context.head_commit}`",
        f"- default_base_ref: `{context.default_base_ref}`",
        "",
        "Authoritative current-state sections below are generated from canonical",
        "`tasks/TASK-*.yaml`, `experiments/*.yaml`, and `results/*/*/result.yaml`",
        "artifacts. Maintainer-facing docs such as `docs/status.md` and",
        "`docs/next-steps.md` remain useful context, but they are secondary and",
        "may lag behind the structured repository state.",
        "",
        "Large tree, task, result, and knowledge dumps remain included later as",
        "archive context for deep audits.",
    ]
    return "\n".join(lines)


def render_current_state_summary(root: Path, *, recent_done_limit: int = 5, recent_result_limit: int = 5) -> str:
    """Render a markdown summary of current structured repository state."""
    entries = load_board_entries(root.resolve())
    experiments = _load_experiment_rows(root)
    results = _load_recent_results(root, limit=recent_result_limit)

    lines = [
        "### Current Task State",
        "",
    ]
    for status, _header in STATUS_SECTION_ORDER:
        section_entries = [entry for entry in entries if entry.status == status]
        lines.append(f"- {status}: {len(section_entries)}")

    ready_entries = [entry for entry in entries if entry.status == "READY"]
    review_ready_entries = [entry for entry in entries if entry.status == "REVIEW_READY"]
    blocked_entries = [entry for entry in entries if entry.status == "BLOCKED"]
    done_entries = [entry for entry in entries if entry.status == "DONE"]

    lines.extend(_render_entry_list("READY now", ready_entries, limit=6))
    lines.extend(_render_entry_list("REVIEW_READY now", review_ready_entries, limit=6))
    lines.extend(_render_entry_list("BLOCKED now", blocked_entries, limit=6))
    lines.extend(_render_entry_list("Recently DONE", done_entries, limit=recent_done_limit, merged=True))

    lines.extend(
        [
            "",
            "### Current Experiment State",
            "",
        ]
    )
    experiment_status_counts: dict[str, int] = {}
    for experiment in experiments:
        experiment_status_counts[experiment["status"]] = experiment_status_counts.get(experiment["status"], 0) + 1
    for status in sorted(experiment_status_counts):
        lines.append(f"- {status}: {experiment_status_counts[status]}")
    lines.extend(_render_experiment_list(experiments, limit=8))

    lines.extend(
        [
            "",
            "### Recent Result Surface",
            "",
        ]
    )
    if results:
        for result in results:
            lines.append(
                f"- `{result.result_id}` / `{result.experiment_id}` / `{result.run_id}` "
                f"({result.best_verdict}) [{result.task_id}] - {result.path}"
            )
            lines.append(f"  {result.title} | generated_at `{result.generated_at}`")
    else:
        lines.append("- none")
    return "\n".join(lines)


def _render_entry_list(title: str, entries: list, *, limit: int, merged: bool = False) -> list[str]:
    lines = ["", f"### {title}", ""]
    if not entries:
        lines.append("- none")
        return lines

    sorted_entries = sorted(entries, key=lambda entry: entry.task_number, reverse=merged)
    for entry in sorted_entries[:limit]:
        if merged:
            lines.append(f"- `{entry.task_id}` - {entry.title}")
        else:
            lines.append(
                f"- `{entry.task_id}` - {entry.title} "
                f"(`{entry.type}`, priority `{entry.priority}`, difficulty `{entry.difficulty}`)"
            )
    return lines


def _render_experiment_list(experiments: list[dict[str, str]], *, limit: int) -> list[str]:
    lines = ["", "### Canonical Experiments", ""]
    if not experiments:
        lines.append("- none")
        return lines

    for experiment in experiments[:limit]:
        lines.append(
            f"- `{experiment['id']}` - {experiment['title']} "
            f"(`{experiment['status']}`, domain `{experiment['domain']}`)"
        )
    return lines


def _load_experiment_rows(root: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted((root / "experiments").glob("EXP-*.yaml")):
        payload = load_experiment(path)
        rows.append(
            {
                "id": str(payload["id"]),
                "title": str(payload["title"]),
                "status": str(payload["status"]),
                "domain": str(payload["domain"]),
            }
        )
    return rows


def _load_recent_results(root: Path, *, limit: int) -> list[ResultSnapshot]:
    rows: list[ResultSnapshot] = []
    for path in sorted((root / "results").glob("*/*/result.yaml")):
        payload = load_result(path)
        rows.append(
            ResultSnapshot(
                result_id=str(payload["result_id"]),
                experiment_id=str(payload["experiment_id"]),
                run_id=str(payload["run_id"]),
                task_id=str(payload.get("task_id", "unknown")),
                best_verdict=str(payload["best_verdict"]),
                generated_at=str(payload.get("generated_at", "")),
                path=path.relative_to(root).as_posix(),
                title=str(payload["title"]),
            )
        )
    rows.sort(key=lambda row: (row.generated_at, row.path), reverse=True)
    return rows[:limit]


def _run_git(root: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return ""
    return completed.stdout.strip()


def _git_ref_exists(root: Path, ref: str) -> bool:
    try:
        subprocess.run(
            ["git", "rev-parse", "--verify", ref],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return False
    return True
