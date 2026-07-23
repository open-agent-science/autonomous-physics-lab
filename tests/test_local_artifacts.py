"""Tests for shared private-source and task-workspace resolution."""

from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess

import pytest

from scripts import apl_local_artifacts


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def test_primary_checkout_root_uses_shared_git_common_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    primary = tmp_path / "APL"
    worktree = tmp_path / "worktrees" / "task"
    worktree.mkdir(parents=True)

    def fake_run(*args, **kwargs):  # noqa: ANN002, ANN003
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout=f"{primary / '.git'}\n",
            stderr="",
        )

    monkeypatch.setattr(apl_local_artifacts.subprocess, "run", fake_run)

    assert apl_local_artifacts.primary_checkout_root(worktree) == primary


def test_root_precedence_is_cli_then_environment_then_default(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "APL"
    env_root = tmp_path / "env-sources"
    cli_root = tmp_path / "cli-sources"
    monkeypatch.setenv("APL_PRIVATE_SOURCE_ROOT", str(env_root))
    monkeypatch.setattr(
        apl_local_artifacts,
        "primary_checkout_root",
        lambda repo_root: repo,
    )

    assert apl_local_artifacts.resolve_private_source_root(cli_root, repo_root=repo) == (
        cli_root,
        "cli",
    )
    assert apl_local_artifacts.resolve_private_source_root(repo_root=repo) == (
        env_root,
        "environment",
    )

    monkeypatch.delenv("APL_PRIVATE_SOURCE_ROOT")
    assert apl_local_artifacts.resolve_private_source_root(repo_root=repo) == (
        tmp_path / "APL-private-sources",
        "default",
    )


def test_locate_prefers_source_scoped_file_then_legacy_root(tmp_path: Path) -> None:
    root = tmp_path / "private-sources"
    payload = b"pinned source\n"
    scoped = root / "source-001" / "archive.tgz"
    scoped.parent.mkdir(parents=True)
    scoped.write_bytes(payload)
    legacy = root / "archive.tgz"
    legacy.write_bytes(payload)

    located = apl_local_artifacts.locate_source(
        filename="archive.tgz",
        source_id="source-001",
        expected_sha256=_sha256(payload),
        private_source_root=root,
    )
    assert located["path"] == str(scoped.resolve())
    assert located["layout"] == "source_scoped"

    scoped.unlink()
    located = apl_local_artifacts.locate_source(
        filename="archive.tgz",
        source_id="source-001",
        expected_sha256=_sha256(payload),
        private_source_root=root,
    )
    assert located["path"] == str(legacy.resolve())
    assert located["layout"] == "legacy_root"


def test_explicit_missing_input_does_not_fall_back_to_vault(tmp_path: Path) -> None:
    root = tmp_path / "private-sources"
    root.mkdir()
    payload = b"available elsewhere\n"
    (root / "archive.tgz").write_bytes(payload)

    with pytest.raises(apl_local_artifacts.LocalArtifactError, match="not found"):
        apl_local_artifacts.locate_source(
            filename="archive.tgz",
            expected_sha256=_sha256(payload),
            explicit_input=tmp_path / "missing" / "archive.tgz",
            private_source_root=root,
        )


def test_locate_rejects_checksum_mismatch(tmp_path: Path) -> None:
    root = tmp_path / "private-sources"
    root.mkdir()
    (root / "archive.tgz").write_bytes(b"wrong\n")

    with pytest.raises(apl_local_artifacts.LocalArtifactError, match="checksum mismatch"):
        apl_local_artifacts.locate_source(
            filename="archive.tgz",
            expected_sha256="0" * 64,
            private_source_root=root,
        )


def test_locate_is_exact_and_does_not_scan_nested_directories(tmp_path: Path) -> None:
    root = tmp_path / "private-sources"
    nested = root / "unrelated" / "deep"
    nested.mkdir(parents=True)
    payload = b"hidden from exact lookup\n"
    (nested / "archive.tgz").write_bytes(payload)

    with pytest.raises(apl_local_artifacts.LocalArtifactError, match="exact paths checked"):
        apl_local_artifacts.locate_source(
            filename="archive.tgz",
            expected_sha256=_sha256(payload),
            private_source_root=root,
        )


@pytest.mark.parametrize(
    "filename", ["../archive.tgz", "nested/archive.tgz", r"nested\archive.tgz"]
)
def test_locate_rejects_filename_traversal(tmp_path: Path, filename: str) -> None:
    with pytest.raises(apl_local_artifacts.LocalArtifactError, match="exact basename"):
        apl_local_artifacts.locate_source(
            filename=filename,
            expected_sha256="0" * 64,
            private_source_root=tmp_path,
        )


def test_workdir_is_task_and_run_scoped_and_created_on_request(tmp_path: Path) -> None:
    root = tmp_path / "local-work"

    payload = apl_local_artifacts.resolve_task_workdir(
        task_id="TASK-1091",
        run_id="replay-agent-a",
        local_work_root=root,
        create=True,
    )

    expected = root / "TASK-1091" / "replay-agent-a"
    assert payload["path"] == str(expected)
    assert payload["exists"] is True
    assert expected.is_dir()


def test_workdir_rejects_unsafe_task_or_run_ids(tmp_path: Path) -> None:
    with pytest.raises(apl_local_artifacts.LocalArtifactError, match="--task"):
        apl_local_artifacts.resolve_task_workdir(
            task_id="1091",
            local_work_root=tmp_path,
        )
    with pytest.raises(apl_local_artifacts.LocalArtifactError, match="--run"):
        apl_local_artifacts.resolve_task_workdir(
            task_id="TASK-1091",
            run_id="../escape",
            local_work_root=tmp_path,
        )
