# Literature-effective-mass InP-ZnSe confinement transfer

**Task:** `TASK-0850`  **Run:** `AGENT-RUN-0085`
**Verdict:** `MATERIAL_SPECIFIC_AFTER_EFFECTIVE_MASS_SCALING`

## Frozen model

The TASK-0842 confinement curve is calibrated on one material only. Its coefficient is transferred as `C_target=C_source*(mu_source/mu_target)`, where `mu=(1/me+1/mh)^-1` and all masses come from the pre-registered literature input file. No mass, exponent, coefficient, or scaling factor is fit on a holdout.

- InP: `me=0.08 m0`, `mh=0.64 m0`, `mu=0.071111 m0`; Wu et al., Chemical Science 2020, DOI `10.1039/D0SC01039A`.
- ZnSe: `me=0.16 m0`, `mh=0.75 m0`, `mu=0.131868 m0`; Jang et al., Research Square 2022, DOI `10.21203/rs.3.rs-1183117/v1` (CC BY 4.0 preprint).

## Primary equivalent-diameter results

### InP -> ZnSe

- Literature-mass MAE: `0.161570 eV`.
- TASK-0842 bulk-gap-only MAE: `0.099216 eV`.
- Improvement versus bulk-gap-only: `-0.062354 eV`.
- Best control: `per_material_mean` at `0.145800 eV`.
- Margin versus best control: `-0.015770 eV` (required `0.05 eV`; clears: `False`).
- Reduced-mass scaling factor: `0.539259`; holdout fit: `none`.

### ZnSe -> InP

- Literature-mass MAE: `0.991542 eV`.
- TASK-0842 bulk-gap-only MAE: `0.119375 eV`.
- Improvement versus bulk-gap-only: `-0.872168 eV`.
- Best control: `per_material_mean` at `0.219500 eV`.
- Margin versus best control: `-0.772042 eV` (required `0.05 eV`; clears: `False`).
- Reduced-mass scaling factor: `1.854396`; holdout fit: `none`.

The literature-mass prefactor worsens transfer in both directions relative to the TASK-0842 bulk-gap-only model and fails even the strongest control in both directions. The honest bounded result is material-specificity after this particular bulk effective-mass correction; no parameter is refit to rescue it.

## Controls

Each direction includes a calibration-material mean null, a held-out per-material mean upper-bound control, and a deterministic shuffled-size control. The predeclared survival threshold remains `0.05 eV`.

## Scope and routing

- Direct-size rows only: six InP TEM rows and ten ZnSe SAXS rows.
- Two materials and bulk scalar effective masses only; nonparabolicity, anisotropy, dielectric confinement, and finite barriers are outside scope.
- Gate A: not attempted; output remains sandbox because the bounded model fails controls and this task does not create protected HYP/EXP links.
- Gate B: replay metadata complete; independent replay must use a different agent.
- Claim status impact: none. No RESULT/PRED/CLAIM/KNOW is created.
