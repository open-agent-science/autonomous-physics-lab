#!/usr/bin/env python3
"""Generate the TASK-0539 NMD-0003 F2 coverage-gate selection manifest.

Pre-score coverage check only: computes the frozen TASK-0478 residual-free F2
finer-taxonomy bin populations from Z/N/A and checks the reopen coverage gate.
No candidate is fit, no F2 score is computed, and no residual or source-status
input is read.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_DATASET = "data/nuclear_masses/nmd-0003-ame2020-measured-training.yaml"
DEFAULT_OUTPUT = "data/nuclear_masses/f2-coverage-selection-manifest.yaml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    return parser


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    from physics_lab.engines.nuclear_f2_coverage import (
        F2_TAXONOMY,
        evaluate_f2_coverage_for_dataset,
    )

    args = build_parser().parse_args()
    dataset_path = Path(args.dataset)
    output_path = Path(args.output)

    coverage = evaluate_f2_coverage_for_dataset(dataset_path)
    gate = coverage["gate"]

    manifest = {
        "manifest_id": "NMD-0003-F2-COVERAGE-SELECTION-MANIFEST",
        "task_id": "TASK-0539",
        "status": "frozen_pre_score_coverage_manifest",
        "feature_family": "F2",
        "eligibility_class": "diagnostic_only",
        "source_dataset": str(dataset_path),
        "source_dataset_sha256": _sha256(dataset_path),
        "frozen_taxonomy": coverage["taxonomy"],
        "coverage_floors": gate["floors"],
        "gate_result": {
            "row_count": gate["row_count"],
            "total_scored_rows": gate["total_scored_rows"],
            "scored_bins": gate["scored_bins"],
            "scored_bins_outside_near_magic": gate["scored_bins_outside_near_magic"],
            "gate_criteria": gate["gate_criteria"],
            "gate_clears": gate["gate_clears"],
        },
        "bins": [
            {
                "bin": bin_id,
                "count": gate["bins"][bin_id]["count"],
                "role": gate["bins"][bin_id]["role"],
                "near_magic_family": gate["bins"][bin_id]["near_magic_family"],
                "nuclide_ids": coverage["bin_assignments"][bin_id],
            }
            for bin_id in F2_TAXONOMY
        ],
        "usage_note": (
            "Pre-score coverage selection only. A future gated F2 scoring task may "
            "use these frozen bins and floors but must run the full controls-first "
            "gauntlet (TASK-0478) and author no PRED/CLAIM/KNOW/RESULT artifact "
            "from this manifest. F2 stays diagnostic_only."
        ),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"F2 coverage selection manifest written: {output_path}")
    print(f"Gate clears: {gate['gate_clears']}")
    print(f"Scored bins: {len(gate['scored_bins'])}; total scored rows: {gate['total_scored_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
