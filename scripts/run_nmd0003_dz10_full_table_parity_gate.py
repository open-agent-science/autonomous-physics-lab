#!/usr/bin/env python3
"""Run the TASK-0911 local-only DZ10 full-table parity gate.

Points the gate at an externally supplied local AMDC cache (table + Fortran
source). Skips cleanly with ``SOURCE_BYTES_NOT_AVAILABLE`` (exit 0) when the
cache is absent, exits 1 on a contested identity or failed parity check, and
never fetches or vendors source bytes itself.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from physics_lab.engines.nmd0003_dz10_full_table_parity_gate import (  # noqa: E402
    VERDICT_CONTESTED,
    run_full_table_parity_gate,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        required=True,
        help="Local directory holding du_zu_10.feb96 and du_zu_10.feb96fort.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional path for the machine-readable JSON gate report.",
    )
    args = parser.parse_args()

    report = run_full_table_parity_gate(
        args.cache_dir / "du_zu_10.feb96",
        args.cache_dir / "du_zu_10.feb96fort",
    )
    payload = json.dumps(report, indent=2, sort_keys=True)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    print(f"Gate verdict: {report['verdict']}")
    return 1 if report["verdict"] == VERDICT_CONTESTED else 0


if __name__ == "__main__":
    raise SystemExit(main())
