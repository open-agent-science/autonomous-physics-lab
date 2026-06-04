# Research Proposal Namespace Policy

`hypothesis_proposals/` and `experiment_proposals/` are campaign-scoped
scientific memory surfaces. Early campaign batches reused ids such as
`HYP-PROPOSAL-0049` and `EXP-PROPOSAL-0015` across different campaign folders.
Those historical files remain valid scientific memory, but their bare ids are
not globally unique.

## Current Rule

- Treat hypothesis and experiment proposal references as **path-scoped** when a
  bare id is ambiguous.
- Prefer full repository paths in run manifests, reviews, and task outputs:
  `hypothesis_proposals/<campaign>/HYP-PROPOSAL-XXXX-<slug>.yaml`.
- Do not create new duplicate unscoped proposal ids.
- Do not rename historical proposal files in small follow-up PRs unless the PR
  also updates every script, result, review, and test reference that points to
  them.

## Validation

`validate-repo --strict` reports duplicate research-proposal ids as `INFO` by
default. This keeps historical proposal memory visible without failing normal CI
while the repository still contains known campaign-scoped duplicates.

For an explicit architecture audit, run:

```bash
APL_ENFORCE_RESEARCH_PROPOSAL_ID_UNIQUENESS=1 \
  python3 -m physics_lab.cli validate-repo . --strict
```

That escalation reports duplicate research-proposal ids as `ERROR`.

## Future Normalization Options

The next cleanup should choose one strategy before any mass rename:

- Keep ids campaign-scoped permanently and require path-scoped references.
- Move to globally unique ids and migrate historical references in one reviewed
  batch.
- Introduce campaign-prefixed ids for future proposals while preserving old
  files as legacy scientific memory.
