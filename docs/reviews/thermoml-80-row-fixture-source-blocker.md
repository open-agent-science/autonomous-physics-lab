# ThermoML 80-Row Fixture Source Blocker

- Task: `TASK-0955`
- Date: 2026-07-08
- Agent: Codex
- Verdict: `BLOCKED`

## Contract Check

`TASK-0955` requires the bounded 80-row `Tb` fixture to be extracted from the
pinned local archive `ThermoML.v2020-09-30.tgz` under the frozen `TASK-0895`
contract. The source contract forbids a live agent fetch for this task.

The relevant pinned archive identity is:

- filename: `ThermoML.v2020-09-30.tgz`
- size: `189433115` bytes
- SHA-256:
  `231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2`
- source manifest: `data/thermophysical/source_manifest.yaml`
- decision packet:
  `docs/reviews/thermoml-80-row-bounded-extract-maintainer-decision-packet.md`

## Local Availability Check

The checkout and writable temp roots available to the agent were checked for a
matching local archive path:

- repository checkout root
- writable system temp root
- session-specific writable temp root

No `ThermoML.v2020-09-30.tgz` archive was present in those locations during
this run. Because the task explicitly requires the local checksum-matching
archive and forbids a live agent fetch, the extraction cannot proceed.

## Unblock Condition

A maintainer should provide the checksum-matching archive at an agreed
untracked local path, or update the source-access contract in a separate
maintainer-reviewed task. Until then, `TASK-0955` should not be treated as
available execution work.

## Output Routing

- Canonical destination: task lifecycle blocker note.
- Review tier: maintainer review.
- Gate A status: not applicable.
- Gate B status: not applicable.
- Claim impact: no claim promotion.
- Knowledge impact: no knowledge promotion.
- Publication blocker: required local source bytes are unavailable to the
  agent, and live fetch is prohibited.
