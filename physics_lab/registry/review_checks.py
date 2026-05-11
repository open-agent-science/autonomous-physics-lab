"""Content safety and artifact checks for maintainer review."""

from __future__ import annotations

from pathlib import Path
import re
import tempfile
from typing import Any

from physics_lab.registry.claims import load_claim
from physics_lab.registry.review_git import run_command, current_branch


OVERCLAIM_TERMS = (
    "solved",
    "proved",
    "exact discovery",
    "100% correct",
    "new physics",
    "theory of everything",
    "global validity",
)
NEGATION_MARKERS = ("do not", "don't", "must not", "should not", "no ", "avoid ")
GUARDRAIL_CONTEXT_MARKERS = (
    *NEGATION_MARKERS,
    "forbidden",
    "guardrail",
    "guardrails",
    "banned",
    "blocklist",
    "not a ",
    "not an ",
    "without ",
)
OVERCLAIM_PATTERNS = tuple(
    re.compile(rf"(?<![a-z]){re.escape(term)}(?![a-z])") for term in OVERCLAIM_TERMS
)
PROTECTED_PREFIXES = ("results/", "claims/", "hypotheses/", "experiments/")
SEMANTIC_PROTECTED_PREFIX_HINTS = {
    "results/": (
        "result artifact",
        "result artifacts",
        "run artifact",
        "run artifacts",
        "benchmark result artifact",
        "benchmark result artifacts",
        "canonical result artifact",
        "canonical result artifacts",
        "canonical run artifact",
        "canonical run artifacts",
        "reproducible benchmark result artifact",
        "reproducible benchmark result artifacts",
    ),
}
KNOWN_OUTPUT_EXTENSIONS = (
    ".md",
    ".yaml",
    ".yml",
    ".py",
    ".json",
    ".txt",
    ".csv",
    ".ipynb",
)
SENSITIVE_PATH_RULES = (
    (".github/workflows/", "CI workflow files changed."),
    ("scripts/", "Repository scripts changed."),
    ("pyproject.toml", "Project dependency or tooling configuration changed."),
)
SECURITY_BLOCK_RULES = (
    (re.compile(r"\beval\s*\("), "Introduces eval(...)."),
    (re.compile(r"\bexec\s*\("), "Introduces exec(...)."),
    (re.compile(r"\bpickle\.loads\s*\("), "Introduces pickle.loads(...)."),
    (re.compile(r"\byaml\.load\s*\("), "Introduces yaml.load(...)."),
    (re.compile(r"\bos\.system\s*\("), "Introduces os.system(...)."),
    (
        re.compile(r"\bsubprocess\.(?:Popen|run|call)\b.*shell\s*=\s*True"),
        "Introduces subprocess shell=True execution.",
    ),
    (re.compile(r"curl\b.*\|\s*(?:sh|bash)\b"), "Introduces curl-pipe-shell execution."),
)
QUOTED_LINE_PATTERN = re.compile(r'^\s*["\'].*["\'],?\s*$')


def line_is_rule_catalog_line(line: str) -> bool:
    """Return whether a diff line is clearly a catalog entry rather than live code."""
    stripped = line.strip()
    if "re.compile(" in stripped:
        return True
    return QUOTED_LINE_PATTERN.match(stripped) is not None


def line_is_guardrail_context(line: str, previous_lines: tuple[str, ...] = ()) -> bool:
    """Return whether a line is describing a rule against overclaiming."""
    context = " ".join((*previous_lines[-2:], line)).lower()
    return any(marker in context for marker in GUARDRAIL_CONTEXT_MARKERS)


def _overclaim_hits_by_severity(
    added_lines: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return blocking and advisory overclaim terms from added diff lines."""
    blockers: list[str] = []
    advisory: list[str] = []
    previous_lines: list[str] = []
    for line in added_lines:
        lowered = line.lower()
        if line_is_rule_catalog_line(line):
            previous_lines.append(line)
            continue
        for term, pattern in zip(OVERCLAIM_TERMS, OVERCLAIM_PATTERNS):
            if pattern.search(lowered):
                if line_is_guardrail_context(line, tuple(previous_lines)):
                    advisory.append(term)
                else:
                    blockers.append(term)
        previous_lines.append(line)
    return tuple(dict.fromkeys(blockers)), tuple(dict.fromkeys(advisory))


def overclaim_hits(added_lines: tuple[str, ...]) -> tuple[str, ...]:
    """Return blocking overclaim terms found in added diff lines."""
    blockers, _advisory = _overclaim_hits_by_severity(added_lines)
    return blockers


def overclaim_advisory_hits(added_lines: tuple[str, ...]) -> tuple[str, ...]:
    """Return non-blocking overclaim terms found in guardrail context."""
    _blockers, advisory = _overclaim_hits_by_severity(added_lines)
    return advisory


def security_pattern_hits(added_lines: tuple[str, ...]) -> tuple[str, ...]:
    """Return dangerous code patterns found in added diff lines."""
    hits: list[str] = []
    for line in added_lines:
        lowered = line.lower()
        if line_is_rule_catalog_line(line):
            continue
        for pattern, description in SECURITY_BLOCK_RULES:
            if pattern.search(lowered):
                hits.append(description)
    return tuple(dict.fromkeys(hits))


def sensitive_surface_hits(changed_files: tuple[str, ...]) -> tuple[str, ...]:
    """Return security-relevant changed surfaces that deserve maintainer review."""
    hits: list[str] = []
    for path in changed_files:
        for prefix, description in SENSITIVE_PATH_RULES:
            if path == prefix or path.startswith(prefix):
                hits.append(f"{description} Path: {path}")
                break
    return tuple(dict.fromkeys(hits))


def normalize_output_path(raw_output: str) -> str | None:
    """Extract a path-like accepted output from a human string."""
    cleaned = raw_output.strip().strip("`")
    if cleaned.startswith("updated "):
        cleaned = cleaned.removeprefix("updated ").strip().strip("`")
    if "/" not in cleaned:
        return None
    if cleaned.endswith(KNOWN_OUTPUT_EXTENSIONS):
        return cleaned
    parts = cleaned.split()
    if len(parts) == 1:
        return cleaned
    return None


def output_paths(task_payload: dict[str, Any]) -> tuple[str, ...]:
    """Return accepted output paths that look like tracked files."""
    paths: list[str] = []
    for item in task_payload.get("accepted_outputs", []):
        path = normalize_output_path(str(item))
        if path is not None:
            paths.append(path)
    return tuple(paths)


def path_exists_in_ref(root: Path, ref: str, repo_path: str) -> bool:
    """Return whether a path exists in a git ref."""
    result = run_command(
        ["git", "cat-file", "-e", f"{ref}:{repo_path}"],
        cwd=root,
    )
    return result.returncode == 0


def missing_expected_outputs(
    root: Path,
    branch: str,
    task_payload: dict[str, Any],
    changed_files: tuple[str, ...],
) -> tuple[str, ...]:
    """Return accepted output paths that appear to be missing."""
    missing: list[str] = []
    for op in output_paths(task_payload):
        if op.startswith("tasks/") and op.endswith(".yaml"):
            if path_exists_in_ref(root, branch, op):
                continue
        if op in changed_files:
            continue
        if branch == current_branch(root) and (root / op).exists():
            continue
        if path_exists_in_ref(root, branch, op):
            continue
        missing.append(op)
    return tuple(missing)


def task_allows_prefix(task_payload: dict[str, Any], prefix: str) -> bool:
    """Return whether task metadata explicitly allows a protected prefix."""
    texts = []
    texts.extend(str(item) for item in task_payload.get("accepted_outputs", []))
    texts.extend(str(item) for item in task_payload.get("requirements", []))
    texts.extend(str(item) for item in task_payload.get("input", {}).get("related_objects", []))
    lowered_texts = tuple(text.lower() for text in texts)
    normalized_prefix = prefix.rstrip("/")
    if any(normalized_prefix in text or prefix in text for text in texts):
        return True
    semantic_hints = SEMANTIC_PROTECTED_PREFIX_HINTS.get(prefix, ())
    return any(hint in text for hint in semantic_hints for text in lowered_texts)


def unexpected_protected_changes(
    changed_files: tuple[str, ...],
    task_payload: dict[str, Any],
) -> tuple[str, ...]:
    """Return protected file changes that are not task-authorized."""
    unexpected: list[str] = []
    for path in changed_files:
        for prefix in PROTECTED_PREFIXES:
            if path.startswith(prefix) and not task_allows_prefix(task_payload, prefix):
                unexpected.append(path)
                break
    return tuple(unexpected)


def load_claim_status_from_ref(root: Path, ref: str, repo_path: str) -> str | None:
    """Load claim status from a git ref if the file exists."""
    if not path_exists_in_ref(root, ref, repo_path):
        return None
    show_result = run_command(["git", "show", f"{ref}:{repo_path}"], cwd=root)
    if show_result.returncode != 0:
        return None
    temp_handle = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".md",
        prefix="claim_status_",
        delete=False,
    )
    temp_path = Path(temp_handle.name)
    try:
        temp_handle.write(show_result.stdout)
    finally:
        temp_handle.close()
    try:
        return str(load_claim(temp_path)["status"])
    finally:
        if temp_path.exists():
            temp_path.unlink()


def claim_status_promotions(
    root: Path,
    branch: str,
    changed_files: tuple[str, ...],
) -> tuple[str, ...]:
    """Return claim files whose status changed away from DRAFT or PARTIALLY_SUPPORTED."""
    promotions: list[str] = []
    for path in changed_files:
        if not path.startswith("claims/") or not path.endswith(".md"):
            continue
        before_status = load_claim_status_from_ref(root, "main", path)
        after_status = load_claim_status_from_ref(root, branch, path)
        if before_status is None or after_status is None:
            continue
        if before_status != after_status and after_status not in {"DRAFT", "PARTIALLY_SUPPORTED"}:
            promotions.append(f"{path}: {before_status} -> {after_status}")
    return tuple(promotions)
