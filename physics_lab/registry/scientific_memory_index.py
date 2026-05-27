"""Render a lightweight review-tier index for scientific memory artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Iterable

import yaml


REVIEW_TIERS = (
    "AGENT_PUBLISHED",
    "AGENT_VALIDATED",
    "MAINTAINER_REVIEWED",
    "EXTERNAL_REPLICATED",
    "LEGACY_UNTIERED",
)

ARTIFACT_CLASSES = ("RESULT", "PRED", "CLAIM", "KNOW")

LEGACY_TIER = "LEGACY_UNTIERED"


@dataclass(frozen=True, order=True)
class MemoryArtifact:
    """One canonical scientific-memory artifact entry."""

    artifact_class: str
    artifact_id: str
    title: str
    review_tier: str
    next_action: str
    path: str
    status: str | None = None


def collect_scientific_memory_artifacts(root: str | Path = ".") -> list[MemoryArtifact]:
    """Collect RESULT, PRED, CLAIM, and KNOW artifacts from the repository."""
    root_path = Path(root)
    artifacts: list[MemoryArtifact] = []
    artifacts.extend(_collect_results(root_path))
    artifacts.extend(_collect_predictions(root_path))
    artifacts.extend(_collect_claims(root_path))
    artifacts.extend(_collect_knowledge(root_path))
    return sorted(artifacts, key=lambda item: (item.review_tier, item.artifact_class, item.artifact_id, item.path))


def render_scientific_memory_index(root: str | Path = ".") -> str:
    """Render the review-tier index as Markdown."""
    root_path = Path(root)
    artifacts = collect_scientific_memory_artifacts(root_path)

    lines = [
        "# Scientific Memory Review Tiers",
        "",
        "> Generated from canonical scientific-memory artifacts. Refresh with",
        "> `python3 scripts/apl_scientific_memory_index.py --write`.",
        "",
        "This index separates publication and review tiers so `AGENT_PUBLISHED`",
        "evidence is not mistaken for maintainer-endorsed claims. It is a",
        "visibility layer only: it does not promote, re-tier, or edit canonical",
        "scientific artifacts.",
        "",
        "## Tier Meaning",
        "",
        "| Tier | Meaning | Default next action |",
        "| --- | --- | --- |",
        "| `AGENT_PUBLISHED` | Agent-created canonical evidence after Gate A. | Independent replay or maintainer review, depending on artifact class. |",
        "| `AGENT_VALIDATED` | A different agent reproduced the artifact through Gate B. | Maintainer review before stronger interpretation. |",
        "| `MAINTAINER_REVIEWED` | Maintainer endorsed the artifact tier/scope. | External replication or monitored reveal when relevant. |",
        "| `EXTERNAL_REPLICATED` | External source, contributor, or reveal independently replicated the artifact. | Preserve as strongest public memory. |",
        "| `LEGACY_UNTIERED` | Artifact predates the review-tier protocol. | Do not infer endorsement; triage only when a new promotion task asks for it. |",
        "",
        "## Counts",
        "",
    ]

    lines.extend(_render_counts(artifacts))
    lines.append("")

    for tier in REVIEW_TIERS:
        tier_artifacts = [artifact for artifact in artifacts if artifact.review_tier == tier]
        lines.append(f"## {tier}")
        lines.append("")
        if not tier_artifacts:
            lines.append("_No artifacts in this tier._")
            lines.append("")
            continue
        lines.extend(_render_artifact_table(tier_artifacts))
        lines.append("")

    lines.extend(
        [
            "## Notes",
            "",
            "- Missing `review_tier` fields are displayed as `LEGACY_UNTIERED` for",
            "  visibility only; this task intentionally leaves canonical artifacts",
            "  unchanged.",
            "- `PRED` entries often need reveal or source-state review rather than Gate B",
            "  replay.",
            "- `CLAIM` and `KNOW` artifacts remain maintainer-sensitive in Phase 1 even",
            "  when a future agent creates draft supporting material.",
            "",
        ]
    )
    return "\n".join(lines)


def write_scientific_memory_index(
    root: str | Path = ".",
    output_path: str | Path = "docs/scientific-memory-review-tiers.md",
) -> Path:
    """Write the rendered index and return its path."""
    root_path = Path(root)
    destination = Path(output_path)
    if not destination.is_absolute():
        destination = root_path / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_scientific_memory_index(root_path), encoding="utf-8")
    return destination


def _collect_results(root: Path) -> list[MemoryArtifact]:
    artifacts: list[MemoryArtifact] = []
    for path in sorted((root / "results").glob("EXP-*/RUN-*/result.yaml")):
        payload = _load_yaml(path)
        if not isinstance(payload, dict):
            continue
        artifact_id = _string(payload.get("result_id")) or path.parent.name
        artifacts.append(
            MemoryArtifact(
                artifact_class="RESULT",
                artifact_id=artifact_id,
                title=_string(payload.get("title")) or _string(payload.get("experiment_id")) or artifact_id,
                review_tier=_review_tier(payload),
                next_action=_next_action("RESULT", _review_tier(payload)),
                path=_relative(path, root),
                status=_string(payload.get("best_verdict")),
            )
        )
    return artifacts


def _collect_predictions(root: Path) -> list[MemoryArtifact]:
    artifacts: list[MemoryArtifact] = []
    registry_root = root / "prediction_registry"
    if not registry_root.exists():
        return artifacts
    for path in sorted(registry_root.rglob("PRED-*.yaml")):
        if "TEMPLATE" in path.name:
            continue
        payload = _load_yaml(path)
        if not isinstance(payload, dict):
            continue
        artifact_id = _string(payload.get("prediction_id")) or path.stem
        artifacts.append(
            MemoryArtifact(
                artifact_class="PRED",
                artifact_id=artifact_id,
                title=_string(payload.get("title")) or artifact_id,
                review_tier=_review_tier(payload),
                next_action=_next_action("PRED", _review_tier(payload)),
                path=_relative(path, root),
                status=_string(payload.get("registry_status")),
            )
        )
    return artifacts


def _collect_claims(root: Path) -> list[MemoryArtifact]:
    artifacts: list[MemoryArtifact] = []
    for path in sorted((root / "claims").glob("CLAIM-*.md")):
        payload = _load_front_matter(path)
        artifact_id = _string(payload.get("id")) or path.stem
        artifacts.append(
            MemoryArtifact(
                artifact_class="CLAIM",
                artifact_id=artifact_id,
                title=_string(payload.get("title")) or artifact_id,
                review_tier=_review_tier(payload),
                next_action=_next_action("CLAIM", _review_tier(payload)),
                path=_relative(path, root),
                status=_string(payload.get("status")),
            )
        )
    return artifacts


def _collect_knowledge(root: Path) -> list[MemoryArtifact]:
    artifacts: list[MemoryArtifact] = []
    knowledge_root = root / "knowledge"
    if not knowledge_root.exists():
        return artifacts
    for path in sorted(knowledge_root.rglob("*")):
        if path.is_dir() or path.name.startswith("."):
            continue
        if path.suffix not in {".md", ".yaml", ".yml"}:
            continue
        payload = _load_front_matter(path) if path.suffix == ".md" else _load_yaml(path)
        if not isinstance(payload, dict):
            continue
        artifact_id = _string(payload.get("id"))
        if not artifact_id or not artifact_id.startswith(("KNOW-", "KN-")):
            continue
        artifacts.append(
            MemoryArtifact(
                artifact_class="KNOW",
                artifact_id=artifact_id,
                title=_string(payload.get("title")) or _string(payload.get("topic")) or artifact_id,
                review_tier=_review_tier(payload),
                next_action=_next_action("KNOW", _review_tier(payload)),
                path=_relative(path, root),
                status=_string(payload.get("status")),
            )
        )
    return artifacts


def _render_counts(artifacts: list[MemoryArtifact]) -> list[str]:
    lines = [
        "| Tier | RESULT | PRED | CLAIM | KNOW | Total |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for tier in REVIEW_TIERS:
        row = [artifact for artifact in artifacts if artifact.review_tier == tier]
        counts = {
            artifact_class: sum(1 for artifact in row if artifact.artifact_class == artifact_class)
            for artifact_class in ARTIFACT_CLASSES
        }
        total = sum(counts.values())
        lines.append(
            f"| `{tier}` | {counts['RESULT']} | {counts['PRED']} | {counts['CLAIM']} | {counts['KNOW']} | {total} |"
        )
    return lines


def _render_artifact_table(artifacts: Iterable[MemoryArtifact]) -> list[str]:
    lines = [
        "| Class | Artifact | Status | Next action | Path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for artifact in artifacts:
        status = artifact.status or "n/a"
        title = _escape_markdown(artifact.title)
        lines.append(
            f"| `{artifact.artifact_class}` | `{artifact.artifact_id}` - {title} | `{status}` | `{artifact.next_action}` | [`{artifact.path}`](../{artifact.path}) |"
        )
    return lines


def _next_action(artifact_class: str, review_tier: str) -> str:
    if review_tier == "AGENT_PUBLISHED":
        if artifact_class == "RESULT":
            return "replay-needed"
        if artifact_class == "PRED":
            return "reveal-needed"
        return "maintainer-review-needed"
    if review_tier == "AGENT_VALIDATED":
        return "maintainer-review-needed"
    if review_tier == "MAINTAINER_REVIEWED":
        if artifact_class == "PRED":
            return "external-reveal-needed"
        return "external-replication-optional"
    if review_tier == "EXTERNAL_REPLICATED":
        return "preserve"
    return "legacy-triage-only"


def _review_tier(payload: dict[str, Any]) -> str:
    value = _string(payload.get("review_tier"))
    if value in REVIEW_TIERS and value != LEGACY_TIER:
        return value
    return LEGACY_TIER


def _load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None


def _load_front_matter(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return {}
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return {}
    payload = yaml.safe_load(match.group(1))
    return payload if isinstance(payload, dict) else {}


def _relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _string(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _escape_markdown(value: str) -> str:
    return value.replace("|", "\\|")
