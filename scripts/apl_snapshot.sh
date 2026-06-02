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

  section "Strategic Context For Agents"

  echo '```markdown'
  "$PYTHON_BIN" - <<'PY'
from pathlib import Path
from physics_lab.registry.snapshot import render_strategic_context_map

print(render_strategic_context_map(Path(".")))
PY
  echo '```'

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
    docs/current-missions.md \
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

  section "Repository Structure Map"

  echo '```text'
  "$PYTHON_BIN" - <<'PY'
from pathlib import Path

KEY_DIRS = [
    "agents",
    "agent_runs",
    "campaign_profiles",
    "docs",
    "docs/campaigns",
    "docs/reviews",
    "docs/task-views",
    "experiments",
    "hypothesis_proposals",
    "experiment_proposals",
    "missions",
    "prediction_registry",
    "results",
    "scripts",
    "tasks",
    "tasks/proposals",
    "tests",
]

print("Important repository surfaces:")
for raw_dir in KEY_DIRS:
    path = Path(raw_dir)
    if not path.exists():
        print(f"- {raw_dir}/: missing")
        continue
    file_count = sum(1 for child in path.rglob("*") if child.is_file())
    immediate_dirs = sorted(child.name for child in path.iterdir() if child.is_dir())[:8]
    suffix = f" | subdirs: {', '.join(immediate_dirs)}" if immediate_dirs else ""
    print(f"- {raw_dir}/: {file_count} files{suffix}")

print("")
print("Recent high-numbered task files:")
task_paths = sorted(
    Path("tasks").glob("TASK-[0-9][0-9][0-9][0-9]-*.yaml"),
    key=lambda path: path.name,
    reverse=True,
)
for path in task_paths[:40]:
    print(f"- {path.as_posix()}")
if len(task_paths) > 40:
    print(f"- ... {len(task_paths) - 40} older task files omitted")

print("")
print("Recent agent-run artifacts:")
agent_run_paths = sorted(
    Path("agent_runs").glob("AGENT-RUN-*/agent_run.yaml"),
    key=lambda path: path.parent.name,
    reverse=True,
)
for path in agent_run_paths[:20]:
    print(f"- {path.as_posix()}")
if len(agent_run_paths) > 20:
    print(f"- ... {len(agent_run_paths) - 20} older agent runs omitted")
PY
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
    docs/agent-operating-model.md \
    docs/agent-task-protocol.md \
    docs/maintainer-review-agent.md \
    docs/review-checklists/task-closeout-checklist.md \
    docs/result-promotion-protocol.md \
    docs/campaign-output-scorecard.md \
    docs/scientific-memory-review-tiers.md \
    docs/result-artifacts-index.md \
    docs/negative-results-registry.md \
    docs/fresh-data-readiness-matrix.md \
    docs/fresh-data-intake-protocol.md \
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

  section "Task Registry Snapshot"

  echo '```text'
  "$PYTHON_BIN" - <<'PY'
from collections import Counter
from pathlib import Path

import yaml

task_rows = []
for path in sorted(Path("tasks").glob("TASK-[0-9][0-9][0-9][0-9]-*.yaml")):
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    task_id = str(payload.get("id", path.stem))
    try:
        task_number = int(task_id.removeprefix("TASK-"))
    except ValueError:
        task_number = -1
    task_rows.append(
        {
            "id": task_id,
            "number": task_number,
            "title": str(payload.get("title", "")),
            "status": str(payload.get("status", "unknown")),
            "type": str(payload.get("type", "")),
            "priority": str(payload.get("priority", "")),
            "difficulty": str(payload.get("difficulty", "")),
            "path": path.as_posix(),
        }
    )

counts = Counter(row["status"] for row in task_rows)
print("Task status counts:")
for status, count in sorted(counts.items()):
    print(f"- {status}: {count}")

print("")
print("Task contracts included below in full:")
for status in ("READY", "REVIEW_READY", "BLOCKED"):
    rows = [row for row in task_rows if row["status"] == status]
    print(f"- {status}: {len(rows)}")

print("")
print("Recent DONE history (short list only):")
done_rows = sorted(
    [row for row in task_rows if row["status"] == "DONE"],
    key=lambda row: row["number"],
    reverse=True,
)
for row in done_rows[:40]:
    print(f"- {row['id']} — {row['title']} [{row['path']}]")
if len(done_rows) > 40:
    print(f"- ... {len(done_rows) - 40} older DONE tasks omitted from full snapshot context")
PY
  echo '```'

  section "Current Task Contracts"

  echo ""
  echo "Only READY, REVIEW_READY, and BLOCKED task contracts are included in full."
  echo "Historical DONE and older PROPOSED task files are summarized above to keep"
  echo "strategy snapshots focused and token-efficient."
  echo ""

  live_task_contract_paths="$("$PYTHON_BIN" - <<'PY'
from pathlib import Path

import yaml

live_statuses = {"READY", "REVIEW_READY", "BLOCKED"}
rows = []
for path in sorted(Path("tasks").glob("TASK-[0-9][0-9][0-9][0-9]-*.yaml")):
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if str(payload.get("status", "")) in live_statuses:
        task_id = str(payload.get("id", path.stem))
        try:
            number = int(task_id.removeprefix("TASK-"))
        except ValueError:
            number = -1
        rows.append((number, path.as_posix()))
for _number, path in sorted(rows):
    print(path)
PY
  )"
  while IFS= read -r f; do
    file_block "$f" 220
  done <<< "$live_task_contract_paths"

  section "Registry Objects"

  for f in \
    hypotheses/*.yaml \
    experiments/*.yaml \
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
