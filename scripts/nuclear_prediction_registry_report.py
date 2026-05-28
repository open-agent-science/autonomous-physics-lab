"""Build a reveal-readiness summary for the nuclear prediction registry.

This helper only inspects committed registry metadata. It does not fetch live
measurement sources, compare predictions, score targets, or alter frozen
prediction entries.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


ACTUAL_PREDICTION_RE = re.compile(r"^PRED-(\d{4})$")
DEFAULT_REGISTRY_DIR = Path("prediction_registry") / "nuclear_masses"
DEFAULT_OUTPUT_PATH = DEFAULT_REGISTRY_DIR / "registry_summary.yaml"
REVEAL_PROTOCOL_PATH = "docs/nuclear-prediction-reveal-protocol.md"
SOURCE_CHECKLIST_PATH = "docs/nuclear-reveal-source-readiness-checklist.md"


def build_registry_summary(
    repo_root: Path,
    registry_dir: Path | None = None,
) -> dict[str, Any]:
    """Return deterministic registry count and reveal-readiness metadata."""
    root = repo_root.resolve()
    resolved_registry = _resolve_registry_dir(root, registry_dir)
    entries, template_count = load_registry_entries(resolved_registry)
    prediction_ids = [entry["prediction_id"] for entry in entries]
    target_rows = [
        target
        for entry in entries
        for target in entry.get("target_set", {}).get("target_nuclides", [])
    ]

    source_task_counts: Counter[str] = Counter(str(entry.get("task_id", "UNKNOWN")) for entry in entries)
    target_batch_counts: Counter[str] = Counter(
        str(entry.get("target_set", {}).get("label", "UNKNOWN")) for entry in entries
    )
    model_family_counts: Counter[str] = Counter(_model_family(entry) for entry in entries)

    reveal_rows = [_reveal_row(entry) for entry in entries]
    reveal_state_counts: Counter[str] = Counter(row["reveal_state"] for row in reveal_rows)
    blocker_counts: Counter[str] = Counter(
        blocker for row in reveal_rows for blocker in row["blockers"]
    )
    blocked_rows = [row for row in reveal_rows if row["blockers"]]
    ready_rows = [
        row
        for row in reveal_rows
        if row["reveal_state"] == "READY_FOR_REVEAL_REVIEW" and not row["blockers"]
    ]
    awaiting_source_rows = [
        row
        for row in reveal_rows
        if row["reveal_state"] == "AWAITING_SOURCE_PREFLIGHT"
    ]

    return {
        "task_id": "TASK-0381",
        "summary_scope": {
            "registry_path": _repo_relative(root, resolved_registry),
            "generated_by": "scripts/nuclear_prediction_registry_report.py",
            "live_external_fetch_performed": False,
            "scoring_performed": False,
            "frozen_prediction_values_modified": False,
        },
        "highest_pred_id": prediction_ids[-1] if prediction_ids else None,
        "actual_entry_count": len(entries),
        "template_count": template_count,
        "blocked_reveal_count": len(blocked_rows),
        "ready_for_reveal_count": len(ready_rows),
        "awaiting_source_count": len(awaiting_source_rows),
        "target_row_count": len(target_rows),
        "id_gaps": _id_gaps(prediction_ids),
        "source_task_counts": _counter_items(source_task_counts),
        "target_batch_counts": _counter_items(target_batch_counts),
        "model_family_counts": _counter_items(model_family_counts),
        "reveal_state_counts": _counter_items(reveal_state_counts),
        "blocker_counts": _counter_items(blocker_counts),
        "entries_must_not_be_scored_before_reveal_gate": reveal_rows,
        "wording_boundary": [
            "Registry volume is bookkeeping, not scientific success.",
            "No entry is reveal-ready until source preflight, no-peek review, and maintainer approval pass.",
            "This summary performs no live source fetch, prediction scoring, reveal, or claim promotion.",
        ],
    }


def load_registry_entries(registry_dir: Path) -> tuple[list[dict[str, Any]], int]:
    """Load actual PRED entries and count templates without treating them as entries."""
    entries: list[dict[str, Any]] = []
    template_count = 0
    for path in sorted(registry_dir.glob("PRED*.yaml")):
        payload = _load_yaml(path)
        prediction_id = str(payload.get("prediction_id", ""))
        if path.name == "PRED-TEMPLATE.yaml" or not ACTUAL_PREDICTION_RE.fullmatch(prediction_id):
            template_count += 1
            continue
        entries.append(payload)
    entries.sort(key=lambda entry: entry["prediction_id"])
    return entries, template_count


def write_registry_summary(
    repo_root: Path,
    output_path: Path = DEFAULT_OUTPUT_PATH,
    registry_dir: Path | None = None,
) -> dict[str, Any]:
    """Write the summary YAML and return the payload."""
    root = repo_root.resolve()
    summary = build_registry_summary(root, registry_dir=registry_dir)
    resolved_output = output_path if output_path.is_absolute() else root / output_path
    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    resolved_output.write_text(
        yaml.safe_dump(summary, sort_keys=False, allow_unicode=False, width=100),
        encoding="utf-8",
    )
    return summary


def _resolve_registry_dir(root: Path, registry_dir: Path | None) -> Path:
    if registry_dir is None:
        return root / DEFAULT_REGISTRY_DIR
    return registry_dir if registry_dir.is_absolute() else root / registry_dir


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping YAML in {path}")
    return payload


def _reveal_row(entry: dict[str, Any]) -> dict[str, Any]:
    blockers = _reveal_blockers(entry)
    return {
        "prediction_id": entry["prediction_id"],
        "task_id": entry.get("task_id", "UNKNOWN"),
        "target_batch": entry.get("target_set", {}).get("label", "UNKNOWN"),
        "model_family": _model_family(entry),
        "target_row_count": len(entry.get("target_set", {}).get("target_nuclides", [])),
        "reveal_state": "AWAITING_SOURCE_PREFLIGHT"
        if blockers
        else "READY_FOR_REVEAL_REVIEW",
        "blockers": blockers,
    }


def _reveal_blockers(entry: dict[str, Any]) -> list[str]:
    blockers = [
        "SOURCE_PREFLIGHT_REQUIRED",
        "NO_PEEK_REVIEW_REQUIRED",
        "MAINTAINER_APPROVAL_REQUIRED",
    ]
    source_state = entry.get("source_state", {})
    holdout_refs = set(source_state.get("holdout_protocol_references", []))
    if REVEAL_PROTOCOL_PATH not in holdout_refs:
        blockers.append("REVEAL_PROTOCOL_REFERENCE_MISSING")
    if SOURCE_CHECKLIST_PATH not in holdout_refs:
        blockers.append("SOURCE_READINESS_CHECKLIST_REFERENCE_MISSING")
    if source_state.get("live_external_fetch_allowed") is not False:
        blockers.append("LIVE_EXTERNAL_FETCH_FLAG_NOT_FALSE")
    return blockers


def _model_family(entry: dict[str, Any]) -> str:
    task_id = str(entry.get("task_id", ""))
    target_label = str(entry.get("target_set", {}).get("label", "")).lower()
    model_reference = entry.get("source_state", {}).get("model_reference", {})
    model_id = str(model_reference.get("model_id", "")).lower()
    frozen_note = str(model_reference.get("frozen_parameters_note", "")).lower()
    lane_text = f"{task_id.lower()} {target_label} {model_id}"

    if "shell-axis" in lane_text:
        return "shell_axis"
    if task_id == "TASK-0265" or "feature terms frozen" in frozen_note:
        return "feature_term_selected"
    if task_id == "TASK-0251" or "blend-with-reference" in model_id:
        return "factory_coefficient_transform"
    if "pairing" in model_id or "odd-even" in target_label:
        return "pairing_or_odd_even"
    if "neutron-excess" in model_id or "asymmetry" in model_id or "asymmetry" in target_label:
        return "neutron_excess_or_asymmetry"
    if "shell" in model_id or "magic" in target_label:
        return "shell_or_magic_control"
    if "reference" in model_id or "blend" in model_id or "volume" in model_id:
        return "smooth_or_reference_control"
    return "baseline_or_manual_control"


def _counter_items(counter: Counter[str]) -> list[dict[str, Any]]:
    return [
        {"label": label, "count": count}
        for label, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def _id_gaps(prediction_ids: list[str]) -> list[str]:
    if not prediction_ids:
        return []
    observed = {int(prediction_id.split("-")[1]) for prediction_id in prediction_ids}
    highest = max(observed)
    return [f"PRED-{idx:04d}" for idx in range(1, highest + 1) if idx not in observed]


def _repo_relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write a deterministic nuclear prediction reveal-readiness summary.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--registry-dir", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    summary = write_registry_summary(
        args.repo_root,
        output_path=args.output,
        registry_dir=args.registry_dir,
    )
    print(
        "Wrote registry summary: "
        f"{args.output} "
        f"({summary['actual_entry_count']} entries, "
        f"{summary['ready_for_reveal_count']} reveal-ready)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
