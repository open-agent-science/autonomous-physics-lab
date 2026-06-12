# DEBCat Blocker Notes

## Current Blocker

DEBCat is the selected first source path for Stellar M-L independent dynamical
masses, but this package remains `METADATA_ONLY_BLOCKER` because the raw
ASCII table is value-bearing and no explicit redistribution license was found
on the consulted catalogue page. `TASK-0707` accepted Route 2, so the raw table
remains uncommitted but a later row-curation task may commit normalized
component rows with a reviewed extraction ledger.

## What Is Unblocked

- Stable source locator.
- Machine-readable artifact locator.
- Retrieval date.
- HTTP Last-Modified and ETag.
- SHA-256 checksum for the retrieved `debs.dat` artifact.
- Source version note from the catalogue update log.
- Citation posture.
- Storage route: Route 2, metadata-only checksum with extraction ledger and no
  raw `debs.dat` commit.

## What Remains Blocked

- committing raw `debs.dat`;
- creating normalized Stellar M-L rows without a reviewed extraction ledger;
- deriving luminosities outside the `TASK-0688` tiered luminosity policy;
- fitting or auditing the textbook M-L exponent;
- result, prediction, claim, or knowledge promotion.

## Recommended Next Step

Execute a separate row-curation gate using Route 2: keep raw `debs.dat`
uncommitted, commit only normalized component rows, and include a reviewed
extraction ledger bound to the recorded checksum and luminosity/no-leakage
policies.
