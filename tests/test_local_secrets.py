"""Tests for the cross-platform local source-secret helper."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts import apl_local_secrets


def test_load_env_file_supports_comments_export_and_quotes(tmp_path: Path) -> None:
    secrets = tmp_path / "secrets.env"
    secrets.write_text(
        "\n".join(
            [
                "# local only",
                "MP_API_KEY=abc123",
                "export OTHER_KEY='quoted value'",
                'DOUBLE_KEY="double quoted"',
            ]
        ),
        encoding="utf-8",
    )

    assert apl_local_secrets.load_env_file(secrets) == {
        "MP_API_KEY": "abc123",
        "OTHER_KEY": "quoted value",
        "DOUBLE_KEY": "double quoted",
    }


def test_load_env_file_accepts_utf8_bom_from_windows_powershell(tmp_path: Path) -> None:
    secrets = tmp_path / "secrets.env"
    secrets.write_text("MP_API_KEY=abc123\n", encoding="utf-8-sig")

    assert apl_local_secrets.load_env_file(secrets) == {"MP_API_KEY": "abc123"}


def test_status_reports_presence_without_values(tmp_path: Path, capsys) -> None:
    secrets = tmp_path / "secrets.env"
    secrets.write_text("MP_API_KEY=secret-value\n", encoding="utf-8")

    status = apl_local_secrets.cmd_status(
        argparse_namespace(
            require=["MP_API_KEY", "MISSING_KEY"],
            secrets_file=secrets,
            json=False,
        )
    )
    captured = capsys.readouterr()

    assert status == 2
    assert "MP_API_KEY SET" in captured.out
    assert "MISSING_KEY not set" in captured.out
    assert "secret-value" not in captured.out


def test_run_loads_secret_for_child_process_without_shell(tmp_path: Path) -> None:
    secrets = tmp_path / "secrets.env"
    secrets.write_text("MP_API_KEY=secret-value\n", encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/apl_local_secrets.py",
            "run",
            "--secrets-file",
            str(secrets),
            "--",
            sys.executable,
            "-c",
            (
                "import os, json; "
                "print(json.dumps({'present': bool(os.environ.get('MP_API_KEY'))}))"
            ),
        ],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(completed.stdout) == {"present": True}
    assert "secret-value" not in completed.stdout


def test_env_var_can_point_to_shared_secret_file(tmp_path: Path, monkeypatch) -> None:
    secrets = tmp_path / "shared.env"
    secrets.write_text("MP_API_KEY=secret-value\n", encoding="utf-8")
    monkeypatch.setenv("APL_LOCAL_SECRETS_FILE", str(secrets))

    assert apl_local_secrets.status_payload(["MP_API_KEY"]) == {"MP_API_KEY": "SET"}


def argparse_namespace(**kwargs):
    """Build a tiny argparse-like object without importing argparse in tests."""

    class Namespace:
        pass

    namespace = Namespace()
    for key, value in kwargs.items():
        setattr(namespace, key, value)
    return namespace
