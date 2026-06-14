"""Metadata-only acquisition queue helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import yaml


DEFAULT_QUEUE_PATH = Path("data/acquisition_queue.yaml")

ALLOWED_ACCESS_CLASSES = {
    "public_keyfree",
    "key_gated",
    "manual_artifact",
    "restricted_or_unknown",
}
ALLOWED_STATUSES = {
    "ready_for_maintainer_action",
    "ready_for_separate_acquisition_task",
    "waiting_on_upstream_task",
    "blocked",
}
READY_STATUSES = {
    "ready_for_maintainer_action",
    "ready_for_separate_acquisition_task",
}
REPORT_ONLY_FALSE_POLICY_FIELDS = (
    "live_fetch_allowed",
    "secrets_read_allowed",
    "local_artifacts_read_allowed",
    "benchmark_input_allowed",
    "value_bearing_rows_allowed",
    "artifact_bytes_allowed",
)
REQUIRED_ENTRY_FIELDS = (
    "entry_id",
    "source_id",
    "title",
    "campaign_id",
    "domain",
    "status",
    "access_class",
    "blocker_type",
    "source_locator",
    "license_readiness",
    "checksum_policy",
    "downstream_task",
    "maintainer_action",
    "local_artifact_expectation",
    "agent_local_work_allowed",
    "forbidden_actions",
    "evidence",
)
FORBIDDEN_FIELD_NAME_PARTS = (
    "secret_value",
    "token_value",
    "cookie_value",
    "password",
    "raw_rows",
    "measurement_values",
    "value_bearing_rows",
    "benchmark_inputs",
    "source_bytes",
    "pdf_bytes",
    "table_values",
)
FORBIDDEN_LOCAL_PATH_PREFIXES = (
    "/Users/",
    "/home/",
    "C:\\",
    "C:/",
)


def load_acquisition_queue(path: Path = DEFAULT_QUEUE_PATH) -> dict[str, Any]:
    """Load a metadata-only acquisition queue YAML file."""
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Acquisition queue must be a YAML mapping: {path}")
    return payload


def acquisition_queue_errors(payload: Mapping[str, Any]) -> tuple[str, ...]:
    """Return schema and no-fetch/no-secret policy errors for a queue payload."""
    errors: list[str] = []
    policy = payload.get("policy")
    if not isinstance(policy, Mapping):
        errors.append("policy must be a mapping.")
    else:
        if policy.get("mode") != "report_only_no_fetch":
            errors.append("policy.mode must be report_only_no_fetch.")
        for field in REPORT_ONLY_FALSE_POLICY_FIELDS:
            if policy.get(field) is not False:
                errors.append(f"policy.{field} must be false.")

    entries = payload.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("entries must be a non-empty list.")
        entries = []

    for index, entry in enumerate(entries):
        entry_label = _entry_label(entry, index)
        if not isinstance(entry, Mapping):
            errors.append(f"{entry_label} must be a mapping.")
            continue
        missing = [field for field in REQUIRED_ENTRY_FIELDS if field not in entry]
        if missing:
            errors.append(f"{entry_label} missing required fields: {', '.join(missing)}.")
        status = entry.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(
                f"{entry_label} status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}."
            )
        access_class = entry.get("access_class")
        if access_class not in ALLOWED_ACCESS_CLASSES:
            errors.append(
                f"{entry_label} access_class must be one of: "
                + ", ".join(sorted(ALLOWED_ACCESS_CLASSES))
                + "."
            )
        if access_class == "key_gated" and not str(entry.get("local_secret_name") or "").strip():
            errors.append(f"{entry_label} key_gated entries must name local_secret_name.")
        if access_class == "manual_artifact" and not str(
            entry.get("local_artifact_expectation") or ""
        ).strip():
            errors.append(f"{entry_label} manual_artifact entries need local_artifact_expectation.")
        for field in ("forbidden_actions", "evidence"):
            values = entry.get(field)
            if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
                errors.append(f"{entry_label} {field} must be a list of strings.")

    errors.extend(_metadata_only_errors(payload))
    return tuple(dict.fromkeys(errors))


def render_acquisition_queue_report(
    payload: Mapping[str, Any],
    *,
    queue_path: Path = DEFAULT_QUEUE_PATH,
) -> str:
    """Render a human-readable dry-run report without acquiring any source."""
    errors = acquisition_queue_errors(payload)
    if errors:
        error_lines = ["Acquisition queue is invalid:", *[f"- {error}" for error in errors]]
        return "\n".join(error_lines) + "\n"

    entries = _entries(payload)
    ready_entries = [entry for entry in entries if entry["status"] in READY_STATUSES]
    waiting_entries = [entry for entry in entries if entry["status"] not in READY_STATUSES]
    policy = payload["policy"]

    lines = [
        "Acquisition queue dry-run report",
        f"Queue: {queue_path.as_posix()}",
        f"Mode: {policy['mode']}",
        "Fetches: disabled",
        "Secrets: names may be listed; values are never read",
        "",
        "Ready for maintainer action:",
    ]
    lines.extend(_render_entry_lines(ready_entries))
    lines.extend(["", "Blocked or waiting:"])
    lines.extend(_render_entry_lines(waiting_entries))
    lines.extend(
        [
            "",
            "This report is metadata-only: it did not fetch sources, read local",
            "artifacts, read secret values, create rows, or create benchmark inputs.",
        ]
    )
    return "\n".join(lines) + "\n"


def _render_entry_lines(entries: Iterable[Mapping[str, Any]]) -> list[str]:
    rendered: list[str] = []
    entries = tuple(entries)
    if not entries:
        return ["- none"]
    for entry in entries:
        blocked_by = entry.get("blocked_by") or []
        blocked_text = ""
        if isinstance(blocked_by, list) and blocked_by:
            blocked_text = " blocked_by=" + ",".join(str(item) for item in blocked_by)
        rendered.extend(
            [
                (
                    f"- {entry['entry_id']} {entry['source_id']} "
                    f"[{entry['access_class']}; {entry['status']}; "
                    f"downstream={entry['downstream_task']}{blocked_text}]"
                ),
                f"  Action: {_inline(entry['maintainer_action'])}",
                f"  Agent local work: {_inline(entry['agent_local_work_allowed'])}",
            ]
        )
    return rendered


def _inline(value: Any) -> str:
    return " ".join(str(value).split())


def _metadata_only_errors(payload: Any) -> tuple[str, ...]:
    errors: list[str] = []
    for path, value in _walk_payload(payload):
        key = path[-1] if path else "<root>"
        key_lower = str(key).lower()
        is_false_policy_field = len(path) == 2 and path[0] == "policy" and key in (
            *REPORT_ONLY_FALSE_POLICY_FIELDS,
        )
        if not is_false_policy_field and any(part in key_lower for part in FORBIDDEN_FIELD_NAME_PARTS):
            errors.append(f"metadata-only queue must not include field {'.'.join(path)}.")
        if isinstance(value, str):
            stripped = value.strip()
            if any(stripped.startswith(prefix) for prefix in FORBIDDEN_LOCAL_PATH_PREFIXES):
                errors.append(
                    f"metadata-only queue must not record machine-local path at {'.'.join(path)}."
                )
    return tuple(errors)


def _walk_payload(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            child_path = (*path, str(key))
            yield child_path, child
            yield from _walk_payload(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = (*path, str(index))
            yield child_path, child
            yield from _walk_payload(child, child_path)


def _entries(payload: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    entries = payload.get("entries", ())
    if not isinstance(entries, list):
        return ()
    return tuple(entry for entry in entries if isinstance(entry, Mapping))


def _entry_label(entry: Any, index: int) -> str:
    if isinstance(entry, Mapping):
        entry_id = str(entry.get("entry_id") or "").strip()
        if entry_id:
            return entry_id
    return f"entries[{index}]"
