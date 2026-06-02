"""Replay the pinned Exoplanet normalized-snapshot checksums without network access."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from physics_lab.datasets.exoplanets import normalized_snapshot_checksum  # noqa: E402

DEFAULT_SNAPSHOT = ROOT / "data" / "exoplanets" / "exo-0001-pscomppars-snapshot.yaml"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", nargs="?", type=Path, default=DEFAULT_SNAPSHOT)
    args = parser.parse_args(argv)

    snapshot_path = args.snapshot.resolve()
    with snapshot_path.open("r", encoding="utf-8") as fh:
        payload = yaml.safe_load(fh)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping at top of {snapshot_path}")

    provenance = payload.get("snapshot_provenance")
    if not isinstance(provenance, dict):
        raise ValueError("snapshot_provenance must be a mapping")

    expected = provenance.get("normalized_checksum_sha256")
    actual = normalized_snapshot_checksum(payload)
    print(f"snapshot={snapshot_path}")
    print(f"embedded_canonical_payload_sha256={expected}")
    print(f"computed_canonical_payload_sha256={actual}")
    print(f"committed_file_sha256={_sha256_file(snapshot_path)}")
    if expected != actual:
        print("status=DRIFT")
        return 1
    print("status=OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
