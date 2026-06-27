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
- **Subprocess environment overrides**: if a test or helper needs to set proxy,
  token, or `PATH` values for one child process, start from the inherited
  environment and override only the needed keys. Use
  `physics_lab.registry.subprocess_env.env_with_overrides(...)`. The older
  `physics_lab.registry.pr_capability.env_with_overrides(...)` import remains a
  compatibility alias for existing PR-helper callers. A tiny replacement
  `env={...}` is allowed only when the test name or comment makes dependency
  loss, missing tools, or minimal environment behavior the scenario under test.
- **Line endings & encoding**: always pass `encoding="utf-8"` to `open(...)` and
  `read_text` / `write_text`. Line-ending normalization is handled by
  `.gitattributes`; do not write `\r\n` by hand.
- **No new bash-only entrypoints on the critical path**: see the next section.

If a platform-specific branch is genuinely required, isolate it behind
`sys.platform` / `os.name` checks and keep a working default for every platform.

## Shell Scripts: Avoid Needless Wrappers

`.sh` scripts do not run on Windows without an extra bash environment. Every
shell script that a third-party agent is *required* to run is a portability
cliff. The operative rule:

> **Maintainer-only and optional `.sh` scripts are acceptable and may stay.**
> Only a script that a third-party agent is *required* to run to execute or hand
> off a task needs a cross-platform (Python) equivalent.

Before adding or keeping a `scripts/*.sh`, ask:

1. **Is it a needless wrapper?** If the script just runs one or two commands
   (e.g. `ruff check` then `pytest`), do not add it — document the raw commands
   instead, or expose them through the Python CLI / a helper module that any
   agent can call on any OS.
2. **Who must run it?** A script that is maintainer-only, or merely *optional*
   for agents, can stay as a bash convenience. Only a script that is *required*
   on a third-party agent's critical path needs a cross-platform equivalent so
   non-bash (Windows) agents are not blocked.
3. **Does it use real orchestration logic** (git worktree setup, multi-step
   snapshotting)? Then a thin port is not worth it yet, but record the gap.

### Audit of existing `scripts/*.sh` (2026-05-31, TASK-0503)

| Script | Verdict | Action |
| --- | --- | --- |
| `validate_quick.sh` | Needless wrapper — only `ruff check .` + `pytest -q`. | Agents run the two commands directly (works on every OS); keep the script as a Linux convenience only. |
| `apl_review_bundle.sh` | Linux/macOS convenience wrapper for the portable `scripts/apl_review_bundle.py` entrypoint. The PR preflight no longer requires a bundle, but maintainer review may generate one. | Keep the Python entrypoint canonical and the shell wrapper thin. |
| `apl_new_worktree.sh` | Real bash logic (git worktree + validation); convenience, not required to execute a task. | Acceptable to keep. Optional Python equivalent if a Windows agent needs scripted worktrees. |
| `apl_setup_worktree.sh` | Real git plumbing (`--git-common-dir`) + file copy; agent-environment convenience. | Acceptable to keep. Optional Python equivalent. |
| `apl_snapshot.sh` | Maintainer-only, already delegates heavy work to `physics_lab.registry.snapshot`. | No action; maintainer-only. |

Conclusion: no existing shell script is a *required* step on a third-party
agent's critical path, so none must be ported right now. The portability rule
applies going forward — do not add a new `.sh` on the required task-execution
or review path without a cross-platform equivalent, and do not add needless
wrappers. The optional Python ports above are nice-to-haves, not blockers.

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

## Windows Agent Bootstrap

Windows contributors and Codex sessions may start with stale process-level
`PATH` values even after Python, Git, or GitHub CLI have been installed. Before
starting task work or before publishing a PR from Windows, run the read-only
doctor:

```powershell
.\.venv\Scripts\python.exe scripts\apl_agent_doctor.py
```

If the repository virtual environment is not usable yet, run the same script
with whichever Python the contributor intends to use. The doctor reports:

- the active Python executable and whether `pip`, `pytest`, `ruff`, and
  `yaml` are importable;
- discovered `git` and `gh` paths, including common Git for Windows and
  GitHub CLI install locations when the current shell `PATH` is stale;
- token fallback availability (`GH_TOKEN` / `GITHUB_TOKEN`);
- suspicious proxy variables such as `HTTP_PROXY=http://127.0.0.1:9` that make
  GitHub CLI failures look like authentication failures.

The doctor does **not** install packages, mutate global `PATH`, store
credentials, or relax validation. Treat missing modules as environment setup
work, not as a task failure. Treat a `127.0.0.1:9` proxy warning as a local
publication blocker. After confirming network access is allowed, prefer the
explicit `--ignore-suspicious-proxy` flag on
`scripts/apl_task_pr_helper.py create` or `ready`. The flag clears only known
loopback blocker values for the child `gh` process; it does not mutate the
parent shell or remove legitimate proxies. Other GitHub CLI commands may still
need the equivalent one-command environment override.

`scripts/apl_mission.py --output onboarding` also attempts a dynamic GitHub
availability check before showing `READY` options. It excludes tasks with an
open claim, an open PR, or a merged PR pending local closeout when metadata is
available. If `gh`, network access, or proxy settings block the lookup, the
script reports a local registry-only fallback instead of hiding tasks or
failing normal offline contributor onboarding. Use
`--github-availability required --ignore-suspicious-proxy` when an operator
wants the live check to be mandatory in an approved networked session.

The default doctor path is read-only. If parallel pytest fails on Windows,
run the opt-in disposable runtime probe:

```powershell
.\.venv\Scripts\python.exe scripts\apl_agent_doctor.py --probe-pytest-runtime --no-gh-auth-check
```

The probe checks the default xdist path, then tries a unique short basetemp
such as `--basetemp=C:/tmp/apl-pytest-<unique-id>` on Windows, then tries an
ignored workspace-local fallback such as
`--basetemp=.pytest-basetemp/session-<unique-id>`. Prefer the short system-temp
fallback when it works: deep worktree paths can hit Windows path-length limits.
Use a unique path so parallel agents do not share scratch state. A restricted
sandbox may deny all fallback paths; in that case request permission for the
targeted pytest command instead of switching to a serial full-suite run. For
narrow task PRs, do not automatically run the full suite serially after an
xdist or temp-directory failure. Use targeted `-n0` debugging and rely on CI
for the broad cross-platform lane. The advisory
`scripts/apl_task_validation_plan.py --task TASK-XXXX` helper prints the
task-specific local commands and flags changed surfaces that warrant the
parallel fast lane.

When a task runs from a dedicated worktree or a sandboxed agent shell, run the
read-only worktree runtime preflight before inventing local fixes:

```powershell
.\.venv\Scripts\python.exe scripts\apl_agent_doctor.py --worktree-runtime-preflight --no-gh-auth-check
```

The preflight reports whether the checkout is a git worktree, where the
worktree git metadata and common git directory live, whether a repository
`.venv` Python can be found from either the current worktree or the common
checkout, whether the active Python matches that interpreter, whether the
system temp directory looks accessible, a recommended unique pytest
`--basetemp`, and read-only git `index.lock`/parent-writability diagnostics.
It does not create files or test-write the git index. If it reports that git
metadata is not writable from the sandbox, follow the normal protocol: rerun
the same `git add` or `git commit` with approved escalation, and do not delete
an `index.lock` unless a separate check verifies that it is stale and no git
process is active.

`scripts/validate_fast.py` also isolates measured `resource_sensitive` tests
as a final serial layer on Windows while leaving the rest of the suite
parallel. It automatically falls back to the ignored workspace-local
`.pytest-basetemp/session-*` root when `C:/tmp` is unavailable. This is
deliberately narrower than a serial full-suite fallback.

For `cmd.exe`, do not use PowerShell's call operator (`&`). For example:

```cmd
"C:\Program Files\GitHub CLI\gh.exe" auth login --hostname github.com --git-protocol https --web --scopes repo
```

For PowerShell, the equivalent is:

```powershell
& "C:\Program Files\GitHub CLI\gh.exe" auth login --hostname github.com --git-protocol https --web --scopes repo
```

The canonical PR helpers (`scripts/apl_task_pr_helper.py` and
`scripts/apl_proposal_pr_helper.py`) now run GitHub CLI with discovered Git and
GitHub CLI directories prepended to the subprocess `PATH`, so a newly installed
Windows `gh.exe` can work without restarting the entire agent session.

## See Also

- `AGENTS.md` — Cross-Platform Compatibility principle
- `docs/agent-task-protocol.md` — execution guidance and forbidden actions
- `docs/maintainer-review-agent.md` — review required-checks list
- `agents/architect.yaml` — cross-platform audit responsibility
