# Raw And Derived Artifact Policy

## Raw Artifacts

Raw artifacts are source-provided files or responses, such as:

- PDF or supplementary information files;
- CSV, TSV, JSON, YAML, or FITS snapshots;
- API responses;
- figure images;
- repository release assets.

Raw artifacts may be committed only when the task explicitly allows it and the
license review permits repository storage. Otherwise, preserve metadata,
locator, checksum, and blocker notes without committing the file.

## Derived Artifacts

Derived artifacts are outputs created by APL contributors or agents, such as:

- table transcriptions;
- digitised figure points;
- normalized source manifests;
- extraction ledgers;
- row-curation drafts.

Derived artifacts may contain value-bearing data. They require task approval,
source references, extraction notes, reviewer notes, and validation commands.

## Not Data

The following are not data:

- LLM-recalled numbers;
- prose-only numerical summaries;
- screenshots without extraction records;
- unreviewed figure reads;
- values copied from memory or secondary prose.

Preserve these only as blocker notes.
