# TASK-1029: Gaia DR4 stellar-transfer freeze-readiness packet

- Task: `TASK-1029`
- Mode: value-blind pre-release readiness decision (planning only)
- Access date for all official metadata: `2026-07-13`
- Anchor result: `RESULT-0022` (`results/EXP-0015/RUN-0001/result.yaml`)
- Predecessor scout: `TASK-0834`
  ([gaia-dr4-stellar-ml-reveal-contract-scout.md](../gaia-dr4-stellar-ml-reveal-contract-scout.md),
  verdict `NEEDS_FIELDS`)

## Scope and non-goals

This packet decides GO/HOLD/STOP for arming a future prospective Gaia DR4
stellar mass-luminosity freeze, and specifies the exact target-independent
functional payload, the DEBCat leakage policy, and the prediction-registry
compatibility a later freeze task would need. It supersedes the scout's
`NEEDS_FIELDS` blocker only on the field-readiness question, using the newly
published official DR4 draft data model.

No DR4 value was read. No target row was invented. No `PRED-*` entry was
registered, no registry schema was changed, and no `RESULT-*`, `CLAIM-*`, or
knowledge artifact was created or modified. `RESULT-0022` and the frozen
DEBCat slice are unchanged. Only official ESA/Gaia metadata and committed
repository artifacts were inspected; every retrieved official artifact is
pinned by SHA-256 below and is not vendored.

## Event trigger status (official, pinned)

The task's admissible event trigger is "Gaia DR4 officially published **or** an
official draft data model published." The second arm is now satisfied.

| Official artifact | Locator | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| Gaia Data Release Scenario | `https://www.cosmos.esa.int/web/gaia/release` | 110,331 | `1f981dc8aa16a6cb0571800459f649fbd414faab407ee6d42f592b9456fd3ee1` |
| Gaia DR4 landing page | `https://www.cosmos.esa.int/web/gaia/data-release-4` | 126,859 | `6fcd9d34062b025f3c2c29531c640ae097076910939f2ec69afb7a76a8d75dc3` |
| Gaia DR4 content overview | `https://www.cosmos.esa.int/web/gaia/dr4` | 129,065 | `323b3bc50f1405c8189b6ec692b7d1bf1ca5e0cb51083e6e97fbb9ca659c734a` |
| **DR4 draft data model (zip)** | `https://anonftp.cosmos.esa.int/pub/GAIA_PUBLIC_DATA/Gaia_DR4/dr4-prerelease/gaia-dr4-prerelease-draft-data-model_2026-06-26.zip` | 2,840,832 | `d807eae98acbeec0a0af2ce6a5d7d352298df6f270a1f13207cc8d1becf42c66` |
| DR4 draft data model (PDF inside zip) | `gaia-dr4-prerelease-draft-data-model.pdf` | 2,948,311 | `8c33055c122eb3f5ef6ac64e8624e6c11a1e261f6fa4108c635296b52feeb043` |

Load-bearing official wording (paraphrased, with status):

- **Release date:** the DR4 landing page shows "Coming up: 2 December 2026";
  the release-scenario page lists "Gaia DR4 (based on 66 months of data)
  2 December 2026" and states "The final, detailed release contents will be
  decided on only after completion of the validation work." The date remains a
  **target scenario**, not a completed release. DR4 is **not yet released**.
- **Draft data model:** the DR4 content page states "The Gaia DR4 draft data
  model will be published in advance of the data release," and the landing page
  states "A draft version is now available." The pinned zip is dated
  `2026-06-26`, matching ESA's promised end-of-June update window. This is a
  **draft**; column names/units may still change before release.
- **Source counts:** the landing page still reads "End of June 2026 an update
  can be expected specifying number of sources for data products." Final
  per-product source counts and final contents remain **pending validation**;
  the draft data model publishes the schema, not the counts.
- **Data license:** the draft-model readme points to
  `https://www.cosmos.esa.int/web/gaia-users/license`; no DR4 data bytes are
  committed by this packet (metadata only).

## Field readiness from the official draft data model

The scout's `NEEDS_FIELDS` rested on three unresolved field questions. The DR4
draft data model (pinned above) now answers all three at the schema level.

### Mass axis — table `nss_masses`

Official description: "Table of masses derived from the non-single stars (NSS)
solutions with orbital parameters."

| Column | Draft-model definition | Unit |
| --- | --- | --- |
| `source_id` | Unique source identifier (join key) | — |
| `m1`, `m1_lower`, `m1_upper` | Primary mass with 16th/84th percentile confidence | Solar Mass |
| `m2`, `m2_lower`, `m2_upper` | Secondary mass with 16th/84th percentile confidence | Solar Mass |
| `combination_method` | Which NSS solution combination produced the masses | string |
| `fluxratio`, `_lower`, `_upper` | G-band secondary/primary flux ratio | — |

The draft model's `combination_method` summary table names exactly which
combinations constrain **both** component masses: `ASTROSPECTROSB2`,
`ORBITAL_SB2`, `ECLIPSINGSPECTROSB2`, and `ECLIPSING_SB2` yield both `m1` and
`m2`; the `*_SB1_M1`, `SB1_M1`, `ORBITAL_M1`, `PAIR_M1`, and `VIMO_*` methods
yield only partial (primary-only, or lower-bound) constraints. This resolves
the scout's "two-component-mass solution types" question: the eligible subset
is the four both-mass combinations, in `Solar Mass` units — directly
compatible with RESULT-0022's `direct dynamical mass, M_sun` domain.

### Luminosity axis — FLAME astrophysical parameters

Two bolometric-luminosity columns are published in the draft model, both in
`Solar Luminosity`:

| Column | Draft-model definition | Product |
| --- | --- | --- |
| `lum_flame` (+ `_lower`, `_upper`) | "Luminosity of the star from FLAME using G band magnitude, extinction, parallax or distance, and a bolometric correction" | GSP-Phot-based FLAME (`ap`/`ap_xp`) |
| `lum_flame_spec` (+ `_lower`, `_upper`) | "Luminosity of the star from FLAME using G band magnitude, extinction, parallax and a bolometric correction" | GSP-Spec-based FLAME (`ap_rvs`) |

Both are genuine bolometric luminosity in `L_sun` (median = 50th percentile,
with 16/84 percentile confidence). This maps onto RESULT-0022's
`log_luminosity_solar` target. The draft model also publishes
`radius_flame_spec` and effective temperature, so the Stefan-Boltzmann
`log L` route (part of RESULT-0022's own mixed provenance) is available as a
predeclared fallback.

**Provenance reconciliation, still required at reveal:** FLAME luminosity is
derived from parallax + extinction + bolometric correction (GSP-Phot/GSP-Spec),
whereas RESULT-0022's luminosities are DEBCat catalogue-reported plus
Stefan-Boltzmann from `log R`, `log T`. The reveal task must either (a) use the
Stefan-Boltzmann FLAME route to match provenance, or (b) declare and bound the
provenance difference as a systematic. This is a reveal-time reconciliation,
not a field-readiness blocker.

## Proposed target-independent functional payload

The freeze is **target-independent**: it fixes the predictor, comparators,
eligibility rule, metric, and decision rule now, and resolves actual DR4
targets only at reveal. Exact frozen values from
`results/EXP-0015/RUN-0001/result.yaml`:

| Element | Frozen value |
| --- | --- |
| Relation form | `log L = alpha * log M`, fixed intercept `log L0 = 0` (`L0 = 1`) |
| Frozen textbook comparators | `alpha = 3.5` (recorded holdout MAE 0.184954 dex); `alpha = 4.0` (0.137608 dex) |
| Frozen train-fitted exponent | `alpha_hat = 4.526004`, fixed intercept `log L0 = 0` (recorded holdout MAE 0.119925 dex) |
| Null baseline | per-mass-band train-median (recorded holdout MAE 0.331817 dex) |
| Predicted quantity | `log L` in `L_sun` for each eligible DR4 star given its DR4 dynamical `log M` |
| Eligibility regime | per-component dynamical mass `0.5-2.0 M_sun`, main-sequence-compatible, both-mass NSS combinations only (`ECLIPSING_SB2`, `ORBITAL_SB2`, `ASTROSPECTROSB2`, `ECLIPSINGSPECTROSB2`), DEBCat-disjoint |
| Crossmatch key | Gaia `source_id`, joining `nss_masses` (mass) to `ap`/`ap_rvs` FLAME (luminosity) for the same source |
| Metric | holdout MAE in `dex` of `log L` on the DEBCat-disjoint eligible DR4 set |
| Decision rule | frozen exponents CONFIRM the RESULT-0022 reading only if they beat the null by more than the recorded `0.04 dex` split-noise reference; otherwise out-of-sample falsification, or `INCONCLUSIVE` (preferred for small reveal-N) |
| Missing-field behavior | if bolometric FLAME luminosity absent but Teff + radius present, derive `log L` via Stefan-Boltzmann (predeclared route); if two-mass coverage below a predeclared minimum-N, report `INCONCLUSIVE` |
| Post-release tuning | forbidden — no refit, no new model family, no coefficient re-tuning, no regime/threshold change after reveal |

Payload freezes cleanly today: every element is fixed by RESULT-0022 and the
draft data model, and none requires a DR4 value.

## DEBCat leakage / overlap policy (value-blind)

RESULT-0022 trained on DEBCat, so DEBCat is the training source, not an
independent control. The frozen comparison surface is the committed
`data/textbook_formula_audit/stellar_ml/debcat_component_rows.yaml`
(SHA-256 `7e8fe4a2359f53f7fd7c80cdba5f56dc024fa45f985879d3faecb8bc8398db08`,
373 system identifiers), the same surface frozen for the TASK-1025 alias audit.

- **Blind target set:** DR4-NSS both-mass systems with **no** DEBCat
  counterpart (DEBCat-disjoint). This tests extrapolation onto genuinely
  independent dynamical masses.
- **Identity evidence required (future manifest, not built here):** crossmatch
  the frozen DEBCat system set to Gaia `source_id` using existing DEBCat-Gaia
  cross-identifications and coordinates with a **predeclared fixed match
  radius**; require stable identifier evidence, not coordinate proximity alone.
  Any DEBCat-matched DR4 system is excluded from the blind score (it may be
  reported only as a separate, labelled, non-blind diagnostic).
- **Ambiguity stops:** unresolved, coordinate-only, or hierarchy-ambiguous
  DR4↔DEBCat identities are treated as potential leakage and excluded from the
  blind set by default (fail-closed), consistent with the TASK-1025 rule.
- **Split discipline:** keep any per-system aggregation system-level (no
  binary-component leakage), matching RESULT-0022.
- **Pre-reveal boundary:** the frozen payload must be committed before the DR4
  release timestamp, auditable in git/PR history; no DR4 value may inform
  candidate selection, exponent choice, cuts, thresholds, or wording.

The identity manifest itself is a later task; this packet specifies its shape
and rules only.

## Prediction-registry compatibility audit

Audited against the generic domain-neutral schema
`physics_lab/schemas/prediction.schema.json` (the registry has already extended
beyond nuclear masses: `prediction_registry/radio_transients/PRED-0001.yaml`
and `prediction_registry/exoplanet_mass_radius/` exist).

| Freeze need | Schema support | Verdict |
| --- | --- | --- |
| Domain-neutral entry | schema title "Prediction (generic, domain-neutral)"; no nuclear-only required fields | supported |
| Frozen predictor + coefficients | `source_state.model_reference` requires `model_id`, allows `frozen_parameters_note`, `selected_formula`, `source_sha256` (`additionalProperties: true`) — the pattern PRED-0001 already uses | supported |
| Target-independent target set | `target_set` requires only `label`, `quantity`, `unit`, with `additionalProperties: true`; the `targets` list is **not** required, so an eligibility-rule + deferred-resolution target set is representable | supported |
| Reveal gating | `reveal_conditions` requires `comparison_source_class`, `reveal_controlled_by`, `no_peek_rule`; allows `expected_reveal_window` | supported |
| No live fetch | `source_state.live_external_fetch_allowed` is `const: false` | supported |

**Finding:** the existing generic schema can represent this freeze with no
schema change. The one soft gap is that a target-independent functional freeze
must express its eligibility predicate and comparator table via `target_set`
extension fields (`additionalProperties`), rather than first-class properties.
That is adequate for a valid entry; a later schema task **may** optionally add
first-class `functional_payload` / `eligibility_rule` fields to make
target-independent freezes self-documenting, but this is an enhancement, not a
blocker. No registry schema change is required to proceed.

## Verdict

**`GO_GAIA_FREEZE_PREPARATION`.**

Reasoning: the scout's `NEEDS_FIELDS` blocker was field readiness. The official
DR4 draft data model (pinned, dated 2026-06-26) now publishes the exact tables,
columns, and units for both axes — `nss_masses.m1/m2` (Solar Mass, with
confidence bounds) and the named both-mass NSS combinations, plus FLAME
`lum_flame`/`lum_flame_spec` (Solar Luminosity, with confidence bounds) and a
Stefan-Boltzmann fallback route — all semantically compatible with RESULT-0022.
The functional payload freezes today without any DR4 value; the prediction
registry can represent it with no schema change; and the DEBCat leakage policy
is fully specifiable value-blind against the frozen DEBCat surface. The route
does not require post-release tuning. The remaining unknowns (final source
counts, final contents, the draft-vs-final schema delta, and the possibility of
a date slip) are all handled by keeping the freeze target-independent and
gating the actual reveal on the confirmed release — they do not block freeze
preparation. GO authorizes opening the bounded follow-on tasks below; it does
not authorize registering a PRED, reading DR4 values, or scoring.

## Bounded follow-on task shapes (not opened here)

1. **Freeze task:** register one target-independent `PRED-*` entry under
   `prediction_registry/stellar_mass_luminosity/` using the functional payload
   above; pin RESULT-0022's git commit and the draft-data-model SHA-256;
   commit before the DR4 release timestamp. Re-verify the pinned draft columns
   against the final DR4 data model at release and, if any column/unit changed,
   adjust the frozen field mapping **before** the pre-release commit (never
   after reveal).
2. **Identity-manifest task:** build the value-blind DEBCat↔Gaia `source_id`
   crossmatch with the predeclared match radius and the fail-closed ambiguity
   rule, producing the DEBCat-disjoint eligibility manifest.
3. **(Optional) registry-schema task:** add first-class
   `functional_payload`/`eligibility_rule` fields to the generic prediction
   schema for target-independent freezes.
4. **Reveal task (post-release only):** after DR4 is officially released and
   its data model is final, join `nss_masses` and FLAME luminosity on
   `source_id`, apply the frozen eligibility and leakage exclusion, and score
   the frozen comparators against the null under the frozen decision rule. This
   is a separate maintainer-reviewed task; neither outcome auto-promotes to a
   claim.

## Output routing

- Task verdict: `not_applicable` (readiness decision; packet-level outcome is
  `GO_GAIA_FREEZE_PREPARATION`).
- Canonical destination: this prospective-reveal readiness packet under
  `docs/reviews/stellar/`; no `agent_runs/`, `results/`,
  `prediction_registry/`, `claims/`, or `knowledge/` artifact created or
  changed.
- Review tier: none (planning / readiness only).
- Gate A: not attempted (no RESULT/PRED created).
- Gate B: not attempted (no replay target created).
- PRED: none frozen, registered, or scored.
- DR4 data: not fetched, not ingested; official metadata pinned by SHA-256 and
  not vendored; the release date is recorded with its target-scenario status,
  not hardcoded.
- Claim / knowledge / result impact: none; RESULT-0022 and the frozen DEBCat
  slice are unchanged.
- Limitations / blockers: the DR4 data model is a **draft** (columns/units may
  change before release, so the freeze task must re-verify at release); final
  per-product source counts and DR4 two-mass coverage in `0.5-2.0 M_sun`
  remain unpublished (may force `INCONCLUSIVE` at reveal); FLAME luminosity
  provenance must be reconciled to RESULT-0022 at reveal; DEBCat-DR4 overlap is
  non-zero and must be excluded from any blind score; the RESULT-0022 headline
  remains scoped to its frozen `0.5-2.0 M_sun` slice and is `AGENT_VALIDATED`,
  not maintainer-reviewed.
