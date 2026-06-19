# Textbook Wien Displacement — FIRAS Source-Artifact Curation (TASK-0793)

**Task:** `TASK-0793` · **Campaign:** `textbook-formula-audit` ·
**Mode:** source-curation only (planning).
**Verdict:** `SOURCE_ROUTE_OPEN_PENDING_FETCH_AND_PIN` — the NASA LAMBDA COBE/FIRAS
monopole spectrum is an open, reusable, blackbody-grade route for a future
**wavelength-domain Wien-peak consistency audit**. It is **not a no-go**, but it carries
**two unresolved gates** that must be closed before any metric: (1) the selected product
must be an **absolute** monopole spectrum, not a residual/model-normalized one; and (2)
the **spectrum source and the reference-temperature source must be pinned separately**.
No data was fetched, no metric was run, and no `RESULT`/`PRED`/`CLAIM`/`KNOW` artifact is
created here.

Builds on the Wien source/baseline plan (`docs/reviews/textbook-wien-displacement-source-baseline-plan.md`, TASK-0492) and the slice selection (`docs/reviews/textbook-next-formula-source-baseline-slice.md`, TASK-0783); it pins the empirical FIRAS route those notes deferred.

## Audit question (scoped, for a future metric task — not run here)

> On the pinned COBE/FIRAS **absolute** CMB monopole spectrum, does the
> **wavelength-domain** peak of the spectral radiance agree with `lambda_peak = b / T`
> (CODATA `b`; an explicitly sourced `T`) within a pre-registered tolerance, after a
> declared `B_nu → B_lambda` conversion?

This is a **spectral-domain consistency audit**, not a claim that Wien displacement is
universally validated or falsified, and not a blackbody-universality, cosmology, or
discovery statement.

## Unresolved gate 1 — absolute spectrum vs residual product (must close before metrics)

FIRAS historically measured the **difference** between the sky and an internal blackbody
calibrator near 2.7 K; several distributed FIRAS products are therefore **residuals from a
fitted blackbody** or model-normalized, not an absolute spectral radiance. A residual-only
or model-normalized product **cannot** support direct peak location.

> **Gate:** the selected NASA LAMBDA product must contain an **absolute monopole spectral
> radiance with documented ordinate semantics**. If the only available product is
> residual-only or model-normalized, **stop the route or select a different product** —
> do not attempt a peak-location metric on it.

(See Fixsen et al. 1996, ApJ 473, 576, on the FIRAS calibration/residual structure.)

## Unresolved gate 2 — separate spectrum source from temperature source

The reference temperature must **not** be assumed to come from the selected spectrum
product. Pin them separately:

- **Spectrum source:** COBE/FIRAS monopole product / Fixsen et al. 1996.
- **Reference temperature:** a separately cited estimate, e.g. Fixsen 2009, ApJ 707, 916
  — literature combined `T = 2.72548 ± 0.00057 K`, and a FIRAS-recalibrated
  `T = 2.7260 ± 0.0013 K`. The metric task must state **which** `T` it uses and why, and
  treat the choice as part of the provenance (not a free parameter).

## Source route

- **Product:** COBE/FIRAS CMB monopole (absolute) spectrum — calibrated CMB brightness vs
  spectral axis, with per-point uncertainty and residual columns.
- **Archive:** NASA LAMBDA (`lambda.gsfc.nasa.gov`, COBE/FIRAS products). Exact product
  URL/id + retrieval timestamp to be pinned at fetch time.
- **Primary citations:** Fixsen et al. 1996, ApJ 473, 576 (spectrum); Fixsen 2009, ApJ
  707, 916 (temperature); Mather et al. 1999. All must be attributed in any committed artifact.

## License / reuse status

COBE/FIRAS products on NASA LAMBDA are **U.S. Government works, not subject to domestic
copyright**, freely reusable with attribution per NASA data-use guidance — materially
cleaner than the DEBCat route (which needed an explicit redistribution grant). The table
is therefore **Route 1 eligible** (full value-bearing table committable with citation), but
the future fetch task must still record the URL, retrieval timestamp, and a
`DATA_LICENSES.yaml` entry (`public_domain_us_gov` + NASA attribution) before committing rows.

## Checksum policy (no fetch performed here)

A future fetch task pins the exact FIRAS product by **SHA-256** under
`data/textbook_formula_audit/wien_firas/` and records the checksum + retrieval timestamp in
a source manifest; the replay path reads only the committed pinned file (no live fetch at
audit time, same Route-1 discipline as MD-0002). This curation task records the *policy*,
not a checksum, because no bytes were retrieved.

## Row schema (to confirm against the pinned product header)

| field | unit | role |
| --- | --- | --- |
| `spectral_axis` | wavenumber `cm^-1` (FIRAS native) | independent variable |
| `monopole_intensity` | `MJy/sr` — **absolute** spectral radiance per unit frequency (`B_nu`) | measured |
| `uncertainty` | `kJy/sr` | per-point sigma |
| `residual` | `kJy/sr` | diagnostic only, **not** the audited ordinate |

FIRAS reports the spectrum on a **frequency / wavenumber** axis (`B_nu` vs `cm^-1`), i.e.
the frequency domain. The **ordinate semantics (per-Hz vs per-wavenumber, absolute vs
residual)** and exact column order/units must be confirmed against the pinned product header.

## Baseline contract (the spectral-axis crux)

The Wien plan (TASK-0492) is the **wavelength-domain** peak `lambda_peak = b / T` and
rejects frequency-domain peaks unless converted. FIRAS is frequency-domain, so the audit
must declare a deterministic conversion: `B_lambda = B_nu * nu^2 / c` (equivalently
`c / lambda^2`), then locate the wavelength-domain peak. Switching scope to the
frequency-domain Wien constant (`nu_peak / T`) is a *different* relation, out of scope for
TASK-0492.

The peaks are genuinely different (Wien non-invariance); for `T ≈ 2.7255 K`:

- Wavelength-domain peak: `lambda_peak = b/T ≈ 1.063 mm` (≈ `9.4 cm^-1`).
- Frequency-domain peak: `nu_peak ≈ 160 GHz` (≈ `5.3 cm^-1`).

Both fall inside the nominal FIRAS window (≈ `2–21 cm^-1`) with margin — to confirm against
the pinned file. A bare axis relabel without the Jacobian gives the **wrong** "Wien peak";
this is the central point of the benchmark, not a detail. Constant convention unchanged:
`b = 2.897771955e-3 m K` (CODATA 2022, NIST), SI internally.

## Required controls (declared now; run only in the future metric task)

1. **Absolute-vs-residual product gate** (Unresolved gate 1) — fail if the product is
   residual-only / model-normalized.
2. **No-Jacobian-conversion control** — relabelling the axis without the `B_nu → B_lambda`
   Jacobian must produce a *wrong* peak and must **fail** the consistency check.
3. **Domain-consistency control** — the wavelength-domain and frequency-domain peaks must
   differ by the known Planck factor; a spectrum/conversion that collapses them is
   non-blackbody or mis-converted.
4. **Sampling/interpolation-resolution control** — compare the raw-bin maximum against a
   local interpolation/fit of the peak; report sensitivity, since the FIRAS bin spacing may
   limit peak-location precision.
5. **Wrong-temperature control** — a deliberately offset `T` must be rejected.
6. **Units control** — explicit `GHz ↔ cm^-1 ↔ m` conversions checked end to end.
7. **Circularity caveat (mandatory framing)** — the reference `T` is itself obtained by
   fitting a Planck spectrum to FIRAS, so a raw "peak vs `b/T`" comparison is partly a
   **self-consistency** check, not independent validation; use an independently determined
   `T` or frame the outcome explicitly as blackbody self-consistency.

## Result naming and admissible verdicts (for the future metric task)

- **Do not** name it "APL validated Wien's law with FIRAS".
- **Do** name it a **"FIRAS spectral-domain consistency audit for Wien displacement"**.
- Admissible verdicts: `CONSISTENT_IN_SCOPE`, `DOMAIN_CONVERSION_MISMATCH`,
  `INCONCLUSIVE_PRODUCT_SEMANTICS`, `INCONCLUSIVE_SAMPLING_RESOLUTION`.

## Next steps — exactly two follow-up tasks (each needs its own authorization)

1. **Pin and validate the FIRAS product (no metrics):** exact LAMBDA URL/product id;
   SHA-256; source-specific reuse/attribution + `DATA_LICENSES.yaml`; column schema;
   **absolute vs residual** determination; ordinate (per-Hz vs per-wavenumber);
   uncertainty/covariance availability; **temperature source kept separate**.
2. **Run the empirical Wien/FIRAS audit:** deterministic `B_nu → B_lambda` with the
   declared Jacobian; all controls above; sampling/interpolation sensitivity; empirical
   metrics; limitations; an `AGENT_PUBLISHED` RESULT only if Gate A passes — then a
   **different** agent runs Gate B replay.

Do not spawn additional planning-only loops; these two tasks are sufficient.

## Output routing

- Source-readiness impact only. Gate A / Gate B **not attempted**. Claim impact: none.
  Knowledge impact: none. No metrics, fit, or peak-finding run.

## Limitations / no-claim

Planning/source-curation note only. No COBE/FIRAS bytes were retrieved, no checksum was
computed, no spectrum was fit, and no Wien verdict is asserted. Not a blackbody-universality,
cosmology, CMB-physics, or discovery claim.
