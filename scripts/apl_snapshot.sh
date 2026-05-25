#!/usr/bin/env bash

set -u
shopt -s nullglob

TS="$(date -u +%Y%m%d_%H%M%S)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
CANONICAL_REPO_ROOT="$("${PYTHON_BIN}" - <<'PY'
from pathlib import Path
from physics_lab.registry.snapshot import build_snapshot_context

print(build_snapshot_context(Path(".")).canonical_root)
PY
)"
SNAPSHOT_DIR="${APL_SNAPSHOT_DIR:-${CANONICAL_REPO_ROOT}/_snapshots}"
mkdir -p "$SNAPSHOT_DIR"
OUT="${SNAPSHOT_DIR}/apl_snapshot_${TS}.md"

section() {
  echo ""
  echo "## $1"
  echo ""
}

file_block() {
  local file="$1"
  local max_lines="${2:-220}"

  if [ -f "$file" ]; then
    echo ""
    echo "### FILE: $file"
    echo ""
    echo '```'
    sed -n "1,${max_lines}p" "$file"
    echo '```'
  fi
}

cmd_block() {
  local title="$1"
  shift

  echo ""
  echo "### $title"
  echo ""
  echo '```bash'
  printf '$'
  printf ' %q' "$@"
  echo ""
  "$@" 2>&1 || true
  echo '```'
}

{
  echo "# Autonomous Physics Lab Snapshot"
  echo ""
  echo "- generated_at_utc: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "- repo: $("${PYTHON_BIN}" - <<'PY'
from pathlib import Path
from physics_lab.registry.snapshot import build_snapshot_context

print(build_snapshot_context(Path(".")).repo_name)
PY
)"
  echo "- invocation_path: $(pwd)"
  echo "- canonical_repo_root: $("${PYTHON_BIN}" - <<'PY'
from pathlib import Path
from physics_lab.registry.snapshot import build_snapshot_context

print(build_snapshot_context(Path(".")).canonical_root)
PY
)"
  echo "- current_branch: $("${PYTHON_BIN}" - <<'PY'
from pathlib import Path
from physics_lab.registry.snapshot import build_snapshot_context

print(build_snapshot_context(Path(".")).current_branch)
PY
)"
  echo "- default_base_ref: $("${PYTHON_BIN}" - <<'PY'
from pathlib import Path
from physics_lab.registry.snapshot import build_snapshot_context

print(build_snapshot_context(Path(".")).default_base_ref)
PY
)"

  section "Current Authoritative State"

  echo '```markdown'
  "$PYTHON_BIN" - <<'PY'
from pathlib import Path
from physics_lab.registry.snapshot import render_authority_notes, render_current_state_summary

root = Path(".")
print(render_authority_notes(root))
print("")
print(render_current_state_summary(root))
PY
  echo '```'

  section "Git State"

  cmd_block "Current branch" git branch --show-current
  cmd_block "Git status" git status --short
  cmd_block "Last commits" git log --oneline -n 12
  cmd_block "Changed files" git diff --name-only
  cmd_block "Diff stat" git diff --stat
  cmd_block "Tracked cache check" git ls-files .pytest_cache .ruff_cache

  section "Open Pull Requests"

  echo '```text'
  if command -v gh >/dev/null 2>&1; then
    origin_url="$(git remote get-url origin 2>/dev/null || true)"
    repo_slug="$(printf '%s\n' "$origin_url" | sed -E 's#^git@github.com:##; s#^https://github.com/##; s#\.git$##')"
    if [ -n "$repo_slug" ] && [ "$repo_slug" != "$origin_url" ]; then
      pr_list_output="$(gh pr list --repo "$repo_slug" --state open --limit 30 2>&1)"
    else
      pr_list_output="$(gh pr list --state open --limit 30 2>&1)"
    fi
    pr_list_status=$?
    if [ "$pr_list_status" -eq 0 ]; then
      if [ -n "$pr_list_output" ]; then
        printf '%s\n' "$pr_list_output"
      else
        echo "No open pull requests."
      fi
    else
      echo "Skipped: gh pr list failed."
      printf '%s\n' "$pr_list_output"
    fi
  else
    echo "Skipped: gh CLI is not installed."
  fi
  echo '```'

  section "Local Path Leak Check"

  cmd_block "Absolute local path grep" \
    git grep -n "/Users/roman\\|MacBook\\|Autonomous%20Physics%20Lab" \
    README.md AGENTS.md CODEX_TASK.md docs claims knowledge results physics_lab

  section "Maintainer Docs Context"

  for f in \
    docs/status.md \
    docs/next-steps.md \
    docs/roadmap.md \
    docs/mission-control.md
  do
    file_block "$f" 220
  done

  section "Archive Context"

  echo ""
  echo "These sections remain intentionally verbose for deep audit and historical"
  echo "inspection. Treat them as supporting context, not the primary source of"
  echo "truth when they disagree with the generated current-state summary above."
  echo ""

  section "Repository Tree"

  echo '```text'
  find . \
    -path ./.git -prune -o \
    -path ./.worktrees -prune -o \
    -path ./.venv -prune -o \
    -path ./.pytest_cache -prune -o \
    -path ./.ruff_cache -prune -o \
    -path ./.claude -prune -o \
    -path ./__pycache__ -prune -o \
    -path ./_snapshots -prune -o \
    -name .DS_Store -prune -o \
    -print | sort
  echo '```'

  section "Top-Level Project Files"

  for f in \
    README.md \
    AGENTS.md \
    CODEX_TASK.md \
    CONTRIBUTING.md \
    LICENSE \
    pyproject.toml \
    .github/workflows/ci.yml
  do
    file_block "$f" 260
  done

  section "Core Docs"

  for f in \
    docs/architecture.md \
    docs/implementation-plan.md \
    docs/roadmap.md \
    docs/backlog.md \
    docs/knowledge-base.md \
    docs/open-agent-network.md
  do
    file_block "$f" 260
  done

  section "Proposal Backlog"

  echo '```text'
  "$PYTHON_BIN" - <<'PY'
from pathlib import Path
import yaml

task_paths = sorted(Path("tasks").glob("TASK-*.yaml"))
proposal_paths = sorted(Path("tasks/proposals").glob("*.yaml"))

print("Canonical tasks with status PROPOSED:")
found_proposed_tasks = False
for path in task_paths:
    if path.name == "TASK-TEMPLATE.yaml":
        continue
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if payload.get("status") == "PROPOSED":
        found_proposed_tasks = True
        print(
            f"- {payload.get('id', path.stem)} — "
            f"{payload.get('title', '')} [{path.as_posix()}]"
        )
if not found_proposed_tasks:
    print("- none")

print("")
print("Task proposal files:")
found_proposals = False
for path in proposal_paths:
    if path.name == "TASK-PROPOSAL-TEMPLATE.yaml":
        continue
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    found_proposals = True
    print(
        f"- {payload.get('proposal_id', path.stem)} — "
        f"{payload.get('title', '')} [{path.as_posix()}]"
    )
if not found_proposals:
    print("- none")
PY
  echo '```'

  section "Registry Objects"

  for f in \
    hypotheses/*.yaml \
    experiments/*.yaml \
    tasks/*.yaml \
    tasks/proposals/*.yaml \
    agents/*.yaml \
    claims/*.md
  do
    file_block "$f" 260
  done

  while IFS= read -r f; do
    file_block "$f" 260
  done < <(find knowledge -type f -name '*.md' ! -name '.DS_Store' | sort 2>/dev/null || true)

  section "Result Artifacts"

  echo '```text'
  find results -maxdepth 5 -type f ! -name '.DS_Store' | sort 2>/dev/null || true
  echo '```'

  while IFS= read -r f; do
    file_block "$f" 320
  done < <(find results -maxdepth 5 -type f \( -name '*.yaml' -o -name '*.json' -o -name '*.md' \) ! -name '.DS_Store' | sort 2>/dev/null || true)

  section "Schemas"

  for f in physics_lab/schemas/*.json
  do
    file_block "$f" 220
  done

  section "Snapshot Scope"

  echo "This snapshot is an inventory artifact. It records repository state,"
  echo "task state, docs context, result artifacts, and open PRs without running"
  echo "validation or experiment commands."

  section "Recommended Human Summary"

  echo "Fill this manually before sending if needed:"
  echo ""
  echo "- What changed:"
  echo "- Why it changed:"
  echo "- What is uncertain:"
  echo "- What Codex reported:"
  echo "- Next planned step:"

} > "$OUT"

echo "Snapshot written to: $OUT"
