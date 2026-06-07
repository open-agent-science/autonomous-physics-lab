# DEBCat Blocker Notes

## Current Blocker

DEBCat is the selected first source path for Stellar M-L independent dynamical
masses, but this package remains `METADATA_ONLY_BLOCKER` because the raw
ASCII table is value-bearing and no explicit redistribution license was found
on the consulted catalogue page.

## What Is Unblocked

- Stable source locator.
- Machine-readable artifact locator.
- Retrieval date.
- HTTP Last-Modified and ETag.
- SHA-256 checksum for the retrieved `debs.dat` artifact.
- Source version note from the catalogue update log.
- Citation posture.

## What Remains Blocked

- committing raw `debs.dat`;
- copying value-bearing rows into APL;
- creating normalized Stellar M-L rows;
- deriving luminosities;
- fitting or auditing the textbook M-L exponent;
- result, prediction, claim, or knowledge promotion.

## Recommended Next Step

Create a separate row-curation gate only after maintainers choose one of these
routes:

1. explicit permission or license basis for committing DEBCat-derived
   value-bearing rows;
2. metadata-only checksum route with no raw table committed and a reviewed
   extraction ledger;
3. a replacement source with clearer redistribution terms.
