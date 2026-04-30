#!/usr/bin/env bash

set -u
shopt -s nullglob

mkdir -p _snapshots

TS="$(date -u +%Y%m%d_%H%M%S)"
OUT="_snapshots/apl_snapshot_${TS}.md"

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
  echo "- repo: $(basename "$(pwd)")"
  echo "- path: $(pwd)"

  section "Git State"

  cmd_block "Current branch" git branch --show-current
  cmd_block "Git status" git status --short
  cmd_block "Last commits" git log --oneline -n 12
  cmd_block "Changed files" git diff --name-only
  cmd_block "Diff stat" git diff --stat
  cmd_block "Tracked cache check" git ls-files .pytest_cache .ruff_cache

  section "Local Path Leak Check"

  cmd_block "Absolute local path grep" \
    git grep -n "/Users/roman\\|MacBook\\|Autonomous%20Physics%20Lab" \
    README.md AGENTS.md CODEX_TASK.md docs claims knowledge results physics_lab

  section "Repository Tree"

  echo '```text'
  find . \
    -path ./.git -prune -o \
    -path ./.venv -prune -o \
    -path ./.pytest_cache -prune -o \
    -path ./.ruff_cache -prune -o \
    -path ./__pycache__ -prune -o \
    -path ./_snapshots -prune -o \
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
    docs/status.md \
    docs/architecture.md \
    docs/implementation-plan.md \
    docs/next-steps.md \
    docs/roadmap.md \
    docs/backlog.md \
    docs/knowledge-base.md \
    docs/open-agent-network.md
  do
    file_block "$f" 260
  done

  section "Registry Objects"

  for f in \
    hypotheses/*.yaml \
    experiments/*.yaml \
    tasks/*.yaml \
    agents/*.yaml \
    claims/*.md
  do
    file_block "$f" 260
  done

  while IFS= read -r f; do
    file_block "$f" 260
  done < <(find knowledge -type f -name '*.md' | sort 2>/dev/null || true)

  section "Result Artifacts"

  echo '```text'
  find results -maxdepth 5 -type f | sort 2>/dev/null || true
  echo '```'

  while IFS= read -r f; do
    file_block "$f" 320
  done < <(find results -maxdepth 5 -type f \( -name '*.yaml' -o -name '*.json' -o -name '*.md' \) | sort 2>/dev/null || true)

  section "Schemas"

  for f in physics_lab/schemas/*.json
  do
    file_block "$f" 220
  done

  section "Validation Commands"

  cmd_block "ruff" python3 -m ruff check .
  cmd_block "pytest" python3 -m pytest
  cmd_block "validate repo" python3 -m physics_lab.cli validate-repo .

  if [ "${RUN_EXPERIMENT:-0}" = "1" ]; then
    cmd_block "run pendulum example" python3 -m physics_lab.cli run examples/pendulum.yaml
  else
    echo ""
    echo "### run pendulum example"
    echo ""
    echo "Skipped. To include it, run:"
    echo ""
    echo '```bash'
    echo "RUN_EXPERIMENT=1 ./scripts/apl_snapshot.sh"
    echo '```'
  fi

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
