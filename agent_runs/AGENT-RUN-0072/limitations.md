# AGENT-RUN-0072 Limitations

- The dataset contains computed DFT values, not experimental measurements.
- The accepted slice has 362 materials and does not represent all ternary oxides.
- Exact cation-pair means are descriptive train-only baselines, not physical laws.
- Unseen cation pairs use the global train mean fallback.
- The cation-family leave-one-group-out diagnostic is undefined because all rows
  collapse to one available family label under the current coarse element map.
- Formation energy is scored separately; no band-gap conclusion is drawn.
- No material recommendation, synthesis claim, or universal materials relation
  is supported.
