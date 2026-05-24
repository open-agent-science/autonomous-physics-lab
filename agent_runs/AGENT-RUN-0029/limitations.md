# Limitations

- Uncertainty fields are review-only for this lane because baseline model uncertainty is not represented.
- The NMD-0002 training slice uses a coarse curated uncertainty floor and must not be treated as a fit-grade likelihood surface.
- Inverse-variance weighting can concentrate effective weight on small-uncertainty rows even with a median-sigma floor.
- The lane audits baseline residual stability only; it does not re-score or promote prior candidate lanes.
- No source fetch, canonical result rewrite, PRED entry, claim update, or public-facing physics claim is authorized.
