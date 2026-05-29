# AGENT-RUN-0044 Limitations

- NMD-0002 has 11 training rows; the neutron-rich subset is sparse.
- Frozen baseline residuals are retrospective; this is not a blind prediction.
- The boundary threshold (0.18) is declared before the run and not retuned.
- Chain-transfer metric is computed only on chains with >=2 rows on full_known.
- Matched-high-error control depends on baseline residual rank from the same frozen baseline; control is a non-neutron-rich proxy, not a fully orthogonal regressor.
- Verdict: `NEGATIVE_RESULT`. See `report.md` rationale.
