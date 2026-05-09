# Microtask Runs

`microtask_runs/` stores append-only claim and completion records for campaign
microtasks. These records reduce duplicate work without rewriting queue files
for every claim.

The registry is coordination memory, not canonical scientific evidence:

- it does not promote claims;
- it does not create canonical `results/` artifacts;
- it does not replace maintainer review;
- it does not make queue items unavailable forever.

Use one YAML file per claimed or completed microtask run. Prefer this layout:

```text
microtask_runs/<queue-id>/MICROTASK-RUN-0001.yaml
```

Before claiming work, check:

1. recent files under this registry for the same `queue_id` and `microtask_id`;
2. open PRs with the same microtask id or queue id;
3. existing notes or result summaries linked from the queue file.

Copy `MICROTASK-RUN-TEMPLATE.yaml` for new entries. Keep paths
repository-relative and use `REVIEW_NEEDED` when interpretation is uncertain.