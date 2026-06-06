# DEBCat Raw And Derived Artifact Policy

## Raw Artifact

`debs.dat` is a value-bearing source table. It may not be committed from this
package because TASK-0628 did not find an explicit redistribution license on
the consulted catalogue page.

The checksum and HTTP metadata are sufficient to identify the source version
used for future review:

```text
sha256: 326902535b4da2fd94f227806ff339247d6df224ef8faea8857703e553b464da
last_modified: Sat, 16 May 2026 11:14:34 GMT
etag: "17441-651ed6f2a15a0"
```

## Derived Artifacts

No derived extraction products are authorized by this task. A later task must
define:

- row schema;
- source-value extraction method;
- uncertainty semantics;
- binary-system holdout/no-leakage policy;
- luminosity provenance policy;
- license and storage decision.

## Forbidden In This Package

- table transcription;
- row normalization;
- luminosity computation;
- exponent fitting;
- residual or benchmark metrics;
- claim, prediction, result, or knowledge promotion.
