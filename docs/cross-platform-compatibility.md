# Cross-Platform Compatibility

Autonomous Physics Lab must stay usable by third-party agents and contributors
on **Linux, macOS, and Windows**. CI currently runs on Linux only, so the
burden of keeping the repository portable falls on the agents writing the code
and on the maintainer review agent — not on a Windows CI runner. This document
is the canonical standard for that responsibility.

Scope note: this is about keeping *contributor-facing* code and tooling
portable. It is **not** a request to change CI runners or add a Windows/macOS CI
matrix; that is tracked separately.

## Rule For Agents Writing Code

When you implement a task, write code that runs on all three platforms:

- **Paths**: build paths with `pathlib.Path` (or `os.path.join`), never by
  concatenating with hardcoded `/`. Use `Path.as_posix()` only for display or
  for git paths, not for filesystem access.
- **Temp files**: use `tempfile.gettempdir()`, `tempfile.TemporaryDirectory()`,
  or `tempfile.NamedTemporaryFile`. Never hardcode `/tmp`.
- **Home directory**: use `Path.home()`, not `os.getenv("HOME")` (Windows uses
  `USERPROFILE`).
- **The Python interpreter**: invoke subprocesses with `sys.executable`, not a
  hardcoded `"python3"` (Windows ships `python` / the `py` launcher).
- **Subprocesses**: pass an argument list, keep `shell=False` (the default), and
  do not rely on shell features (`|`, `&&`, globbing, `&`). `shell=True` is also
  a security smell and is blocked by review.
- **Line endings & encoding**: always pass `encoding="utf-8"` to `open(...)` and
  `read_text` / `write_text`. Line-ending normalization is handled by
  `.gitattributes`; do not write `\r\n` by hand.
- **No new bash-only entrypoints on the critical path**: see the next section.

If a platform-specific branch is genuinely required, isolate it behind
`sys.platform` / `os.name` checks and keep a working default for every platform.

## Shell Scripts: Avoid Needless Wrappers

`.sh` scripts do not run on Windows without an extra bash environment. Every
shell script on a third-party agent's critical path is a portability cliff.
Before adding or keeping a `scripts/*.sh`, ask:

1. **Is it a needless wrapper?** If the script just runs one or two commands
   (e.g. `ruff check` then `pytest`), do not add it — document the raw commands
   instead, or expose them through the Python CLI / a helper module that any
   agent can call on any OS.
2. **Is it on the critical path for executing/reviewing a task?** If yes, it
   needs a cross-platform (Python) equivalent so non-bash agents are not
   blocked. Maintainer-only convenience scripts are lower priority.
3. **Does it use real orchestration logic** (git worktree setup, multi-step
   snapshotting)? Then a thin port is not worth it yet, but record the gap.

### Audit of existing `scripts/*.sh` (2026-05-31, TASK-0503)

| Script | Verdict | Action |
| --- | --- | --- |
| `validate_quick.sh` | Needless wrapper — only `ruff check .` + `pytest -q`. | Agents run the two commands directly (works on every OS); keep the script as a Linux convenience only. |
| `apl_review_bundle.sh` | **Critical path** — required in the review flow (`microtask_pr_helper`, `maintainer_review` invoke/expect it) but unrunnable on Windows. | Recommended follow-up: add a cross-platform Python entrypoint that produces the same review bundle. |
| `apl_new_worktree.sh` | Real bash logic (git worktree + validation), but on the external-agent path. | Lower-priority follow-up: optional Python equivalent. |
| `apl_setup_worktree.sh` | Real git plumbing (`--git-common-dir`) + file copy. | Lower-priority follow-up: optional Python equivalent. |
| `apl_snapshot.sh` | Maintainer-only, already delegates heavy work to `physics_lab.registry.snapshot`. | No action; not on the external-agent critical path. |

The most valuable follow-up is a portable `apl_review_bundle` entrypoint,
because the review bundle is *required* and currently bash-only.

## What Review Checks

The maintainer review agent surfaces portability regressions as **advisory**
warnings (never auto-blocking), via `cross_platform_advisory_hits` and
`cross_platform_surface_hits` in `physics_lab/registry/review_checks.py`:

- added code that hardcodes `/tmp`, `"python3"`, `HOME`, or invokes a `.sh`
  script directly;
- any changed `scripts/*.sh` (reminder to confirm it is not a needless wrapper
  and that a cross-platform path exists).

Reviewers treat these as a checklist prompt, not a merge blocker, and ask for a
portable alternative when the smell is on a contributor-facing path.

## See Also

- `AGENTS.md` — Cross-Platform Compatibility principle
- `docs/agent-task-protocol.md` — execution guidance and forbidden actions
- `docs/maintainer-review-agent.md` — review required-checks list
- `agents/architect.yaml` — cross-platform audit responsibility
