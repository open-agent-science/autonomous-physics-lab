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
CROSS_PLATFORM_ADVISORY_RULES = (
    (
        re.compile(r"""['"]/tmp/"""),
        "Hardcoded /tmp path; use tempfile.gettempdir() or "
        "tempfile.TemporaryDirectory() for a cross-platform temporary location.",
    ),
    (
        re.compile(r"""['"]python3['"]"""),
        "Hardcoded 'python3' executable; prefer sys.executable so the command "
        "also resolves on Windows (python / py launcher).",
    ),
    (
        re.compile(r"""['"]\./scripts/[^'"]+\.sh['"]"""),
        "Invokes a .sh script directly; ensure a cross-platform (Python) "
        "entrypoint exists so non-bash (Windows) agents are not blocked.",
    ),
    (
        re.compile(r"""\bos\.(?:getenv|environ(?:\.get)?)\(\s*['"]HOME['"]"""),
        "Reads the HOME environment variable directly; use Path.home() so the "
        "home directory also resolves on Windows (USERPROFILE).",
    ),
)
QUOTED_LINE_PATTERN = re.compile(r'^\s*["\'].*["\'],?\s*$')
DECISION_REGRESSION_GUARDRAIL_MARKERS = (
    *GUARDRAIL_CONTEXT_MARKERS,
    "retire",
    "retired",
    "remove",
    "removed",
    "reject",
    "rejected",
    "redundant",
    "postmortem",
    "decision-regression",
    "regression guard",
    "sanity check",
    "explicit maintainer confirmation",
)
DECISION_REGRESSION_RULES = (
    (
        re.compile(r"\b(?:add|create|generate|write|commit|sync)\b.*\btasks/active\.md\b"),
        "Potential regression to retired tasks/ACTIVE.md generated-board workflow.",
    ),
    (
        re.compile(
            r"\b(?:add|create|generate|write|commit|sync)\b.*\bcampaigns/task-index\.yaml\b"
        ),
        "Potential regression to retired committed campaign task-index cache.",
    ),
    (
        re.compile(
            r"\b(?:add|create|generate|write|commit|sync)\b.*\bagent-capacity-board\.md\b"
        ),
        "Potential regression to retired agent capacity board layer.",
    ),
    (
        re.compile(
            r"\b(?:add|create|generate|write|commit|sync)\b.*\bstatic\b.*\bagent\b"
        ),
        "Potential static agent-facing state layer; agents should query canonical YAML, CLI, or snapshots.",
    ),
    (
        re.compile(
            r"\b(?:add|create|generate|write|commit|sync)\b.*\bagent\b.*\bstatic\b"
        ),
        "Potential static agent-facing state layer; agents should query canonical YAML, CLI, or snapshots.",
    ),
    (
        re.compile(r"\b(?:new|second|duplicate)\b.*\bsource of truth\b"),
        "Potential duplicate source-of-truth architecture decision.",
    ),
    (
        re.compile(
            r"\b(?:portfolio|campaign|mission)s?\b.*\b"
            r"(?:lane[- ]map|open[- ]data lane|priority ranking|prioriti[sz]ation|routing surface)\b"
        ),
        "Potential duplicate live campaign/mission routing surface; use canonical mission/campaign surfaces or an explicit dated non-canonical memo.",
    ),
    (
        re.compile(
            r"\b(?:see|refer to|link(?:s|ed)? to|points? to|pointer to)\b.*\b"
            r"(?:lane[- ]map|priority ranking|prioriti[sz]ation|routing surface)\b"
        ),
        "Potential live pointer to a duplicate routing/prioritization surface; confirm it is not replacing canonical mission/campaign state.",
    ),
)
FOLLOW_UP_TASK_PATTERNS = (
    re.compile(r"\bfollow[- ]up task\b"),
    re.compile(r"\bfollow[- ]up tasks\b"),
    re.compile(r"\bseparate task\b"),
    re.compile(r"\bminimal schema follow[- ]up\b"),
)
FORMAL_FOLLOW_UP_PATH_PREFIXES = (
    "tasks/proposals/",
)
COAUTHOR_TRAILER_PATTERN = re.compile(r"^\s*co-authored-by\s*:", re.IGNORECASE)


def line_is_rule_catalog_line(line: str) -> bool:
    """Return whether a diff line is clearly a catalog entry rather than live code."""
    stripped = line.strip()
    if "re.compile(" in stripped:
        return True
    return QUOTED_LINE_PATTERN.match(stripped) is not None


def match_is_guardrail_context(
    line: str,
    match_start: int,
    previous_lines: tuple[str, ...] = (),
) -> bool:
    """Return whether a matched term is in nearby rule-against-claim context."""
    previous_context = " ".join(previous_lines[-2:]).lower()
    if any(marker in previous_context for marker in GUARDRAIL_CONTEXT_MARKERS):
        return True
    prefix = line[:match_start].lower()
    return any(marker in prefix for marker in GUARDRAIL_CONTEXT_MARKERS)


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
            for match in pattern.finditer(lowered):
                if match_is_guardrail_context(line, match.start(), tuple(previous_lines)):
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


def cross_platform_advisory_hits(added_lines: tuple[str, ...]) -> tuple[str, ...]:
    """Return non-blocking cross-platform portability smells in added diff lines.

    These are advisory only: APL must run on Linux, macOS, and Windows for
    third-party agents, so portability regressions are surfaced to the reviewer
    rather than blocking a merge. See docs/cross-platform-compatibility.md.
    """
    hits: list[str] = []
    for line in added_lines:
        if line_is_rule_catalog_line(line):
            continue
        for pattern, description in CROSS_PLATFORM_ADVISORY_RULES:
            if pattern.search(line):
                hits.append(description)
    return tuple(dict.fromkeys(hits))


def cross_platform_surface_hits(changed_files: tuple[str, ...]) -> tuple[str, ...]:
    """Return changed shell scripts that need a cross-platform-entrypoint check."""
    hits: list[str] = []
    for path in changed_files:
        if path.endswith(".sh"):
            hits.append(
                f"Shell script changed ({path}): confirm it is not a needless "
                "wrapper around a Python command and that non-bash (Windows) "
                "agents have an equivalent path."
            )
    return tuple(dict.fromkeys(hits))


def coauthor_trailer_advisory_hits(lines: tuple[str, ...]) -> tuple[str, ...]:
    """Return advisory-only hits for AI co-author trailer noise.

    AI tool involvement belongs in PR metadata, not git co-author trailers.
    The trailer is still undesirable, but it is review hygiene rather than a
    merge blocker: maintainers can omit it from the final squash body.
    """
    hits: list[str] = []
    for line in lines:
        if COAUTHOR_TRAILER_PATTERN.search(line):
            hits.append(
                "Co-authored-by trailer detected; keep AI attribution in PR "
                "metadata and omit the trailer from the final squash merge body."
            )
    return tuple(dict.fromkeys(hits))


def line_is_decision_regression_guardrail(
    line: str,
    previous_lines: tuple[str, ...] = (),
) -> bool:
    """Return whether a decision-regression term appears in a rule-against context."""
    context = " ".join((*previous_lines[-2:], line)).lower()
    return any(marker in context for marker in DECISION_REGRESSION_GUARDRAIL_MARKERS)


def decision_regression_advisory_hits(added_lines: tuple[str, ...]) -> tuple[str, ...]:
    """Return architecture-decision regressions that need maintainer confirmation.

    This is intentionally heuristic. It catches PRs that may implement a task
    correctly while reviving a retired coordination pattern or adding a duplicate
    source-of-truth layer. Guardrail/postmortem text is ignored so documentation
    that warns against the pattern does not block itself.
    """
    hits: list[str] = []
    previous_lines: list[str] = []
    for line in added_lines:
        if line_is_rule_catalog_line(line):
            previous_lines.append(line)
            continue
        if line_is_decision_regression_guardrail(line, tuple(previous_lines)):
            previous_lines.append(line)
            continue
        lowered = line.lower()
        for pattern, description in DECISION_REGRESSION_RULES:
            if pattern.search(lowered):
                hits.append(description)
        previous_lines.append(line)
    return tuple(dict.fromkeys(hits))


def follow_up_task_advisory_hits(
    added_lines: tuple[str, ...],
    changed_files: tuple[str, ...],
    *,
    pr_title: str = "",
    pr_body: str = "",
) -> tuple[str, ...]:
    """Return advisory warnings for informal follow-up task mentions.

    Review notes may legitimately mention future work without creating it.
    However, when a PR says a follow-up task is needed but does not include a
    formal task proposal or task-queue artifact, the reviewer should surface
    that handoff explicitly so useful work is not lost in PR prose.
    """
    if pr_title.startswith("TASK-QUEUE:"):
        return ()
    if any(path.startswith(FORMAL_FOLLOW_UP_PATH_PREFIXES) for path in changed_files):
        return ()

    searchable_lines = [
        line.lower()
        for line in added_lines
        if not line_is_rule_catalog_line(line)
    ]
    if pr_body:
        searchable_lines.extend(pr_body.lower().splitlines())

    for line in searchable_lines:
        if any(pattern.search(line) for pattern in FOLLOW_UP_TASK_PATTERNS):
            return (
                "Follow-up task is mentioned but no TASK-QUEUE or "
                "tasks/proposals/ artifact is changed. If the follow-up is "
                "required to preserve the work, create a formal task/proposal; "
                "otherwise state that it is advisory only.",
            )
    return ()


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
    """Extract a required path-like accepted output from a human string.

    Returns ``None`` unless the entry is a single concrete required path token.
    Multi-word descriptive entries are skipped even when they end in a known
    file extension, and entries explicitly marked optional or conditional are
    never required (so they are not reported as missing). See TASK-0466, F4.
    """
    cleaned = raw_output.strip().strip("`")
    lowered = cleaned.lower()
    if lowered.startswith("optional") or " only if " in lowered:
        return None
    if cleaned.startswith("updated "):
        cleaned = cleaned.removeprefix("updated ").strip().strip("`")
    if "/" not in cleaned:
        return None
    if len(cleaned.split()) != 1:
        return None
    return cleaned


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
