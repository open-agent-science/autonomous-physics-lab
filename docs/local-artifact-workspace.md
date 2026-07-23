# Local Artifact Workspace

This document is the canonical cross-campaign contract for local scientific
files that must stay outside git. It separates immutable private source inputs
from generated task work and keeps both locations stable across git worktrees.

This contract does not change source admissibility, redistribution rights, or
result-promotion rules. A locally available file is only an input candidate
until its checksum, provenance, and rights posture pass the relevant gates.

## Two Local Roots

| Class | Environment override | Default |
| --- | --- | --- |
| Private or non-redistributable source bytes | `APL_PRIVATE_SOURCE_ROOT` | sibling of the primary checkout named `<checkout>-private-sources` |
| Durable generated task work | `APL_LOCAL_WORK_ROOT` | sibling of the primary checkout named `<checkout>-local-work` |

The helper resolves the primary checkout from git's common directory. Linked
worktrees therefore see the same two roots even when the worktree itself lives
under a temporary directory or a different parent.

Use `scripts/apl_local_artifacts.py` to inspect the resolved roots:

```bash
python3 scripts/apl_local_artifacts.py roots
```

The command is read-only and does not create either root. On a nonstandard
clone or agent host, set an absolute environment override or pass the matching
CLI root option. Relative roots are rejected because their meaning changes
between worktrees.

## Private Source Layout

New private source files should use a source-scoped directory:

```text
<private-source-root>/
  <source-id>/
    <upstream-filename>
```

For example, a future placement of the pinned ThermoML archive may be:

```text
<private-source-root>/
  nist-trc-thermoml-archive/
    ThermoML.v2020-09-30.tgz
```

Existing files directly under the private-source root remain supported as a
legacy fallback. They do not need to be moved merely to adopt this contract.
Source bytes are read-only inputs for executor agents: do not unpack archives,
write sidecars, normalize rows, or place generated files beside them.

Locate one exact source and verify its frozen digest before a scientific
workflow reads it:

```bash
python3 scripts/apl_local_artifacts.py locate \
  --source-id nist-trc-thermoml-archive \
  --filename ThermoML.v2020-09-30.tgz \
  --sha256 231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2
```

The lookup order is:

1. `--input <absolute-file>` when supplied;
2. `--private-source-root <absolute-directory>`;
3. `APL_PRIVATE_SOURCE_ROOT`;
4. the worktree-shared sibling default.

Within a selected root the helper checks only
`<source-id>/<filename>`, then the legacy `<filename>` fallback. It never
recursively scans the vault, home directory, Downloads, Desktop, other clones,
or unrelated directories. An explicit path or root that does not contain the
requested file is a stop, not permission to search elsewhere.

## Generated Task Work

Generated local artifacts that should survive beyond one temporary process but
must not be committed belong under a task and run namespace:

```text
<local-work-root>/
  TASK-XXXX/
    primary/
    replay-<agent-id>/
```

Resolve or create a run directory with:

```bash
python3 scripts/apl_local_artifacts.py workdir \
  --task TASK-1091 \
  --run primary \
  --create
```

Use `primary` for the task's main execution and a distinct stable run id for an
independent replay. Disposable files that do not need to survive a process may
still use `tempfile`; canonical evidence and approved small artifacts still go
to their repository-defined destinations.

## Committed Versus Local Artifacts

`data/**/source_artifacts/` contains committed provenance packages and only
those source bytes whose redistribution route has been explicitly approved. It
is not the private source vault.

Committed manifests, reviews, results, and PR text may record:

- source id and upstream filename;
- source version, DOI, URL, or other stable locator;
- byte size and SHA-256 checksum;
- retrieval date and attribution;
- redistribution and derived-output posture.

They must not record a maintainer username, home directory, drive-specific
absolute path, local worktree path, or private-root listing. Machine paths may
appear in local console output only. Use stable artifact identity and checksum
in committed evidence.

## Rights And Safety

- Never commit private, licensed, key-gated, or redistribution-unclear source
  bytes merely because they are available locally.
- A checksum match proves byte identity, not permission to redistribute,
  publish a dataset, mint a DOI, or apply a repository license.
- Derived local files inherit the source's most restrictive rights posture
  until a separate rights review approves a narrower public artifact.
- Keep credentials in the separate `APL_LOCAL_SECRETS_FILE` flow documented in
  [Local Source Secrets](local-source-secrets.md). Do not put credentials in
  source or work roots.
- Stop on a missing file, checksum mismatch, path traversal, or source identity
  conflict. Do not substitute a similarly named archive or newer release.
- Do not copy absolute local paths from helper output into tasks, manifests,
  reviews, results, issues, or PR bodies.

## Relationship To Other Protocols

- [Source Acquisition Lane](source-acquisition-lane.md) controls who may fetch
  or accept a source and what acquisition evidence is required.
- [Published-Source and Reusable-Dataset Standard](published-source-dataset-standard.md)
  controls admissibility, rights, and external publication.
- [Fresh-Data Intake Protocol](fresh-data-intake-protocol.md) controls the
  source-to-row lifecycle.
- [Local Source Secrets](local-source-secrets.md) controls credentials, not
  artifact placement.
- Campaign-specific `data/**/source_artifacts/` packages remain committed
  provenance surfaces and may add stricter requirements.
