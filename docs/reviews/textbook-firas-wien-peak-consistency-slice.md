# Textbook FIRAS Wien-Peak Consistency Slice

Task: `TASK-0802` · Campaign: `textbook-formula-audit`

Verdict: `CONSISTENT_IN_SCOPE`

This note records the one bounded, deterministic spectral-domain consistency
metric authorized by `TASK-0793` and pre-contracted by `TASK-0815`. It compares
the wavelength-domain peak of the pinned COBE/FIRAS absolute monopole spectrum
against the frozen textbook Wien-displacement reference `lambda_peak = b / T` at
the separately pinned reference temperature. It is a FIRAS spectral-domain
consistency audit only. It is **not** a universal validation or falsification of
Wien displacement, blackbody physics, CMB physics, or textbook-formula truth.

No blackbody spectrum was fit, no source was re-pinned or re-fetched, no
temperature was chosen after seeing output, and no fitted free parameter was
introduced. No `RESULT-*`, `PRED-*`, `CLAIM-*`, or `KNOW-*` artifact is created.

## Pinned inputs (consumed read-only)

- FIRAS monopole rows:
  `data/textbook_formula_audit/wien_firas/firas_monopole_rows.yaml`
  (43 absolute monopole rows; the source `.txt` carries
  sha256 `df793c3dca09ebfa7dbc5aa0ec1951daa8884431bc30eff28a710d7516cf50fa`).
- Frozen Wien wavelength-domain exact-reference fixture:
  `data/textbook_formula_audit/fixtures/wien_displacement_exact_reference.yaml`.
- Reference temperature and domain/control contract:
  [Textbook Wien/FIRAS Temperature And Domain Contract](textbook-wien-firas-temperature-domain-contract.md)
  (`TASK-0815`), built on
  [the FIRAS source-artifact route note](textbook-wien-firas-source-artifact.md)
  (`TASK-0793`).

## Reference

- Reference temperature `T_ref = 2.72548 K` (`sigma = 0.00057 K`),
  citation Fixsen 2009, ApJ 707, 916 — separately pinned provenance, not a
  fitted parameter chosen from the FIRAS rows.
- Wien constant `b = 2.897771955e-3 m K` (CODATA 2022 / NIST).
- Textbook wavelength-domain peak `lambda_peak = b / T_ref = 1.0632 mm`
  (= `9.405 cm^-1`).

## Domain-conversion handling (reported separately from the metric)

FIRAS is tabulated on a native wavenumber/frequency axis (`B_nu` vs `cm^-1`), so
the wavelength-domain peak requires the explicit Jacobian before peak location:

```text
k[m^-1] = k[cm^-1] * 100
nu      = c * k[m^-1]
lambda  = 1 / k[m^-1]
B_lambda = B_nu * nu^2 / c    (proportional; arbitrary units, scale cancels under argmax)
```

The frequency-domain and wavelength-domain peaks are genuinely different (Wien
non-invariance):

| domain | peak location |
| --- | --- |
| frequency-domain (native `B_nu` argmax) | `5.45 cm^-1` (`163.4 GHz`) |
| wavelength-domain (after Jacobian, raw bin) | `9.53 cm^-1` (`1.0493 mm`) |
| wavelength-domain (fixed parabolic refinement) | `1.0642 mm` |

## Primary metric

| quantity | value | tolerance |
| --- | --- | --- |
| reference `b / T_ref` | `1.0632 mm` | — |
| raw-bin relative difference | `0.0131` | `0.02` |
| interpolated relative difference | `0.00092` | `0.005` |

The raw-bin peak is limited by the uniform `~0.45 cm^-1` FIRAS bin spacing; the
fixed parabolic-vertex refinement (a deterministic sampling-resolution
diagnostic, not a model fit) lands within `0.092 %` of the textbook reference.
Both gates pass, so the scoped verdict is `CONSISTENT_IN_SCOPE`.

## Controls (all predeclared, all passed)

| control | outcome |
| --- | --- |
| `absolute_product_gate` (fail if residual-only/model-normalized) | pass |
| `no_jacobian_relabel_rejected` (relabel `B_nu` argmax as wavelength → `1.835 mm`, `72.6 %` off) | pass |
| `frequency_domain_peak_distinct` (`5.45` vs `9.53 cm^-1`, > one bin apart) | pass |
| `wrong_temperature_rejected` (`+10 %` offset `T` → `8.6 %` miss) | pass |

## Circularity caveat (mandatory framing)

The Fixsen 2009 reference temperature is itself obtained by fitting a Planck
spectrum to FIRAS, so this comparison is a blackbody **self-consistency** check
in scope, not independent empirical validation of Wien displacement. The
FIRAS-recalibrated value (`2.7260 +/- 0.0013 K`) is reserved for a sensitivity
appendix only and was not substituted as the primary reference.

## Reproduce

```text
python3 scripts/run_textbook_wien_firas_peak_consistency.py --out-dir agent_runs/AGENT-RUN-0079
```

Deterministic: engine `physics_lab/engines/textbook_wien_firas_peak.py`
(version `0.1.0`), input sha256 hashes and git commit recorded in
`agent_runs/AGENT-RUN-0079/metrics.json`. No stochastic step.

## Output routing

- Canonical destination: sandbox agent-run package
  `agent_runs/AGENT-RUN-0079/` plus this `docs/reviews/` consistency note.
- Review tier: none (sandbox-by-default).
- Gate A: not attempted. The metric passes cleanly and would support a future
  Gate A result-packaging task, but per `TASK-0802` the default destination is
  sandbox-only; no `RESULT-*` is forced here.
- Gate B: not attempted.
- Claim impact: none. Knowledge impact: none.
- Promotion blocker: a separate maintainer-reviewed Gate A result-packaging
  task (with a populated `agent_proposal_evaluation` block) would be required
  before any `RESULT-*`, and a different agent would run Gate B replay.

## Limitations

- Single pinned COBE/FIRAS absolute monopole product (43 rows, one spectral
  axis); one separately pinned reference temperature.
- The reference temperature is FIRAS-derived (self-consistency, not independent
  validation).
- Raw-bin peak precision is limited by FIRAS bin spacing; the interpolation is a
  fixed diagnostic, not a fit.
- Sandbox evidence only; not a blackbody-universality, textbook-falsification,
  proof, or discovery statement.
