"""Garbage collection for disposable PR-review worktrees (TASK-0724).

Maintainer review (``physics_lab/registry/maintainer_review.py``) checks out each
reviewed PR head in a throwaway *detached* git worktree under
``<root>/.worktrees/_reviews/``. Those checkouts are safe to delete once the
review run finishes, but nothing tore them down, so they accumulated across many
PRs and crashed runs and exhausted local disk (the failure that motivated this
module: a full volume turned ``apl_review_pr.py`` into a false ``BLOCKED``).

This is the single, conservative cleanup path. It is intentionally narrow:

- it only ever touches worktrees under ``<root>/.worktrees/_reviews/`` — never a
  normal task worktree;
- it never removes a worktree that has a branch checked out (only ``detached``
  review checkouts are candidates), so a parallel agent's active review is safe;
- the age-based backstop keeps anything younger than the TTL (default 48h, which
  matches the claim-expiry window in ``docs/agent-task-claiming.md``);
- ``teardown_own_worktree`` is the exception that removes a specific worktree the
  current review run just created, age-independent but still branch-safety
  checked.

Everything is cross-platform: ``pathlib`` paths, argument-list git subprocesses
via :mod:`physics_lab.registry.review_git`, and UTF-8 throughout.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import shutil
import time

from physics_lab.registry.review_git import run_git_command

# Review worktrees live under ``<root>/.worktrees/_reviews``. Keep this in one
# place so the helper, GC script, and doctor agree on the location.
REVIEW_WORKTREES_RELPARTS: tuple[str, ...] = (".worktrees", "_reviews")

# Conservative default age before the backstop janitor reclaims an abandoned
# detached review worktree. 48h mirrors the branch-claim expiry window so a
# long-running or parallel review is never reclaimed out from under an agent.
DEFAULT_GC_AGE_HOURS: float = 48.0

# Doctor thresholds: recommend a GC run when review worktrees pile up or free
# disk runs low. Read-only — the doctor never deletes.
DOCTOR_REVIEW_COUNT_THRESHOLD: int = 5
DOCTOR_MIN_FREE_BYTES: int = 2 * 1024 * 1024 * 1024  # 2 GiB


def review_worktrees_root(root: Path) -> Path:
    """Return the directory that holds disposable PR-review worktrees."""
    return root.joinpath(*REVIEW_WORKTREES_RELPARTS)


@dataclass(frozen=True)
class ReviewWorktree:
    """A git worktree registered under ``.worktrees/_reviews``."""

    path: Path
    head: str
    branch: str | None
    detached: bool
    age_seconds: float | None
    exists: bool


@dataclass(frozen=True)
class RemovalOutcome:
    """Result of attempting to remove a single review worktree."""

    path: Path
    removed: bool
    reason: str


@dataclass(frozen=True)
class GcReport:
    """Summary of an age-based review-worktree GC pass."""

    root: Path
    older_than_hours: float
    dry_run: bool
    scanned: int
    outcomes: tuple[RemovalOutcome, ...] = ()

    @property
    def removed(self) -> tuple[RemovalOutcome, ...]:
        return tuple(o for o in self.outcomes if o.removed)

    @property
    def skipped(self) -> tuple[RemovalOutcome, ...]:
        return tuple(o for o in self.outcomes if not o.removed)


@dataclass(frozen=True)
class ReviewWorktreeDiskReport:
    """Read-only disk/buildup snapshot for the agent doctor."""

    review_worktree_count: int
    free_bytes: int
    total_bytes: int
    recommend_gc: bool
    reasons: tuple[str, ...] = field(default_factory=tuple)


def _is_under(path: Path, parent: Path) -> bool:
    """Return whether ``path`` is ``parent`` or nested under it (resolved)."""
    try:
        resolved = path.resolve()
        base = parent.resolve()
    except OSError:
        resolved = path
        base = parent
    if resolved == base:
        return True
    return base in resolved.parents


def _worktree_age_seconds(path: Path, now: float) -> float | None:
    """Return the worktree's age in seconds from its directory mtime.

    Directory mtime reflects creation time for a review checkout that is written
    once and never edited; reading files does not bump it. If anything *does*
    touch the worktree, mtime moves forward, which only makes the age-based GC
    more conservative (it waits longer). Returns ``None`` if the path is gone.
    """
    try:
        return max(0.0, now - path.stat().st_mtime)
    except OSError:
        return None


def _parse_worktree_porcelain(text: str) -> list[dict[str, str | bool]]:
    """Parse ``git worktree list --porcelain`` into per-worktree records."""
    records: list[dict[str, str | bool]] = []
    current: dict[str, str | bool] = {}
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line:
            if current:
                records.append(current)
                current = {}
            continue
        if line.startswith("worktree "):
            if current:
                records.append(current)
            current = {"worktree": line[len("worktree "):].strip()}
        elif line.startswith("HEAD "):
            current["head"] = line[len("HEAD "):].strip()
        elif line.startswith("branch "):
            current["branch"] = line[len("branch "):].strip()
        elif line == "detached":
            current["detached"] = True
    if current:
        records.append(current)
    return records


def list_review_worktrees(root: Path, *, now: float | None = None) -> tuple[ReviewWorktree, ...]:
    """List git worktrees registered under ``<root>/.worktrees/_reviews``.

    Best-effort: returns an empty tuple if git is unavailable or the command
    fails, so callers on the review critical path never break on cleanup.
    """
    moment = time.time() if now is None else now
    result = run_git_command(["worktree", "list", "--porcelain"], cwd=root)
    if result.returncode != 0:
        return ()
    reviews_root = review_worktrees_root(root)
    found: list[ReviewWorktree] = []
    for record in _parse_worktree_porcelain(result.stdout):
        raw_path = record.get("worktree")
        if not isinstance(raw_path, str) or not raw_path:
            continue
        path = Path(raw_path)
        if not _is_under(path, reviews_root):
            continue
        branch = record.get("branch")
        exists = path.exists()
        found.append(
            ReviewWorktree(
                path=path,
                head=str(record.get("head") or ""),
                branch=str(branch) if isinstance(branch, str) else None,
                detached=bool(record.get("detached")) or branch is None,
                age_seconds=_worktree_age_seconds(path, moment) if exists else None,
                exists=exists,
            )
        )
    return tuple(found)


def _git_remove_worktree(root: Path, path: Path) -> RemovalOutcome:
    """Run ``git worktree remove --force`` for a single review worktree."""
    result = run_git_command(
        ["worktree", "remove", "--force", str(path)],
        cwd=root,
        extra_safe_directories=(path,),
        timeout=120,
    )
    if result.returncode == 0:
        return RemovalOutcome(path=path, removed=True, reason="removed")
    detail = (result.stderr or result.stdout).strip().splitlines()
    message = detail[-1] if detail else "git worktree remove failed"
    return RemovalOutcome(path=path, removed=False, reason=f"git_error: {message}")


def prune_worktrees(root: Path) -> None:
    """Prune dangling worktree administrative entries (best-effort)."""
    run_git_command(["worktree", "prune"], cwd=root)


def teardown_own_worktree(root: Path, path: Path, *, dry_run: bool = False) -> RemovalOutcome:
    """Remove exactly the review worktree the current review run created.

    Age-independent (the current run owns it) but still branch-safety checked:
    refuses to remove anything outside ``.worktrees/_reviews`` or anything that
    has a branch checked out. Treats an already-gone path as success.
    """
    if not _is_under(path, review_worktrees_root(root)):
        return RemovalOutcome(path=path, removed=False, reason="not_review_worktree")
    matches = {wt.path.resolve(): wt for wt in list_review_worktrees(root)}
    entry = matches.get(path.resolve())
    if entry is None:
        # Not registered anymore (already removed or never created); prune any
        # dangling admin entry and report success.
        if not dry_run:
            prune_worktrees(root)
        return RemovalOutcome(path=path, removed=True, reason="already_absent")
    if not entry.detached or entry.branch is not None:
        return RemovalOutcome(path=path, removed=False, reason="branch_checked_out")
    if dry_run:
        return RemovalOutcome(path=path, removed=False, reason="dry_run")
    outcome = _git_remove_worktree(root, path)
    if outcome.removed:
        prune_worktrees(root)
    return outcome


def gc_review_worktrees(
    root: Path,
    *,
    older_than_hours: float = DEFAULT_GC_AGE_HOURS,
    dry_run: bool = False,
    keep_paths: tuple[Path, ...] = (),
    now: float | None = None,
) -> GcReport:
    """Remove abandoned *detached* review worktrees older than the TTL.

    Conservative by construction: a worktree is removed only when it lives under
    ``.worktrees/_reviews``, is detached (no branch), is at least
    ``older_than_hours`` old, and is not in ``keep_paths``. Everything else is
    skipped with an explicit reason. Never raises on the review critical path —
    a git failure yields an empty scan.
    """
    ttl_seconds = max(0.0, older_than_hours) * 3600.0
    keep = {p.resolve() for p in keep_paths}
    worktrees = list_review_worktrees(root, now=now)
    outcomes: list[RemovalOutcome] = []
    removed_any = False
    for wt in worktrees:
        if wt.path.resolve() in keep:
            outcomes.append(RemovalOutcome(path=wt.path, removed=False, reason="kept"))
            continue
        if not wt.detached or wt.branch is not None:
            outcomes.append(
                RemovalOutcome(path=wt.path, removed=False, reason="branch_checked_out")
            )
            continue
        if not wt.exists:
            # Directory gone but still registered: let prune reclaim it.
            removed_any = True
            outcomes.append(
                RemovalOutcome(path=wt.path, removed=not dry_run, reason="pruned_missing")
            )
            continue
        if wt.age_seconds is None or wt.age_seconds < ttl_seconds:
            outcomes.append(RemovalOutcome(path=wt.path, removed=False, reason="too_recent"))
            continue
        if dry_run:
            outcomes.append(RemovalOutcome(path=wt.path, removed=False, reason="dry_run"))
            continue
        outcome = _git_remove_worktree(root, wt.path)
        removed_any = removed_any or outcome.removed
        outcomes.append(outcome)
    if removed_any and not dry_run:
        prune_worktrees(root)
    return GcReport(
        root=root,
        older_than_hours=older_than_hours,
        dry_run=dry_run,
        scanned=len(worktrees),
        outcomes=tuple(outcomes),
    )


def review_worktree_disk_report(
    root: Path,
    *,
    count_threshold: int = DOCTOR_REVIEW_COUNT_THRESHOLD,
    min_free_bytes: int = DOCTOR_MIN_FREE_BYTES,
) -> ReviewWorktreeDiskReport:
    """Read-only snapshot of review-worktree buildup and free disk (doctor).

    Counts review worktrees and reads free space on the volume holding ``root``.
    Recommends a GC run when worktrees pile up or free disk runs low. Never
    deletes anything.
    """
    worktrees = list_review_worktrees(root)
    count = len(worktrees)
    try:
        usage = shutil.disk_usage(root)
        free_bytes = int(usage.free)
        total_bytes = int(usage.total)
    except OSError:
        free_bytes = -1
        total_bytes = -1
    reasons: list[str] = []
    if count >= count_threshold:
        reasons.append(
            f"{count} review worktrees under .worktrees/_reviews "
            f"(>= {count_threshold})"
        )
    if 0 <= free_bytes < min_free_bytes:
        reasons.append(
            f"free disk {free_bytes // (1024 * 1024)} MiB is below "
            f"{min_free_bytes // (1024 * 1024)} MiB"
        )
    return ReviewWorktreeDiskReport(
        review_worktree_count=count,
        free_bytes=free_bytes,
        total_bytes=total_bytes,
        recommend_gc=bool(reasons),
        reasons=tuple(reasons),
    )


def render_gc_report(report: GcReport) -> str:
    """Render a human-readable summary of a GC pass."""
    lines = [
        "Review worktree GC",
        f"- root: {report.root}",
        f"- older-than-hours: {report.older_than_hours}",
        f"- dry-run: {report.dry_run}",
        f"- scanned: {report.scanned}",
        f"- removed: {len(report.removed)}",
    ]
    for outcome in report.removed:
        verb = "would remove" if report.dry_run else "removed"
        lines.append(f"  * {verb}: {outcome.path} ({outcome.reason})")
    skipped = report.skipped
    if skipped:
        lines.append(f"- kept: {len(skipped)}")
        for outcome in skipped:
            lines.append(f"  * kept: {outcome.path} ({outcome.reason})")
    return "\n".join(lines)
