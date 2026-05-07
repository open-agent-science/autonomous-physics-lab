"""Shared artifact helpers for workflow execution."""

from __future__ import annotations

from dataclasses import dataclass
import difflib
import hashlib
from pathlib import Path
import re
import subprocess
from typing import Any

from physics_lab.engines.scoring import ModelScore


TEXT_HASH_SUFFIXES = {
    ".csv",
    ".json",
    ".md",
    ".py",
    ".svg",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class ExperimentArtifacts:
    """Filesystem artifact locations for a workflow run."""

    result_path: Path
    report_path: Path
    metrics_path: Path
    claim_update_path: Path
    claim_update_patch_path: Path
    knowledge_update_path: Path
    knowledge_update_patch_path: Path
    review_summary_path: Path
    review_metadata_path: Path


@dataclass(frozen=True)
class ExperimentOutcome:
    """Structured result of a workflow run."""

    title: str
    result_id: str
    run_id: str
    hypothesis_id: str
    task_id: str
    artifacts: ExperimentArtifacts
    train_range: tuple[float, float] | None = None
    test_range: tuple[float, float] | None = None
    scores: list[ModelScore] | None = None
    verdicts: dict[str, str] | None = None
    best_model_id: str | None = None
    summary_lines: tuple[str, ...] = ()


def resolve_path(base_path: Path, relative_path: str) -> Path:
    """Resolve a possibly relative path from a config or directory."""
    candidate = Path(relative_path)
    if candidate.is_absolute():
        return candidate.resolve()
    base_directory = base_path.parent if base_path.is_file() else base_path
    return (base_directory / candidate).resolve()


def hash_file(path: Path, repo_root: Path) -> dict[str, str]:
    """Return a stable SHA-256 digest payload for a repository input file."""
    payload = path.read_bytes()
    if path.suffix.lower() in TEXT_HASH_SUFFIXES:
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    digest = hashlib.sha256(payload).hexdigest()
    try:
        relative_path = path.resolve().relative_to(repo_root.resolve())
        normalized_path = relative_path.as_posix()
    except ValueError:
        normalized_path = str(path.resolve())
    return {"path": normalized_path, "sha256": digest}


def relative_or_absolute(path: Path, repo_root: Path) -> str:
    """Prefer repository-relative paths when possible."""
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def write_text_atomic(path: Path, content: str) -> None:
    """Write a text file via a temporary path, then replace atomically."""
    temporary_path = path.with_name(f"{path.name}.tmp")
    temporary_path.write_text(content, encoding="utf-8")
    temporary_path.replace(path)


def write_bytes_atomic(path: Path, content: bytes) -> None:
    """Write a binary file via a temporary path, then replace atomically."""
    temporary_path = path.with_name(f"{path.name}.tmp")
    temporary_path.write_bytes(content)
    temporary_path.replace(path)


def git_commit(repo_root: Path) -> str | None:
    """Return the current git commit hash when available."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return result.stdout.strip() or None


def snapshot_input_files(
    *,
    run_dir: Path,
    repo_root: Path,
    input_files: dict[str, Path],
) -> dict[str, dict[str, str]]:
    """Freeze workflow input files inside the run directory and hash the snapshots."""
    snapshots_dir = run_dir / "inputs"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    snapshot_hashes: dict[str, dict[str, str]] = {}
    for artifact_kind, source_path in input_files.items():
        snapshot_path = snapshots_dir / f"{artifact_kind}{source_path.suffix or '.txt'}"
        write_bytes_atomic(snapshot_path, source_path.read_bytes())
        snapshot_hashes[artifact_kind] = hash_file(snapshot_path, repo_root)
    return snapshot_hashes


def task_path(repo_root: Path, task_id: str) -> Path:
    """Locate a task file by task id."""
    matches = sorted((repo_root / "tasks").glob(f"{task_id}-*.yaml"))
    if not matches:
        raise ValueError(f"Unable to locate task file for {task_id}")
    return matches[0]


def find_repo_root(start_path: Path) -> Path:
    """Walk up from a path until pyproject.toml is found."""
    current = start_path.resolve()
    if current.is_file():
        current = current.parent
    for directory in [current, *current.parents]:
        if (directory / "pyproject.toml").exists():
            return directory
    return current


def split_dataset(sample_count: int, train_fraction: float) -> int:
    """Compute a safe train/test split index with at least 2 samples on each side."""
    split_index = int(sample_count * train_fraction)
    return min(max(split_index, 2), sample_count - 1)


def serialize_scores(scores: list[ModelScore], verdicts: dict[str, str]) -> list[dict[str, Any]]:
    """Convert scored models to a repository result payload."""
    return [
        {
            "model_id": score.model_id,
            "formula": score.formula,
            "coefficients": score.coefficients,
            "complexity_score": score.complexity_score,
            "train_metrics": {
                "mean_relative_error": score.train_metrics.mean_relative_error,
                "max_relative_error": score.train_metrics.max_relative_error,
            },
            "test_metrics": {
                "mean_relative_error": score.test_metrics.mean_relative_error,
                "max_relative_error": score.test_metrics.max_relative_error,
            },
            "composite_score": score.composite_score,
            "verdict": verdicts[score.model_id],
        }
        for score in scores
    ]


def best_result_verdict(model_verdict: str) -> str:
    """Promote a model-level VALID verdict to the repository-level range-aware label."""
    if model_verdict == "VALID":
        return "VALID_IN_RANGE"
    return model_verdict


def replace_frontmatter_field(text: str, field_name: str, new_value: str) -> str:
    """Replace a simple scalar field inside YAML front matter."""
    pattern = re.compile(rf"(?m)^({re.escape(field_name)}:\s*).*$")
    updated_text, count = pattern.subn(rf"\1{new_value}", text, count=1)
    if count != 1:
        raise ValueError(f"Unable to replace front matter field: {field_name}")
    return updated_text


def replace_markdown_section(text: str, heading: str, new_body: str) -> str:
    """Replace the body of a markdown `## Heading` section."""
    normalized_body = new_body.strip("\n")
    pattern = re.compile(
        rf"(?ms)(^## {re.escape(heading)}\n\n)(.*?)(?=^## |\Z)"
    )

    def _replace(match: re.Match[str]) -> str:
        return f"{match.group(1)}{normalized_body}\n\n"

    updated_text, count = pattern.subn(_replace, text, count=1)
    if count != 1:
        raise ValueError(f"Unable to replace markdown section: {heading}")
    return updated_text


def render_patch_artifact(
    *,
    title: str,
    target_file: str,
    evidence_basis: list[str],
    original_text: str,
    proposed_text: str,
    proposed_status: str | None = None,
    sections_to_update: list[str] | None = None,
    rationale: str | None = None,
) -> str:
    """Render a maintainer-facing patch artifact with a unified diff."""
    diff_lines = list(
        difflib.unified_diff(
            original_text.splitlines(),
            proposed_text.splitlines(),
            fromfile=target_file,
            tofile=f"{target_file} (proposed)",
            lineterm="",
        )
    )
    diff_text = (
        "\n".join(diff_lines)
        if diff_lines
        else "# No textual diff proposed; the current file already matches this suggested update."
    )
    lines = [
        f"# {title}",
        "",
        "## Target File",
        "",
        f"`{target_file}`",
        "",
    ]
    if proposed_status is not None:
        lines.extend(["## Proposed Status", "", f"`{proposed_status}`", ""])
    if sections_to_update:
        lines.extend(["## Sections To Update", ""])
        lines.extend([f"- `{section}`" for section in sections_to_update])
        lines.append("")
    lines.extend(["## Evidence Basis", ""])
    lines.extend([f"- `{item}`" for item in evidence_basis])
    lines.extend(["", "## Required Human Review", "", "Yes", ""])
    if rationale is not None:
        lines.extend(["## Rationale", "", rationale, ""])
    lines.extend(["## Proposed Diff", "", "```diff", diff_text, "```", ""])
    return "\n".join(lines)


def render_review_metadata(
    *,
    result_id: str,
    run_id: str,
    experiment_id: str,
    claim_id: str,
    knowledge_id: str,
    generated_at: str,
    proposed_claim_status: str,
    evidence_basis: list[str],
    claim_target_file: str,
    knowledge_target_file: str,
    claim_patch_path: str,
    knowledge_patch_path: str,
    review_summary_path: str,
) -> dict[str, Any]:
    """Build a machine-readable review metadata payload for a workflow run.

    The returned dict is intended to be serialised as YAML alongside the
    human-readable patch artifacts.  It captures the structured information that
    a tool or automated reviewer would otherwise have to parse from markdown.
    """
    return {
        "schema_version": "1",
        "artifact_type": "review_metadata",
        "result_id": result_id,
        "run_id": run_id,
        "experiment_id": experiment_id,
        "claim_id": claim_id,
        "knowledge_id": knowledge_id,
        "generated_at": generated_at,
        "proposed_claim_status": proposed_claim_status,
        "required_human_review": True,
        "evidence_basis": list(evidence_basis),
        "claim_target_file": claim_target_file,
        "knowledge_target_file": knowledge_target_file,
        "patch_artifacts": {
            "claim_patch": claim_patch_path,
            "knowledge_patch": knowledge_patch_path,
            "review_summary": review_summary_path,
        },
    }


def render_review_summary(
    *,
    result_id: str,
    claim_id: str,
    knowledge_id: str,
    suggested_status: str,
    rationale: str,
    highlights: list[str],
    limitations: list[str],
) -> str:
    """Render a short maintainer-facing review summary for a canonical run."""
    lines = [
        "# Review Summary",
        "",
        f"- Result: `{result_id}`",
        f"- Claim target: `{claim_id}`",
        f"- Knowledge target: `{knowledge_id}`",
        f"- Suggested claim status if accepted: `{suggested_status}`",
        "",
        "## Why This Artifact Changed",
        "",
        rationale,
        "",
        "## Highlights",
        "",
    ]
    lines.extend([f"- {highlight}" for highlight in highlights])
    lines.extend(["", "## Limitations To Preserve", ""])
    lines.extend([f"- {limitation}" for limitation in limitations])
    lines.extend(
        [
            "",
            "## Required Maintainer Action",
            "",
            "Review the patch artifacts before editing any canonical claim or knowledge file. Do not copy these suggestions blindly into public scientific memory.",
            "",
        ]
    )
    return "\n".join(lines)
