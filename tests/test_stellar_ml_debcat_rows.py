"""TASK-0708 regression tests for the DEBCat stellar M-L row package.

The full normalized DEBCat row set is intentionally NOT committed (DEBCat has no
explicit open-redistribution licence; see TASK-0731). These tests therefore
validate (a) the pure extraction helpers, and (b) the small illustrative
``*.sample.yaml`` artifacts. A guard test asserts the full value-bearing
datasets are not re-introduced into the public tree.
"""

from __future__ import annotations

import hashlib
import importlib.util
import math
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
STELLAR_DIR = REPO_ROOT / "data/textbook_formula_audit/stellar_ml"
SAMPLE_ROWS_PATH = STELLAR_DIR / "debcat_component_rows.sample.yaml"
SAMPLE_MANIFEST_PATH = STELLAR_DIR / "debcat_holdout_manifest.sample.yaml"
FULL_ROWS_PATH = STELLAR_DIR / "debcat_component_rows.yaml"
FULL_MANIFEST_PATH = STELLAR_DIR / "debcat_holdout_manifest.yaml"
SCRIPT_PATH = REPO_ROOT / "scripts" / "extract_debcat_stellar_ml_rows.py"

_SPEC = importlib.util.spec_from_file_location(
    "extract_debcat_stellar_ml_rows", SCRIPT_PATH
)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# --- Pure-helper unit tests (no dataset needed) -------------------------------

def test_derive_log_luminosity_matches_stefan_boltzmann() -> None:
    # log10(L/Lsun) = 2 logR + 4 (logT - log10(5772)); solar R=0,T=log10(5772) -> 0.
    log_l, unc = _MODULE.derive_log_luminosity(0.0, math.log10(5772.0), 0.0, 0.0)
    assert abs(log_l) < 1e-9
    assert unc == 0.0
    # Independent-error propagation in log space.
    log_l, unc = _MODULE.derive_log_luminosity(-0.6893, 3.476, 0.0102, 0.014)
    assert math.isclose(log_l, -2.519905, abs_tol=1e-6)
    expected = math.sqrt((2 * 0.0102) ** 2 + (4 * 0.014) ** 2)
    assert math.isclose(unc, round(expected, 6), abs_tol=1e-6)
    # Missing a log-space error -> uncertainty is None.
    _, unc_none = _MODULE.derive_log_luminosity(-0.6893, 3.476, None, 0.014)
    assert unc_none is None


def test_mass_band_thresholds() -> None:
    assert _MODULE.mass_band(0.3) == "very_low"
    assert _MODULE.mass_band(0.5) == "low"
    assert _MODULE.mass_band(1.0) == "solar"
    assert _MODULE.mass_band(2.0) == "intermediate"
    assert _MODULE.mass_band(20.0) == "high"


def test_assign_lane_is_deterministic_and_blind() -> None:
    # Stable across calls and matches the documented hash rule; this is what
    # keeps the holdout split frozen without committing the full membership list.
    sid = "2MASS_J05221817-2507112"
    bucket = int(hashlib.sha256(sid.encode("utf-8")).hexdigest(), 16) % 10
    assert _MODULE.assign_lane(sid) == _MODULE.LANE_BUCKETS[bucket]
    assert _MODULE.assign_lane(sid) == _MODULE.assign_lane(sid)


# --- Public-safety guard (forward-compatible with future DEBCat permission) ---

# Mirrors the TASK-0731 PDF guard: a value-bearing third-party file may be
# committed only alongside an explicit redistribution marker. This makes the
# permission flip a drop-in (add marker + force-add full files); no test edit.
ALLOWED_REDISTRIBUTION_STATES = {
    "cc_by_4_0",
    "cc0",
    "public_domain",
    "explicit_permission_recorded",
}


def _has_valid_license_marker(full_path: Path) -> bool:
    marker = full_path.with_suffix(full_path.suffix + ".license.yaml")
    if not marker.exists():
        return False
    payload = _load(marker)
    return (
        isinstance(payload, dict)
        and payload.get("redistribution_status") in ALLOWED_REDISTRIBUTION_STATES
        and bool(payload.get("permission_evidence"))
    )


def test_full_debcat_dataset_requires_license_marker() -> None:
    """Full DEBCat rows/manifest may be committed ONLY with an explicit licence.

    Without a sibling ``<file>.license.yaml`` carrying a recorded redistribution
    permission, the full value-bearing files must not be committed (TASK-0731).
    After DEBCat grants permission, dropping in the marker file flips this guard
    open with no code/test changes.
    """
    for full_path in (FULL_ROWS_PATH, FULL_MANIFEST_PATH):
        if full_path.exists():
            assert _has_valid_license_marker(full_path), (
                f"{full_path.name} is committed without a valid "
                f"{full_path.name}.license.yaml redistribution marker; ship the "
                "extractor + sample instead, or add the permission marker."
            )


# --- Sample-artifact invariants ----------------------------------------------

def test_sample_is_small_and_marked() -> None:
    doc = _load(SAMPLE_ROWS_PATH)
    assert doc.get("sample") is True
    assert "publication_notice" in doc
    assert len(doc["rows"]) <= 12  # non-substitutive sample only
    # Full counts retained as documentation, not as committed rows.
    assert doc["full_dataset_counts"]["component_rows_admitted"] > len(doc["rows"])


def test_sample_covers_each_row_class() -> None:
    doc = _load(SAMPLE_ROWS_PATH)
    classes = set()
    for r in doc["rows"]:
        classes.add(r.get("luminosity_provenance_class") or r.get("exclusion_reason"))
    assert {"direct_observation", "derived_luminosity"} <= classes
    assert "ambiguous_duplicate_system_id" in classes
    assert "no_admissible_luminosity_path" in classes


def test_sample_rows_are_well_formed() -> None:
    doc = _load(SAMPLE_ROWS_PATH)
    for r in doc["rows"]:
        if r["admissibility"] == "excluded":
            assert r.get("exclusion_reason")
            continue
        assert r["mass_provenance_class"] == "direct_observation"
        assert r["luminosity_provenance_class"] in {"direct_observation", "derived_luminosity"}
        assert "log_mass_solar" in r and "log_luminosity_solar" in r


def test_sample_derived_luminosity_matches_recomputation() -> None:
    doc = _load(SAMPLE_ROWS_PATH)
    checked = 0
    for r in doc["rows"]:
        if r.get("luminosity_provenance_class") != "derived_luminosity":
            continue
        log_l, _ = _MODULE.derive_log_luminosity(
            r["log_radius_solar"], r["log_teff_k"], None, None
        )
        assert math.isclose(log_l, r["log_luminosity_solar"], abs_tol=1e-6), r["row_id"]
        checked += 1
    assert checked > 0


def test_sample_manifest_lane_matches_hash_rule() -> None:
    rows_doc = _load(SAMPLE_ROWS_PATH)
    manifest = _load(SAMPLE_MANIFEST_PATH)
    assert manifest.get("sample") is True
    assert manifest["freeze"]["frozen_before_residual_inspection"] is True
    row_lane = {
        r["system_id"]: r["lane"]
        for r in rows_doc["rows"]
        if r["admissibility"] == "admitted"
    }
    valid = {"train", "validation", "holdout", "excluded"}
    for entry in manifest["systems"]:
        sid = entry["system_id"]
        lane = entry["lane"]
        assert lane in valid
        if lane == "excluded":
            assert entry.get("exclusion_reason")
            continue
        assert lane == _MODULE.assign_lane(sid), sid
        # Cross-check the row lane only when the sample includes this system's
        # admitted component (a one-component-admitted system may contribute
        # only its excluded component to the sample).
        if sid in row_lane:
            assert row_lane[sid] == lane, sid
