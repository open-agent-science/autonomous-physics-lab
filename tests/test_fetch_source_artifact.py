from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fetch_source_artifact.py"


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def test_fetch_source_artifact_accepts_matching_file_url(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    payload = b"apl source artifact\n"
    source.write_bytes(payload)
    output = tmp_path / "out" / "artifact.txt"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--url",
            source.as_uri(),
            "--output",
            str(output),
            "--sha256",
            _sha256(payload),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert output.read_bytes() == payload
    assert "status=OK" in result.stdout


def test_fetch_source_artifact_rejects_checksum_mismatch(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_bytes(b"wrong payload\n")
    output = tmp_path / "artifact.txt"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--url",
            source.as_uri(),
            "--output",
            str(output),
            "--sha256",
            "0" * 64,
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert not output.exists()
    assert "Checksum mismatch" in result.stderr


def test_fetch_source_artifact_reads_sidecar_and_refuses_overwrite(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    payload = b"sidecar payload\n"
    source.write_bytes(payload)
    sidecar = tmp_path / "source.txt.sha256"
    sidecar.write_text(f"{_sha256(payload)}  source.txt\n", encoding="utf-8")
    output = tmp_path / "artifact.txt"
    output.write_text("existing\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--url",
            source.as_uri(),
            "--output",
            str(output),
            "--sha256-file",
            str(sidecar),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert output.read_text(encoding="utf-8") == "existing\n"
    assert "Refusing to overwrite" in result.stderr


def test_fetch_source_artifact_rejects_invalid_sidecar(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_bytes(b"payload\n")
    sidecar = tmp_path / "source.txt.sha256"
    sidecar.write_text("not-a-sha\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--url",
            source.as_uri(),
            "--output",
            str(tmp_path / "artifact.txt"),
            "--sha256-file",
            str(sidecar),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "does not start with a SHA-256" in result.stderr
