# Task Proposals

Use this directory for new task ideas that are not yet assigned a canonical
`TASK-XXXX` id.

Default rule:

- contributors and agents create **task proposals**
- maintainers assign canonical task ids after acceptance

This avoids task-number conflicts during parallel work.

## Files

Filename format:

`YYYYMMDD-<contributor-id>-<short-slug>.yaml`

Examples:

- `20260502-gladunrv-koide-track.yaml`
- `20260502-ihor-github-rf-signal-sandbox.yaml`
- `20260502-romanhladun24-dot-diffusion-benchmark.yaml`

Use the lowercased GitHub username as `contributor-id` when available;
otherwise use a stable maintainer-approved short id.

Use [./TASK-PROPOSAL-TEMPLATE.yaml](./TASK-PROPOSAL-TEMPLATE.yaml) as the
starting point.

## Branch And PR Format

Branch:

`agent/<contributor-id>/<agent-id>/propose-task-<short-slug>`

PR title:

`TASK-PROPOSAL: <short title>`

## Promotion

Accepted proposals may be promoted into canonical task files such as:

`TASK-0043`

Only the maintainer, or a maintainer-directed task-admin/review agent, should
assign that canonical id.

Read [../../docs/task-proposal-protocol.md](../../docs/task-proposal-protocol.md)
for the full protocol.
