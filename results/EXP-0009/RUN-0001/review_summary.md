# Review Summary

- Result: `RESULT-0011`
- Claim target: `CLAIM-0007`
- Knowledge target: `KNOW-0006`
- Suggested claim status if accepted: `DRAFT`

## Why This Artifact Changed

Nuclear shell correction experiment: best formula 'multi_gauss_NZ_shared_sigma' achieves 28.8% test-set RMS improvement (BW baseline: 8.978 MeV → 6.393 MeV). Threshold was 20%. Verdict: VALID.

## Highlights

- BW RMS baseline: 8.978 MeV (test set, 19 nuclides).
- Best correction: `multi_gauss_NZ_shared_sigma` → RMS 6.393 MeV (28.8% improvement).
- Simple distance models (Gaussian/Lorentzian in d_N, d_Z) give <1% improvement.
- Per-magic-number amplitude models (multi_gauss_N, multi_gauss_NZ) give 26-29% improvement.
- Different magic numbers require different correction amplitudes and signs — no universal shell correction shape.

## Limitations To Preserve

- Curated ~97-nuclide AME2020 subset; not full ~3500-nuclide table.
- Standard BW liquid-drop coefficients used (not jointly refit with shell correction).
- Heavier nuclides (A > 140) have approximate B_exp values (~0.5 MeV uncertainty in dataset).
- Several multi-magic amplitudes hit fitting bounds (±20 MeV); light-nuclei (A < 10) corrections may absorb A-dependent BW errors.
- Gaussian width σ shared across all magic numbers; per-closure widths untested.
- Only stable AME2020 nuclides included; no radioactive isotopes.
- Simple distance-based models (d_N or d_Z only) provide <1% improvement; improvement requires per-magic-number amplitudes.

## Required Maintainer Action

Review the patch artifacts before editing any canonical claim or knowledge file. Do not copy these suggestions blindly into public scientific memory.
