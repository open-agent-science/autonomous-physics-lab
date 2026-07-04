from __future__ import annotations

import hashlib
from decimal import Decimal
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = (
    ROOT
    / "data"
    / "particle_masses"
    / "source_artifacts"
    / "antusch-hinze-saad-2026"
)
ROWS_PATH = SOURCE_DIR / "equation-2.4-2024-pdg-mz-yukawas.yaml"
PROVENANCE_PATH = SOURCE_DIR / "provenance.yaml"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_ahs_common_scheme_rows_match_equation_2_4() -> None:
    payload = _load(ROWS_PATH)

    assert payload["status"] == "SOURCE_ROWS_PINNED_NO_METRIC"
    assert payload["surface"] == {
        "input_edition": "2024 Particle Data Group",
        "theory_branch": "Standard Model",
        "representation": "running_yukawa",
        "row_class": "derived_running_yukawa",
        "units": "dimensionless",
        "renormalization_scheme": "MS-bar",
        "renormalization_scale": "M_Z",
        "interval_semantics": "source-reported symmetric one-sigma HPD marginal",
        "covariance_status": "no recoverable six-parameter covariance matrix",
        "dependence_note": payload["surface"]["dependence_note"],
    }

    expected = {
        "y_u": (Decimal("7.04e-6"), Decimal("1.5e-7")),
        "y_d": (Decimal("1.54e-5"), Decimal("2.0e-7")),
        "y_s": (Decimal("3.06e-4"), Decimal("4.0e-6")),
        "y_c": (Decimal("3.56e-3"), Decimal("6.0e-5")),
        "y_b": (Decimal("1.630e-2"), Decimal("9.0e-5")),
        "y_t": (Decimal("0.967"), Decimal("0.004")),
    }
    actual = {
        row["parameter"]: (
            Decimal(str(row["central_value"])),
            Decimal(str(row["uncertainty"]["value"])),
        )
        for row in payload["entries"]
    }
    assert actual == expected
    assert all(row["uncertainty"]["type"] == "symmetric" for row in payload["entries"])
    assert all(
        row["uncertainty"]["confidence"] == "one_sigma_hpd"
        for row in payload["entries"]
    )


def test_ahs_row_artifact_checksum_and_boundaries_are_pinned() -> None:
    payload = _load(ROWS_PATH)
    provenance = _load(PROVENANCE_PATH)
    digest = hashlib.sha256(ROWS_PATH.read_bytes()).hexdigest()

    assert provenance["curated_rows"]["sha256"] == digest
    assert provenance["curated_rows"]["path"] == str(
        ROWS_PATH.relative_to(ROOT)
    ).replace("\\", "/")
    assert payload["source"]["accepted_manuscript_pdf_sha256"] == (
        "64e1d141cdfb2bcd3f45efe0b16e3ebdfa6130fd27f361d14353ecbb96d2aabd"
    )
    assert payload["use_constraints"] == {
        "existing_particle_rows_overwritten": False,
        "metric_run_authorized": False,
        "covariance_aware_claim_authorized": False,
        "next_step": payload["use_constraints"]["next_step"],
    }
