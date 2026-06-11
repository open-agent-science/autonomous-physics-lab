from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def _load_context_bundle_script() -> ModuleType:
    script_path = Path(__file__).resolve().parent.parent / "scripts" / "generate_context_bundle.py"
    spec = importlib.util.spec_from_file_location("generate_context_bundle", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


context_bundle = _load_context_bundle_script()


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

    normalized = context_bundle.normalize_generated_timestamp(bundle)

    assert "Generated: <timestamp>" in normalized
    assert "Generated timestamps in prose should remain untouched." in normalized


def test_differs_only_by_generated_timestamp_detects_timestamp_drift() -> None:
    existing = "# Bundle\n\nGenerated: 2026-05-11 10:44 UTC\nMode: core\n"
    candidate = "# Bundle\n\nGenerated: 2026-05-11 10:52 UTC\nMode: core\n"

    assert context_bundle.differs_only_by_generated_timestamp(existing, candidate) is True


def test_differs_only_by_generated_timestamp_rejects_content_change() -> None:
    existing = "# Bundle\n\nGenerated: 2026-05-11 10:44 UTC\nMode: core\nA\n"
    candidate = "# Bundle\n\nGenerated: 2026-05-11 10:52 UTC\nMode: core\nB\n"

    assert context_bundle.differs_only_by_generated_timestamp(existing, candidate) is False


def test_write_bundle_if_changed_preserves_timestamp_only_existing_file(tmp_path: Path) -> None:
    out_path = tmp_path / "CONTEXT.md"
    existing = "# Bundle\n\nGenerated: 2026-05-11 10:44 UTC\nMode: core\n"
    candidate = "# Bundle\n\nGenerated: 2026-05-11 10:52 UTC\nMode: core\n"
    out_path.write_text(existing, encoding="utf-8")

    changed = context_bundle.write_bundle_if_changed(out_path, candidate)

    assert changed is False
    assert out_path.read_text(encoding="utf-8") == existing


def test_write_bundle_if_changed_writes_real_content_change(tmp_path: Path) -> None:
    out_path = tmp_path / "CONTEXT.md"
    existing = "# Bundle\n\nGenerated: 2026-05-11 10:44 UTC\nMode: core\nA\n"
    candidate = "# Bundle\n\nGenerated: 2026-05-11 10:52 UTC\nMode: core\nB\n"
    out_path.write_text(existing, encoding="utf-8")

    changed = context_bundle.write_bundle_if_changed(out_path, candidate)

    assert changed is True
    assert out_path.read_text(encoding="utf-8") == candidate


def test_bundle_is_current_accepts_timestamp_only_drift(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    out_path = tmp_path / "CONTEXT.md"
    existing = "# Bundle\n\nGenerated: 2026-05-11 10:44 UTC\nMode: core\n"
    out_path.write_text(existing, encoding="utf-8")

    def fake_build_bundle(*, full: bool = False) -> str:
        del full
        return "# Bundle\n\nGenerated: 2026-05-11 10:52 UTC\nMode: core\n"

    monkeypatch.setattr(context_bundle, "build_bundle", fake_build_bundle)
    assert context_bundle.bundle_is_current(out_path=out_path) is True


def test_bundle_is_current_rejects_content_drift(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    out_path = tmp_path / "CONTEXT.md"
    out_path.write_text(
        "# Bundle\n\nGenerated: 2026-05-11 10:44 UTC\nMode: core\nA\n",
        encoding="utf-8",
    )

    def fake_build_bundle(*, full: bool = False) -> str:
        del full
        return "# Bundle\n\nGenerated: 2026-05-11 10:52 UTC\nMode: core\nB\n"

    monkeypatch.setattr(context_bundle, "build_bundle", fake_build_bundle)
    assert context_bundle.bundle_is_current(out_path=out_path) is False
