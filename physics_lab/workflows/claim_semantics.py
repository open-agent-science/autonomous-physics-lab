"""Helpers for cautious claim-status suggestions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ClaimStatusSuggestion:
    """Suggested claim status plus a short rationale."""

    status: str
    rationale: str
    pass_count: int
    fail_count: int


def suggest_claim_status(
    *,
    verification_summary: dict[str, Any],
    best_verdict: str | None = None,
    range_limited: bool,
    exact_verification: bool,
) -> ClaimStatusSuggestion:
    """Return a cautious claim-status suggestion from workflow evidence."""
    checks = list(verification_summary.get("checks", []))
    pass_count = sum(1 for check in checks if check["status"] == "PASS")
    fail_count = sum(1 for check in checks if check["status"] == "FAIL")
    verification_passed = bool(verification_summary.get("passed", False))

    if not verification_passed:
        return ClaimStatusSuggestion(
            status="DRAFT",
            rationale="Verification checks did not fully pass, so the claim should remain draft until failures are resolved or reviewed.",
            pass_count=pass_count,
            fail_count=fail_count,
        )

    if exact_verification and fail_count == 0:
        return ClaimStatusSuggestion(
            status="SUPPORTED",
            rationale="The configured benchmark passed exact, in-scope verification checks without failure.",
            pass_count=pass_count,
            fail_count=fail_count,
        )

    if range_limited or best_verdict in {"VALID_IN_RANGE", "PARTIALLY_VALID", "VALID"}:
        return ClaimStatusSuggestion(
            status="PARTIALLY_SUPPORTED",
            rationale="The benchmark supports the claim only within the tested scope and should remain range-aware.",
            pass_count=pass_count,
            fail_count=fail_count,
        )

    return ClaimStatusSuggestion(
        status="DRAFT",
        rationale="Evidence exists, but the status should remain draft until the scope and support level are reviewed explicitly.",
        pass_count=pass_count,
        fail_count=fail_count,
    )
