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
)

ARTIFACT_CLASSES = ("RESULT", "PRED", "CLAIM", "KNOW")

# Not a trust tier: canonical artifacts that predate the review-tier protocol
# carry no review_tier and are reported outside the ladder, preserved and
# discoverable but never presented as reviewed or endorsed.
HISTORICAL_CLASSIFICATION = "PRE_TIER_PROTOCOL"

INDEX_OUTPUT_PATH = "docs/scientific-memory-review-tiers.md"
HISTORICAL_LEDGER_OUTPUT_PATH = "docs/historical-scientific-memory.md"


@dataclass(frozen=True)
class MemoryArtifact:
    """One canonical scientific-memory artifact entry."""

    artifact_class: str
    artifact_id: str
    title: str
    review_tier: str | None
    next_action: str
    path: str
    status: str | None = None
    validation_independence: str | None = None
    historical_classification: str | None = None

    @property
    def is_historical(self) -> bool:
        return self.review_tier is None


def collect_scientific_memory_artifacts(root: str | Path = ".") -> list[MemoryArtifact]:
    """Collect RESULT, PRED, CLAIM, and KNOW artifacts from the repository."""
    root_path = Path(root)
    artifacts: list[MemoryArtifact] = []
    artifacts.extend(_collect_results(root_path))
    artifacts.extend(_collect_predictions(root_path))
    artifacts.extend(_collect_claims(root_path))
    artifacts.extend(_collect_knowledge(root_path))
    def _sort_key(item: MemoryArtifact) -> tuple[int, str, str, str]:
        rank = (
            REVIEW_TIERS.index(item.review_tier)
            if item.review_tier in REVIEW_TIERS
            else len(REVIEW_TIERS)
        )
        return (rank, item.artifact_class, item.artifact_id, item.path)

    return sorted(artifacts, key=_sort_key)


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

    lines.extend(_render_historical_summary(artifacts))

    lines.extend(
        [
            "## Notes",
            "",
            "- Historical pre-tier artifacts (missing `review_tier`) are summarized",
            "  above and listed in the historical ledger only; they are not part of",
            "  the trust ladder, and their canonical files stay unchanged.",
            "- `PRED` entries often need reveal or source-state review rather than Gate B",
            "  replay.",
            "- `CLAIM` and `KNOW` artifacts remain maintainer-sensitive in Phase 1 even",
            "  when a future agent creates draft supporting material.",
            "- `Independence` is a separate axis from the tier: `AGENT_VALIDATED`",
            "  means replayed; the independence value records who replayed relative",
            "  to the publisher (see docs/result-promotion-protocol.md, Validation",
            "  Independence). `not_recorded` marks replays that predate the axis.",
            "",
        ]
    )
    return "\n".join(lines)


def render_historical_scientific_memory_ledger(root: str | Path = ".") -> str:
    """Render the full pre-tier historical ledger as Markdown."""
    root_path = Path(root)
    historical = [
        artifact
        for artifact in collect_scientific_memory_artifacts(root_path)
        if artifact.is_historical
    ]

    lines = [
        "# Historical Scientific Memory (Pre-Tier Ledger)",
        "",
        "> Generated from canonical scientific-memory artifacts. Refresh with",
        "> `python3 scripts/apl_scientific_memory_index.py --write`.",
        "",
        f"These {len(historical)} canonical artifacts predate the explicit",
        "review-tier protocol. They are preserved and discoverable here, but they",
        "sit outside the review-trust ladder in",
        "[`docs/scientific-memory-review-tiers.md`](scientific-memory-review-tiers.md)",
        "and must not be read as reviewed or endorsed. A historical artifact",
        "enters the ladder only through a dedicated review or replay PR that",
        "assigns an explicit `review_tier`; do not backfill tiers in bulk.",
        "",
        "## Counts",
        "",
    ]
    lines.extend(_render_class_counts(historical))
    lines.extend(["", "## Artifacts", ""])
    if historical:
        lines.extend(
            [
                "| Class | Artifact | Status | Path |",
                "| --- | --- | --- | --- |",
            ]
        )
        for artifact in historical:
            status = artifact.status or "n/a"
            title = _escape_markdown(artifact.title)
            lines.append(
                f"| `{artifact.artifact_class}` | `{artifact.artifact_id}` - {title} | `{status}` | [`{artifact.path}`](../{artifact.path}) |"
            )
    else:
        lines.append("_No historical pre-tier artifacts._")
    lines.append("")
    return "\n".join(lines)


def write_scientific_memory_index(
    root: str | Path = ".",
    output_path: str | Path = INDEX_OUTPUT_PATH,
) -> Path:
    """Write the rendered index and return its path."""
    return _write_surface(root, output_path, render_scientific_memory_index)


def write_historical_scientific_memory_ledger(
    root: str | Path = ".",
    output_path: str | Path = HISTORICAL_LEDGER_OUTPUT_PATH,
) -> Path:
    """Write the rendered historical ledger and return its path."""
    return _write_surface(root, output_path, render_historical_scientific_memory_ledger)


def write_scientific_memory_surfaces(root: str | Path = ".") -> list[Path]:
    """Write every generated scientific-memory surface and return the paths."""
    return [
        write_scientific_memory_index(root),
        write_historical_scientific_memory_ledger(root),
    ]


# Generated public surfaces covered by `--write` and `--check`.
GENERATED_SURFACES = {
    INDEX_OUTPUT_PATH: render_scientific_memory_index,
    HISTORICAL_LEDGER_OUTPUT_PATH: render_historical_scientific_memory_ledger,
}


def _write_surface(root: str | Path, output_path: str | Path, render) -> Path:
    root_path = Path(root)
    destination = Path(output_path)
    if not destination.is_absolute():
        destination = root_path / destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render(root_path), encoding="utf-8")
    return destination


def _collect_results(root: Path) -> list[MemoryArtifact]:
    artifacts: list[MemoryArtifact] = []
    for path in sorted((root / "results").glob("EXP-*/RUN-*/result.yaml")):
        payload = _load_yaml(path)
        if not isinstance(payload, dict):
            continue
        artifact_id = _string(payload.get("result_id")) or path.parent.name
        tier = _review_tier(payload)
        artifacts.append(
            MemoryArtifact(
                artifact_class="RESULT",
                artifact_id=artifact_id,
                title=_string(payload.get("title")) or _string(payload.get("experiment_id")) or artifact_id,
                review_tier=tier,
                next_action=_next_action("RESULT", tier),
                path=_relative(path, root),
                status=_string(payload.get("best_verdict")),
                validation_independence=_validation_independence(payload),
                historical_classification=None if tier else HISTORICAL_CLASSIFICATION,
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
        tier = _review_tier(payload)
        artifacts.append(
            MemoryArtifact(
                artifact_class="PRED",
                artifact_id=artifact_id,
                title=_string(payload.get("title")) or artifact_id,
                review_tier=tier,
                next_action=_next_action("PRED", tier),
                path=_relative(path, root),
                status=_string(payload.get("registry_status")),
                historical_classification=None if tier else HISTORICAL_CLASSIFICATION,
            )
        )
    return artifacts


def _collect_claims(root: Path) -> list[MemoryArtifact]:
    artifacts: list[MemoryArtifact] = []
    for path in sorted((root / "claims").glob("CLAIM-*.md")):
        payload = _load_front_matter(path)
        artifact_id = _string(payload.get("id")) or path.stem
        tier = _review_tier(payload)
        artifacts.append(
            MemoryArtifact(
                artifact_class="CLAIM",
                artifact_id=artifact_id,
                title=_string(payload.get("title")) or artifact_id,
                review_tier=tier,
                next_action=_next_action("CLAIM", tier),
                path=_relative(path, root),
                status=_string(payload.get("status")),
                historical_classification=None if tier else HISTORICAL_CLASSIFICATION,
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
        tier = _review_tier(payload)
        artifacts.append(
            MemoryArtifact(
                artifact_class="KNOW",
                artifact_id=artifact_id,
                title=_string(payload.get("title")) or _string(payload.get("topic")) or artifact_id,
                review_tier=tier,
                next_action=_next_action("KNOW", tier),
                path=_relative(path, root),
                status=_string(payload.get("status")),
                historical_classification=None if tier else HISTORICAL_CLASSIFICATION,
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


def _render_historical_summary(artifacts: list[MemoryArtifact]) -> list[str]:
    historical = [artifact for artifact in artifacts if artifact.is_historical]
    lines = [
        "## Historical Pre-Tier Artifacts",
        "",
    ]
    if not historical:
        lines.extend(["_No historical pre-tier artifacts._", ""])
        return lines
    lines.extend(
        [
            f"{len(historical)} canonical artifacts predate the explicit review-tier",
            "protocol. They are preserved and discoverable, but they sit outside the",
            "review-trust ladder above and must not be read as reviewed or endorsed.",
            "",
        ]
    )
    lines.extend(_render_class_counts(historical))
    lines.extend(
        [
            "",
            "Full list: [`docs/historical-scientific-memory.md`](historical-scientific-memory.md).",
            "",
        ]
    )
    return lines


def _render_class_counts(artifacts: list[MemoryArtifact]) -> list[str]:
    lines = [
        "| Class | Count |",
        "| --- | ---: |",
    ]
    for artifact_class in ARTIFACT_CLASSES:
        count = sum(1 for artifact in artifacts if artifact.artifact_class == artifact_class)
        lines.append(f"| `{artifact_class}` | {count} |")
    lines.append(f"| Total | {len(artifacts)} |")
    return lines


def _render_artifact_table(artifacts: Iterable[MemoryArtifact]) -> list[str]:
    lines = [
        "| Class | Artifact | Status | Independence | Next action | Path |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for artifact in artifacts:
        status = artifact.status or "n/a"
        independence = artifact.validation_independence or "n/a"
        title = _escape_markdown(artifact.title)
        lines.append(
            f"| `{artifact.artifact_class}` | `{artifact.artifact_id}` - {title} | `{status}` | `{independence}` | `{artifact.next_action}` | [`{artifact.path}`](../{artifact.path}) |"
        )
    return lines


def _next_action(artifact_class: str, review_tier: str | None) -> str:
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


def _validation_independence(payload: dict[str, Any]) -> str | None:
    """Independence of the recorded replay; separate axis from the tier."""
    tier = _string(payload.get("review_tier"))
    ape = payload.get("agent_proposal_evaluation")
    record = ape.get("validation_record") if isinstance(ape, dict) else None
    value = _string(record.get("validation_independence")) if isinstance(record, dict) else None
    if value:
        return value
    if tier in ("AGENT_VALIDATED", "MAINTAINER_REVIEWED", "EXTERNAL_REPLICATED"):
        return "not_recorded"
    return None


def _review_tier(payload: dict[str, Any]) -> str | None:
    """Return one of REVIEW_TIERS, or None for historical pre-tier artifacts."""
    value = _string(payload.get("review_tier"))
    if value in REVIEW_TIERS:
        return value
    return None


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
