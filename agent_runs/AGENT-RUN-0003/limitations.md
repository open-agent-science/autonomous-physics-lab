# Limitations - AGENT-RUN-0003

- This is sandbox-only evidence and does not update `RESULT-0007`.
- The five executed classifications are pilot examples, not benchmark metrics.
- The live challenge set and frozen MVP replay inputs are unchanged.
- `KNOWN_LIMIT_FAIL` behavior depends on human-curated semantic context; the
  dimension-only validator is expected to compute `VALID` for dimensionally
  balanced known-limit examples.
- The SUSPICIOUS result for dimensionless-only formulas depends on the current
  MVP heuristic and should not be treated as final validator semantics.
- Rejected proposals were triaged by scope and novelty checks, not by numerical
  execution.
