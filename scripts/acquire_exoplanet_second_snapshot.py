"""Acquire the TASK-0565 second PSCompPars exoplanet snapshot.

This runner intentionally stops at source acquisition and deterministic
normalization. It does not score targets, compute residuals, promote claims, or
write prediction/result artifacts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from physics_lab.checksums import sha256_file, sha256_lf_canonical_file  # noqa: E402
from physics_lab.datasets.exoplanets import (  # noqa: E402
    load_and_filter,
    normalized_snapshot_checksum,
    summarize,
)
from physics_lab.registry.validation import validate_document  # noqa: E402
from scripts import ingest_exoplanet_pscomppars_snapshot as first_snapshot  # noqa: E402

TASK_ID = "TASK-0565"
EXPECTED_QUERY_SHA256 = "28b8baf9f14e4ba544658fccbad5ef1271a21f91228afe8afff4db968512acf8"
DATASET_ID = "exo-0002-pscomppars-snapshot"
ROW_ID_PREFIX = "EXO-0002"

QUERY_PATH = ROOT / "data" / "exoplanets" / "snapshot_plans" / "pscomppars_query.adql"
MANIFEST_PATH = ROOT / "data" / "exoplanets" / "second_snapshot_manifest.yaml"
RAW_DIR = ROOT / "data" / "exoplanets" / "raw"
DATASET_PATH = ROOT / "data" / "exoplanets" / "exo-0002-pscomppars-snapshot.yaml"
REVIEW_PATH = ROOT / "docs" / "reviews" / "exoplanet-second-snapshot-source-acquisition.md"


def _repo_relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _retrieval_slug(timestamp: str) -> str:
    return timestamp.replace("-", "").replace(":", "").removesuffix("Z") + "Z"


def _second_snapshot_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    remapped: list[dict[str, Any]] = []
    for entry in entries:
        next_entry = dict(entry)
        row_id = str(next_entry["row_id"])
        next_entry["row_id"] = row_id.replace("EXO-0001-", f"{ROW_ID_PREFIX}-", 1)
        remapped.append(next_entry)
    return remapped


def _build_payload(
    *,
    retrieval_timestamp: str,
    raw_checksum: str,
    normalized_checksum: str | None,
    entries: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "dataset_id": DATASET_ID,
        "title": "NASA Exoplanet Archive PSCompPars pinned second mass-radius snapshot",
        "status": "curated",
        "description": (
            "Second pinned NASA Exoplanet Archive Planetary Systems default-row "
            "snapshot for Exoplanet Mass-Radius source review. This dataset "
            "preserves row classes and inclusion decisions but is not a "
            "benchmark result."
        ),
        "source_policy": (
            "Retrieved once from the NASA Exoplanet Archive TAP service using "
            f"the committed {TASK_ID} query contract. Raw CSV and normalized "
            "YAML are committed with checksums; live external fetches are "
            "forbidden for downstream benchmarks."
        ),
        "snapshot_provenance": {
            "source_family_id": first_snapshot.SOURCE_ID,
            "source_locator": first_snapshot.TAP_URL,
            "retrieval_date_utc": retrieval_timestamp,
            "release_date_or_publication_date": None,
            "snapshot_kind": "composite_catalog_snapshot",
            "live_external_fetch_allowed": False,
            "raw_checksum_sha256": raw_checksum,
            "normalized_checksum_sha256": normalized_checksum,
            "parser_or_normalizer": "scripts/acquire_exoplanet_second_snapshot.py",
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


def _write_manifest(
    *,
    actor: str,
    approval_reference: str,
    retrieval_timestamp: str,
    raw_path: Path,
    raw_checksum: str,
    normalized_file_checksum: str,
    normalized_payload_checksum: str,
    row_count: int,
    included_count: int,
    excluded_count: int,
) -> None:
    with MANIFEST_PATH.open("r", encoding="utf-8") as fh:
        manifest = yaml.safe_load(fh)
    if not isinstance(manifest, dict):
        raise ValueError(f"Expected mapping in {MANIFEST_PATH}")

    manifest["task_id"] = TASK_ID
    manifest["status"] = "pinned_snapshot_acquired"
    manifest["updated_utc"] = retrieval_timestamp
    manifest["scope"] = {
        **manifest["scope"],
        "purpose": (
            "Pinned second NASA Exoplanet Archive PSCompPars source snapshot "
            "for acquisition review only. The artifact contains row values and "
            "checksums, but it does not authorize scoring, predictions, "
            "claims, or knowledge promotion."
        ),
        "live_fetch_performed": True,
        "future_data_values_included": True,
        "raw_snapshot_committed": True,
        "normalized_snapshot_committed": True,
        "benchmark_allowed": False,
        "prediction_registry_allowed": False,
        "claim_promotion_allowed": False,
        "result_artifact_allowed": False,
    }
    manifest["planned_acquisition"] = {
        **manifest["planned_acquisition"],
        "approval_required_before_fetch": False,
        "acquisition_actor": actor,
        "approval_reference": approval_reference,
        "retrieval_timestamp_utc": retrieval_timestamp,
        "response_format": "csv",
        "raw_artifact_path": _repo_relative(raw_path),
        "normalized_artifact_path": _repo_relative(DATASET_PATH),
        "raw_row_count": row_count,
        "normalized_row_count": row_count,
        "included_post_filter_count": included_count,
        "excluded_count": excluded_count,
        "redistribution_decision": "file_committed_with_attribution",
    }
    manifest["checksum_policy"] = {
        **manifest["checksum_policy"],
        "raw_checksum_sha256": raw_checksum,
        "normalized_file_checksum_sha256": normalized_file_checksum,
        "normalized_payload_checksum_sha256": normalized_payload_checksum,
    }
    manifest["no_peek_attestation_by_approved_actor"] = {
        "actor": actor,
        "approval_reference": approval_reference,
        "attested_utc": retrieval_timestamp,
        "statements": [
            "Committed query contract was hash-checked before live acquisition.",
            "Retrieval timestamp, row counts, and checksums were recorded before scoring.",
            "No residual metrics, target scoring, predictions, claims, or result promotion were run.",
            "True-mass, minimum-mass, model-derived, and excluded rows remain separate.",
        ],
    }
    manifest["blocked_until_filled"] = []
    manifest["limitations"] = [
        "This acquisition task does not unblock benchmark scoring by itself.",
        "This file does not promote prediction entries, result artifacts, claims, or knowledge.",
        "Future analysis must keep true-mass and minimum-mass axes separate.",
    ]

    MANIFEST_PATH.write_text(
        yaml.safe_dump(manifest, sort_keys=False, allow_unicode=False, width=100),
        encoding="utf-8",
    )


def _write_review(
    *,
    actor: str,
    approval_reference: str,
    retrieval_timestamp: str,
    raw_path: Path,
    raw_checksum: str,
    normalized_file_checksum: str,
    normalized_payload_checksum: str,
    raw_summary: dict[str, Any],
    filter_summary: dict[str, Any],
) -> None:
    REVIEW_PATH.write_text(
        "\n".join(
            [
                "# Exoplanet Second Snapshot Source Acquisition",
                "",
                f"**Task:** `{TASK_ID}`",
                "**Status:** review (pinned real catalog snapshot acquired)",
                f"**Actor:** `{actor}`",
                f"**Approval reference:** `{approval_reference}`",
                f"**Retrieval timestamp:** `{retrieval_timestamp}`",
                "**Verdict:** `VALID` as a pinned source artifact; no benchmark run.",
                "",
                "## Scope",
                "",
                "This review records the second pinned NASA Exoplanet Archive "
                "Planetary Systems snapshot for the Exoplanet Mass-Radius "
                "campaign. It commits a raw CSV, normalized YAML dataset, and "
                "filled acquisition manifest. It does not compute residuals, "
                "plots, baseline metrics, habitability analysis, target "
                "prioritization, prediction entries, claims, or canonical "
                "results.",
                "",
                "## Source And Pinning",
                "",
                f"- Source family: `{first_snapshot.SOURCE_ID}`",
                f"- TAP endpoint: `{first_snapshot.TAP_URL}`",
                f"- Query contract: `{_repo_relative(QUERY_PATH)}`",
                f"- Query SHA-256: `{EXPECTED_QUERY_SHA256}`",
                f"- Raw snapshot: `{_repo_relative(raw_path)}`",
                f"- Raw SHA-256: `{raw_checksum}`",
                f"- Normalized snapshot: `{_repo_relative(DATASET_PATH)}`",
                f"- Normalized file SHA-256: `{normalized_file_checksum}`",
                f"- Normalized payload SHA-256: `{normalized_payload_checksum}`",
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
                "## No-Peek Attestation",
                "",
                "- The committed ADQL query hash was checked before live acquisition.",
                "- Counts and checksums were recorded before any analysis stage.",
                "- No target scoring, reopen coverage metric, residual metric, prediction, claim, or knowledge promotion was run.",
                "- True-mass, minimum-mass, model-derived, radius-only or mass-only, and excluded rows remain separate through row classes and loader summaries.",
                "",
                "## Result-Promotion Routing",
                "",
                "The output is intentionally limited to source-acquisition "
                "artifacts. Per result-promotion protocol, this task does not "
                "create a canonical result, claim, prediction entry, or "
                "scientific memory promotion.",
                "",
                "## Next Step",
                "",
                "A separate review or benchmark task may decide whether this "
                "pinned snapshot is eligible for reopen coverage or mass-radius "
                "baseline analysis. That future task must not merge true-mass "
                "and minimum-mass rows into a single scored axis.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actor", required=True)
    parser.add_argument("--approval-reference", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--skip-fetch", action="store_true")
    parser.add_argument("--raw-path", type=Path)
    args = parser.parse_args(argv)

    query_hash = sha256_lf_canonical_file(QUERY_PATH)
    if query_hash != EXPECTED_QUERY_SHA256:
        raise RuntimeError(
            "Committed PSCompPars query hash drifted before acquisition: "
            f"{query_hash}"
        )

    query_text = QUERY_PATH.read_text(encoding="utf-8")
    query = first_snapshot._strip_adql_comments(query_text)
    retrieval_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = args.raw_path or RAW_DIR / (
        f"exo-pscomppars-second-snapshot-{_retrieval_slug(retrieval_timestamp)}.csv"
    )

    if not args.skip_fetch:
        body = first_snapshot._fetch_snapshot(query, args.timeout_seconds)
        text_prefix = body[:256].decode("utf-8", "replace").lower()
        if "<html" in text_prefix or "error" in text_prefix[:80]:
            raise RuntimeError("TAP response did not look like CSV")
        raw_path.write_bytes(body)
    elif not raw_path.exists():
        raise FileNotFoundError(raw_path)
    else:
        match = re.search(r"second-snapshot-(\d{8}T\d{6})Z\.csv$", raw_path.name)
        if match:
            raw_stamp = datetime.strptime(match.group(1), "%Y%m%dT%H%M%S")
            retrieval_timestamp = raw_stamp.replace(tzinfo=timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )

    raw_checksum = sha256_file(raw_path)
    rows = first_snapshot._read_csv_rows(raw_path)
    method_map, mass_map = first_snapshot._load_maps()
    first_entries, raw_summary = first_snapshot._normalize_rows(rows, method_map, mass_map)
    entries = _second_snapshot_entries(first_entries)

    payload = _build_payload(
        retrieval_timestamp=retrieval_timestamp,
        raw_checksum=raw_checksum,
        normalized_checksum=None,
        entries=entries,
    )
    normalized_payload_checksum = normalized_snapshot_checksum(payload)
    payload["snapshot_provenance"]["normalized_checksum_sha256"] = normalized_payload_checksum
    validate_document(payload, "exoplanet_mass_radius", DATASET_PATH)
    DATASET_PATH.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=False, width=100),
        encoding="utf-8",
    )
    normalized_file_checksum = sha256_lf_canonical_file(DATASET_PATH)

    filtered = load_and_filter(DATASET_PATH)
    filter_summary = summarize(filtered)
    _write_manifest(
        actor=args.actor,
        approval_reference=args.approval_reference,
        retrieval_timestamp=retrieval_timestamp,
        raw_path=raw_path,
        raw_checksum=raw_checksum,
        normalized_file_checksum=normalized_file_checksum,
        normalized_payload_checksum=normalized_payload_checksum,
        row_count=len(entries),
        included_count=filtered.post_filter_included_count,
        excluded_count=len(filtered.excluded_rows),
    )
    _write_review(
        actor=args.actor,
        approval_reference=args.approval_reference,
        retrieval_timestamp=retrieval_timestamp,
        raw_path=raw_path,
        raw_checksum=raw_checksum,
        normalized_file_checksum=normalized_file_checksum,
        normalized_payload_checksum=normalized_payload_checksum,
        raw_summary=raw_summary,
        filter_summary=filter_summary,
    )

    print(json.dumps(filter_summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
