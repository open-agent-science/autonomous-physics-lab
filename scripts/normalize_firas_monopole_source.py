"""Normalize the pinned COBE/FIRAS monopole spectrum without running metrics."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import yaml


EXPECTED_SHA256 = "df793c3dca09ebfa7dbc5aa0ec1951daa8884431bc30eff28a710d7516cf50fa"
EXPECTED_ROW_COUNT = 43


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_rows(source_path: Path) -> list[dict[str, object]]:
    checksum = sha256_file(source_path)
    if checksum != EXPECTED_SHA256:
        raise ValueError(
            f"Unexpected FIRAS source checksum: expected {EXPECTED_SHA256}, got {checksum}"
        )

    rows: list[dict[str, object]] = []
    for line in source_path.read_text(encoding="ascii").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        fields = stripped.split()
        if len(fields) != 5:
            raise ValueError(f"Expected five FIRAS columns, got {len(fields)}: {line}")
        axis, monopole, residual, uncertainty, galaxy = fields
        rows.append(
            {
                "row_id": f"FIRAS-MONOPOLE-{len(rows) + 1:03d}",
                "spectral_axis_cm_inverse": float(axis),
                "spectral_axis_class": "source_reported_direct",
                "monopole_intensity_mjy_sr": float(monopole),
                "monopole_intensity_class": "source_derived_absolute",
                "residual_kjy_sr": int(residual),
                "residual_class": "source_reported_residual",
                "uncertainty_1sigma_kjy_sr": int(uncertainty),
                "uncertainty_class": "source_reported_1sigma",
                "galaxy_model_kjy_sr": int(galaxy),
                "galaxy_model_class": "source_modeled",
                "admissibility": "admitted_for_future_domain_conversion_audit",
            }
        )

    if len(rows) != EXPECTED_ROW_COUNT:
        raise ValueError(
            f"Unexpected FIRAS row count: expected {EXPECTED_ROW_COUNT}, got {len(rows)}"
        )
    return rows


def build_dataset(source_path: Path) -> dict[str, object]:
    rows = parse_rows(source_path)
    return {
        "dataset_id": "TFA-WIEN-FIRAS-MONOPOLE-V1",
        "schema_version": "0.1.0",
        "task_id": "TASK-0801",
        "campaign_profile_id": "textbook-formula-audit",
        "status": "source_pinned_rows_curated_no_metrics",
        "source": {
            "source_id": "cobe-firas-cmb-monopole-spectrum-v1",
            "artifact_path": source_path.as_posix(),
            "artifact_url": (
                "https://lambda.gsfc.nasa.gov/data/cobe/firas/monopole_spec/"
                "firas_monopole_spec_v1.txt"
            ),
            "checksum_sha256": EXPECTED_SHA256,
            "version": "v1",
            "revision_date": "2005-05",
            "retrieval_date_utc": "2026-06-21",
            "citation": (
                "Fixsen et al. 1996, ApJ 473, 576, Table 4; "
                "Fixsen and Mather 2002, ApJ 581, 817."
            ),
        },
        "column_semantics": {
            "spectral_axis_cm_inverse": "FIRAS native wavenumber/frequency axis",
            "monopole_intensity_mjy_sr": (
                "NASA LAMBDA absolute monopole spectrum computed as a 2.725 K "
                "blackbody plus the published residual"
            ),
            "residual_kjy_sr": "Table 4 residual monopole spectrum; diagnostic only",
            "uncertainty_1sigma_kjy_sr": "Table 4 spectrum uncertainty",
            "galaxy_model_kjy_sr": "modeled Galaxy spectrum at the Galactic poles",
        },
        "scope": {
            "metric_run_performed": False,
            "blackbody_fit_performed": False,
            "wien_peak_computed": False,
            "temperature_source_pinned_here": False,
            "allowed_next_step": "TASK-0802 metric task after separate temperature pinning",
        },
        "counts": {
            "rows_total": len(rows),
            "rows_admitted": len(rows),
            "rows_excluded": 0,
        },
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Normalize the checksum-pinned FIRAS monopole source table."
    )
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)

    payload = build_dataset(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )
    print(f"rows={len(payload['rows'])}")
    print(f"output={args.output}")
    print(f"source_sha256={EXPECTED_SHA256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
