# AGENT-RUN-0081 Limitations

- Computed-DFT Materials Project formation energies only (CC BY 4.0); no
  experimental measurements. Residuals are computed-DFT benchmark diagnostics,
  not measurement errors, and inherit any DFT systematic offset.
- Bounded model-vs-model generalization benchmark on one frozen, checksum-pinned
  362-row MD-0002 stable ternary-oxide slice. It is not a materials-discovery,
  material-design-law, property-prediction, synthesis, device, or biomedical
  claim.
- Exactly one disjoint A-site cation-family split is evaluated
  (alkali-transition vs alkaline-earth-transition). This is a single
  chemistry-defined family axis, not a broad transfer study across many splits.
- By construction the two A-site families share no unordered cation pair, so the
  frozen exact-cation-pair model has no learned pair for any held-out row and
  falls back to the global train mean on 100% of the held-out family. The test
  measures whether that fallback still beats the controls; it does not.
- Formation energy is evaluated alone; band gap is neither scored nor pooled, per
  the MD-0002 holdout manifest.
- The frozen RESULT-0021 model and descriptor were fixed before any transfer
  error was read. The negative outcome is recorded as-is; no refit, feature
  addition, hyperparameter change, or split change was made to rescue it.
