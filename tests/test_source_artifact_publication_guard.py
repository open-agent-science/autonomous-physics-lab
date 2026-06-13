from __future__ import annotations

import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_PDF_REDISTRIBUTION_STATES = {
    "cc_by_4_0",
    "cc0",
    "public_domain",
    "explicit_permission_recorded",
}


def _tracked_data_pdfs() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "data/**/*.pdf"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line) for line in result.stdout.splitlines() if line.strip()]


def _load_permission_marker(pdf_path: Path) -> dict[str, object] | None:
    marker = ROOT / pdf_path.with_suffix(pdf_path.suffix + ".license.yaml")
    if not marker.exists():
        return None
    payload = yaml.safe_load(marker.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_tracked_data_pdfs_require_explicit_redistribution_marker() -> None:
    violations: list[str] = []
    for pdf_path in _tracked_data_pdfs():
        marker = _load_permission_marker(pdf_path)
        if marker is None:
            violations.append(f"{pdf_path}: missing {pdf_path.name}.license.yaml marker")
            continue
        status = marker.get("redistribution_status")
        evidence = marker.get("permission_evidence")
        if status not in ALLOWED_PDF_REDISTRIBUTION_STATES or not evidence:
            violations.append(
                f"{pdf_path}: marker must set redistribution_status to one of "
                f"{sorted(ALLOWED_PDF_REDISTRIBUTION_STATES)} and permission_evidence"
            )

    assert violations == []


def test_atomic_arxiv_pdfs_are_metadata_only_with_expected_checksums() -> None:
    source_dirs = [
        ROOT / "data" / "atomic_clocks" / "source_artifacts" / "2021-beloy-bacon",
        ROOT / "data" / "atomic_clocks" / "source_artifacts" / "2016-nemitz-riken",
    ]
    for source_dir in source_dirs:
        provenance = yaml.safe_load(
            (source_dir / "provenance.yaml").read_text(encoding="utf-8")
        )
        assert isinstance(provenance, dict)
        assert provenance["preprint_committed"] is False
        assert provenance["redistribution_status"] == "not_redistributable_arxiv_nonexclusive"
        assert provenance["source_files_vendored"] == []
        assert (
            provenance["expected_artifact"]["fetch_helper"]
            == "scripts/fetch_source_artifact.py"
        )
        assert (source_dir / provenance["expected_artifact"]["checksum_sidecar"]).exists()
