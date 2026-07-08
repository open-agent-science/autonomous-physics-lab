"""Build the FRB Catalog 1 pre-T exposure feature surface for TASK-0963.

The helper reads local, checksum-pinned source bytes and writes only a compact
derived feature fixture. It intentionally does not read repeater labels.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import numpy as np
import yaml

TASK_ID = "TASK-0963"
FIXED_EPOCH_UTC = "2019-07-02"
FIXED_EPOCH_MJD = 58666.0
NSIDE = 4096
EXPOSURE_SECONDS_PER_COUNT = 4.0
CATALOG_EXPECTED_SHA256 = "5108ada779d279a2547d9f9e73ae25bfdd40d8496d6ba7255ec29c6629057a48"
CATALOG_EXPECTED_BYTES = 4_057_396
CATALOG_URL = (
    "https://cadc-west-01.canfar.net/vault/files/"
    "AstroDataCitationDOI/CISTI.CANFAR/25.0066/data/table/chimefrbcat2.csv"
)
UPPER_URL = (
    "https://cadc-west-01.canfar.net/vault/files/"
    "AstroDataCitationDOI/CISTI.CANFAR/21.0007/data/exposure/"
    "exposure_int_20180828_20190702_transit_U_beam_FWHM-600_res_4s_0.86_arcmin.npz"
)
LOWER_URL = (
    "https://cadc-west-01.canfar.net/vault/files/"
    "AstroDataCitationDOI/CISTI.CANFAR/21.0007/data/exposure/"
    "exposure_int_20180828_20190702_transit_L_beam_FWHM-600_res_4s_0.86_arcmin.npz"
)
UPPER_FILENAME = "exposure_int_20180828_20190702_transit_U_beam_FWHM-600_res_4s_0.86_arcmin.npz"
LOWER_FILENAME = "exposure_int_20180828_20190702_transit_L_beam_FWHM-600_res_4s_0.86_arcmin.npz"
UPPER_EXPECTED_SHA256 = "088a0617104e5400dc12a8bcaf12621f3c61e82cab3eadc3f842cd6da7018536"
LOWER_EXPECTED_SHA256 = "e8cc1a47b916fc5cb89f6df3ea0f07d57d5b2a1b22262e9ead57937100b5966a"
UPPER_EXPECTED_BYTES = 186_745_827
LOWER_EXPECTED_BYTES = 12_800_403
EXPOSURE_ARRAY_KEY = "exposure"


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_file(path: Path, *, expected_bytes: int, expected_sha256: str, label: str) -> str:
    actual_bytes = path.stat().st_size
    if actual_bytes != expected_bytes:
        raise SystemExit(f"{label}: unexpected byte length {actual_bytes} != {expected_bytes}")
    actual_sha256 = sha256_file(path)
    if actual_sha256 != expected_sha256:
        raise SystemExit(f"{label}: unexpected sha256 {actual_sha256} != {expected_sha256}")
    return actual_sha256


def download_file(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    request = Request(url, headers={"User-Agent": "APL-frb-task0963/1.0"})
    with urlopen(request, timeout=120) as response, path.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)


def finite_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except ValueError:
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def first_detection_mjd(row: dict[str, str]) -> float | None:
    mjd_inf = finite_float(row.get("mjd_inf"))
    if mjd_inf is not None:
        return mjd_inf
    return finite_float(row.get("mjd_400"))


def read_pre_t_sources(csv_path: Path, *, epoch_mjd: float) -> list[dict[str, Any]]:
    required_columns = {
        "tns_name",
        "ra",
        "dec",
        "mjd_inf",
        "mjd_400",
        "excluded_flag",
        "catalog1_flag",
    }
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = sorted(required_columns.difference(reader.fieldnames or []))
        if missing:
            raise SystemExit(f"catalog CSV missing required columns: {', '.join(missing)}")
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        raw_rows = 0
        for row in reader:
            raw_rows += 1
            if row.get("excluded_flag") != "0" or row.get("catalog1_flag") != "1":
                continue
            mjd = first_detection_mjd(row)
            ra = finite_float(row.get("ra"))
            dec = finite_float(row.get("dec"))
            source_id = (row.get("tns_name") or "").strip()
            if mjd is None or ra is None or dec is None or not source_id:
                continue
            if mjd > epoch_mjd:
                continue
            grouped[source_id].append({"source_id": source_id, "ra_deg": ra, "dec_deg": dec, "mjd": mjd})
    sources = []
    for source_id, rows in grouped.items():
        chosen = min(rows, key=lambda item: item["mjd"])
        sources.append(chosen | {"pre_t_detection_count_for_source_id": len(rows)})
    sources.sort(key=lambda item: item["source_id"])
    return sources


def healpix_ring_ang2pix(nside: int, ra_deg: np.ndarray, dec_deg: np.ndarray) -> np.ndarray:
    """Return RING-ordered HEALPix indices for celestial RA/Dec coordinates."""
    if nside <= 0:
        raise ValueError("nside must be positive")
    theta = np.deg2rad(90.0 - dec_deg)
    phi = np.deg2rad(np.mod(ra_deg, 360.0))
    z = np.cos(theta)
    za = np.abs(z)
    tt = np.mod(phi / (0.5 * np.pi), 4.0)
    nside_float = float(nside)
    ncap = 2 * nside * (nside - 1)
    npix = 12 * nside * nside
    output = np.empty(z.shape, dtype=np.int64)

    equatorial = za <= (2.0 / 3.0)
    if np.any(equatorial):
        temp1 = nside_float * (0.5 + tt[equatorial])
        temp2 = nside_float * z[equatorial] * 0.75
        jp = np.floor(temp1 - temp2).astype(np.int64)
        jm = np.floor(temp1 + temp2).astype(np.int64)
        ir = nside + 1 + jp - jm
        kshift = 1 - (ir & 1)
        ip = (jp + jm - nside + kshift + 1) // 2
        ip = np.mod(ip, 4 * nside)
        output[equatorial] = ncap + (ir - 1) * (4 * nside) + ip

    polar = ~equatorial
    if np.any(polar):
        tp = tt[polar] - np.floor(tt[polar])
        tmp = nside_float * np.sqrt(3.0 * (1.0 - za[polar]))
        jp = np.floor(tp * tmp).astype(np.int64)
        jm = np.floor((1.0 - tp) * tmp).astype(np.int64)
        ir = jp + jm + 1
        ip = np.floor(tt[polar] * ir).astype(np.int64)
        ip = np.mod(ip, 4 * ir)
        north = z[polar] > 0
        polar_output = np.empty(ir.shape, dtype=np.int64)
        polar_output[north] = 2 * ir[north] * (ir[north] - 1) + ip[north]
        polar_output[~north] = npix - 2 * ir[~north] * (ir[~north] + 1) + ip[~north]
        output[polar] = polar_output

    if np.any((output < 0) | (output >= npix)):
        raise ValueError("computed HEALPix index outside map bounds")
    return output


def load_exposure_values(path: Path, pixels: np.ndarray) -> np.ndarray:
    with np.load(path) as payload:
        if EXPOSURE_ARRAY_KEY not in payload:
            raise SystemExit(f"{path}: missing {EXPOSURE_ARRAY_KEY!r} array")
        array = payload[EXPOSURE_ARRAY_KEY]
        values = np.zeros(pixels.shape, dtype=np.float64)
        in_prefix = pixels < len(array)
        if np.any(in_prefix):
            values[in_prefix] = array[pixels[in_prefix]]
        return values


def rounded(value: float) -> float:
    return round(float(value), 12)


def feature_table_digest(features: list[dict[str, Any]]) -> str:
    encoded = json.dumps(features, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def build_fixture(
    *,
    csv_path: Path,
    upper_npz: Path,
    lower_npz: Path,
    generated_at_utc: str,
    output_path: Path,
) -> dict[str, Any]:
    catalog_sha = verify_file(
        csv_path,
        expected_bytes=CATALOG_EXPECTED_BYTES,
        expected_sha256=CATALOG_EXPECTED_SHA256,
        label="catalog CSV",
    )
    upper_sha = verify_file(
        upper_npz,
        expected_bytes=UPPER_EXPECTED_BYTES,
        expected_sha256=UPPER_EXPECTED_SHA256,
        label="upper exposure NPZ",
    )
    lower_sha = verify_file(
        lower_npz,
        expected_bytes=LOWER_EXPECTED_BYTES,
        expected_sha256=LOWER_EXPECTED_SHA256,
        label="lower exposure NPZ",
    )
    sources = read_pre_t_sources(csv_path, epoch_mjd=FIXED_EPOCH_MJD)
    ras = np.array([item["ra_deg"] for item in sources], dtype=np.float64)
    decs = np.array([item["dec_deg"] for item in sources], dtype=np.float64)
    pixels = healpix_ring_ang2pix(NSIDE, ras, decs)
    upper_counts = load_exposure_values(upper_npz, pixels)
    lower_counts = load_exposure_values(lower_npz, pixels)

    features: list[dict[str, Any]] = []
    for item, pixel, upper_count, lower_count in zip(
        sources, pixels, upper_counts, lower_counts, strict=True
    ):
        upper_hours = upper_count * EXPOSURE_SECONDS_PER_COUNT / 3600.0
        lower_hours = lower_count * EXPOSURE_SECONDS_PER_COUNT / 3600.0
        score = math.log1p(upper_hours + lower_hours)
        features.append(
            {
                "source_id": item["source_id"],
                "ra_deg": rounded(item["ra_deg"]),
                "dec_deg": rounded(item["dec_deg"]),
                "first_detection_mjd": rounded(item["mjd"]),
                "pre_t_detection_count_for_source_id": item["pre_t_detection_count_for_source_id"],
                "healpix_nside": NSIDE,
                "healpix_ordering": "RING",
                "healpix_index": int(pixel),
                "E_upper_counts": int(upper_count) if float(upper_count).is_integer() else rounded(upper_count),
                "E_lower_counts": int(lower_count) if float(lower_count).is_integer() else rounded(lower_count),
                "E_upper_hours": rounded(upper_hours),
                "E_lower_hours": rounded(lower_hours),
                "score_pre_t": rounded(score),
            }
        )

    nonzero_upper = sum(1 for item in features if item["E_upper_counts"] != 0)
    nonzero_lower = sum(1 for item in features if item["E_lower_counts"] != 0)
    fixture = {
        "artifact_kind": "frb_catalog1_pre_t_exposure_feature_surface",
        "artifact_id": "FRB-CAT1-PRET-EXPOSURE-0001",
        "task_id": TASK_ID,
        "status": "constructed_feature_surface",
        "generated_at_utc": generated_at_utc,
        "output_path": output_path.as_posix(),
        "source_inputs": {
            "catalog2_csv": {
                "filename": "chimefrbcat2.csv",
                "storage_file_endpoint": CATALOG_URL,
                "sha256": catalog_sha,
                "expected_bytes": CATALOG_EXPECTED_BYTES,
                "committed_to_repo": False,
                "columns_read": [
                    "tns_name",
                    "ra",
                    "dec",
                    "mjd_inf",
                    "mjd_400",
                    "excluded_flag",
                    "catalog1_flag",
                ],
                "columns_intentionally_not_read": ["repeater_name", "exp_up", "exp_low"],
            },
            "catalog1_upper_exposure_npz": {
                "filename": UPPER_FILENAME,
                "storage_file_endpoint": UPPER_URL,
                "sha256": upper_sha,
                "expected_bytes": UPPER_EXPECTED_BYTES,
                "committed_to_repo": False,
            },
            "catalog1_lower_exposure_npz": {
                "filename": LOWER_FILENAME,
                "storage_file_endpoint": LOWER_URL,
                "sha256": lower_sha,
                "expected_bytes": LOWER_EXPECTED_BYTES,
                "committed_to_repo": False,
            },
        },
        "feature_contract": {
            "fixed_epoch_t_utc": FIXED_EPOCH_UTC,
            "fixed_epoch_t_mjd": FIXED_EPOCH_MJD,
            "cohort_rule": (
                "Catalog-1-flagged Catalog 2 rows with excluded_flag == '0' and first "
                "detection MJD <= 58666.0; source_id is tns_name only."
            ),
            "label_contact": False,
            "label_columns_read": [],
            "source_association_columns_read": [],
            "scoring_rule": "score_pre_t = log1p(E_upper_hours + E_lower_hours)",
            "count_to_hours": "E_hours = 4 * exposure_count / 3600",
            "forbidden_features_excluded": [
                "repeater_name",
                "Catalog 2 full-window exp_up / exp_low",
                "morphology columns",
                "post-T source associations",
            ],
        },
        "aggregate_counts": {
            "pre_t_feature_rows": len(features),
            "nonzero_upper_exposure_rows": nonzero_upper,
            "nonzero_lower_exposure_rows": nonzero_lower,
            "nonzero_total_exposure_rows": sum(
                1 for item in features if (item["E_upper_counts"] + item["E_lower_counts"]) != 0
            ),
            "zero_total_exposure_rows": sum(
                1 for item in features if (item["E_upper_counts"] + item["E_lower_counts"]) == 0
            ),
        },
        "feature_table_sha256": feature_table_digest(features),
        "features": features,
        "limitations": [
            "The fixture uses Catalog-1 interval exposure maps at the single approved T=2019-07-02 epoch only.",
            "Source identifiers are pre-label TNS names; repeater labels and later source associations are intentionally not read.",
            "The fixture is a feature surface for a later freeze task; it registers no prediction and makes no FRB population claim.",
            "Raw Catalog CSV and NPZ bytes are local inputs only and are not committed to the repository.",
        ],
        "verdict": "PRE_T_EXPOSURE_FEATURE_SURFACE_CONSTRUCTED",
    }
    return fixture


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=False), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, help="Local pinned CHIME/FRB Catalog 2 CSV.")
    parser.add_argument("--upper-npz", type=Path, help="Local pinned upper-transit exposure NPZ.")
    parser.add_argument("--lower-npz", type=Path, help="Local pinned lower-transit exposure NPZ.")
    parser.add_argument(
        "--download-dir",
        type=Path,
        help="Download missing local inputs to this untracked directory before verification.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/radio_transients/frb_catalog1_pre_t_exposure_feature_surface.yaml"),
    )
    parser.add_argument("--generated-at-utc", default=utc_now())
    return parser.parse_args()


def resolve_input(path: Path | None, *, download_dir: Path | None, filename: str, url: str) -> Path:
    if path is not None:
        return path
    if download_dir is None:
        raise SystemExit(f"missing input {filename}; pass its path or --download-dir")
    target = download_dir / filename
    if not target.exists():
        download_file(url, target)
    return target


def main() -> int:
    args = parse_args()
    csv_path = resolve_input(
        args.csv,
        download_dir=args.download_dir,
        filename="chimefrbcat2.csv",
        url=CATALOG_URL,
    )
    upper_npz = resolve_input(
        args.upper_npz,
        download_dir=args.download_dir,
        filename=UPPER_FILENAME,
        url=UPPER_URL,
    )
    lower_npz = resolve_input(
        args.lower_npz,
        download_dir=args.download_dir,
        filename=LOWER_FILENAME,
        url=LOWER_URL,
    )
    fixture = build_fixture(
        csv_path=csv_path,
        upper_npz=upper_npz,
        lower_npz=lower_npz,
        generated_at_utc=args.generated_at_utc,
        output_path=args.output,
    )
    write_yaml(args.output, fixture)
    print(f"feature_rows={fixture['aggregate_counts']['pre_t_feature_rows']}")
    print(f"feature_table_sha256={fixture['feature_table_sha256']}")
    print(f"wrote={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
