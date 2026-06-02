"""Ingest a pinned NASA Exoplanet Archive PSCompPars snapshot.

This script is intentionally narrow for TASK-0353. It reads the committed
ADQL and mapping contracts, performs one TAP retrieval, writes the raw CSV,
normalizes rows into the exoplanet mass-radius schema, and writes a review
summary. It does not compute baseline metrics or residuals.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from physics_lab.datasets.exoplanets import (  # noqa: E402
    load_and_filter,
    normalized_snapshot_checksum,
    summarize,
)
from physics_lab.registry.validation import validate_document  # noqa: E402


SOURCE_ID = "EXO-SRC-CLASS-001"
TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
QUERY_PATH = ROOT / "data" / "exoplanets" / "snapshot_plans" / "pscomppars_query.adql"
METHOD_MAP_PATH = (
    ROOT / "data" / "exoplanets" / "snapshot_plans" / "pscomppars_method_map.yaml"
)
MASS_MAP_PATH = (
    ROOT / "data" / "exoplanets" / "snapshot_plans" / "pscomppars_mass_provenance_map.yaml"
)
RAW_DIR = ROOT / "data" / "exoplanets" / "raw"
DATASET_PATH = ROOT / "data" / "exoplanets" / "exo-0001-pscomppars-snapshot.yaml"
SOURCE_MANIFEST_PATH = ROOT / "data" / "exoplanets" / "source_manifest.yaml"
REVIEW_PATH = ROOT / "docs" / "reviews" / "exoplanet-pscomppars-snapshot-ingestion.md"


EXPECTED_COLUMNS = [
    "pl_name",
    "hostname",
    "default_flag",
    "soltype",
    "disc_year",
    "discoverymethod",
    "pl_orbper",
    "pl_orbsmax",
    "pl_orbeccen",
    "pl_eqt",
    "pl_insol",
    "pl_rade",
    "pl_radeerr1",
    "pl_radeerr2",
    "pl_radj",
    "pl_bmasse",
    "pl_bmasseerr1",
    "pl_bmasseerr2",
    "pl_bmassj",
    "pl_bmassprov",
    "pl_dens",
    "st_spectype",
    "st_teff",
    "st_tefferr1",
    "st_tefferr2",
    "st_rad",
    "st_mass",
    "st_met",
    "st_meterr1",
    "st_meterr2",
    "st_age",
    "st_logg",
    "sy_dist",
    "pl_refname",
    "st_refname",
    "disc_refname",
]


def _strip_adql_comments(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines() if not line.strip().startswith("--")
    ).strip()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_relative(path: Path) -> str:
    return str(Path(path).resolve().relative_to(ROOT))


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        payload = yaml.safe_load(fh)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping in {path}")
    return payload


def _load_maps() -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    method_payload = _load_yaml(METHOD_MAP_PATH)
    mass_payload = _load_yaml(MASS_MAP_PATH)
    method_map = method_payload.get("mapping")
    mass_map = mass_payload.get("mapping")
    if not isinstance(method_map, dict) or not isinstance(mass_map, dict):
        raise ValueError("Mapping contract files must contain mapping dictionaries")
    return dict(method_map), dict(mass_map)


def _fetch_snapshot(query: str, timeout_seconds: int) -> bytes:
    data = urllib.parse.urlencode(
        {
            "REQUEST": "doQuery",
            "LANG": "ADQL",
            "FORMAT": "csv",
            "QUERY": query,
        }
    ).encode("utf-8")
    request = urllib.request.Request(TAP_URL, data=data)
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    request.add_header("User-Agent", "autonomous-physics-lab-task-0353")
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        body = response.read()
        status = getattr(response, "status", None)
        if status != 200:
            raise RuntimeError(f"TAP request returned HTTP status {status}")
        return body


def _read_csv_rows(raw_path: Path) -> list[dict[str, str]]:
    with raw_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise ValueError(
                "Unexpected CSV columns from PSCompPars snapshot: "
                f"{reader.fieldnames!r}"
            )
        return [dict(row) for row in reader]


def _none_if_blank(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


def _float_or_none(value: str | None) -> float | None:
    stripped = _none_if_blank(value)
    if stripped is None:
        return None
    return float(stripped)


def _int_or_none(value: str | None) -> int | None:
    stripped = _none_if_blank(value)
    if stripped is None:
        return None
    return int(float(stripped))


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "unnamed"


def _radius_class(discovery_method: str, radius_value: float | None) -> str:
    if radius_value is None:
        return "not_measured"
    if discovery_method in {"transit", "transit_timing_variation"}:
        return "transit_radius"
    if discovery_method == "direct_imaging":
        return "direct_imaging_radius"
    return "model_inferred"


def _radius_method_label(discovery_method_raw: str, radius_class: str) -> str | None:
    if radius_class == "not_measured":
        return None
    if radius_class == "model_inferred":
        return f"radius present in PSCompPars but discovery method is {discovery_method_raw}"
    return f"{discovery_method_raw} radius from PSCompPars composite row"


def _host_notes(row: dict[str, str]) -> str | None:
    parts: list[str] = []
    if _none_if_blank(row.get("st_refname")):
        parts.append(f"st_refname={row['st_refname']}")
    if _none_if_blank(row.get("st_logg")):
        parts.append(f"st_logg={row['st_logg']}")
    return "; ".join(parts) if parts else None


def _source_table_ref(row: dict[str, str]) -> str:
    parts = [
        f"pl_refname={_none_if_blank(row.get('pl_refname')) or 'not reported'}",
        f"disc_refname={_none_if_blank(row.get('disc_refname')) or 'not reported'}",
    ]
    return "; ".join(parts)


def _inclusion_decision(
    *,
    row: dict[str, str],
    mass_class: str,
    radius_class: str,
    mass_value: float | None,
    radius_value: float | None,
) -> tuple[str, str]:
    if row.get("soltype") != "Published Confirmed":
        return "excluded", "solution_type_not_confirmed"
    if row.get("pl_bmassprov") == "Msin(i)/sin(i)":
        return "excluded", "mass_provenance_requires_source_specific_review"
    if mass_class == "model_inferred":
        return "excluded", "mass_inferred_from_mass_radius_relationship"
    if radius_class == "model_inferred":
        return "excluded", "radius_inferred_from_non_transit_method"
    if mass_value is None and radius_value is None:
        return "excluded", "mass_and_radius_absent"
    return "included", "pre_quality_filter_included"


def _normalize_rows(
    rows: list[dict[str, str]],
    method_map: dict[str, str],
    mass_map: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    unknown_methods = sorted(
        {
            row.get("discoverymethod", "")
            for row in rows
            if row.get("discoverymethod", "") not in method_map
        }
    )
    unknown_mass_provenance = sorted(
        {
            row.get("pl_bmassprov", "")
            for row in rows
            if row.get("pl_bmassprov", "") not in mass_map
        }
    )
    duplicate_names = sorted(
        name for name, count in Counter(row["pl_name"] for row in rows).items() if count > 1
    )
    if unknown_methods or unknown_mass_provenance or duplicate_names:
        raise ValueError(
            "Stop condition before normalization: "
            f"unknown_methods={unknown_methods!r}, "
            f"unknown_mass_provenance={unknown_mass_provenance!r}, "
            f"duplicate_names={duplicate_names[:10]!r}"
        )

    for index, row in enumerate(rows, start=1):
        planet_name = row["pl_name"]
        detection_method_raw = row["discoverymethod"]
        detection_method = method_map[detection_method_raw]
        mass_provenance_raw = row.get("pl_bmassprov", "")
        mass_rule = mass_map[mass_provenance_raw]

        mass_value = _float_or_none(row.get("pl_bmasse"))
        radius_value = _float_or_none(row.get("pl_rade"))
        mass_class = str(mass_rule["mass_class"])
        radius_class = _radius_class(detection_method, radius_value)
        row_class_key = (
            "row_class_when_radius_present"
            if radius_value is not None
            else "row_class_when_radius_absent"
        )
        row_class = str(mass_rule[row_class_key])
        inclusion_status, inclusion_reason = _inclusion_decision(
            row=row,
            mass_class=mass_class,
            radius_class=radius_class,
            mass_value=mass_value,
            radius_value=radius_value,
        )

        entry = {
            "row_id": f"EXO-0001-{index:05d}-{_slugify(planet_name)}",
            "row_class": row_class,
            "planet_name": planet_name,
            "planet_alt_names": [],
            "host_star": {
                "name": row["hostname"],
                "spectral_type": _none_if_blank(row.get("st_spectype")),
                "effective_temperature_K": _float_or_none(row.get("st_teff")),
                "stellar_mass_msun": _float_or_none(row.get("st_mass")),
                "stellar_radius_rsun": _float_or_none(row.get("st_rad")),
                "metallicity_fe_h": _float_or_none(row.get("st_met")),
                "stellar_age_gyr": _float_or_none(row.get("st_age")),
                "notes": _host_notes(row),
            },
            "detection_method": detection_method,
            "mass": {
                "value": mass_value,
                "unit": "msini_mearth" if mass_class == "minimum_mass_msini" else "mearth",
                "uncertainty_upper": _float_or_none(row.get("pl_bmasseerr1")),
                "uncertainty_lower": _float_or_none(row.get("pl_bmasseerr2")),
                "uncertainty_semantics": "1-sigma asymmetric uncertainty per NASA Exoplanet Archive PS table",
                "mass_class": mass_class,
                "mass_method_label": mass_provenance_raw or None,
            },
            "radius": {
                "value": radius_value,
                "unit": "rearth",
                "uncertainty_upper": _float_or_none(row.get("pl_radeerr1")),
                "uncertainty_lower": _float_or_none(row.get("pl_radeerr2")),
                "uncertainty_semantics": "1-sigma asymmetric uncertainty per NASA Exoplanet Archive PS table",
                "radius_class": radius_class,
                "radius_method_label": _radius_method_label(
                    detection_method_raw,
                    radius_class,
                ),
            },
            "equilibrium_temperature_K": _float_or_none(row.get("pl_eqt")),
            "irradiation_flux_earth_units": _float_or_none(row.get("pl_insol")),
            "orbital_period_days": _float_or_none(row.get("pl_orbper")),
            "orbital_semimajor_axis_au": _float_or_none(row.get("pl_orbsmax")),
            "discovery_year": _int_or_none(row.get("disc_year")),
            "source_id": SOURCE_ID,
            "source_table_ref": _source_table_ref(row),
            "inclusion_status": inclusion_status,
            "inclusion_reason": inclusion_reason,
            "provenance_notes": (
                "Normalized from NASA Exoplanet Archive ps table with default_flag=1; "
                f"soltype={row.get('soltype')}; pl_bmassprov={mass_provenance_raw or 'blank'}; "
                f"discoverymethod={detection_method_raw}."
            ),
        }
        entries.append(entry)

    summary = {
        "source_row_count": len(rows),
        "solution_type_counts": dict(sorted(Counter(row.get("soltype", "") for row in rows).items())),
        "raw_detection_method_counts": dict(
            sorted(Counter(row.get("discoverymethod", "") for row in rows).items())
        ),
        "raw_mass_provenance_counts": dict(
            sorted(Counter(row.get("pl_bmassprov", "") for row in rows).items())
        ),
    }
    return entries, summary


def _write_source_manifest(
    *,
    retrieval_timestamp: str,
    raw_path: Path,
    raw_checksum: str,
    normalized_checksum: str | None,
    row_count: int,
    included_count: int,
    excluded_count: int,
) -> None:
    manifest = {
        "manifest_id": "EXO-MR-SOURCE-MANIFEST-0001",
        "schema_version": "0.1.0",
        "task_id": "TASK-0353",
        "status": "pinned_snapshot_ingested",
        "campaign_profile_id": "exoplanet-mass-radius",
        "live_fetch_allowed": False,
        "benchmark_allowed": False,
        "claim_promotion_allowed": False,
        "sources": [
            {
                "source_id": SOURCE_ID,
                "source_family": "NASA Exoplanet Archive Planetary Systems table",
                "title": "NASA Exoplanet Archive Planetary Systems Composite Parameters snapshot",
                "homepage": "https://exoplanetarchive.ipac.caltech.edu/",
                "documentation": "https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html",
                "access_surface": TAP_URL,
                "query_contract": _repo_relative(QUERY_PATH),
                "method_map": _repo_relative(METHOD_MAP_PATH),
                "mass_provenance_map": _repo_relative(MASS_MAP_PATH),
                "retrieval_date_utc": retrieval_timestamp,
                "raw_snapshot_path": _repo_relative(raw_path),
                "raw_checksum_sha256": raw_checksum,
                "normalized_snapshot_path": _repo_relative(DATASET_PATH),
                "normalized_checksum_sha256": normalized_checksum,
                "row_count": row_count,
                "included_post_filter_count": included_count,
                "excluded_count": excluded_count,
                "license_note": (
                    "NASA Exoplanet Archive public data; preserve per-row "
                    "pl_refname, st_refname, and disc_refname attribution."
                ),
                "archive_policy": "committed_raw_csv_plus_normalized_yaml",
                "value_status": "real_catalog_values_pinned_no_metrics",
                "forbidden_uses": [
                    "baseline_metrics_in_this_task",
                    "habitability_or_biosignature_inference",
                    "target_prioritization",
                    "claim_promotion",
                ],
            }
        ],
    }
    SOURCE_MANIFEST_PATH.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )


def _write_review(
    *,
    retrieval_timestamp: str,
    raw_path: Path,
    raw_checksum: str,
    normalized_checksum: str,
    raw_summary: dict[str, Any],
    filter_summary: dict[str, Any],
) -> None:
    REVIEW_PATH.write_text(
        "\n".join(
            [
                "# Exoplanet PSCompPars Snapshot Ingestion",
                "",
                "**Task:** `TASK-0353`",
                "**Status:** review (pinned real catalog snapshot ingested)",
                f"**Retrieval timestamp:** `{retrieval_timestamp}`",
                "**Verdict:** `VALID` as a pinned dataset artifact; no benchmark run.",
                "",
                "## Scope",
                "",
                "This review records the first pinned NASA Exoplanet Archive "
                "Planetary Systems snapshot for the Exoplanet Mass-Radius "
                "campaign. It commits a raw CSV and normalized YAML dataset, "
                "but does not compute residuals, plots, baseline metrics, "
                "habitability analysis, target prioritization, prediction "
                "entries, claims, or canonical results.",
                "",
                "## Source And Pinning",
                "",
                f"- Source family: `{SOURCE_ID}`",
                f"- TAP endpoint: `{TAP_URL}`",
                f"- Query contract: `{_repo_relative(QUERY_PATH)}`",
                f"- Raw snapshot: `{_repo_relative(raw_path)}`",
                f"- Raw SHA-256: `{raw_checksum}`",
                f"- Normalized snapshot: `{_repo_relative(DATASET_PATH)}`",
                f"- Normalized SHA-256: `{normalized_checksum}`",
                "",
                "## Counts",
                "",
                "```json",
                json.dumps(filter_summary, indent=2, sort_keys=True),
                "```",
                "",
                "## Raw Source Diagnostics",
                "",
                "```json",
                json.dumps(raw_summary, indent=2, sort_keys=True),
                "```",
                "",
                "## Method",
                "",
                "1. Read the committed TASK-0345 ADQL query and mapping files.",
                "2. Retrieved the TAP CSV once for this task branch and recorded "
                "the UTC timestamp and checksum.",
                "3. Normalized each row into the exoplanet mass-radius schema.",
                "4. Preserved every row with explicit `inclusion_status` and "
                "`inclusion_reason` instead of silently dropping rows.",
                "5. Ran the existing loader filter chain to produce pre/post "
                "quality-filter counts.",
                "",
                "## Limitations",
                "",
                "- The dataset is a catalog snapshot, not a benchmark result.",
                "- Composite rows preserve source references but are not "
                "per-publication primary-table extractions.",
                "- Model-inferred masses and non-transit-derived radii are "
                "explicitly excluded from the production residual axis.",
                "- True-mass and `M sin i` rows remain separated by `mass_class` "
                "and must not be averaged in a future benchmark.",
                "- Planet-class labels are intentionally not assigned at ingestion "
                "time; class binning belongs to a later benchmark task.",
                "",
                "## What This Review Did Not Do",
                "",
                "- It did not run Chen-Kipping or other mass-radius baselines.",
                "- It did not compute residuals, metrics, or plots.",
                "- It did not add prediction registry entries.",
                "- It did not promote claims or knowledge entries.",
                "- It did not add habitability, biosignature, or target-priority "
                "fields.",
                "",
                "## Next Step",
                "",
                "A later benchmark task may consume this pinned snapshot only "
                "after maintainer review. That task must keep true-mass, "
                "minimum-mass, radius-only, and model-inferred rows on separate "
                "diagnostic axes per the baseline protocol.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _build_payload(
    *,
    retrieval_timestamp: str,
    raw_checksum: str,
    normalized_checksum: str | None,
    entries: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "dataset_id": "exo-0001-pscomppars-snapshot",
        "title": "NASA Exoplanet Archive PSCompPars pinned mass-radius snapshot",
        "status": "curated",
        "description": (
            "Pinned NASA Exoplanet Archive Planetary Systems default-row "
            "snapshot for Exoplanet Mass-Radius source review. This dataset "
            "preserves row classes and inclusion decisions but is not a "
            "benchmark result."
        ),
        "source_policy": (
            "Retrieved once from the NASA Exoplanet Archive TAP service using "
            "the committed TASK-0345 query contract. Raw CSV and normalized "
            "YAML are committed with checksums; live external fetches are "
            "forbidden for downstream benchmarks."
        ),
        "snapshot_provenance": {
            "source_family_id": SOURCE_ID,
            "source_locator": TAP_URL,
            "retrieval_date_utc": retrieval_timestamp,
            "release_date_or_publication_date": None,
            "snapshot_kind": "composite_catalog_snapshot",
            "live_external_fetch_allowed": False,
            "raw_checksum_sha256": raw_checksum,
            "normalized_checksum_sha256": normalized_checksum,
            "parser_or_normalizer": "scripts/ingest_exoplanet_pscomppars_snapshot.py",
            "license_or_reuse_notes": (
                "NASA Exoplanet Archive public data; preserve per-row source "
                "references from pl_refname, st_refname, and disc_refname."
            ),
        },
        "row_class_coverage": sorted({entry["row_class"] for entry in entries}),
        "entries": entries,
        "limitations": [
            "Composite catalog snapshot; not a per-publication primary-table extraction.",
            "No baseline metrics, residuals, habitability analysis, or claim promotion.",
            "Planet-class binning is intentionally deferred to a later benchmark task.",
        ],
        "fake_source_warning": None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--skip-fetch", action="store_true")
    parser.add_argument("--raw-path", type=Path)
    args = parser.parse_args(argv)

    query_text = QUERY_PATH.read_text(encoding="utf-8")
    query = _strip_adql_comments(query_text)
    retrieval_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    retrieval_slug = retrieval_timestamp.replace("-", "").replace(":", "").replace("T", "T").removesuffix("Z")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = args.raw_path or RAW_DIR / f"exo-pscomppars-{retrieval_slug}Z.csv"

    if not args.skip_fetch:
        body = _fetch_snapshot(query, args.timeout_seconds)
        text_prefix = body[:256].decode("utf-8", "replace").lower()
        if "<html" in text_prefix or "error" in text_prefix[:80]:
            raise RuntimeError(f"TAP response did not look like CSV: {body[:256]!r}")
        raw_path.write_bytes(body)
    elif not raw_path.exists():
        raise FileNotFoundError(raw_path)
    else:
        match = re.search(r"exo-pscomppars-(\d{8}T\d{6})Z\.csv$", raw_path.name)
        if match:
            raw_stamp = datetime.strptime(match.group(1), "%Y%m%dT%H%M%S")
            retrieval_timestamp = raw_stamp.replace(tzinfo=timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )

    raw_checksum = _sha256_file(raw_path)
    rows = _read_csv_rows(raw_path)
    method_map, mass_map = _load_maps()
    entries, raw_summary = _normalize_rows(rows, method_map, mass_map)

    payload = _build_payload(
        retrieval_timestamp=retrieval_timestamp,
        raw_checksum=raw_checksum,
        normalized_checksum=None,
        entries=entries,
    )
    payload["snapshot_provenance"]["normalized_checksum_sha256"] = (
        normalized_snapshot_checksum(payload)
    )
    validate_document(payload, "exoplanet_mass_radius", DATASET_PATH)
    DATASET_PATH.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=False, width=100),
        encoding="utf-8",
    )
    normalized_checksum = _sha256_file(DATASET_PATH)

    filtered = load_and_filter(DATASET_PATH)
    filter_summary = summarize(filtered)
    _write_source_manifest(
        retrieval_timestamp=retrieval_timestamp,
        raw_path=raw_path,
        raw_checksum=raw_checksum,
        normalized_checksum=normalized_checksum,
        row_count=len(entries),
        included_count=filtered.post_filter_included_count,
        excluded_count=len(filtered.excluded_rows),
    )
    _write_review(
        retrieval_timestamp=retrieval_timestamp,
        raw_path=raw_path,
        raw_checksum=raw_checksum,
        normalized_checksum=normalized_checksum,
        raw_summary=raw_summary,
        filter_summary=filter_summary,
    )
    print(json.dumps(filter_summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
