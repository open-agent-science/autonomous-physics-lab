# APL Software Release v0.2 — Maintainer Pack (TASK-0954)

- Purpose: mint the first **software** DOI for the APL workflow (Decision
  Day #2 D2-8), completing the publication roadmap's short-term release
  layer. `CITATION.cff` and `.zenodo.json` are bumped to `0.2.0` in this PR.
- Non-claims: a software release cites the workflow/codebase, not any
  physics result; no result, claim, or prediction changes tier by this
  release.

## Maintainer steps

1. **Enable the GitHub–Zenodo integration** for this repository (Zenodo ->
   GitHub -> flip the repo toggle) if not already on. With the integration
   on, `.zenodo.json` supplies the deposit metadata automatically.
2. **Verify the version is consistent everywhere** (this PR bumps all
   four surfaces to `0.2.0`: `CITATION.cff`, `.zenodo.json`,
   `pyproject.toml`, `physics_lab/__init__.py`) and tag **on the same day**
   as `CITATION.cff` `date-released` (2026-07-07) — or update that date in
   the tag commit if tagging later, so the archived metadata is
   self-consistent.
3. **Tag and Release:**

```bash
git tag -a v0.2.0 -m "APL v0.2.0 — public-alpha workflow release

Verification-first multi-agent physics lab: review-tier + validation
independence protocol, decision-autonomy policy v0 (dry-run), first
external dataset DOI (MD-0002, 10.5281/zenodo.21207072), sealed tier-1
nuclear point forecasts with external-anchor pack."
git push origin v0.2.0
```

Then create the GitHub Release on tag `v0.2.0` (title:
`APL v0.2.0 — public alpha`). With the integration enabled, Zenodo mints
the software DOI automatically from the Release; otherwise upload the
Release tarball manually using the `.zenodo.json` metadata.

4. **Record back — DONE (2026-07-07):** Release published
   2026-07-07T20:38:12Z; Zenodo minted the software DOI automatically via
   the GitHub integration. Version DOI `10.5281/zenodo.21249915`, concept
   DOI `10.5281/zenodo.21249914`, archive
   `open-agent-science/autonomous-physics-lab-v0.2.0.zip` (13,617,960 B),
   metadata API-verified (software / 0.2.0 / MIT software-layer licence /
   creators and keywords from .zenodo.json / isSupplementedBy ->
   10.5281/zenodo.21207072). `MIT` is not a blanket relicensing of every
   archived data, documentation, prediction, or third-party-derived artifact;
   those retain file-specific or dataset-specific terms recorded in
   `data/DATA_LICENSES.yaml` and provenance records.
   Recorded into CITATION.cff, README How To Cite, and the publication
   roadmap. Future releases archive automatically.

## Release notes draft (paste into the GitHub Release body)

> Public-alpha release of the Autonomous Physics Lab workflow: a
> verification-first, multi-agent scientific engine with version-controlled
> scientific memory. Highlights since 0.1.0: public repository opening;
> review-tier protocol with the validation-independence axis; first
> externally published, byte-verified benchmark dataset (MD-0002,
> DOI 10.5281/zenodo.21207072); sealed tier-1 nuclear mass point forecasts
> (PRED-0069..0072) with a deterministic external-anchor capsule;
> negative-results and blocker memory discipline; decision-autonomy policy
> v0 (dry-run). APL is a hypothesis-testing and benchmarking system, not a
> source of automatic discoveries.
