# Particle AHS Common-Scheme Source-Row Pin

**Task:** `TASK-0926`

**Verdict:** `SOURCE_ROWS_PINNED_NO_METRIC`

**Review date:** 2026-07-04

## Scope

This task pins one common-scheme source surface for a later fixed-target
sensitivity test. It transcribes exactly the six 2024-PDG Standard Model quark
Yukawa couplings from Equation (2.4) of Antusch, Hinze, and Saad. It does not
convert Yukawas to masses, run a Koide metric, overwrite existing particle
rows, or change any `RESULT-*` or `CLAIM-*` artifact.

## Source Identity

- Stefan Antusch, Kevin Hinze, and Shaikh Saad, "Updated running quark and
  lepton parameters at various scales," *Physical Review D* **113**, 095011
  (2026), DOI [10.1103/fdcc-ycph](https://doi.org/10.1103/fdcc-ycph).
- accepted-manuscript audit surface:
  [arXiv:2510.01312v2](https://arxiv.org/abs/2510.01312v2), revised
  2026-03-23;
- exact extraction surface: Equation (2.4), PDF page 4 (printed page 3),
  2024-PDG input, Standard Model, `MS-bar`, `M_Z`;
- accepted-manuscript PDF SHA-256:
  `64e1d141cdfb2bcd3f45efe0b16e3ebdfa6130fd27f361d14353ecbb96d2aabd`.

The version of record is open access under CC BY 4.0. The primary source calls
the six selected quantities dimensionless running Yukawa couplings. Calling
them quark masses would change their semantics and is not allowed by this pin.

## Pinned Rows

| Parameter | Source notation | Stored central value | Stored uncertainty |
| --- | --- | ---: | ---: |
| `y_u` | `(7.04 +/- 0.15) x 10^-6` | `7.04e-6` | `1.5e-7` |
| `y_d` | `(1.54 +/- 0.02) x 10^-5` | `1.54e-5` | `2.0e-7` |
| `y_s` | `(3.06 +/- 0.04) x 10^-4` | `3.06e-4` | `4.0e-6` |
| `y_c` | `(3.56 +/- 0.06) x 10^-3` | `3.56e-3` | `6.0e-5` |
| `y_b` | `(1.630 +/- 0.009) x 10^-2` | `1.630e-2` | `9.0e-5` |
| `y_t` | `0.967 +/- 0.004` | `0.967` | `0.004` |

All uncertainties are source-reported symmetric one-sigma HPD marginals. The
source does not provide a recoverable six-output covariance matrix. Shared PDG
inputs and matching/running assumptions therefore prevent treating these rows
as statistically independent.

## Rights Determination

| Question | Decision |
| --- | --- |
| May APL analyze the source locally? | Yes. |
| May APL redistribute source bytes? | CC BY 4.0 permits it with attribution, but no source bytes are committed because they are unnecessary. |
| May APL publish the derived/source rows? | Yes. This is a limited factual extract with attribution under CC BY 4.0. |

The declaration is recorded in `data/DATA_LICENSES.yaml`. The committed row
artifact contains no manuscript prose, PDF, figure, or table image.

## Integrity And Boundaries

- row artifact:
  `data/particle_masses/source_artifacts/antusch-hinze-saad-2026/equation-2.4-2024-pdg-mz-yukawas.yaml`;
- row artifact SHA-256:
  `b96709627e13542c6c047ca565713028321bba98fcb070d1a016ab774e29b480`;
- source provenance:
  `data/particle_masses/source_artifacts/antusch-hinze-saad-2026/provenance.yaml`;
- parity test: `tests/test_particle_common_scheme_source.py`.

The top row is derived from the source pipeline beginning with a top pole-mass
input; it is not a direct top-mass measurement. Missing covariance blocks any
full covariance-aware interpretation. Existing particle datasets remain
unchanged.

## Output Routing

- Task verdict: `SOURCE_ROWS_PINNED_NO_METRIC`.
- Canonical destination: the checksummed Equation (2.4) source-row artifact and
  its provenance package.
- Review tier: `none`; this is a source dataset, not a `RESULT-*`.
- Gate A: not attempted; no metric or result was produced.
- Gate B: not applicable.
- Claim impact: none; `CLAIM-0006` and `CLAIM-0007` remain `DRAFT` and
  unchanged.
- Knowledge impact: none.
- Limitation: source marginals share upstream inputs and do not supply a full
  covariance model.
