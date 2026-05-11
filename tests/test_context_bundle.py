from __future__ import annotations

from pathlib import Path

from scripts.generate_context_bundle import (
    differs_only_by_generated_timestamp,
    normalize_generated_timestamp,
    write_bundle_if_changed,
)


def test_normalize_generated_timestamp_masks_only_generated_line() -> None:
    bundle = "\n".join(
        [
            "# Autonomous Physics Lab — Context Bundle",
            "",
            "Generated: 2026-05-11 10:44 UTC",
            "Mode: core",
            "Generated timestamps in prose should remain untouched.",
        ]
    )

    normalized = normalize_generated_timestamp(bundle)

    assert "Generated: <timestamp>" in normalized
    assert "Generated timestamps in prose should remain untouched." in normalized


def test_differs_only_by_generated_timestamp_detects_timestamp_drift() -> None:
    existing = "# Bundle\n\nGenerated: 2026-05-11 10:44 UTC\nMode: core\n"
    candidate = "# Bundle\n\nGenerated: 2026-05-11 10:52 UTC\nMode: core\n"

    assert differs_only_by_generated_timestamp(existing, candidate) is True


def test_differs_only_by_generated_timestamp_rejects_content_change() -> None:
    existing = "# Bundle\n\nGenerated: 2026-05-11 10:44 UTC\nMode: core\nA\n"
    candidate = "# Bundle\n\nGenerated: 2026-05-11 10:52 UTC\nMode: core\nB\n"

    assert differs_only_by_generated_timestamp(existing, candidate) is False


def test_write_bundle_if_changed_preserves_timestamp_only_existing_file(tmp_path: Path) -> None:
    out_path = tmp_path / "CONTEXT.md"
    existing = "# Bundle\n\nGenerated: 2026-05-11 10:44 UTC\nMode: core\n"
    candidate = "# Bundle\n\nGenerated: 2026-05-11 10:52 UTC\nMode: core\n"
    out_path.write_text(existing, encoding="utf-8")

    changed = write_bundle_if_changed(out_path, candidate)

    assert changed is False
    assert out_path.read_text(encoding="utf-8") == existing


def test_write_bundle_if_changed_writes_real_content_change(tmp_path: Path) -> None:
    out_path = tmp_path / "CONTEXT.md"
    existing = "# Bundle\n\nGenerated: 2026-05-11 10:44 UTC\nMode: core\nA\n"
    candidate = "# Bundle\n\nGenerated: 2026-05-11 10:52 UTC\nMode: core\nB\n"
    out_path.write_text(existing, encoding="utf-8")

    changed = write_bundle_if_changed(out_path, candidate)

    assert changed is True
    assert out_path.read_text(encoding="utf-8") == candidate
