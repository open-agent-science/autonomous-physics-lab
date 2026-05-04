# Private Multi-Agent Dry Run

This document records incremental observations for `TASK-0012`.

It is not, by itself, a declaration that `TASK-0012` is complete. The task
still requires multiple task-based PRs and a broader workflow summary.

## Run #1

- Date: `2026-05-02`
- Task: `TASK-0014`
- Task file: `tasks/TASK-0014-thought-experiment-consistency-suite-planning.yaml`
- Agent branch: `agent/claude/task-0014-thought-experiment-plan`
- Pull request: `#6`
- PR title: `TASK-0014: Plan a thought-experiment consistency suite`
- Merge commit: `9835ac6`
- Scope: planning only, with no implementation or scientific claim promotion

### Maintainer review focus

- confirmed the output stayed in planning scope rather than implementation;
- confirmed the planning document includes assumptions, invariants, and known
  limits;
- confirmed no "we proved" or "new physics" style claim language was added;
- confirmed `TASK-0014` remained `REVIEW_READY` until maintainer closeout.

### Artifacts reviewed

- `docs/notes/thought-experiment-consistency-suite.md`
- `tasks/TASK-0014-thought-experiment-consistency-suite-planning.yaml`
- `tasks/ACTIVE.md`

### Outcome

- the planning PR was merged into `main`;
- the repository now has a reusable thought-experiment planning artifact;
- this maintainer follow-up closes `TASK-0014` and records the first dry-run
  event for `TASK-0012`.

### Limitations

- this is only the first recorded run toward `TASK-0012`;
- GitHub review discussion and CI details live in the PR UI and are not copied
  into this repository note;
- the private multi-agent dry run still needs additional task-based PRs before
  `TASK-0012` can be considered complete.

### Lessons so far

- the task/branch/PR protocol supports planning-only contributions cleanly;
- maintainer follow-up is still needed to move `REVIEW_READY` work to `DONE`;
- keeping planning outputs separate from implementation artifacts reduces
  overclaiming risk during review.

## Run #2

- Date: `2026-05-02`
- Task: `TASK-0033`
- Task file: `tasks/TASK-0033-standardize-contributor-agent-identity-format.yaml`
- Agent branch: `agent/roman/codex/task-0033-standardize-contributor-agent-identity-format`
- Pull request: `#16`
- PR title: `TASK-0033: Standardize contributor-agent identity format`
- Merge commit: `40d0d7d`
- Scope: workflow improvement only, with no scientific artifact or claim changes

### Maintainer review focus

- confirmed the new branch format preserves both the human owner and the agent tool;
- confirmed PR metadata now captures contributor and agent details explicitly;
- confirmed the new commit-permission rules keep `main`, force-push, and other
  destructive git actions restricted;
- confirmed historical private-pilot branch names were preserved rather than
  rewritten.

### Artifacts reviewed

- `AGENTS.md`
- `docs/agent-task-protocol.md`
- `docs/private-contributor-pilot.md`
- `docs/contributing-workflow.md`
- `.github/pull_request_template.md`
- `tasks/TASK-0033-standardize-contributor-agent-identity-format.yaml`
- `tasks/ACTIVE.md`

### Outcome

- the workflow-improvement PR was merged into `main`;
- the repository now records both contributor identity and agent-tool identity
  in its canonical branch and PR metadata rules;
- agent commit permissions are now explicit instead of implied by maintainer
  convention.

### Limitations

- this run improved contributor workflow only and did not exercise scientific
  validation beyond repository integrity checks;
- older branch names from the private pilot remain as historical artifacts, so
  repository history still contains mixed legacy naming patterns;
- the dry run still needs more merged examples across different task types and
  contributors before `TASK-0012` can be considered complete.

### Lessons so far

- scaling agent-assisted contribution review requires tracking both the human
  owner and the tool used;
- agent autonomy benefits from explicit git guardrails written into repository
  policy;
- merged workflow tasks should be recorded in the dry-run log so protocol
  improvements are visible in repository memory.

## Run #3

- Date: `2026-05-03`
- Task: `TASK-0027`
- Task file: `tasks/TASK-0027-units-and-constants-reference.yaml`
- Agent branch: `agent/akutenyov/claude/task-0027-units-and-constants-reference`
- Pull request: `#24`
- PR title: `TASK-0027: Create units and physical constants reference`
- Merge commit: pending maintainer review
- Contributor: `akutenyov` (human), `claude` (agent tool)
- Scope: physics reference documentation, no scientific claims

### Maintainer review focus

- confirm `knowledge/reference/units-and-dimensions.md` has correct YAML front
  matter matching the knowledge schema;
- confirm `knowledge/reference/physical-constants.yaml` uses CODATA 2018 values
  with explicit uncertainty and source fields;
- confirm reference-data warning note is present in both files;
- confirm `physics_lab/schemas/knowledge.schema.json` change (minItems: 0)
  does not break existing knowledge file validation;
- confirm all CI checks pass including strict validation.

### Artifacts reviewed

- `knowledge/reference/units-and-dimensions.md`
- `knowledge/reference/physical-constants.yaml`
- `physics_lab/schemas/knowledge.schema.json`
- `tests/test_pendulum.py`
- `tasks/TASK-0027-units-and-constants-reference.yaml`

### Outcome

- PR opened and CI passing;
- repository now has a reusable reference layer for SI units, dimensions, and
  physical constants;
- knowledge schema updated to allow reference-type files without mandatory
  linked hypotheses, experiments, or claims.

### Limitations

- PR is pending maintainer review and merge;
- working without Claude Code required manual file transfer and git operations
  via PowerShell, which introduced extra friction;
- knowledge schema change (minItems: 0) is a broader schema relaxation that
  maintainer should review carefully.

### Lessons so far

- working without Claude Code via chat interface requires extra discipline to
  avoid staging unrelated files;
- schema validation errors surface only in CI, not locally without a Python
  environment — earlier local validation would reduce iteration cycles;
- the contributor-agent identity format (`akutenyov/claude`) worked cleanly for
  branch naming and PR metadata.

## Pilot Summary

Three dry-run events have now been recorded across two contributors
(`roman` and `akutenyov`) and two agent tools (`codex` and `claude`).

### PR inventory

| Run | Task | Contributor | Agent | PR | Status |
|-----|------|-------------|-------|----|--------|
| #1 | TASK-0014 | roman | claude | #6 | merged |
| #2 | TASK-0033 | roman | codex | #16 | merged |
| #3 | TASK-0027 | akutenyov | claude | #24 | review |

### Workflow friction observed

- working without Claude Code requires manual file transfer between chat and
  filesystem, which increases error surface;
- `ACTIVE.md` merge conflicts are a recurring friction point when multiple
  contributors work in parallel;
- schema validation errors are invisible without a local Python environment.

### Workflow strengths observed

- branch-based task protocol cleanly separates contributor work;
- PR template captures both human and agent identity without ambiguity;
- CI pipeline catches schema and validation errors before maintainer review.

### Open items before TASK-0012 can be marked DONE

- at least one more PR from a distinct contributor or task type is recommended;
- maintainer must review and merge all REVIEW_READY PRs from this pilot;
- lessons learned should be incorporated into contributor documentation.

## Run #1

- Date: `2026-05-04`
- Task: `TASK-0062`
- Pull request: `#64`
- Scope: maintainer closeout entry for a merged contributor or workflow task

### Outcome

- the merged PR was reviewed and closed out on `main`;
- the task moved from `REVIEW_READY` to `DONE`.

### Limitations

- this note is a short maintainer closeout summary only;
- detailed review discussion remains in the PR thread.
