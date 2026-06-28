"""Build the CHIME/FRB Catalog 2 exposure-only baseline artifact.

This helper intentionally does not vendor the upstream catalog. It fetches or
reads a local copy, verifies the pinned SHA-256, and writes metadata-only APL
artifacts with aggregate source-level calibration metrics.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import math
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import yaml

TASK_ID = "TASK-0852"
SOURCE_URL = (
    "https://cadc-west-01.canfar.net/vault/files/"
    "AstroDataCitationDOI/CISTI.CANFAR/25.0066/data/table/chimefrbcat2.csv"
)
STORAGE_UI_URL = (
    "https://www.canfar.net/storage/vault/list/"
    "AstroDataCitationDOI/CISTI.CANFAR/25.0066/data/table"
)
VOSPACE_URI = (
    "vos://cadc.nrc.ca~vault/"
    "AstroDataCitationDOI/CISTI.CANFAR/25.0066/data/table/chimefrbcat2.csv"
)
EXPECTED_SHA256 = "5108ada779d279a2547d9f9e73ae25bfdd40d8496d6ba7255ec29c6629057a48"
EXPECTED_BYTES = 4_057_396
HEADER_MD5_BASE64 = "6OhFih4Hv5kP3BS/UaygSA=="
HEADER_LAST_MODIFIED = "Mon, 05 Jan 2026 23:16:21 GMT"


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_csv(path: Path) -> None:
    request = Request(SOURCE_URL, headers={"User-Agent": "APL-frb-catalog2-checksum/1.0"})
    path.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(request, timeout=60) as response, path.open("wb") as fh:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            fh.write(chunk)


def finite_float(value: str) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(parsed) or math.isinf(parsed):
        return None
    return parsed


def read_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def source_key(row: dict[str, str]) -> str:
    return row.get("repeater_name", "").strip() or row.get("tns_name", "").strip()


def build_source_entries(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    eligible_rows = [row for row in rows if row.get("excluded_flag") == "0"]
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in eligible_rows:
        key = source_key(row)
        if key:
            grouped[key].append(row)

    entries: list[dict[str, Any]] = []
    for key, source_rows in grouped.items():
        exposures: list[float] = []
        mjds: list[float] = []
        for row in source_rows:
            up = finite_float(row.get("exp_up", ""))
            low = finite_float(row.get("exp_low", ""))
            if up is not None and low is not None:
                exposures.append(up + low)
            mjd = finite_float(row.get("mjd_inf", "")) or finite_float(row.get("mjd_400", ""))
            if mjd is not None:
                mjds.append(mjd)
        if not exposures:
            continue
        entries.append(
            {
                "source_id": key,
                "exposure_total": max(exposures),
                "score_log1p_exposure_total": math.log1p(max(exposures)),
                "is_repeater": any(row.get("repeater_name", "").strip() for row in source_rows),
                "eligible_burst_count": len(source_rows),
                "first_detection_mjd": min(mjds) if mjds else None,
            }
        )
    return entries


def quantile_bins(entries: list[dict[str, Any]], bins: int = 5) -> list[dict[str, Any]]:
    ordered = sorted(entries, key=lambda item: item["exposure_total"])
    output = []
    n = len(ordered)
    for index in range(bins):
        lo = index * n // bins
        hi = (index + 1) * n // bins
        chunk = ordered[lo:hi]
        repeaters = sum(1 for item in chunk if item["is_repeater"])
        output.append(
            {
                "bin": index + 1,
                "source_count": len(chunk),
                "exposure_min": round(chunk[0]["exposure_total"], 6),
                "exposure_max": round(chunk[-1]["exposure_total"], 6),
                "repeater_sources": repeaters,
                "observed_repeater_rate": round(repeaters / len(chunk), 6),
            }
        )
    return output


def auc_rank(entries: list[dict[str, Any]]) -> float:
    scores = sorted((item["score_log1p_exposure_total"], item["is_repeater"]) for item in entries)
    positive_count = sum(1 for _, label in scores if label)
    negative_count = len(scores) - positive_count
    rank_sum = 0.0
    index = 0
    rank = 1
    while index < len(scores):
        end = index + 1
        while end < len(scores) and scores[end][0] == scores[index][0]:
            end += 1
        average_rank = (rank + rank + (end - index) - 1) / 2
        positives_in_tie = sum(1 for _, label in scores[index:end] if label)
        rank_sum += positives_in_tie * average_rank
        rank += end - index
        index = end
    return (rank_sum - positive_count * (positive_count + 1) / 2) / (positive_count * negative_count)


def logistic_one_feature(entries: list[dict[str, Any]]) -> dict[str, float]:
    xs = [item["score_log1p_exposure_total"] for item in entries]
    ys = [1.0 if item["is_repeater"] else 0.0 for item in entries]
    mean_x = sum(xs) / len(xs)
    std_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs) / len(xs))
    zs = [(x - mean_x) / std_x for x in xs]
    positive_count = sum(ys)
    b0 = math.log((positive_count + 0.5) / (len(ys) - positive_count + 0.5))
    b1 = 0.0
    for _ in range(30):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for z, y in zip(zs, ys, strict=True):
            eta = b0 + b1 * z
            p = 1.0 / (1.0 + math.exp(-eta))
            w = p * (1.0 - p)
            g0 += y - p
            g1 += (y - p) * z
            h00 -= w
            h01 -= w * z
            h11 -= w * z * z
        det = h00 * h11 - h01 * h01
        if abs(det) < 1e-12:
            break
        delta_b0 = (g0 * h11 - g1 * h01) / det
        delta_b1 = (h00 * g1 - h01 * g0) / det
        b0 -= delta_b0
        b1 -= delta_b1
        if max(abs(delta_b0), abs(delta_b1)) < 1e-10:
            break
    return {
        "intercept": round(b0, 12),
        "standardized_log_exposure_coefficient": round(b1, 12),
        "odds_ratio_per_1sd_log_exposure": round(math.exp(b1), 12),
    }


def build_artifacts(csv_path: Path, generated_at_utc: str) -> tuple[dict[str, Any], dict[str, Any]]:
    rows = read_rows(csv_path)
    entries = build_source_entries(rows)
    repeaters = sum(1 for item in entries if item["is_repeater"])
    bins = quantile_bins(entries)
    logistic = logistic_one_feature(entries)
    baseline = {
        "artifact_kind": "frb_catalog2_temporal_split_exposure_baseline",
        "task_id": TASK_ID,
        "status": "frozen_baseline_artifact",
        "generated_at_utc": generated_at_utc,
        "source_manifest": "data/radio_transients/frb_catalog2_source_manifest.yaml",
        "source_csv": {
            "vospace_uri": VOSPACE_URI,
            "storage_file_endpoint": SOURCE_URL,
            "expected_sha256": EXPECTED_SHA256,
            "expected_bytes": EXPECTED_BYTES,
        },
        "temporal_split_spec": {
            "split_name": "frb_catalog2_version_locked_repeater_reveal_split_v0",
            "date_locking_alone_suffices": False,
            "version_locking_required": True,
            "reason": (
                "Catalog 2 reprocesses earlier bursts and source associations; a pre-T feature "
                "view read from one late table leaks future exposure, morphology, and repeater decisions."
            ),
            "pre_t_feature_version": (
                "A catalog version or reconstruction that contains only information available at T; "
                "for a retrospective pilot, Catalog 1-native fields or a T-reconstructed Catalog 2 "
                "view are allowed, but late Catalog 2 morphology/source-association fields are not."
            ),
            "label_version": (
                "A strictly later catalog version or external reveal record. A source is positive only "
                "when repeat evidence is published after T and is not encoded in the pre-T feature view."
            ),
            "first_detection_time": "minimum finite mjd_inf, falling back to mjd_400, over bursts assigned to a source",
            "forbidden_pre_t_features": [
                "late-catalog repeater_name labels",
                "post-T source association updates",
                "post-T morphology reprocessing products",
                "full-window exposure summaries when the pre-T view needs T-truncated exposure",
            ],
        },
        "exposure_only_baseline": {
            "baseline_name": "log1p_total_exposure_only_v0",
            "score": "log1p(max(exp_up + exp_low) over population-eligible bursts for the source)",
            "eligibility_filter": "excluded_flag == '0'; sources require finite exp_up and exp_low",
            "label": "source has non-empty repeater_name in Catalog 2 population-eligible rows",
            "morphology_features_used": [],
            "future_gate": (
                "Any future morphology model must beat this exposure-only baseline out-of-sample on "
                "the version-locked split before morphology evidence is interpreted."
            ),
        },
        "aggregate_counts": {
            "raw_burst_rows": len(rows),
            "population_eligible_burst_rows": sum(1 for row in rows if row.get("excluded_flag") == "0"),
            "source_rows_with_finite_exposure": len(entries),
            "repeater_sources_with_finite_exposure": repeaters,
            "nonrepeater_sources_with_finite_exposure": len(entries) - repeaters,
        },
        "calibration": {
            "quintile_bins_by_exposure_total": bins,
            "top_vs_bottom_quintile_rate_ratio": round(
                bins[-1]["observed_repeater_rate"] / bins[0]["observed_repeater_rate"], 6
            ),
            "auc_rank_log1p_exposure": round(auc_rank(entries), 12),
            "logistic_summary": logistic,
            "interpretation": (
                "Exposure has the expected positive but weak source-level association with observed "
                "repetition. The top exposure quintile repeats more often than the bottom quintile; "
                "decile-scale calibration remains noisy because only 81 eligible repeater sources are present."
            ),
        },
        "limitations": [
            "The calibration uses Catalog 2 full-window exposure summaries, so it is a selection-effect gate, not a no-leakage morphology benchmark.",
            "T-truncated per-source exposure still requires a version-locked reconstruction before any future predictive split is scored.",
            "No morphology features, dynamic spectra, PRED entry, RESULT artifact, or claim transition are produced by this task.",
            "The upstream dataset has public read access but no explicit redistribution license in DataCite rightsList, so raw rows are not committed.",
        ],
        "verdict": "SPLIT_AND_EXPOSURE_BASELINE_READY",
    }
    manifest = {
        "manifest_kind": "metadata_only_source_manifest",
        "manifest_id": "FRB-CAT2-SOURCE-0001",
        "task_id": TASK_ID,
        "status": "pinned_public_locator",
        "generated_at_utc": generated_at_utc,
        "source": {
            "title": "The Second CHIME/FRB Catalog of Fast Radio Bursts",
            "dataset_doi": "10.11570/25.0066",
            "paper_doi": "10.3847/1538-4365/ae3828",
            "arxiv": "2601.09399",
            "publisher": "CADC",
            "publication_year": 2025,
            "citation": "The CHIME/FRB Collaboration, The Second CHIME/FRB Catalog of Fast Radio Bursts, ApJS, DOI 10.3847/1538-4365/ae3828; dataset DOI 10.11570/25.0066.",
        },
        "artifact": {
            "path_in_vault": "/AstroDataCitationDOI/CISTI.CANFAR/25.0066/data/table/chimefrbcat2.csv",
            "vospace_uri": VOSPACE_URI,
            "storage_ui_directory": STORAGE_UI_URL,
            "storage_file_endpoint": SOURCE_URL,
            "filename": "chimefrbcat2.csv",
            "file_size_bytes": EXPECTED_BYTES,
            "sha256": EXPECTED_SHA256,
            "http_digest_md5_base64": HEADER_MD5_BASE64,
            "last_modified": HEADER_LAST_MODIFIED,
            "value_bearing": True,
            "committed_to_repo": False,
        },
        "rights_and_access": {
            "read_access": "public",
            "canfar_owner": "ssiegel",
            "datacite_rights_list": [],
            "local_analysis": "allowed_for_public_source_with_citation",
            "source_bytes_redistribution": "not_cleared_no_explicit_open_data_license",
            "derived_rows_publication": "not_cleared_for_bulk_rows_without_maintainer_permission_or_license",
            "repo_policy": "metadata_only_no_raw_catalog_bytes_vendored",
        },
        "fetch_verify": {
            "download_command": (
                "python scripts/run_frb_catalog2_exposure_baseline.py "
                "--download-csv C:/tmp/chimefrbcat2.csv --csv C:/tmp/chimefrbcat2.csv"
            ),
            "verify_command": (
                "python scripts/run_frb_catalog2_exposure_baseline.py "
                "--csv C:/tmp/chimefrbcat2.csv --output-dir data/radio_transients"
            ),
            "expected_sha256": EXPECTED_SHA256,
            "expected_bytes": EXPECTED_BYTES,
        },
        "next_allowed_workflow_step": (
            "Use the pinned CSV only as an external input to reconstruct a version-locked, "
            "T-truncated exposure split before any morphology benchmark or PRED entry."
        ),
    }
    return manifest, baseline


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=False), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True, help="Local CHIME/FRB Catalog 2 CSV path.")
    parser.add_argument("--download-csv", type=Path, help="Download the pinned CSV to this path before verification.")
    parser.add_argument("--output-dir", type=Path, default=Path("data/radio_transients"))
    parser.add_argument("--generated-at-utc", default=utc_now())
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.download_csv:
        download_csv(args.download_csv)
    csv_path = args.csv
    actual_bytes = csv_path.stat().st_size
    actual_sha256 = sha256_file(csv_path)
    if actual_bytes != EXPECTED_BYTES:
        raise SystemExit(f"unexpected byte length: {actual_bytes} != {EXPECTED_BYTES}")
    if actual_sha256 != EXPECTED_SHA256:
        raise SystemExit(f"unexpected sha256: {actual_sha256} != {EXPECTED_SHA256}")
    manifest, baseline = build_artifacts(csv_path, args.generated_at_utc)
    write_yaml(args.output_dir / "frb_catalog2_source_manifest.yaml", manifest)
    write_yaml(args.output_dir / "frb_catalog2_temporal_split_exposure_baseline.yaml", baseline)
    print(f"verified_csv_sha256={actual_sha256}")
    print(f"wrote={args.output_dir / 'frb_catalog2_source_manifest.yaml'}")
    print(f"wrote={args.output_dir / 'frb_catalog2_temporal_split_exposure_baseline.yaml'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())