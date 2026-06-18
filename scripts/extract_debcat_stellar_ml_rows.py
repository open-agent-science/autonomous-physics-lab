#!/usr/bin/env python3
"""Deterministic curation of normalized DEBCat stellar mass-luminosity rows.

This script implements TASK-0708. It reads a locally fetched DEBCat ``debs.dat``
ASCII table (Southworth 2015), verifies it against the pinned checksum from the
TASK-0628 / TASK-0707 Route 2 source package, and emits two normalized
artifacts:

* ``debcat_component_rows.yaml`` - per-component mass + luminosity rows, with
  provenance classes, uncertainty classes, and exclusion reasons.
* ``debcat_holdout_manifest.yaml`` - a frozen, value-blind, system-level
  train/validation/holdout/excluded split manifest.

The raw ``debs.dat`` table is intentionally **not** committed (Route 2:
metadata-only checksum pinning, unclear redistribution licence). The public
tree commits this extractor plus non-substitutive ``*.sample.yaml`` artifacts;
the full normalized rows and manifest are generated locally after fetching
``debs.dat`` from the pinned locator and confirming the checksum.

Scientific guardrails (TASK-0708, TASK-0657 holdout protocol, TASK-0688
luminosity policy):

* Masses are DEBCat direct dynamical component masses (``direct_observation``);
  no model-derived masses are used as truth.
* Luminosity uses the catalogue-reported ``logL`` first (``direct_observation``);
  the Stefan-Boltzmann reconstruction from ``logR`` and ``logT`` is used only as
  a fallback (``derived_luminosity``) when ``logL`` is absent.
* Holdout lanes are assigned at the physical-binary-system level by a
  deterministic hash of the system id - blind to mass/luminosity values - and
  frozen before any residual inspection. No exponent ``alpha`` is fitted and no
  residual is computed here.

Run:

    python3 scripts/extract_debcat_stellar_ml_rows.py \
        --debs-dat /path/to/debs.dat \
        --out-rows data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml \
        --out-manifest data/textbook_formula_audit/stellar_ml/debcat_holdout_manifest.yaml
"""

from __future__ import annotations

import argparse
import hashlib
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

# --- Pinned source provenance (TASK-0628 / TASK-0707 Route 2) -----------------

PINNED_SHA256 = "326902535b4da2fd94f227806ff339247d6df224ef8faea8857703e553b464da"
ARTIFACT_LOCATOR = "https://astro.keele.ac.uk/jkt/debcat/debs.dat"
SOURCE_CITATION = (
    "Southworth, J. (2015), The DEBCat detached eclipsing binary catalogue, "
    "ASP Conference Series, 496, 164."
)
SOURCE_ID = "debcat-detached-eclipsing-binaries"

# --- Predeclared, value-blind protocol parameters -----------------------------

SENTINEL = -9.99  # DEBCat missing-value marker (-9.9900)
SENTINEL_TOL = 5e-4
SOLAR_TEFF_K = 5772.0  # IAU 2015 nominal solar effective temperature
LOG10_SOLAR_TEFF = math.log10(SOLAR_TEFF_K)

# Mass bands in M/M_sun. Standard stellar bins, chosen for audit coverage and
# leakage control, NOT for residuals. Frozen before any fit.
MASS_BANDS = (
    ("very_low", 0.0, 0.5),
    ("low", 0.5, 1.0),
    ("solar", 1.0, 2.0),
    ("intermediate", 2.0, 8.0),
    ("high", 8.0, math.inf),
)

# Uncertainty-class thresholds on the native log10 uncertainty. Frozen.
UNC_PRECISE_MAX = 0.01
UNC_STANDARD_MAX = 0.05

# Deterministic system-level split. bucket = sha256(system_id) % 10.
# Frozen before residual inspection; blind to mass/luminosity values.
LANE_BUCKETS = {
    0: "train", 1: "train", 2: "train", 3: "train", 4: "train",
    5: "validation", 6: "validation",
    7: "holdout", 8: "holdout", 9: "holdout",
}
LANE_PROPORTIONS = {"train": 0.5, "validation": 0.2, "holdout": 0.3}

# debs.dat column order (the leading "# System" header line, tokens after "#").
DEBS_COLUMNS = [
    "System", "SpT1", "SpT2", "Pday", "Vmag", "BmV",
    "logM1", "logM1e", "logM2", "logM2e",
    "logR1", "logR1e", "logR2", "logR2e",
    "logg1", "logg1e", "logg2", "logg2e",
    "logT1", "logT1e", "logT2", "logT2e",
    "logL1", "logL1e", "logL2", "logL2e",
    "MoH", "MoHe",
]


# --- Pure helpers (unit-testable; no I/O) -------------------------------------

def is_missing(value: float) -> bool:
    """True if a parsed DEBCat field equals the -9.99 missing sentinel."""
    return abs(value - SENTINEL) < SENTINEL_TOL


def derive_log_luminosity(
    log_r: float,
    log_t: float,
    log_r_unc: Optional[float],
    log_t_unc: Optional[float],
    *,
    log10_solar_teff: float = LOG10_SOLAR_TEFF,
) -> tuple[float, Optional[float]]:
    """Stefan-Boltzmann log-luminosity reconstruction (TASK-0688 fallback).

    log10(L/Lsun) = 2*log10(R/Rsun) + 4*(log10(Teff) - log10(Teff_sun)).

    Uncertainty (independent R, T errors, already in log space):
        sigma_logL = sqrt((2*sigma_logR)^2 + (4*sigma_logT)^2)
    Returns (log_luminosity, uncertainty_or_None). Uncertainty is None when a
    required log-space error is missing.
    """
    log_l = 2.0 * log_r + 4.0 * (log_t - log10_solar_teff)
    if log_r_unc is None or log_t_unc is None:
        return round(log_l, 6), None
    sigma = math.sqrt((2.0 * log_r_unc) ** 2 + (4.0 * log_t_unc) ** 2)
    return round(log_l, 6), round(sigma, 6)


def mass_band(mass_solar: float) -> str:
    """Predeclared mass band for M/M_sun."""
    for name, lo, hi in MASS_BANDS:
        if lo <= mass_solar < hi:
            return name
    return "unknown"


def uncertainty_class(log_unc: Optional[float]) -> str:
    """Predeclared uncertainty class from a native log10 uncertainty."""
    if log_unc is None:
        return "unknown"
    if log_unc <= UNC_PRECISE_MAX:
        return "precise"
    if log_unc <= UNC_STANDARD_MAX:
        return "standard"
    return "coarse"


def assign_lane(system_id: str) -> str:
    """Deterministic, value-blind system-level lane assignment."""
    digest = hashlib.sha256(system_id.encode("utf-8")).hexdigest()
    bucket = int(digest, 16) % 10
    return LANE_BUCKETS[bucket]


def evolutionary_stage_flag(spectral_type: str) -> str:
    """Best-effort evolutionary stage from a spectral-type luminosity class.

    Metadata only - it does not drive lane assignment. Unknown is returned
    generously when the luminosity class cannot be read unambiguously.
    """
    spt = (spectral_type or "").strip().upper().replace("_", "")
    if not spt or spt in {"-", "?"}:
        return "unknown"
    # Read a trailing Roman-numeral luminosity class.
    for cls, flag in (
        ("VII", "white_dwarf"),
        ("VI", "subdwarf"),
        ("IV", "subgiant"),
        ("III", "evolved"),
        ("II", "evolved"),
        ("IB", "evolved"),
        ("IA", "evolved"),
        ("V", "main_sequence_compatible"),
        ("I", "evolved"),
    ):
        if spt.endswith(cls):
            return flag
    return "unknown"


# --- Parsing ------------------------------------------------------------------

def parse_debs_dat(text: str) -> list[dict]:
    """Parse raw debs.dat text into per-system records keyed by DEBS_COLUMNS."""
    records: list[dict] = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split()
        if len(parts) != len(DEBS_COLUMNS):
            raise ValueError(
                f"Expected {len(DEBS_COLUMNS)} fields, got {len(parts)}: {line[:60]!r}"
            )
        rec = {"System": parts[0], "SpT1": parts[1], "SpT2": parts[2]}
        for name, raw in zip(DEBS_COLUMNS[3:], parts[3:]):
            rec[name] = float(raw)
        records.append(rec)
    return records


def _opt(value: float) -> Optional[float]:
    """Return None for sentinel values, else the float."""
    return None if is_missing(value) else value


def _component_row(rec: dict, comp: int, occurrence_suffix: str) -> dict:
    """Build one component row dict (admitted or excluded) for component 1/2."""
    system_id = rec["System"]
    spt = rec[f"SpT{comp}"]
    log_m = rec[f"logM{comp}"]
    log_m_unc = _opt(rec[f"logM{comp}e"])
    log_r = _opt(rec[f"logR{comp}"])
    log_r_unc = _opt(rec[f"logR{comp}e"])
    log_t = _opt(rec[f"logT{comp}"])
    log_t_unc = _opt(rec[f"logT{comp}e"])
    log_l = _opt(rec[f"logL{comp}"])
    log_l_unc = _opt(rec[f"logL{comp}e"])

    row: dict = {
        "row_id": f"DEBCAT-{system_id}{occurrence_suffix}-C{comp}",
        "system_id": system_id,
        "component": comp,
        "spectral_type": spt,
    }

    # Mass (always a direct dynamical observation in DEBCat).
    if is_missing(log_m):
        row["admissibility"] = "excluded"
        row["exclusion_reason"] = "missing_dynamical_mass"
        return row
    row["log_mass_solar"] = log_m
    row["log_mass_solar_unc"] = log_m_unc
    row["mass_solar"] = round(10.0 ** log_m, 6)
    row["mass_provenance_class"] = "direct_observation"
    row["mass_uncertainty_class"] = uncertainty_class(log_m_unc)
    row["mass_band"] = mass_band(10.0 ** log_m)
    row["evolutionary_stage_flag"] = evolutionary_stage_flag(spt)

    # Luminosity: primary catalogue logL, else Stefan-Boltzmann fallback.
    if log_l is not None:
        row["log_luminosity_solar"] = log_l
        row["log_luminosity_solar_unc"] = log_l_unc
        row["luminosity_solar"] = round(10.0 ** log_l, 6)
        row["luminosity_provenance_class"] = "direct_observation"
        row["luminosity_source"] = "debcat_catalogue_reported_logL"
        row["luminosity_uncertainty_class"] = uncertainty_class(log_l_unc)
    elif log_r is not None and log_t is not None:
        d_log_l, d_log_l_unc = derive_log_luminosity(
            log_r, log_t, log_r_unc, log_t_unc
        )
        row["log_luminosity_solar"] = d_log_l
        row["log_luminosity_solar_unc"] = d_log_l_unc
        row["luminosity_solar"] = round(10.0 ** d_log_l, 6)
        row["luminosity_provenance_class"] = "derived_luminosity"
        row["luminosity_source"] = "stefan_boltzmann_from_debcat_logR_logT"
        row["log_radius_solar"] = log_r
        row["log_radius_solar_unc"] = log_r_unc
        row["log_teff_k"] = log_t
        row["log_teff_k_unc"] = log_t_unc
        row["luminosity_uncertainty_class"] = uncertainty_class(d_log_l_unc)
    else:
        # No catalogue luminosity and no admissible R+T fallback path.
        partial = {
            k: v
            for k, v in (
                ("log_mass_solar", log_m),
                ("log_radius_solar", log_r),
                ("log_teff_k", log_t),
            )
        }
        row.clear()
        row.update(
            {
                "row_id": f"DEBCAT-{system_id}{occurrence_suffix}-C{comp}",
                "system_id": system_id,
                "component": comp,
                "spectral_type": spt,
                "admissibility": "excluded",
                "exclusion_reason": "no_admissible_luminosity_path",
                "available_log_mass_solar": partial["log_mass_solar"],
            }
        )
        return row

    row["admissibility"] = "admitted"
    return row


def build_rows_and_manifest(
    records: list[dict],
    *,
    generated_at: str,
) -> tuple[dict, dict]:
    """Build the row package and frozen holdout manifest from parsed records."""
    # Detect ambiguous duplicate system ids (leakage hazard -> exclude all).
    id_counts = Counter(rec["System"] for rec in records)
    ambiguous_ids = {sid for sid, n in id_counts.items() if n > 1}
    seen_occurrence: Counter = Counter()

    rows: list[dict] = []
    # system_id -> {"lane", "rows": [...], "ambiguous": bool}
    systems: dict[str, dict] = {}

    for rec in records:
        system_id = rec["System"]
        ambiguous = system_id in ambiguous_ids
        suffix = ""
        if ambiguous:
            seen_occurrence[system_id] += 1
            suffix = f"-OCC{seen_occurrence[system_id]}"

        sysinfo = systems.setdefault(
            system_id,
            {"system_id": system_id, "ambiguous": ambiguous, "component_rows": []},
        )

        for comp in (1, 2):
            row = _component_row(rec, comp, suffix)
            if ambiguous:
                # Override: ambiguous identifier -> exclude every component.
                keep = {
                    "row_id": row["row_id"],
                    "system_id": system_id,
                    "component": comp,
                    "spectral_type": rec[f"SpT{comp}"],
                    "admissibility": "excluded",
                    "exclusion_reason": "ambiguous_duplicate_system_id",
                }
                row = keep
            rows.append(row)
            sysinfo["component_rows"].append(row)

    # Assign lanes per physical system (value-blind), freeze.
    manifest_systems: list[dict] = []
    for system_id in sorted(systems):
        sysinfo = systems[system_id]
        admitted = [
            r for r in sysinfo["component_rows"] if r["admissibility"] == "admitted"
        ]
        if sysinfo["ambiguous"] or not admitted:
            lane = "excluded"
            reason = (
                "ambiguous_duplicate_system_id"
                if sysinfo["ambiguous"]
                else "no_admitted_components"
            )
            entry = {
                "system_id": system_id,
                "lane": "excluded",
                "exclusion_reason": reason,
                "n_components_admitted": len(admitted),
                "n_components_total": len(sysinfo["component_rows"]),
            }
        else:
            lane = assign_lane(system_id)
            bands = sorted({r["mass_band"] for r in admitted})
            for r in admitted:
                r["lane"] = lane
            entry = {
                "system_id": system_id,
                "lane": lane,
                "n_components_admitted": len(admitted),
                "n_components_total": len(sysinfo["component_rows"]),
                "mass_bands": bands,
            }
        manifest_systems.append(entry)

    rows.sort(key=lambda r: (r["system_id"], r.get("component", 0), r["row_id"]))

    # Aggregate counts.
    admitted_rows = [r for r in rows if r["admissibility"] == "admitted"]
    excluded_rows = [r for r in rows if r["admissibility"] == "excluded"]
    lane_counts = Counter(s["lane"] for s in manifest_systems)
    exclusion_reasons = Counter(
        r["exclusion_reason"] for r in excluded_rows
    )
    lum_classes = Counter(r["luminosity_provenance_class"] for r in admitted_rows)

    rows_doc = {
        "dataset_id": "TFA-STELLAR-ML-DEBCAT-COMPONENT-ROWS",
        "schema_version": "0.1.0",
        "task_id": "TASK-0708",
        "publication_task_id": "TASK-0763",
        "scope_reconciliation_task_id": "TASK-0779",
        "campaign_profile_id": "textbook-formula-audit",
        "status": "cc_by_4_0_benchmark_source",
        "created_by": {"contributor_id": "roman", "agent_id": "claude"},
        "generated_at": generated_at,
        "scope": {
            "purpose": (
                "First curated empirical row package for the Textbook Formula "
                "Audit stellar mass-luminosity relation. Direct dynamical "
                "component masses paired with catalogue or Stefan-Boltzmann "
                "luminosities, with frozen system-level holdout lanes."
            ),
            "sandbox_only": False,
            "live_external_fetch_allowed": False,
            "benchmark_allowed": True,
            "alpha_fit_allowed": True,
            "residual_inspection_performed": False,
            "claim_promotion_allowed": False,
            "prediction_registry_allowed": False,
            "route_boundary": (
                "Full normalized DEBCat rows are committed under explicit CC BY 4.0 "
                "permission (TASK-0763) and may support the frozen, scope-limited "
                "Stellar M-L benchmark lane. This does not imply universal M-L "
                "validation, stellar-evolution claims, application-domain claims, "
                "claim promotion, or prediction-registry use."
            ),
        },
        "source": {
            "source_id": SOURCE_ID,
            "artifact_locator": ARTIFACT_LOCATOR,
            "checksum_sha256": PINNED_SHA256,
            "checksum_scope": "remote_ascii_table_debs_dat_not_committed",
            "raw_artifact_committed": False,
            "storage_route": "route2_metadata_only_checksum_normalized_rows_only",
            "citation": SOURCE_CITATION,
            "extraction_script": "scripts/extract_debcat_stellar_ml_rows.py",
        },
        "policy_refs": {
            "luminosity_policy": (
                "docs/reviews/stellar-ml-luminosity-provenance-and-license-route.md"
            ),
            "holdout_protocol": (
                "docs/reviews/stellar-ml-debcat-holdout-leakage-protocol.md"
            ),
            "storage_route_decision": (
                "docs/reviews/stellar-ml-debcat-storage-route-decision.md"
            ),
            "full_dataset_publication": (
                "docs/reviews/stellar-ml-debcat-full-dataset-publication.md"
            ),
            "scope_flag_reconciliation": (
                "docs/reviews/stellar-ml-debcat-scope-flag-reconciliation.md"
            ),
            "benchmark_result": "results/EXP-0015/RUN-0001/result.yaml",
        },
        "conventions": {
            "missing_value_sentinel": SENTINEL,
            "solar_teff_k": SOLAR_TEFF_K,
            "stefan_boltzmann_log_form": (
                "log10(L/Lsun) = 2*log10(R/Rsun) + 4*(log10(Teff) - log10(5772))"
            ),
            "luminosity_uncertainty_log_form": (
                "sigma_logL = sqrt((2*sigma_logR)^2 + (4*sigma_logT)^2)"
            ),
            "mass_provenance": "DEBCat direct dynamical masses; no model-derived mass truth.",
        },
        "counts": {
            "systems_total": len(systems),
            "records_total": len(records),
            "systems_admitted": int(
                sum(1 for s in manifest_systems if s["lane"] != "excluded")
            ),
            "systems_excluded": int(lane_counts.get("excluded", 0)),
            "component_rows_total": len(rows),
            "component_rows_admitted": len(admitted_rows),
            "component_rows_excluded": len(excluded_rows),
            "luminosity_direct_observation": int(
                lum_classes.get("direct_observation", 0)
            ),
            "luminosity_derived": int(lum_classes.get("derived_luminosity", 0)),
            "lane_system_counts": dict(sorted(lane_counts.items())),
            "exclusion_reason_counts": dict(sorted(exclusion_reasons.items())),
        },
        "rows": rows,
    }

    manifest_doc = {
        "manifest_id": "TFA-STELLAR-ML-DEBCAT-HOLDOUT-MANIFEST",
        "schema_version": "0.1.0",
        "task_id": "TASK-0708",
        "campaign_profile_id": "textbook-formula-audit",
        "created_by": {"contributor_id": "roman", "agent_id": "claude"},
        "generated_at": generated_at,
        "freeze": {
            "frozen": True,
            "frozen_at": generated_at,
            "frozen_before_residual_inspection": True,
            "no_alpha_fit_performed": True,
            "no_residual_inspection_performed": True,
        },
        "split_policy": {
            "primary_key": "physical_binary_system_id",
            "method": "deterministic_sha256_of_system_id_mod_10",
            "rule": (
                "bucket = int(sha256(system_id).hexdigest(), 16) % 10; "
                "0-4 -> train, 5-6 -> validation, 7-9 -> holdout"
            ),
            "proportions_target": LANE_PROPORTIONS,
            "value_blind": True,
            "no_leakage_rule": (
                "All components of one physical binary share one lane; ambiguous "
                "or fully-inadmissible systems go to excluded."
            ),
        },
        "mass_band_thresholds_solar": [
            {"band": name, "min": lo, "max": (None if hi == math.inf else hi)}
            for name, lo, hi in MASS_BANDS
        ],
        "lane_system_counts": dict(sorted(lane_counts.items())),
        "systems": manifest_systems,
    }

    return rows_doc, manifest_doc


# --- I/O ----------------------------------------------------------------------

def _dump_yaml(doc: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.safe_dump(
            doc,
            fh,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
            width=100,
        )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--debs-dat", required=True, type=Path,
        help="Path to a locally fetched DEBCat debs.dat (not committed).",
    )
    parser.add_argument(
        "--out-rows", required=True, type=Path,
        help="Output path for the normalized component-rows YAML.",
    )
    parser.add_argument(
        "--out-manifest", required=True, type=Path,
        help="Output path for the frozen holdout manifest YAML.",
    )
    parser.add_argument(
        "--expected-sha256", default=PINNED_SHA256,
        help="Override the pinned checksum (default: TASK-0628 pinned value).",
    )
    parser.add_argument(
        "--generated-at", default=None,
        help="Override the ISO-8601 generation timestamp (for reproducible runs).",
    )
    args = parser.parse_args(argv)

    raw_bytes = args.debs_dat.read_bytes()
    actual_sha = hashlib.sha256(raw_bytes).hexdigest()
    if actual_sha != args.expected_sha256:
        print(
            "CHECKSUM MISMATCH - refusing to curate drifted source data.\n"
            f"  expected: {args.expected_sha256}\n  actual:   {actual_sha}",
            file=sys.stderr,
        )
        return 2

    generated_at = args.generated_at or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    text = raw_bytes.decode("utf-8")
    records = parse_debs_dat(text)
    rows_doc, manifest_doc = build_rows_and_manifest(
        records, generated_at=generated_at
    )

    _dump_yaml(rows_doc, args.out_rows)
    _dump_yaml(manifest_doc, args.out_manifest)

    c = rows_doc["counts"]
    print(f"checksum OK ({actual_sha[:12]}...)")
    print(
        f"systems_total={c['systems_total']} "
        f"admitted={c['systems_admitted']} excluded={c['systems_excluded']}"
    )
    print(
        f"component_rows admitted={c['component_rows_admitted']} "
        f"excluded={c['component_rows_excluded']}"
    )
    print(f"luminosity direct={c['luminosity_direct_observation']} "
          f"derived={c['luminosity_derived']}")
    print(f"lane_system_counts={c['lane_system_counts']}")
    print(f"exclusion_reason_counts={c['exclusion_reason_counts']}")
    print(f"wrote {args.out_rows}")
    print(f"wrote {args.out_manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
