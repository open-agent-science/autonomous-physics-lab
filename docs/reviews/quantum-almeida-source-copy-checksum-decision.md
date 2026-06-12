# Quantum Almeida Source-Copy Checksum Decision

**Task:** `TASK-0711`
**Campaign:** Quantum Size Effects
**Source ID:** `almeida-2023-nano-letters-inp-optical`
**Mode:** source-artifact gate only (no digitization, no rows, no metrics)
**Decision:** `METADATA_ONLY_CHECKSUM_BLOCKED_NO_VALID_SOURCE_BYTES`

## Scope

This task selects the next Almeida article/SI source-copy route and records why
no file copy is committed or checksum-pinned yet. It does not digitize Figure 1b,
transcribe optical values, create `qd-*.yaml` rows, run quantum-size baselines,
or promote claims.

## Inputs Reviewed

| Input | Role |
| --- | --- |
| `docs/reviews/quantum-almeida-checksum-source-artifact-package.md` | Prior metadata-only package and locator set. |
| `docs/reviews/quantum-almeida-license-figure-surface-review.md` | License/figure-surface posture and CC-BY recheck requirement. |
| `docs/reviews/quantum-nonspherical-digitization-fixture-design.md` | Synthetic non-spherical fixture; no real Almeida points. |
| `data/quantum_dots/source_manifest.yaml` | Source registry entry and current excluded state. |

## Selected Copies

Exactly one article route and one SI route are selected for the next
maintainer/browser-assisted source-copy attempt:

| Role | Selected locator | Upstream filename | Outcome |
| --- | --- | --- | --- |
| Article copy | `https://dspace.library.uu.nl/bitstream/handle/1874/434964/almeida-et-al-2023-size-dependent-optical-properties-of-inp-colloidal-quantum-dots.pdf` | `almeida-et-al-2023-size-dependent-optical-properties-of-inp-colloidal-quantum-dots.pdf` | Selected institutional route, but not accepted as a source copy in this task because the downloaded body was an HTML shell, not a PDF. |
| SI copy | `https://pubs.acs.org/doi/suppl/10.1021/acs.nanolett.3c02630/suppl_file/nl3c02630_si_001.pdf` | `nl3c02630_si_001.pdf` | Selected canonical ACS SI route, but not accepted as a source copy in this task because access returned a JavaScript/Cloudflare challenge. |

The ChemRxiv SI locator from `TASK-0668` remains a fallback route:
`https://chemrxiv.org/engage/api-gateway/chemrxiv/assets/orp/resource/item/64b00532ae3d1a7b0d9cf337/original/si-size-dependent-optical-properties-of-in-p-colloidal-quantum-dots.pdf`.
It also returned a JavaScript/Cloudflare challenge in this run.

## Retrieval Attempts

Retrieval date: `2026-06-12`.

| Locator | Method | Observed body | Source checksum accepted? |
| --- | --- | --- | --- |
| Utrecht article PDF | `Invoke-WebRequest` GET with normal User-Agent; also tried `?sequence=1&isAllowed=y` | 751-byte HTML shell beginning `<!DOC`; SHA-256 of the failed response body was `4c3c53b8889706e55a82eb7c0cf452cc3aec4b0de0a27c07581963517e3d9d4f`, but this is **not** a PDF checksum. | No |
| TU Delft article PDF | HEAD/GET with normal User-Agent | JavaScript/Cloudflare challenge / forbidden response | No |
| ACS canonical SI PDF | GET with normal User-Agent | JavaScript/Cloudflare challenge | No |
| ChemRxiv SI PDF | HEAD/GET with normal User-Agent | JavaScript/Cloudflare challenge / forbidden response | No |
| ACS article page / PMC mirror | Browser/web probe | challenge-gated or inaccessible to this task environment | No |

Because no valid article or SI PDF bytes were obtained, this task records no
source-file byte size or accepted SHA-256 digest. The failed HTML body hash above
is retained only as an audit clue so a later agent does not mistake it for the
article.

## Reuse Decision

Prior committed reviews indicate that the Almeida article is promising and
public/open-access, with CC-BY 4.0 posture requiring recheck on exact file copies.
This task could not complete that exact-copy recheck because the selected source
bytes were not retrievable in a checksumable form. Therefore:

- do not commit article PDFs, SI PDFs, figure rasters, or extracted coordinates;
- keep the source manifest `inclusion_decision: excluded`;
- keep `checksum_policy` at metadata-only / source-copy-blocked posture;
- allow a later maintainer/browser-assisted task to retry the selected article
  and SI routes, then record true byte sizes and SHA-256 digests if valid source
  files are obtained.

## Next Source-Copy Handoff

The next attempt should use an interactive browser or maintainer-provided copy
that can pass the repository's source-artifact checks:

1. obtain the Utrecht institutional article PDF or another selected article copy;
2. obtain the ACS canonical SI PDF or ChemRxiv SI copy;
3. verify both bodies begin as PDF files and are not challenge HTML;
4. record upstream filename, retrieval date, byte size, SHA-256 checksum, and
   reuse terms for each accepted file;
5. only then decide whether the files themselves may be committed or whether
   locator/checksum-only metadata is the durable route.

Figure 1b coordinate extraction remains a separate digitization task after the
source-copy gate passes.

## Limitations

- The task environment could not bypass JavaScript/Cloudflare challenges.
- No valid source bytes were committed or checksum-pinned.
- No article, SI, figure, row, result, prediction, claim, or knowledge artifact
  was produced.

## Output Routing Summary

- **Task verdict:** `METADATA_ONLY_CHECKSUM_BLOCKED_NO_VALID_SOURCE_BYTES`.
- **Canonical destination:** this review note plus metadata-only source-artifact
  package under `data/quantum_dots/source_artifacts/almeida-2023-inp-optical/`.
- **Review tier:** none; no `RESULT-*` / `PRED-*` artifact.
- **Gate A status:** not applicable because no rows or metrics were produced.
- **Gate B status:** not applicable.
- **Claim impact:** none.
- **Knowledge impact:** none.
- **Dataset impact:** no `qd-*.yaml` row created; Almeida remains excluded from
  usable rows.
- **Publication blocker:** valid article/SI source bytes, exact-copy reuse
  recheck, accepted SHA-256 digests, real Figure 1b digitization export, and
  row-readiness review remain missing.
