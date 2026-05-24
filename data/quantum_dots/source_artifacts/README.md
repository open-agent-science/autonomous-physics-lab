# Quantum Dot Source Artifacts

This directory stores metadata-only or checksum-pinned source-artifact packages
for future Quantum Size Effects row curation.

Use one subdirectory per `source_id` from
`data/quantum_dots/source_manifest.yaml`:

```text
data/quantum_dots/source_artifacts/<source_id>/
```

Follow `docs/quantum-direct-source-artifact-intake.md` before adding a source
artifact. A package may record locators, checksums, extraction plans, and
non-copyrighted extraction logs. It must not contain measurement rows unless a
future row-curation task explicitly accepts and validates them in a `qd-*.yaml`
dataset file.

Default guardrails:

- do not commit publisher PDFs, figures, or tables unless redistribution is
  explicitly allowed by license and maintainer policy;
- do not estimate graph coordinates by eye;
- do not treat calibration-polynomial outputs as direct measurements;
- do not run the quantum baseline benchmark from a source-artifact package
  alone;
- do not promote scientific, device, synthesis, or biomedical claims from this
  directory.
