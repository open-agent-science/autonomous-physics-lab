#!/usr/bin/env python3
"""Build the Pizzocaro 2020 Yb/Sr VLBI per-window diagnostic ledger.

Deterministically parses the committed Figure 2a VLBI time-series from the
Pizzocaro source CSV and emits a machine-readable, diagnostic-only per-window
ledger (TASK-0636). It does not fetch live data, does not create
``data/atomic_clocks/acr-*.yaml`` benchmark rows, and does not compute
cross-window aggregates, drift fits, predictions, claims, knowledge, or results.

The windows share clocks, comb/clock systematics, links, and deadtime/drift
components, so the ledger is marked ``COV_BLOCKED_SHARED_SYSTEMATICS`` per the
Atomic first-benchmark covariance policy. It must stay diagnostic-only until a
future task commits a covariance reconstruction that clears that policy.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = (
    ROOT
    / "data"
    / "atomic_clocks"
    / "source_artifacts"
    / "pizzocaro-2020-yb-sr"
    / "Yb-Sr-ratio-measuremets.csv"
)
DEFAULT_LEDGER = (
    ROOT
    / "data"
    / "atomic_clocks"
    / "source_artifacts"
    / "pizzocaro-2020-yb-sr"
    / "vlbi_per_window_diagnostic_ledger.yaml"
)
VLBI_SECTION_MARKER = "Figure 2a: Yb/Sr ratio measurement via VLBI"
HEADER_PREFIX = "# MJDstart,"

# Header column name -> ledger field name for the components we record per window.
_STATISTICAL = {"uA1": "uA1", "uA2": "uA2", "uA3": "uA3", "uA4": "uA4"}
_SYSTEMATIC = {
    "uB1-comb": "uB1_comb",
    "uB1-clock": "uB1_clock",
    "uB2": "uB2",
    "uB4-comb": "uB4_comb",
    "uB4-clock": "uB4_clock",
}
_EXTRAPOLATION = {
    "udead12": "udead12",
    "udrift12": "udrift12",
    "udead23": "udead23",
    "udrift23": "udrift23",
    "udead34": "udead34",
    "udrift34": "udrift34",
}


def _vlbi_header_and_rows(csv_text: str) -> tuple[list[str], list[list[str]]]:
    """Return the VLBI header column names and raw data rows from the CSV text."""
    lines = csv_text.splitlines()
    in_section = False
    header: list[str] | None = None
    rows: list[list[str]] = []
    for line in lines:
        if VLBI_SECTION_MARKER in line:
            in_section = True
            continue
        if not in_section:
            continue
        if header is None:
            if line.startswith(HEADER_PREFIX):
                header = [name.strip() for name in line.lstrip("# ").split(",")]
            continue
        stripped = line.strip()
        if not stripped:
            break  # blank line ends the VLBI data block
        if stripped.startswith("#"):
            break  # next section starts
        rows.append([cell.strip() for cell in stripped.split(",")])
    if header is None:
        raise ValueError("VLBI header row not found in source CSV")
    return header, rows


def build_vlbi_window_ledger(csv_path: Path = DEFAULT_CSV) -> dict[str, Any]:
    """Build the per-window diagnostic ledger payload from the committed CSV."""
    csv_text = csv_path.read_text(encoding="utf-8")
    source_csv_sha256 = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    header, raw_rows = _vlbi_header_and_rows(csv_text)
    index = {name: position for position, name in enumerate(header)}

    def cell(row: list[str], column: str) -> float:
        return float(row[index[column]])

    value_column = next(name for name in header if name.startswith("yVLBI"))

    windows: list[dict[str, Any]] = []
    for position, row in enumerate(raw_rows, start=1):
        windows.append(
            {
                "window_id": f"PIZZOCARO-VLBI-W{position:02d}",
                "mjd_start": cell(row, "MJDstart"),
                "mjd_stop": cell(row, "MJDstop"),
                "mjd_med": cell(row, "MJDmed"),
                "ratio_orientation": "Yb/Sr",
                "value_yb_sr_relative": cell(row, value_column),
                "final_uncertainty": cell(row, header[-1]),
                "statistical_components": {
                    field: cell(row, column) for column, field in _STATISTICAL.items()
                },
                "systematic_components": {
                    field: cell(row, column) for column, field in _SYSTEMATIC.items()
                },
                "extrapolation_components": {
                    field: cell(row, column) for column, field in _EXTRAPOLATION.items()
                },
                "covariance_state": "COV_BLOCKED_SHARED_SYSTEMATICS",
            }
        )

    # Shared (window-invariant) systematic components are load-bearing for any
    # cross-window covariance and are why independence is not admissible.
    shared_systematics = sorted(
        field
        for column, field in _SYSTEMATIC.items()
        if len({window["systematic_components"][field] for window in windows}) == 1
    )

    return {
        "ledger_id": "ACLOCK-PIZZOCARO-VLBI-WINDOW-DIAGNOSTIC-LEDGER-0001",
        "schema_version": "0.1.0",
        "task_id": "TASK-0636",
        "campaign_profile_id": "atomic-clock-residuals",
        "created_by": {"contributor_id": "roman", "agent_id": "claude"},
        "diagnostic_only": True,
        "source": {
            "artifact_id": "ACLOCK-SRC-ARTIFACT-2020-PIZZOCARO-VLBI",
            "source_file": (
                "data/atomic_clocks/source_artifacts/pizzocaro-2020-yb-sr/"
                "Yb-Sr-ratio-measuremets.csv"
            ),
            "source_csv_sha256": (
                source_csv_sha256
            ),
            "section_locator": VLBI_SECTION_MARKER,
            "dataset_doi": "10.5281/zenodo.5592085",
            "publication_doi": "10.1038/s41567-020-01038-6",
            "processing_path": "VLBI",
        },
        "value_semantics": {
            "ratio_orientation": "Yb/Sr",
            "quantity": "fractional_frequency_ratio_deviation_relative_units",
            "units": "dimensionless_relative",
            "value_column": value_column,
            "final_uncertainty_column": header[-1],
            "uncertainty_confidence_level": "1_sigma",
            "direct_vs_derived_class": "LINK_DERIVED_DIRECT_COMPARISON_CANDIDATE",
        },
        "covariance": {
            "state": "COV_BLOCKED_SHARED_SYSTEMATICS",
            "shared_systematic_components": shared_systematics,
            "reconstruction_attempt": "blocked",
            "blocker_reason": (
                "The 10 VLBI windows share clocks, frequency comb, the maser/optical "
                "and VLBI links, campaign systematics, and deadtime/drift components. "
                "Window-invariant systematic components (for example uB1_comb and "
                "uB4_comb at 8.00e-17 and uB2 at 1.00e-16) are load-bearing for any "
                "cross-window combination, but the committed source artifacts do not "
                "expose a signed off-diagonal covariance or a deterministic "
                "reconstruction recipe."
            ),
            "unblock_condition": (
                "A future task may move toward COV_SOURCE_DERIVED_PSD_APPROX only if "
                "it commits a deterministic covariance reconstruction (row order, unit "
                "convention, shared-component sign convention, pairwise decomposition, "
                "PSD check, omitted-component list) from the committed source, or "
                "COV_EXACT_COMMITTED only if the source publishes the full matrix. "
                "Until then the windows stay diagnostic-only."
            ),
        },
        "promotion_boundary": {
            "writes_acr_benchmark_rows": False,
            "writes_cross_window_aggregate_metric": False,
            "writes_benchmark_metrics": False,
            "writes_prediction_registry": False,
            "writes_canonical_result": False,
            "claim_promotion_allowed": False,
            "knowledge_promotion_allowed": False,
        },
        "window_count": len(windows),
        "windows": windows,
        "limitations": [
            "Diagnostic-only readiness memory; windows are not independent benchmark rows.",
            "No cross-window aggregate value or uncertainty is computed.",
            "Covariance remains COV_BLOCKED_SHARED_SYSTEMATICS until a reconstruction clears the Atomic covariance policy.",
            "Values are copied deterministically from the committed source CSV; no live fetch.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--out", type=Path, default=DEFAULT_LEDGER)
    args = parser.parse_args(argv)

    ledger = build_vlbi_window_ledger(args.csv)
    args.out.write_text(
        yaml.safe_dump(ledger, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    print(f"wrote {args.out} with {ledger['window_count']} VLBI windows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
