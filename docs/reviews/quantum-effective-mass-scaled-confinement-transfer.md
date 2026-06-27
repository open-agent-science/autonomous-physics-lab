# Quantum effective-mass-scaled confinement transfer

Task: `TASK-0850`  
Sandbox run: `AGENT-RUN-0085`  
Verdict: `MATERIAL_SPECIFIC_AFTER_EFFECTIVE_MASS_SCALING`

## Question

Does the borderline TASK-0842 InP-ZnSe confinement transfer become robust when
the power-law prefactor is scaled by a literature electron-hole reduced mass,
without fitting any parameter on either held-out material?

## Pre-registered physics input

The frozen rule is

`mu = (1/me + 1/mh)^-1`

and

`C_target = C_source * mu_source / mu_target`.

The source-material power-law coefficient and exponent are calibrated exactly as
in TASK-0842. Only the coefficient receives the fixed literature-mass scaling.
No mass, coefficient, exponent, threshold, or scaling factor is fit on a
holdout.

| Material | me/m0 | mh/m0 | reduced mass mu/m0 | source |
| --- | ---: | ---: | ---: | --- |
| InP | 0.08 | 0.64 | 0.071111 | Wu et al., Chemical Science 2020, DOI `10.1039/D0SC01039A` |
| ZnSe | 0.16 | 0.75 | 0.131868 | Jang et al., Research Square 2022, DOI `10.21203/rs.3.rs-1183117/v1` |

The InP paper explicitly states both masses and cites the earlier InP carrier
dynamics source (Wu et al., J. Phys. Chem. A 2013, DOI `10.1021/jp402425w`).
The ZnSe source explicitly lists the masses in its effective-mass approximation
section; it is a CC BY 4.0 preprint and this is retained as a limitation.

## Result

Primary framing uses the TASK-0842 equal-volume conversion from tetrahedral InP
edge length to equivalent spherical diameter. Only direct-size rows enter the
judge: six InP TEM rows and ten ZnSe SAXS rows.

| Direction | mass-scaled MAE (eV) | TASK-0842 MAE (eV) | improvement (eV) | best control MAE (eV) | margin (eV) | clears 0.05? |
| --- | ---: | ---: | ---: | ---: | ---: | :---: |
| InP -> ZnSe | 0.161570 | 0.099216 | -0.062354 | 0.145800 | -0.015770 | no |
| ZnSe -> InP | 0.991542 | 0.119375 | -0.872168 | 0.219500 | -0.772042 | no |

The fixed scaling factors are `0.539259` forward and `1.854396` reverse. The
effective-mass correction worsens the bulk-gap-only transfer in both directions
and fails the strongest control in both directions. The result therefore does
not support this simple reduced-mass prefactor as the missing cross-material
correction for these two datasets.

## Controls

Each held-out material is compared with:

- `calibration_mean_null`: calibration-material mean confinement, using no
  holdout labels;
- `per_material_mean`: held-out material mean, a size-independent upper-bound
  control;
- `shuffled_size`: the mass-scaled model on a deterministic size permutation,
  seed `850`.

The survival threshold remains the predeclared TASK-0842 value of `0.05 eV`.
It was not relaxed after reveal.

## Interpretation and limitations

This is an honest material-specificity negative for one simple bulk
effective-mass scaling across two materials. It does not show that effective
mass is physically irrelevant. Bulk scalar masses omit nanocrystal
nonparabolicity, anisotropy, dielectric confinement, Coulomb corrections, and
finite barriers. The samples are small and use one source and morphology per
material. No fitted rescue or material recommendation is permitted.

## Output routing

- Canonical destination: sandbox `agent_runs/AGENT-RUN-0085/` plus this review
  note.
- Gate A: not attempted; no canonical RESULT because this task has no protected
  HYP/EXP publication link and the bounded candidate fails controls.
- Gate B: replay metadata complete; independent replay requires a different
  agent.
- Claim files changed: no.
- Novelty Classification: `n/a`.
- Claim status impact: none.
- No PRED, CLAIM, or KNOW artifact created.
