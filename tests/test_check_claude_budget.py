"""Tests for scripts/check_claude_budget.py."""

from __future__ import annotations

import datetime
import importlib.util
import json
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Load module from scripts/ without requiring it to be a package
# ---------------------------------------------------------------------------
_SCRIPT = pathlib.Path(__file__).parent.parent / "scripts" / "check_claude_budget.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_claude_budget", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()
compute_usage = mod.compute_usage
evaluate = mod.evaluate
main = mod.main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_session(tmp_path: pathlib.Path, messages: list[dict]) -> pathlib.Path:
    """Write a fake project JSONL session file."""
    proj = tmp_path / "proj-abc"
    proj.mkdir(parents=True, exist_ok=True)
    f = proj / "session-001.jsonl"
    with open(f, "w") as fh:
        for m in messages:
            fh.write(json.dumps(m) + "\n")
    return f


def _msg(
    ts: str,
    input_tok: int,
    output_tok: int,
    cache_tok: int = 0,
    cache_creation_tok: int = 0,
) -> dict:
    return {
        "timestamp": ts,
        "message": {
            "usage": {
                "input_tokens": input_tok,
                "output_tokens": output_tok,
                "cache_read_input_tokens": cache_tok,
                "cache_creation_input_tokens": cache_creation_tok,
            }
        },
    }


NOW = datetime.datetime(2026, 5, 19, 12, 0, 0, tzinfo=datetime.timezone.utc)
THIS_MONTH = "2026-05-15T10:00:00+00:00"
LAST_MONTH = "2026-04-28T10:00:00+00:00"


# ---------------------------------------------------------------------------
# compute_usage
# ---------------------------------------------------------------------------

class TestComputeUsage:
    def test_missing_dir_returns_zeros(self, tmp_path):
        result = compute_usage(tmp_path / "nonexistent", now=NOW)
        assert result["total_tokens"] == 0
        assert result["input_tokens"] == 0
        assert result["output_tokens"] == 0

    def test_counts_current_month_only(self, tmp_path):
        _write_session(tmp_path, [
            _msg(THIS_MONTH, 1000, 5000),   # this month → counted
            _msg(LAST_MONTH, 9999, 99999),  # last month → ignored
        ])
        result = compute_usage(tmp_path, now=NOW)
        assert result["input_tokens"] == 1000
        assert result["output_tokens"] == 5000
        assert result["total_tokens"] == 6000

    def test_sums_multiple_messages(self, tmp_path):
        _write_session(tmp_path, [
            _msg(THIS_MONTH, 100, 200),
            _msg(THIS_MONTH, 300, 400),
        ])
        result = compute_usage(tmp_path, now=NOW)
        assert result["input_tokens"] == 400
        assert result["output_tokens"] == 600
        assert result["total_tokens"] == 1000

    def test_cache_read_tokens_counted(self, tmp_path):
        _write_session(tmp_path, [
            _msg(THIS_MONTH, 500, 1000, cache_tok=2000),
        ])
        result = compute_usage(tmp_path, now=NOW)
        assert result["cache_read_tokens"] == 2000
        assert result["total_tokens"] == 1500

    def test_cache_creation_tokens_counted_in_total(self, tmp_path):
        _write_session(tmp_path, [
            _msg(THIS_MONTH, 500, 1000, cache_creation_tok=2000),
        ])
        result = compute_usage(tmp_path, now=NOW)
        assert result["cache_creation_tokens"] == 2000
        assert result["total_tokens"] == 3500

    def test_malformed_lines_skipped(self, tmp_path):
        proj = tmp_path / "proj"
        proj.mkdir()
        f = proj / "sess.jsonl"
        f.write_text("not json\n" + json.dumps(_msg(THIS_MONTH, 100, 200)) + "\n")
        result = compute_usage(tmp_path, now=NOW)
        assert result["total_tokens"] == 300

    def test_messages_without_usage_ignored(self, tmp_path):
        _write_session(tmp_path, [
            {"timestamp": THIS_MONTH, "message": {"type": "text"}},
            _msg(THIS_MONTH, 50, 50),
        ])
        result = compute_usage(tmp_path, now=NOW)
        assert result["total_tokens"] == 100

    def test_files_read_count(self, tmp_path):
        _write_session(tmp_path, [_msg(THIS_MONTH, 10, 10)])
        result = compute_usage(tmp_path, now=NOW)
        assert result["files_read"] == 1


# ---------------------------------------------------------------------------
# evaluate
# ---------------------------------------------------------------------------

class TestEvaluate:
    def _usage(self, total=1_000_000):
        return {
            "input_tokens": total // 2,
            "output_tokens": total // 2,
            "cache_creation_tokens": 0,
            "cache_read_tokens": 0,
            "total_tokens": total,
            "sessions_scanned": 10,
            "files_read": 1,
            "period_start": "2026-05-01T00:00:00+00:00",
        }

    def test_under_threshold_true(self):
        report = evaluate(self._usage(1_000_000), monthly_limit=6_000_000, threshold_pct=50)
        assert report["under_threshold"] is True
        assert report["used_tokens"] == 1_000_000
        assert report["limit_tokens"] == 6_000_000
        assert report["used_pct"] == pytest.approx(16.67, abs=0.01)

    def test_over_threshold_false(self):
        report = evaluate(self._usage(4_000_000), monthly_limit=6_000_000, threshold_pct=50)
        assert report["under_threshold"] is False

    def test_exactly_at_threshold_blocks(self):
        report = evaluate(self._usage(3_000_000), monthly_limit=6_000_000, threshold_pct=50)
        assert report["under_threshold"] is False

    def test_remaining_pct_correct(self):
        report = evaluate(self._usage(600_000), monthly_limit=6_000_000, threshold_pct=50)
        assert report["remaining_pct"] == pytest.approx(90.0, abs=0.01)

    def test_zero_limit_does_not_crash(self):
        report = evaluate(self._usage(0), monthly_limit=0, threshold_pct=50)
        assert report["used_pct"] == 0.0


# ---------------------------------------------------------------------------
# main() CLI
# ---------------------------------------------------------------------------

class TestMain:
    def test_dry_run_always_exits_zero(self, tmp_path, monkeypatch):
        _write_session(tmp_path, [_msg(THIS_MONTH, 10_000_000, 10_000_000)])
        monkeypatch.setenv("CLAUDE_PROJECTS_DIR", str(tmp_path))
        rc = main(["--dry-run", "--limit", "1000"])
        assert rc == 0

    def test_under_threshold_exits_zero(self, tmp_path, monkeypatch, capsys):
        _write_session(tmp_path, [_msg(THIS_MONTH, 100, 100)])
        monkeypatch.setenv("CLAUDE_PROJECTS_DIR", str(tmp_path))
        rc = main(["--limit", "6000000", "--threshold", "50"])
        assert rc == 0
        out = json.loads(capsys.readouterr().out)
        assert out["under_threshold"] is True

    def test_over_threshold_exits_one(self, tmp_path, monkeypatch):
        _write_session(tmp_path, [_msg(THIS_MONTH, 5_000_000, 5_000_000)])
        monkeypatch.setenv("CLAUDE_PROJECTS_DIR", str(tmp_path))
        rc = main(["--limit", "6000000", "--threshold", "50"])
        assert rc == 1

    def test_output_is_valid_json(self, tmp_path, monkeypatch, capsys):
        _write_session(tmp_path, [_msg(THIS_MONTH, 1000, 2000)])
        monkeypatch.setenv("CLAUDE_PROJECTS_DIR", str(tmp_path))
        main(["--dry-run", "--limit", "6000000"])
        out = capsys.readouterr().out
        parsed = json.loads(out)
        for key in ("total_tokens", "used_tokens", "limit_tokens", "used_pct", "under_threshold", "monthly_limit"):
            assert key in parsed

    def test_projects_dir_flag(self, tmp_path, capsys):
        _write_session(tmp_path, [_msg(THIS_MONTH, 500, 500)])
        main(["--dry-run", "--projects-dir", str(tmp_path), "--limit", "6000000"])
        out = json.loads(capsys.readouterr().out)
        assert out["total_tokens"] == 1000

    def test_env_var_limit(self, tmp_path, monkeypatch, capsys):
        _write_session(tmp_path, [_msg(THIS_MONTH, 100, 100)])
        monkeypatch.setenv("CLAUDE_PROJECTS_DIR", str(tmp_path))
        monkeypatch.setenv("CLAUDE_MONTHLY_TOKEN_LIMIT", "1000")
        main(["--dry-run"])
        out = json.loads(capsys.readouterr().out)
        assert out["monthly_limit"] == 1000
