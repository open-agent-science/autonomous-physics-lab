# Canonical Duflo-Zuker Parity Reference Scout

Task: `TASK-0853`
Domain: Nuclear physics
Mode: optional source-reference scout
Verdict: `PARITY_REFERENCE_AVAILABLE`
Scout date: `2026-06-28`

## Scope And Non-Goals

This task scouts for an admissible canonical Duflo-Zuker parity reference: the
archival AMDC DZ10/DZ28 code and/or a published per-nuclide numeric fixture. It
is explicitly a source-readiness note. It does not rerun the TASK-0823 benchmark,
modify the DZ10 published-variant result, create a RESULT, promote a claim, or
reopen TASK-0823.

TASK-0823 remains complete under scope A': a cited DZ10 published-equation
variant stronger baseline. Canonical AMDC parity is a separate future task.

Inputs reviewed:

- [../../tasks/TASK-0823-implement-duflo-zuker-stronger-nuclear-baseline.yaml](../../tasks/TASK-0823-implement-duflo-zuker-stronger-nuclear-baseline.yaml)
- [../../physics_lab/engines/nmd0003_duflo_zuker_baseline.py](../../physics_lab/engines/nmd0003_duflo_zuker_baseline.py)
- [nmd0003-duflo-zuker-structured-baseline.md](nmd0003-duflo-zuker-structured-baseline.md)
- [../../tasks/TASK-0853-canonical-dz-parity-reference-code-scout.yaml](../../tasks/TASK-0853-canonical-dz-parity-reference-code-scout.yaml)

## 1. Accessibility Findings

The original AMDC endpoint cited by earlier work remains unavailable from this
environment:

| Probe | Result on 2026-06-28 |
| --- | --- |
| `http://amdc.in2p3.fr/web/dz.html` | connection failed |
| `https://amdc.in2p3.fr/web/dz.html` | connection failed |
| `http://amdc.impcas.ac.cn/web/dz.html` | connection failed |
| `https://amdc.impcas.ac.cn/web/dz.html` | 404 |

A live IAEA/NDS mirror is available:

```text
https://www-nds.iaea.org/amdc/web/dz.html
```

The page title is `Duflo-Zuker`, last updated `2 May 2005`, and it links the
canonical DZ10 and DZ28 artifacts under `https://www-nds.iaea.org/amdc/theory/`.
The AMDC index at `https://www-nds.iaea.org/amdc/` says the page contains data
provided by the Atomic Mass Data collaboration.

## 2. Reference Artifacts

The following small public files were downloaded to `C:/tmp` only, checksumed,
and not committed to the repository.

| Artifact | URL | Bytes | SHA-256 | Reading |
| --- | --- | ---: | --- | --- |
| DZ10 Fortran | `https://www-nds.iaea.org/amdc/theory/du_zu_10.feb96fort` | 12231 | `cccc8406cfdd0fb79c11ace0dcae2b06df443fa4c4fc852f3114b657a125a25a` | Canonical 10-parameter Fortran program; machine-readable source code. |
| DZ10 table | `https://www-nds.iaea.org/amdc/theory/du_zu_10.feb96` | 196049 | `b80d64caf878ed837b5544d22920e4499d4869053d934d0068c5aab0bcc7ea7b` | Per-nuclide mass-excess fixture, format `i5, i5, f10.3`; 9311 unique `(Z, A)` rows. |
| DZ28 table | `https://www-nds.iaea.org/amdc/theory/du_zu_28.feb95` | 193853 | `7c44af03b08a3c4e4629e3e50612d8daa687cda9081045d5ad2e61fb0b8697b1` | Optional 28-parameter table fixture; 9210 unique `(Z, A)` rows. |

The DZ10 Fortran header identifies:

- `J. Duflo and A.P. Zuker Feb 23, 1996 10 parameters formula`;
- `Phys. Rev. C52, 1995 (for the 28 param. formula)`;
- `Private Communication to AMDC, February 1996`;
- fit to 1810 measured masses from helium-4 and up with RMS 506 keV.

The DZ10 table header records the same references and states:

```text
Format: i5, i5, f10.3
Z A Mass-Excess (MeV)
```

Smoke parsed DZ10 table values:

| Z | A | Mass excess (MeV) |
| ---: | ---: | ---: |
| 8 | 16 | -5.150 |
| 37 | 90 | -78.959 |
| 50 | 132 | -76.052 |
| 82 | 208 | -22.621 |
| 92 | 238 | 47.483 |
| 122 | 297 | 223.211 |

Machine-readability verdict: sufficient for a future parity task. The Fortran
program is small fixed-format source, and the DZ10 table is a direct numeric
fixture with one `(Z, A, mass_excess_mev)` row per entry.

## 3. Rights And Reuse Posture

Using the APL three-question source-rights framework:

| Question | Determination |
| --- | --- |
| Local analysis allowed? | `yes_with_citation`: the files are public on the IAEA/NDS AMDC mirror and are directly downloadable. |
| Source-bytes redistribution allowed? | `not_cleared`: the DZ page itself does not state an open license or redistribution grant. |
| Derived-row publication allowed? | `needs_maintainer_decision`: numeric values are factual fixtures, but bulk vendoring or normalized redistribution should wait for a maintainer-recorded rights decision. |

The IAEA main terms-of-use and copyright pages returned `403` from this
environment, and no explicit license text was present on the AMDC DZ page. A
future parity task should therefore default to metadata-only locators and
checksums, or obtain maintainer approval before committing AMDC source bytes or a
normalized DZ fixture.

## 4. Future Parity-Implementation Task Shape

A bounded future task can now be proposed or assigned without reopening
TASK-0823:

1. Add a metadata-only DZ reference manifest with the URLs, bytes, SHA-256
   checksums, citation, and rights caveat above.
2. Fetch the DZ10 Fortran and DZ10 table into a local/generated cache during
   validation, or use a maintainer-approved vendored copy only after a rights
   decision.
3. Compile/run `du_zu_10.feb96fort` if a Fortran compiler is available, or make
   a line-by-line transliteration that is parity-tested against the AMDC table.
4. Parse the 9311-row DZ10 fixture and require generated mass excess values to
   match the table to the published `0.001 MeV` precision for the supported
   domain.
5. Compare that parity implementation against the existing
   `nmd0003_dz10_published_equation_variant_v2` only as a diagnostic; do not
   mutate TASK-0823 artifacts in the same task.
6. If parity succeeds, run the normal NMD-0003/post-AME2020 benchmark as a new
   canonical task with Gate A/Gate B routing decided at that time.

## Verdict

`PARITY_REFERENCE_AVAILABLE`.

A canonical AMDC mirror provides both the DZ10 Fortran source and a DZ10
per-nuclide mass-excess fixture sufficient for parity testing. The source is
not license-cleared for repository vendoring, so the admissible current route is
metadata-only locators plus checksums, with source bytes fetched during a future
parity task or committed only after maintainer rights approval.

## Output-Routing Summary

- Task verdict: `PARITY_REFERENCE_AVAILABLE`.
- Canonical destination: this review note under `docs/reviews/`.
- Review tier: `none`. Gate A: not applicable. Gate B: not applicable.
- Claim impact: no claim change.
- Knowledge impact: no knowledge change.
- Result/PRED impact: no result, prediction, benchmark rerun, or claim output.
- TASK-0823 impact: not reopened; the A' DZ10 published-variant baseline stands.
- Publication blocker: source-bytes redistribution is not explicitly licensed;
  future work should use metadata-only fetch/checksum unless maintainer approves
  vendoring.

## Sources

- AMDC DZ page: `https://www-nds.iaea.org/amdc/web/dz.html`
- DZ10 Fortran: `https://www-nds.iaea.org/amdc/theory/du_zu_10.feb96fort`
- DZ10 numeric table: `https://www-nds.iaea.org/amdc/theory/du_zu_10.feb96`
- DZ28 numeric table: `https://www-nds.iaea.org/amdc/theory/du_zu_28.feb95`
- AMDC index: `https://www-nds.iaea.org/amdc/`