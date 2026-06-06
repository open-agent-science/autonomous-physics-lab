# DEBCat License And Reuse Review

Task: `TASK-0628`
Source ID: `debcat-detached-eclipsing-binaries`
Review date: 2026-06-06

## Consulted Source Surface

- Catalogue page: `https://astro.keele.ac.uk/jkt/debcat/`
- Machine-readable ASCII table: `https://astro.keele.ac.uk/jkt/debcat/debs.dat`
- Citation/preprint: `https://arxiv.org/abs/1411.1219`

## Observed Reuse Posture

The DEBCat catalogue page is public and states that the DEBCat paper should be
cited if the catalogue is used. The same page links to a machine-readable ASCII
table and describes the catalogue scope and update log.

No explicit license text was found on the consulted DEBCat page that would
authorize committing the value-bearing ASCII table into this repository. The
safe repository posture is therefore metadata-only checksum pinning until a
maintainer confirms redistribution permission or chooses a no-raw-artifact row
curation route.

## Storage Decision

- Raw `debs.dat` committed: no.
- Derived/transcribed rows committed: no.
- Checksum and HTTP metadata committed: yes.
- Citation metadata committed: yes.
- Row curation authorized by this package: no.

## Required Before Any Value-Bearing Commit

1. Record explicit redistribution permission or maintainer-approved
   metadata-only source-use policy.
2. Preserve the exact source checksum used for extraction.
3. Record extraction notes, row schema, and no-leakage holdout policy.
4. Keep component-level mass uncertainties and system identifiers intact.
