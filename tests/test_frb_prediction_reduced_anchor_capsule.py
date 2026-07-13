"""Regression tests for the TASK-1024 reduced FRB anchor capsule."""

from __future__ import annotations

from pathlib import Path
import zipfile

import pytest
import yaml

from scripts.package_frb_prediction_reduced_anchor_capsule import (
    DEFAULT_ARCHIVE_NAME,
    EXCLUSION_POLICY,
    INCLUDED_FILES,
    MANIFEST_MEMBER_PATH,
    README_MEMBER_PATH,
    build_capsule,
    verify_go_reduced_capsule_decision,
)


ROOT = Path(__file__).resolve().parents[1]


def test_frb_reduced_anchor_capsule_is_deterministic(tmp_path: Path) -> None:
    first = build_capsule(ROOT, tmp_path / "first")
    second = build_capsule(ROOT, tmp_path / "second")

    assert first["archive"]["bytes"] == 50_077
    assert first["archive"]["sha256"] == (
        "141a4ef4e0e1bfe626abb721cccf2d170249b91d910cb125132efa4b019ec49a"
    )
    assert first["archive"]["sha256"] == second["archive"]["sha256"]
    assert first["archive"]["bytes"] == second["archive"]["bytes"]
    assert (tmp_path / "first" / DEFAULT_ARCHIVE_NAME).read_bytes() == (
        tmp_path / "second" / DEFAULT_ARCHIVE_NAME
    ).read_bytes()


def test_frb_reduced_anchor_capsule_enforces_allowlist_and_exclusions(
    tmp_path: Path,
) -> None:
    manifest = build_capsule(ROOT, tmp_path / "capsule")
    archive_path = Path(manifest["archive"]["path"])
    expected_names = [
        README_MEMBER_PATH,
        MANIFEST_MEMBER_PATH,
        *[entry.path for entry in INCLUDED_FILES],
    ]

    with zipfile.ZipFile(archive_path) as archive:
        assert archive.namelist() == expected_names
        assert not set(EXCLUSION_POLICY).intersection(archive.namelist())
        for info in archive.infolist():
            assert info.compress_type == zipfile.ZIP_STORED
            assert info.date_time == (1980, 1, 1, 0, 0, 0)

    excluded = manifest["excluded_sealed_members"]
    assert len(excluded) == 8
    assert {item["path"] for item in excluded} == set(EXCLUSION_POLICY)
    assert all(item["bytes"] > 0 for item in excluded)
    assert all(len(item["sha256"]) == 64 for item in excluded)
    assert all(item["redistributed_in_reduced_capsule"] is False for item in excluded)
    assert manifest["zenodo_metadata"]["license"] == "MIT"
    assert "LICENSE" in expected_names


def test_frb_reduced_anchor_capsule_has_no_value_bearing_surface_leakage(
    tmp_path: Path,
) -> None:
    manifest = build_capsule(ROOT, tmp_path / "capsule")
    archive_path = Path(manifest["archive"]["path"])

    with zipfile.ZipFile(archive_path) as archive:
        member_payloads = [archive.read(name) for name in archive.namelist()]

    combined = b"\n".join(member_payloads)
    assert b"predicted_score:" not in combined
    assert b"rank_descending:" not in combined
    assert b"target_id: FRB20" not in combined
    assert manifest["policy"]["source_derived_value_bearing_members_included"] is False
    assert manifest["policy"]["prediction_payload_changed"] is False
    assert manifest["doi_readiness_verdict"] == "REDUCED_CAPSULE_REQUIRED"
    assert (
        manifest["implementation_verdict"]
        == "REDUCED_CAPSULE_READY_FOR_MAINTAINER_UPLOAD"
    )


def test_frb_reduced_anchor_capsule_requires_live_go_decision(tmp_path: Path) -> None:
    verify_go_reduced_capsule_decision(ROOT)
    decision_path = ROOT / "decisions/DEC-20260712-frb-reduced-anchor-publication.yaml"
    decision = yaml.safe_load(decision_path.read_text(encoding="utf-8"))
    decision["veto"]["maintainer_vetoed"] = True
    isolated_root = tmp_path / "repo"
    isolated_decision = isolated_root / decision_path.relative_to(ROOT)
    isolated_decision.parent.mkdir(parents=True)
    isolated_decision.write_text(yaml.safe_dump(decision, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValueError, match="vetoed"):
        verify_go_reduced_capsule_decision(isolated_root)


def test_frb_reduced_anchor_capsule_refuses_repository_output() -> None:
    with pytest.raises(ValueError, match="Refusing to write capsule output"):
        build_capsule(ROOT, ROOT / "_generated" / "task-1024-test")
