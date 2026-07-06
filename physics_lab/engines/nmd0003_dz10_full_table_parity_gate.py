"""Local-only full-table parity gate for the canonical AMDC DZ10 reference.

TASK-0911. The gate validates an externally supplied, license-clear local copy
of the AMDC DZ10 table and Fortran source against the TASK-0878 pinned
identity, then checks parser coverage, printed-precision round-trip, smoke
fixture agreement, and lookup behaviour over the full 9311-row table. The
existing TASK-0823 published-equation variant is compared only as a
diagnostic; nothing here claims canonical model parity, creates a benchmark
result, or mutates RESULT-0025.

Source bytes are never vendored: callers point the gate at a local cache and
the gate skips cleanly with ``SOURCE_BYTES_NOT_AVAILABLE`` when the cache is
absent.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from statistics import mean, quantiles
from typing import Iterable

from physics_lab.engines.nmd0003_canonical_dz10_reference import (
    DZ10_AMDC_METADATA,
    Dz10MassExcessPoint,
    format_dz10_fixture_text,
    lookup_dz10_mass_excess_mev,
    parse_dz10_mass_excess_table,
    published_variant_mass_excess_diagnostic,
    validate_dz10_smoke_fixture,
    DZ10_SMOKE_FIXTURE,
)

EXPECTED_FULL_TABLE_ROW_COUNT = 9311
PRINTED_PRECISION_MEV = 1.0e-3

VERDICT_PASS = "DZ10_FULL_TABLE_PARITY_PASS"
VERDICT_CONTESTED = "DZ10_FULL_TABLE_PARITY_CONTESTED"
VERDICT_SOURCE_BYTES_NOT_AVAILABLE = "SOURCE_BYTES_NOT_AVAILABLE"


def _sha256_of_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_cache_identity(table_path: Path, fortran_path: Path) -> dict[str, object]:
    """Verify a local AMDC cache against the TASK-0878 pinned identity."""
    checks: dict[str, object] = {"files": {}}
    all_present = True
    all_match = True
    expectations = {
        "table": (
            table_path,
            DZ10_AMDC_METADATA["table_sha256"],
            DZ10_AMDC_METADATA["table_byte_size"],
        ),
        "fortran": (
            fortran_path,
            DZ10_AMDC_METADATA["fortran_sha256"],
            DZ10_AMDC_METADATA["fortran_byte_size"],
        ),
    }
    for name, (path, expected_sha, expected_bytes) in expectations.items():
        entry: dict[str, object] = {
            "path": str(path),
            "expected_sha256": expected_sha,
            "expected_bytes": expected_bytes,
        }
        if not path.is_file():
            entry["present"] = False
            all_present = False
        else:
            observed_bytes = path.stat().st_size
            observed_sha = _sha256_of_path(path)
            entry["present"] = True
            entry["observed_bytes"] = observed_bytes
            entry["observed_sha256"] = observed_sha
            entry["matches"] = (
                observed_sha == expected_sha and observed_bytes == expected_bytes
            )
            if not entry["matches"]:
                all_match = False
        checks["files"][name] = entry
    checks["all_present"] = all_present
    checks["all_match"] = all_present and all_match
    return checks


def evaluate_parsed_table(
    rows: Iterable[Dz10MassExcessPoint],
    *,
    expected_row_count: int = EXPECTED_FULL_TABLE_ROW_COUNT,
) -> dict[str, object]:
    """Run the byte-independent parity checks over already parsed rows.

    Separated from cache-identity verification so the check logic is testable
    on synthetic fixtures without pinned source bytes.
    """
    rows = tuple(rows)
    row_count = len(rows)
    coverage = {
        "row_count": row_count,
        "expected_row_count": expected_row_count,
        "row_count_matches": row_count == expected_row_count,
        "z_min": min(row.z for row in rows),
        "z_max": max(row.z for row in rows),
        "a_min": min(row.a for row in rows),
        "a_max": max(row.a for row in rows),
        "n_min": min(row.n for row in rows),
        "n_max": max(row.n for row in rows),
    }

    reparsed = parse_dz10_mass_excess_table(format_dz10_fixture_text(rows))
    roundtrip_exact = reparsed == rows
    max_roundtrip_delta = max(
        (
            abs(after.mass_excess_mev - before.mass_excess_mev)
            for before, after in zip(rows, reparsed)
        ),
        default=float("inf"),
    )
    printed_precision = {
        "roundtrip_exact": roundtrip_exact,
        "max_roundtrip_abs_delta_mev": max_roundtrip_delta,
        "tolerance_mev": PRINTED_PRECISION_MEV,
        "passed": roundtrip_exact and max_roundtrip_delta == 0.0,
    }

    fixture_check = validate_dz10_smoke_fixture(rows)

    lookup_checks = []
    lookup_passed = True
    for expected in DZ10_SMOKE_FIXTURE:
        try:
            observed = lookup_dz10_mass_excess_mev(rows, z=expected.z, a=expected.a)
        except KeyError:
            lookup_checks.append(
                {"z": expected.z, "a": expected.a, "found": False, "matches": False}
            )
            lookup_passed = False
            continue
        matches = abs(observed - expected.mass_excess_mev) <= PRINTED_PRECISION_MEV / 2
        lookup_checks.append(
            {
                "z": expected.z,
                "a": expected.a,
                "found": True,
                "expected_mev": expected.mass_excess_mev,
                "observed_mev": observed,
                "matches": matches,
            }
        )
        lookup_passed = lookup_passed and matches

    passed = (
        coverage["row_count_matches"]
        and printed_precision["passed"]
        and bool(fixture_check["passed"])
        and lookup_passed
    )
    return {
        "coverage": coverage,
        "printed_precision": printed_precision,
        "smoke_fixture": fixture_check,
        "lookup": {"checks": lookup_checks, "passed": lookup_passed},
        "passed": passed,
    }


def run_full_table_parity_gate(
    table_path: str | Path,
    fortran_path: str | Path,
    *,
    include_published_variant_diagnostic: bool = True,
) -> dict[str, object]:
    """Run the full TASK-0911 gate against a local AMDC cache."""
    table_path = Path(table_path)
    fortran_path = Path(fortran_path)
    identity = verify_cache_identity(table_path, fortran_path)
    report: dict[str, object] = {
        "gate": "nmd0003_dz10_full_table_parity_gate",
        "task_id": "TASK-0911",
        "source_identity": identity,
    }
    if not identity["all_present"]:
        report["verdict"] = VERDICT_SOURCE_BYTES_NOT_AVAILABLE
        report["reason"] = (
            "AMDC DZ10 source bytes are not available locally; the gate skips "
            "cleanly without fetching or vendoring restricted bytes."
        )
        return report
    if not identity["all_match"]:
        report["verdict"] = VERDICT_CONTESTED
        report["reason"] = (
            "Local AMDC cache does not match the TASK-0878 pinned SHA-256/byte "
            "identity; refusing to run parity checks on unpinned bytes."
        )
        return report

    rows = parse_dz10_mass_excess_table(table_path.read_text(encoding="utf-8"))
    checks = evaluate_parsed_table(rows)
    report["checks"] = checks

    if include_published_variant_diagnostic:
        diagnostic = published_variant_mass_excess_diagnostic(rows)
        deltas = sorted(
            float(item["abs_delta_mev"]) for item in diagnostic["comparisons"]
        )
        percentile = quantiles(deltas, n=100, method="inclusive")
        worst = sorted(
            diagnostic["comparisons"],
            key=lambda item: item["abs_delta_mev"],
            reverse=True,
        )[:5]
        report["published_variant_diagnostic"] = {
            "verdict": diagnostic["verdict"],
            "comparison_count": diagnostic["comparison_count"],
            "max_abs_delta_mev": diagnostic["max_abs_delta_mev"],
            "mean_abs_delta_mev": round(mean(deltas), 6),
            "p50_abs_delta_mev": round(percentile[49], 6),
            "p90_abs_delta_mev": round(percentile[89], 6),
            "p99_abs_delta_mev": round(percentile[98], 6),
            "worst_rows": tuple(worst),
        }

    report["verdict"] = VERDICT_PASS if checks["passed"] else VERDICT_CONTESTED
    if report["verdict"] == VERDICT_CONTESTED:
        report["reason"] = "One or more full-table parity checks failed."
    return report
