"""Validation helpers for source artifact packages."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any

import yaml


REQUIRED_PACKAGE_FILES = (
    "README.md",
    "provenance.yaml",
    "license_review.md",
    "extraction_notes.md",
    "raw_derived_policy.md",
    "blocker_notes.md",
)
REQUIRED_PROVENANCE_FIELDS = (
    "package_id",
    "schema_version",
    "task_id",
    "package_status",
    "campaign_profile_id",
    "source_id",
    "source_title",
)
PLACEHOLDER_VALUES = {
    "",
    "replace-with-campaign-profile-id",
    "replace-with-source-id",
    "replace-with-source-title",
    "replace-with-doi-arxiv-archive-or-url",
    "stable source locator",
}
UNREVIEWED_LICENSE_STATUSES = {
    "",
    "not_reviewed",
    "license_review_required",
    "replace-with-license-status",
}
PLACEHOLDER_ARCHIVE_POLICIES = {
    "",
    "required_before_value_use",
    "not_applicable_metadata_only",
    "replace-with-archive-policy",
}
BLOCKER_ONLY_STATUSES = {
    "METADATA_ONLY_BLOCKER",
    "metadata_only_blocker",
    "blocked",
    "excluded",
}
HEX_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


@dataclass(frozen=True)
class SourceArtifactIssue:
    """A single validation issue for a source artifact package."""

    severity: str
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class SourceArtifactValidationResult:
    """Validation result for a source artifact package."""

    package_path: Path
    issues: tuple[SourceArtifactIssue, ...]

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "ERROR" for issue in self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "ERROR")

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "WARNING")


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() in PLACEHOLDER_VALUES
    return False


def _as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _load_yaml(path: Path, issues: list[SourceArtifactIssue]) -> dict[str, Any]:
    if not path.exists():
        issues.append(
            SourceArtifactIssue(
                "ERROR",
                "MISSING_PROVENANCE",
                path.name,
                "Source artifact package is missing provenance.yaml.",
            )
        )
        return {}
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        issues.append(
            SourceArtifactIssue(
                "ERROR",
                "INVALID_PROVENANCE_YAML",
                path.name,
                f"provenance.yaml is not valid YAML: {exc}",
            )
        )
        return {}
    if not isinstance(payload, dict):
        issues.append(
            SourceArtifactIssue(
                "ERROR",
                "INVALID_PROVENANCE_SHAPE",
                path.name,
                "provenance.yaml must contain a top-level mapping.",
            )
        )
        return {}
    return payload


def _read_sidecar_checksum(sidecar_path: Path) -> str | None:
    if not sidecar_path.exists():
        return None
    first_token = sidecar_path.read_text(encoding="utf-8").strip().split()
    if not first_token:
        return None
    return first_token[0]


def _sidecar_candidates(package_path: Path, artifact_path_value: str) -> tuple[Path, ...]:
    artifact_path = Path(artifact_path_value)
    if artifact_path.is_absolute():
        resolved = artifact_path
    else:
        resolved = package_path / artifact_path
    return (
        resolved.with_name(f"{resolved.name}.sha256"),
        resolved.with_suffix(".sha256"),
    )


def _has_valid_checksum_or_sidecar(
    package_path: Path,
    provenance: dict[str, Any],
) -> bool:
    artifact = _as_mapping(provenance.get("artifact"))
    checksum = artifact.get("checksum_sha256")
    if isinstance(checksum, str) and HEX_SHA256_RE.fullmatch(checksum.strip()):
        return True
    artifact_path = artifact.get("artifact_path")
    if isinstance(artifact_path, str) and artifact_path.strip():
        for sidecar_path in _sidecar_candidates(package_path, artifact_path.strip()):
            sidecar_checksum = _read_sidecar_checksum(sidecar_path)
            if sidecar_checksum and HEX_SHA256_RE.fullmatch(sidecar_checksum):
                return True
    return False


def _hash_for_json(path: Path) -> str:
    return hashlib.sha256(path.as_posix().encode("utf-8")).hexdigest()


def validate_source_artifact_package(package_path: str | Path) -> SourceArtifactValidationResult:
    """Validate one source artifact package directory.

    The helper is intentionally opt-in. Current historical packages may be
    metadata-only notes; this validator is for new packages that claim to use
    the reusable source-artifact package shape.
    """
    path = Path(package_path)
    issues: list[SourceArtifactIssue] = []
    if not path.exists() or not path.is_dir():
        return SourceArtifactValidationResult(
            package_path=path,
            issues=(
                SourceArtifactIssue(
                    "ERROR",
                    "PACKAGE_NOT_FOUND",
                    path.as_posix(),
                    "Source artifact package path must be an existing directory.",
                ),
            ),
        )

    for filename in REQUIRED_PACKAGE_FILES:
        if not (path / filename).exists():
            issues.append(
                SourceArtifactIssue(
                    "ERROR",
                    "MISSING_REQUIRED_FILE",
                    filename,
                    f"Required source artifact package file is missing: {filename}.",
                )
            )

    provenance = _load_yaml(path / "provenance.yaml", issues)
    for field in REQUIRED_PROVENANCE_FIELDS:
        if _is_missing(provenance.get(field)):
            issues.append(
                SourceArtifactIssue(
                    "ERROR",
                    "MISSING_REQUIRED_METADATA",
                    f"provenance.yaml#{field}",
                    f"Required provenance field is missing or still a placeholder: {field}.",
                )
            )

    locators = _as_mapping(provenance.get("locators"))
    if _is_missing(locators.get("citation")) and all(
        _is_missing(locators.get(key))
        for key in ("doi", "arxiv_id", "archive_url", "source_url")
    ):
        issues.append(
            SourceArtifactIssue(
                "ERROR",
                "MISSING_SOURCE_LOCATOR",
                "provenance.yaml#locators",
                "Record at least a citation or stable locator before source review.",
            )
        )

    artifact = _as_mapping(provenance.get("artifact"))
    artifact_path = artifact.get("artifact_path")
    artifact_locator = artifact.get("artifact_locator")
    value_bearing = bool(artifact.get("value_bearing_artifact"))
    has_artifact_surface = value_bearing or not _is_missing(artifact_path) or not _is_missing(
        artifact_locator
    )
    archive_policy = str(artifact.get("archive_policy") or "").strip()
    if has_artifact_surface and not _has_valid_checksum_or_sidecar(path, provenance):
        if archive_policy in PLACEHOLDER_ARCHIVE_POLICIES:
            issues.append(
                SourceArtifactIssue(
                    "ERROR",
                    "CHECKSUM_OR_ARCHIVE_POLICY_MISSING",
                    "provenance.yaml#artifact",
                    "Value-bearing or pinned artifacts need a SHA-256 checksum sidecar or explicit archive policy.",
                )
            )

    redistribution = _as_mapping(provenance.get("redistribution"))
    package_status = str(provenance.get("package_status") or "").strip()
    redistribution_status = str(redistribution.get("redistribution_status") or "").strip()
    license_review_required = has_artifact_surface or package_status in {
        "SOURCE_ARTIFACT_PINNED",
        "EXTRACTION_REVIEW_READY",
        "ROWS_CURATED_ELSEWHERE",
    }
    if license_review_required and redistribution_status in UNREVIEWED_LICENSE_STATUSES:
        issues.append(
            SourceArtifactIssue(
                "ERROR",
                "LICENSE_REVIEW_MISSING",
                "provenance.yaml#redistribution.redistribution_status",
                "Pinned or value-bearing artifacts require a completed redistribution/license posture.",
            )
        )

    row_admissibility = _as_mapping(provenance.get("row_admissibility"))
    if _is_missing(row_admissibility.get("row_class")):
        issues.append(
            SourceArtifactIssue(
                "ERROR",
                "ROW_CLASS_MISSING",
                "provenance.yaml#row_admissibility.row_class",
                "Record row_class before the package can support row curation.",
            )
        )
    if _is_missing(row_admissibility.get("inclusion_status")):
        issues.append(
            SourceArtifactIssue(
                "ERROR",
                "INCLUSION_STATUS_MISSING",
                "provenance.yaml#row_admissibility.inclusion_status",
                "Record inclusion_status before the package can support row curation.",
            )
        )

    blocker_reasons = _as_list(row_admissibility.get("blocker_reasons"))
    inclusion_status = str(row_admissibility.get("inclusion_status") or "").strip()
    blocker_only = package_status in BLOCKER_ONLY_STATUSES or inclusion_status in {
        "metadata_only",
        "excluded",
        "blocked",
        "requires_review",
    }
    if blocker_only and not blocker_reasons:
        issues.append(
            SourceArtifactIssue(
                "ERROR",
                "BLOCKER_FIELDS_MISSING",
                "provenance.yaml#row_admissibility.blocker_reasons",
                "Blocker-only or non-admissible packages must preserve explicit blocker reasons.",
            )
        )
    if row_admissibility.get("accepted_for_benchmark") is True and blocker_reasons:
        issues.append(
            SourceArtifactIssue(
                "ERROR",
                "BLOCKED_ROW_ACCEPTED_FOR_BENCHMARK",
                "provenance.yaml#row_admissibility",
                "Rows with blocker reasons must not be marked accepted_for_benchmark.",
            )
        )

    review = _as_mapping(provenance.get("review"))
    if _is_missing(review.get("review_status")):
        issues.append(
            SourceArtifactIssue(
                "ERROR",
                "REVIEW_STATUS_MISSING",
                "provenance.yaml#review.review_status",
                "Record review_status before using the package in a curation task.",
            )
        )
    if _is_missing(review.get("allowed_next_step")):
        issues.append(
            SourceArtifactIssue(
                "ERROR",
                "NEXT_STEP_MISSING",
                "provenance.yaml#review.allowed_next_step",
                "Record allowed_next_step so follow-up agents know whether to halt or continue.",
            )
        )

    return SourceArtifactValidationResult(package_path=path, issues=tuple(issues))


def source_artifact_validation_json(result: SourceArtifactValidationResult) -> str:
    """Serialize a source artifact validation result for automation."""
    payload = {
        "package_path": result.package_path.as_posix(),
        "package_id": _hash_for_json(result.package_path),
        "ok": result.ok,
        "error_count": result.error_count,
        "warning_count": result.warning_count,
        "issues": [issue.__dict__ for issue in result.issues],
    }
    return json.dumps(payload, indent=2, sort_keys=True)
