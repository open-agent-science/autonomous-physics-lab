
# AGENT-RUN-0070 Limitations

- Verdict `SANDBOX_PASS` is sandbox-only and does not validate or falsify
  the stellar mass-luminosity relation in universal terms.
- Full DEBCat rows and the raw `debs.dat` table are not committed because DEBCat
  has no explicit open-redistribution licence recorded in the repository.
- The primary benchmark uses the predeclared single-alpha route from
  `TASK-0740`; piecewise textbook-bin scoring remains a later extension.
- DEBCat machine-readable rows provide catalogue-level luminosity provenance,
  not per-row primary-literature luminosity pointers.
- Spectral-stage flags are best-effort metadata; unknown/evolved subsets are
  reported separately and require domain review before interpretation.
