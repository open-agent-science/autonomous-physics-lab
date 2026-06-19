"""Gate B independent replay validation for AGENT_PUBLISHED results."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
from typing import Any

import yaml


DEFAULT_TOLERANCE = 1.0e-9
SAFE_RESULT_COMMANDS = (
    ("physics-lab", "run"),
    ("python3", "-m", "physics_lab.cli", "run"),
    ("python", "-m", "physics_lab.cli", "run"),
)
SKIPPED_NUMERIC_PATH_PREFIXES = (
    "generated_at",
    "git_commit",
)
STABLE_STRING_PATHS = (
    "result_id",
    "experiment_id",
    "hypothesis_id",
    "task_id",
    "run_id",
    "best_model_id",
    "best_verdict",
)


@dataclass(frozen=True)
class ReplayIdentity:
    """Metadata for the agent performing Gate B replay."""

    contributor_id: str
    github_username: str
    agent_tool: str
    model_version: str

    def as_dict(self) -> dict[str, str]:
        return {
            "contributor_id": self.contributor_id,
            "github_username": self.github_username,
            "agent_tool": self.agent_tool,
            "model_version": self.model_version,
        }


@dataclass(frozen=True)
class ReplayIssue:
    """One Gate B issue or warning."""

    code: str
    message: str
    severity: str = "error"


@dataclass(frozen=True)
class ReplayMetricDelta:
    """One numeric metric comparison."""

    path: str
    expected: float
    observed: float
    abs_delta: float
    tolerance: float

    @property
    def ok(self) -> bool:
        return self.abs_delta <= self.tolerance


@dataclass(frozen=True)
class ReplayReport:
    """Gate B replay outcome."""

    result_path: str
    replay_output_dir: str | None
    status: str
    issues: tuple[ReplayIssue, ...]
    metric_deltas: tuple[ReplayMetricDelta, ...]
    validation_record: dict[str, Any] | None
    contested_report: str | None

    @property
    def ok(self) -> bool:
        return self.status == "PASS" and not any(
            issue.severity == "error" for issue in self.issues
        )


def validate_agent_published_result(
    result_path: str | Path,
    *,
    root: str | Path = ".",
    replayed_by: ReplayIdentity,
    output_dir: str | Path | None = None,
    tolerance: float = DEFAULT_TOLERANCE,
    dry_run: bool = False,
) -> ReplayReport:
    """Replay an AGENT_PUBLISHED result and build a Gate B validation report."""
    root_path = Path(root)
    result_file = Path(result_path)
    if not result_file.is_absolute():
        result_file = root_path / result_file

    expected = _load_yaml_mapping(result_file)
    preflight_issues = _preflight_issues(expected, result_file=result_file, root=root_path)
    identity_issues = _identity_issues(expected, replayed_by=replayed_by)
    warning_issues = [issue for issue in identity_issues if issue.severity != "error"]
    if any(issue.severity == "error" for issue in preflight_issues + identity_issues):
        return _blocked_report(
            result_file,
            tuple(preflight_issues + identity_issues),
            replay_output_dir=None,
        )

    command_result = _safe_replay_command(expected, root=root_path)
    if isinstance(command_result, ReplayIssue):
        return _blocked_report(
            result_file,
            tuple(preflight_issues + warning_issues + [command_result]),
            replay_output_dir=None,
        )

    replay_dir = Path(output_dir) if output_dir is not None else None
    temporary_dir: tempfile.TemporaryDirectory[str] | None = None
    try:
        if replay_dir is None:
            temporary_dir = tempfile.TemporaryDirectory(prefix="apl-gate-b-")
            replay_dir = Path(temporary_dir.name)
        replay_dir.mkdir(parents=True, exist_ok=True)

        if not dry_run:
            completed = subprocess.run(
                [*command_result, "--output-dir", str(replay_dir)],
                cwd=root_path,
                text=True,
                capture_output=True,
                check=False,
                timeout=120,
            )
            if completed.returncode != 0:
                return _blocked_report(
                    result_file,
                    tuple(
                        preflight_issues
                        + warning_issues
                        + [
                            ReplayIssue(
                                "replay-command-failed",
                                "Replay command failed: "
                                + (completed.stderr.strip() or completed.stdout.strip()),
                            )
                        ]
                    ),
                    replay_output_dir=str(replay_dir),
                )

        replay_result = _replayed_result_path(expected, replay_dir)
        if not replay_result.exists():
            return _blocked_report(
                result_file,
                tuple(
                    preflight_issues
                    + warning_issues
                    + [
                        ReplayIssue(
                            "replay-result-missing",
                            f"Replay did not write expected result file: {replay_result}.",
                        )
                    ]
                ),
                replay_output_dir=str(replay_dir),
            )

        observed = _load_yaml_mapping(replay_result)
        comparison_issues, metric_deltas = _compare_results(
            expected,
            observed,
            tolerance=tolerance,
        )
        all_issues = tuple(preflight_issues + warning_issues + comparison_issues)
        if any(issue.severity == "error" for issue in all_issues):
            return ReplayReport(
                result_path=str(result_file),
                replay_output_dir=str(replay_dir),
                status="CONTESTED_RESULT",
                issues=all_issues,
                metric_deltas=tuple(metric_deltas),
                validation_record=None,
                contested_report=_render_contested_report(
                    expected,
                    replayed_by=replayed_by,
                    issues=all_issues,
                    metric_deltas=metric_deltas,
                    replay_dir=replay_dir,
                    tolerance=tolerance,
                ),
            )

        return ReplayReport(
            result_path=str(result_file),
            replay_output_dir=str(replay_dir),
            status="PASS",
            issues=all_issues,
            metric_deltas=tuple(metric_deltas),
            validation_record=_validation_record(
                expected,
                replayed_by=replayed_by,
                replay_dir=replay_dir,
                tolerance=tolerance,
                metric_deltas=metric_deltas,
            ),
            contested_report=None,
        )
    finally:
        # Keep explicit output dirs for inspection; temporary dirs are intentionally
        # cleaned unless the caller supplied --output-dir.
        if temporary_dir is not None:
            temporary_dir.cleanup()


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a YAML mapping.")
    return payload


def _preflight_issues(payload: dict[str, Any], *, result_file: Path, root: Path) -> list[ReplayIssue]:
    issues: list[ReplayIssue] = []
    if payload.get("review_tier") != "AGENT_PUBLISHED":
        issues.append(
            ReplayIssue(
                "review-tier",
                "Gate B expects an existing RESULT with review_tier: AGENT_PUBLISHED.",
            )
        )
    if not isinstance(payload.get("result_id"), str):
        issues.append(ReplayIssue("result-id", "RESULT artifact must include result_id."))
    if not isinstance(payload.get("command"), str) or not payload["command"].strip():
        issues.append(ReplayIssue("command", "RESULT artifact must include replay command."))
    if not isinstance(payload.get("git_commit"), str) or not payload["git_commit"].strip():
        issues.append(ReplayIssue("git-commit", "RESULT artifact must pin git_commit."))
    if not isinstance(payload.get("engine_version"), str) or not payload["engine_version"].strip():
        issues.append(ReplayIssue("engine-version", "RESULT artifact must pin engine_version."))
    if not isinstance(payload.get("input_file_hashes"), dict) or not payload["input_file_hashes"]:
        issues.append(ReplayIssue("input-hashes", "RESULT artifact must include input_file_hashes."))
    else:
        issues.extend(_input_hash_issues(payload["input_file_hashes"], root=root))

    if "results" not in result_file.parts:
        issues.append(
            ReplayIssue(
                "result-location",
                "Gate B expects a canonical result file under results/.",
            )
        )
    return issues


def _input_hash_issues(input_hashes: dict[str, Any], *, root: Path) -> list[ReplayIssue]:
    issues: list[ReplayIssue] = []
    for label, entry in input_hashes.items():
        if not isinstance(entry, dict):
            issues.append(ReplayIssue("input-hash-entry", f"{label!r} hash entry is not a mapping."))
            continue
        source_path = entry.get("path")
        expected_hash = entry.get("sha256")
        if not isinstance(source_path, str) or not source_path:
            issues.append(ReplayIssue("input-hash-path", f"{label!r} is missing path."))
            continue
        if not isinstance(expected_hash, str) or len(expected_hash) != 64:
            issues.append(ReplayIssue("input-hash-sha", f"{label!r} is missing 64-char sha256."))
            continue
        path = root / source_path
        if not path.exists():
            issues.append(ReplayIssue("input-file-missing", f"{label!r} input file is missing: {source_path}."))
            continue
        observed_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed_hash != expected_hash:
            issues.append(
                ReplayIssue(
                    "input-hash-mismatch",
                    f"{label!r} hash mismatch for {source_path}: expected {expected_hash}, observed {observed_hash}.",
                )
            )
    return issues


def _identity_issues(
    payload: dict[str, Any],
    *,
    replayed_by: ReplayIdentity,
) -> list[ReplayIssue]:
    """Return Gate B independence issues for the replay identity.

    Gate B certifies that an AGENT_PUBLISHED result reproduces under an
    *independent* replay, so a self-validation by the same contributor and the
    same agent that published the result is forbidden (blocking error). Without a
    recorded original publisher, independence cannot be certified, so that is also
    blocking. A single-axis overlap (same agent only, or same contributor only)
    stays a non-blocking advisory warning, which keeps single-maintainer Gate B
    viable when a different agent tool performs the replay.
    """
    issues: list[ReplayIssue] = []
    publisher = _original_publisher(payload)
    if publisher is None:
        issues.append(
            ReplayIssue(
                "original-publisher-unrecorded",
                "Gate B cannot certify independence: the result does not record an "
                "original publisher. Record `agent_proposal_evaluation.published_by` "
                "(contributor_id, github_username, agent_tool, model_version) before "
                "an independent agent runs Gate B.",
                severity="error",
            )
        )
        return issues

    original_tool = str(publisher.get("agent_tool", "")).strip().lower()
    original_contributor = str(publisher.get("contributor_id", "")).strip().lower()
    same_tool = bool(original_tool) and original_tool == replayed_by.agent_tool.strip().lower()
    same_contributor = (
        bool(original_contributor)
        and original_contributor == replayed_by.contributor_id.strip().lower()
    )

    if same_tool and same_contributor:
        issues.append(
            ReplayIssue(
                "self-validation-forbidden",
                "Gate B requires an independent replayer: the replay identity matches "
                "the original publisher on both contributor and agent tool. Re-run the "
                "replay with a different agent tool (and/or a different contributor).",
                severity="error",
            )
        )
        return issues

    if same_tool:
        issues.append(
            ReplayIssue(
                "same-agent-tool",
                "Replay uses the same agent tool as the original publisher (different "
                "contributor); prefer cross-tool validation when available.",
                severity="warning",
            )
        )
    if same_contributor:
        issues.append(
            ReplayIssue(
                "same-contributor",
                "Replay uses the same contributor id as the original publisher with a "
                "different agent tool; this is acceptable for maintainer-run Gate B, but "
                "record the limitation.",
                severity="warning",
            )
        )
    return issues


def _original_publisher(payload: dict[str, Any]) -> dict[str, Any] | None:
    evaluation = payload.get("agent_proposal_evaluation")
    if not isinstance(evaluation, dict):
        return None
    for key in ("published_by", "created_by", "original_publisher"):
        value = evaluation.get(key)
        if isinstance(value, dict):
            return value
    return None


def _safe_replay_command(payload: dict[str, Any], *, root: Path) -> tuple[str, ...] | ReplayIssue:
    command = str(payload.get("command", "")).strip()
    try:
        parts = tuple(shlex.split(command))
    except ValueError as exc:
        return ReplayIssue("command-parse", f"Cannot parse replay command: {exc}.")

    prefix = next((candidate for candidate in SAFE_RESULT_COMMANDS if parts[: len(candidate)] == candidate), None)
    if prefix is None:
        return ReplayIssue(
            "unsupported-command",
            "Gate B only supports safe physics-lab run commands, not arbitrary shell commands.",
        )
    if any(part in {";", "&&", "||", "|", ">", ">>", "<"} for part in parts):
        return ReplayIssue("unsafe-command", "Replay command contains shell control operators.")

    config_index = len(prefix)
    if len(parts) <= config_index:
        return ReplayIssue("missing-config", "Replay command is missing the workflow config path.")
    config_path = parts[config_index]
    if config_path.startswith("-"):
        return ReplayIssue("missing-config", "Replay command must name a workflow config path.")
    if not (root / config_path).exists():
        return ReplayIssue("config-missing", f"Replay config does not exist: {config_path}.")

    return (sys.executable, "-m", "physics_lab.cli", "run", config_path)


def _replayed_result_path(payload: dict[str, Any], replay_dir: Path) -> Path:
    experiment_id = str(payload.get("experiment_id"))
    run_id = str(payload.get("run_id"))
    return replay_dir / experiment_id / run_id / "result.yaml"


def _compare_results(
    expected: dict[str, Any],
    observed: dict[str, Any],
    *,
    tolerance: float,
) -> tuple[list[ReplayIssue], list[ReplayMetricDelta]]:
    issues: list[ReplayIssue] = []
    for path in STABLE_STRING_PATHS:
        if expected.get(path) != observed.get(path):
            issues.append(
                ReplayIssue(
                    "stable-field-drift",
                    f"{path} changed: expected {expected.get(path)!r}, observed {observed.get(path)!r}.",
                )
            )

    expected_numbers = _flatten_numbers(expected)
    observed_numbers = _flatten_numbers(observed)
    metric_deltas: list[ReplayMetricDelta] = []
    for path, expected_value in sorted(expected_numbers.items()):
        if path not in observed_numbers:
            issues.append(ReplayIssue("metric-missing", f"Replay missing numeric metric {path}."))
            continue
        observed_value = observed_numbers[path]
        delta = abs(expected_value - observed_value)
        metric = ReplayMetricDelta(
            path=path,
            expected=expected_value,
            observed=observed_value,
            abs_delta=delta,
            tolerance=tolerance,
        )
        metric_deltas.append(metric)
        if not metric.ok:
            issues.append(
                ReplayIssue(
                    "metric-drift",
                    f"{path} drifted by {delta:.6g} (tolerance {tolerance:.6g}).",
                )
            )
    return issues, metric_deltas


def _flatten_numbers(value: Any, *, prefix: str = "") -> dict[str, float]:
    if prefix.startswith(SKIPPED_NUMERIC_PATH_PREFIXES):
        return {}
    if isinstance(value, bool):
        return {}
    if isinstance(value, (int, float)):
        return {prefix: float(value)} if prefix else {}
    if isinstance(value, dict):
        output: dict[str, float] = {}
        for key, item in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            output.update(_flatten_numbers(item, prefix=child_prefix))
        return output
    if isinstance(value, list):
        output = {}
        for index, item in enumerate(value):
            child_prefix = f"{prefix}[{index}]" if prefix else f"[{index}]"
            output.update(_flatten_numbers(item, prefix=child_prefix))
        return output
    return {}


def _validation_record(
    payload: dict[str, Any],
    *,
    replayed_by: ReplayIdentity,
    replay_dir: Path,
    tolerance: float,
    metric_deltas: list[ReplayMetricDelta],
) -> dict[str, Any]:
    max_delta = max((metric.abs_delta for metric in metric_deltas), default=0.0)
    return {
        "review_tier_proposed": "AGENT_VALIDATED",
        "best_verdict_proposed": payload.get("best_verdict"),
        "gates_checked": {
            "same_inputs": True,
            "same_deterministic_command": True,
            "metrics_match_within_tolerance": True,
            "verdict_unchanged": True,
            "independent_replay_metadata_recorded": True,
        },
        "evidence_summary": (
            "Independent Gate B replay reproduced the published result metrics "
            "within tolerance and preserved the verdict."
        ),
        "validation_record": {
            "replayed_by": replayed_by.as_dict(),
            "replayed_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "replay_command": str(payload.get("command")),
            "replay_output_dir": str(replay_dir),
            "tolerance_used": tolerance,
            "max_abs_delta": max_delta,
            "metric_count": len(metric_deltas),
            "drift_observed": "none",
        },
    }


def _render_contested_report(
    payload: dict[str, Any],
    *,
    replayed_by: ReplayIdentity,
    issues: tuple[ReplayIssue, ...],
    metric_deltas: list[ReplayMetricDelta],
    replay_dir: Path,
    tolerance: float,
) -> str:
    lines = [
        "# Contested Gate B Replay Report",
        "",
        f"Result: `{payload.get('result_id')}`",
        f"Replay output: `{replay_dir}`",
        f"Tolerance: `{tolerance}`",
        "",
        "## Replayed By",
        "",
        f"- Contributor ID: `{replayed_by.contributor_id}`",
        f"- GitHub username: `{replayed_by.github_username}`",
        f"- Agent tool: `{replayed_by.agent_tool}`",
        f"- Model/version: `{replayed_by.model_version}`",
        "",
        "## Issues",
        "",
    ]
    for issue in issues:
        if issue.severity == "error":
            lines.append(f"- `{issue.code}`: {issue.message}")
    lines.extend(["", "## Largest Metric Deltas", ""])
    for metric in sorted(metric_deltas, key=lambda item: item.abs_delta, reverse=True)[:10]:
        lines.append(
            f"- `{metric.path}`: expected `{metric.expected}`, observed `{metric.observed}`, "
            f"abs delta `{metric.abs_delta}`"
        )
    return "\n".join(lines)


def _blocked_report(
    result_file: Path,
    issues: tuple[ReplayIssue, ...],
    *,
    replay_output_dir: str | None,
) -> ReplayReport:
    return ReplayReport(
        result_path=str(result_file),
        replay_output_dir=replay_output_dir,
        status="BLOCKED",
        issues=issues,
        metric_deltas=(),
        validation_record=None,
        contested_report=None,
    )
