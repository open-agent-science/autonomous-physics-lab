"""PR packaging helpers for autonomous sandbox agent runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from physics_lab.registry.agent_runs import load_agent_run
from physics_lab.registry.research_proposals import (
    load_experiment_proposal,
    load_hypothesis_proposal,
)


def _repo_relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def _read_text(root: Path, value: str) -> str:
    return _resolve(root, value).read_text(encoding="utf-8").strip()


def _read_json(root: Path, value: str) -> dict[str, Any]:
    payload = json.loads(_resolve(root, value).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {value}")
    return payload


def _bullet_lines(values: list[Any] | tuple[Any, ...]) -> list[str]:
    if not values:
        return ["- none recorded"]
    return [f"- {value}" for value in values]


def _compact_metrics(metrics: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for key in ("agent_run_id", "model_id", "formula", "verdict"):
        if key in metrics:
            lines.append(f"- `{key}`: `{metrics[key]}`")
    nested_metrics = metrics.get("metrics")
    if isinstance(nested_metrics, dict):
        for slice_name, slice_metrics in nested_metrics.items():
            if not isinstance(slice_metrics, dict):
                continue
            mean_error = slice_metrics.get("mean_relative_error")
            max_error = slice_metrics.get("max_relative_error")
            if mean_error is not None or max_error is not None:
                lines.append(
                    f"- `{slice_name}`: mean relative error `{mean_error}`, max relative error `{max_error}`"
                )
    reference = metrics.get("reference_comparison")
    if isinstance(reference, dict):
        for key, value in reference.items():
            lines.append(f"- reference `{key}`: `{value}`")
    return lines or ["- metrics file loaded, but no compact numeric summary was recognized"]


def _proposal_summary(prefix: str, proposal: dict[str, Any]) -> list[str]:
    lines = [
        f"- `{prefix}_id`: `{proposal.get('id', 'unknown')}`",
        f"- title: {proposal.get('title', 'unknown')}",
        f"- verdict: `{proposal.get('verdict', 'unknown')}`",
        f"- claim ceiling: {proposal.get('claim_ceiling', 'not recorded')}",
    ]
    if prefix == "hypothesis":
        statement = proposal.get("hypothesis", {}).get("statement")
        if statement:
            lines.append(f"- statement: {statement}")
    if prefix == "experiment":
        question = proposal.get("question")
        method = proposal.get("method", {}).get("summary")
        if question:
            lines.append(f"- question: {question}")
        if method:
            lines.append(f"- method: {method}")
    return lines


def _preflight_summary(agent_run: dict[str, Any]) -> list[str]:
    preflight = agent_run.get("preflight", {})
    lines = [f"- passed: `{preflight.get('passed', 'unknown')}`"]
    checks = preflight.get("checks", [])
    if not checks:
        lines.append("- checks: none recorded")
        return lines
    for check in checks:
        if isinstance(check, dict):
            lines.append(
                f"- `{check.get('name', 'unnamed')}`: `{check.get('status', 'unknown')}` - {check.get('notes', '')}"
            )
    return lines


def build_agent_run_pr_context(
    agent_run_path: str | Path,
    *,
    root: str | Path = ".",
) -> str:
    """Build a maintainer-facing PR context block for one sandbox agent run."""
    root_path = Path(root).resolve()
    manifest_path = Path(agent_run_path)
    if not manifest_path.is_absolute():
        manifest_path = root_path / manifest_path

    agent_run = load_agent_run(manifest_path, root=root_path)
    proposal_paths = agent_run["proposal_paths"]
    hypothesis_path = _resolve(root_path, proposal_paths["hypothesis"])
    experiment_path = _resolve(root_path, proposal_paths["experiment"])
    hypothesis = load_hypothesis_proposal(hypothesis_path, root=root_path)
    experiment = load_experiment_proposal(experiment_path, root=root_path)

    artifacts = agent_run["artifacts"]
    metrics = _read_json(root_path, artifacts["metrics"])
    report = _read_text(root_path, artifacts["report"])
    limitations_text = _read_text(root_path, artifacts["limitations"])
    review_summary = _read_text(root_path, artifacts["review_summary"])

    promotion_boundary = agent_run.get("promotion_boundary", {})
    overclaim_mitigations = hypothesis.get("overclaim_risk", {}).get("mitigations", [])
    rejected_alternatives = hypothesis.get("hypothesis", {}).get("expected_failure_modes", [])

    lines = [
        f"# Agent-Run PR Context - {agent_run['id']}",
        "",
        "## Identity",
        "",
        f"- Agent run: `{agent_run['id']}`",
        f"- Campaign profile: `{agent_run['campaign_profile_id']}`",
        f"- Task ID: `{agent_run['task_id']}`",
        f"- Created by: `{agent_run['created_by']['contributor_id']}/{agent_run['created_by']['agent_id']}`",
        f"- Manifest: `{_repo_relative(root_path, manifest_path)}`",
        f"- Sandbox only: `{agent_run['sandbox_only']}`",
        f"- Verdict: `{agent_run['verdict']}`",
        "",
        "## Hypothesis Summary",
        "",
        *_proposal_summary("hypothesis", hypothesis),
        "",
        "## Experiment Summary",
        "",
        *_proposal_summary("experiment", experiment),
        "",
        "## Preflight Result",
        "",
        *_preflight_summary(agent_run),
        "",
        "## Metrics",
        "",
        *_compact_metrics(metrics),
        "",
        "## Limitations",
        "",
        limitations_text,
        "",
        "## Rejected Alternatives / Failure Modes",
        "",
        *_bullet_lines(list(rejected_alternatives)),
        "",
        "## Overclaim Audit",
        "",
        f"- public claim allowed: `{hypothesis.get('overclaim_risk', {}).get('public_claim_allowed', 'unknown')}`",
        f"- writes canonical result: `{promotion_boundary.get('writes_canonical_result', 'unknown')}`",
        f"- claim promotion allowed: `{promotion_boundary.get('claim_promotion_allowed', 'unknown')}`",
        f"- required next step: {promotion_boundary.get('required_next_step', 'not recorded')}",
        *_bullet_lines(list(overclaim_mitigations)),
        "",
        "## Maintainer Decision Options",
        "",
        "- reject the sandbox run as out of scope or insufficiently supported",
        "- retain it as negative or sandbox-only scientific memory",
        "- promote a follow-up canonical task while keeping this run non-canonical",
        "- promote to canonical experiment/result only through a later reviewed task and claim-promotion review",
        "",
        "## Review Summary Artifact",
        "",
        review_summary,
        "",
        "## Source Report Excerpt",
        "",
        report,
        "",
    ]
    return "\n".join(lines)
