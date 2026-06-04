# Task-to-Campaign Lane Index (TASK-0460/TASK-0509)

A compact map from active canonical tasks to campaign (or support) lanes, so
agents and the Scientific Campaign Director can see which `READY` task belongs
to which lane — and whether it is safe for parallel work — without reading every
task file. It complements the campaign **capacity** view (how many agents are
safe per lane) with an on-demand per-task **ownership** view.

## Artifacts

- `scripts/apl_task_campaign_index.py` — query helper for YAML or Markdown output.
- `physics_lab/registry/task_campaign_index.py` — mapping logic (pure functions).

## Usage

```bash
python3 scripts/apl_task_campaign_index.py                 # print YAML
python3 scripts/apl_task_campaign_index.py --format markdown
```

The index is **computed on demand** from canonical task YAML. Do not commit the
rendered output as a repository board or cache. This keeps the architecture
aligned with the retirement of `tasks/ACTIVE.md`: agents and directors query
current state when they need it, while `tasks/TASK-*.yaml` remains the only task
source of truth.

## How a task is mapped to a lane

Resolution order (first match wins), reusing existing task metadata:

1. **`related_domain` exact match** to a campaign id from `campaign_profiles/_catalog.yaml`
   (normalizing `_` → `-`), e.g. `nuclear_mass_surface` → `nuclear-mass-surface`.
2. **Campaign reference** in `related_objects` or `accepted_outputs`, e.g. a
   `docs/campaigns/<campaign-id>.md` path or the campaign id itself.
3. **Support lane** when `related_domain` is a known cross-campaign support
   domain (e.g. `maintainer_review`, `agent_capacity`, `result_promotion`) or
   the task `type` is a workflow/maintenance type.
4. Otherwise **`UNMAPPED`** — flagged for curator review rather than guessed.
   This is the expected state for a task whose campaign does not exist yet
   (e.g. a scaffold task that *creates* the campaign).

## Per-task fields

- `lane` — campaign id, `support`, or `UNMAPPED`.
- `mapping_basis` — why the task landed in that lane (auditable).
- `artifact_surface` — likely top-level write surfaces, derived from
  `accepted_outputs` path tokens.
- `parallel_safe` — `false` when the task writes a shared mutable canonical
  surface (`results/`, `claims/`, `knowledge/`, `prediction_registry/`,
  `hypotheses/`, `experiments/`, `campaign_profiles/_catalog.yaml`,
  `missions/current.yaml`);
  `true` for planning/doc/script tasks that only touch their own files.
- `path_conflicts` (index-level) — concrete `accepted_outputs` paths claimed by
  more than one active task, the clearest signal of a real write collision.

## Limitations

- `parallel_safe` is a conservative per-task heuristic from declared accepted
  outputs; it does not parse code to find every file a task might touch.
- A task whose campaign id is not yet in the catalog is `UNMAPPED` by design;
  add the campaign profile (and regenerate `campaign_profiles/_catalog.yaml`)
  to map it.
- The index is descriptive: it never changes task status or campaign metadata.
- Because the output is intentionally not committed, historical state should be
  read from task files, snapshots, and git history rather than from a stale
  generated cache.
