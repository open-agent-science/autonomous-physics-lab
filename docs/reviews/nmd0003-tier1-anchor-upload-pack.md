# NMD-0003 Tier-1 Freeze — External Anchor Upload Pack (TASK-0945)

- Task: TASK-0945, executing Decision Day #2 D2-8/R2
  (`docs/reviews/maintainer-decision-day-2026-07-06.md`).
- Purpose: give the sealed tier-1 point-only forecasts PRED-0069..0072 a
  third-party-verifiable timestamp before any AME/NUBASE-class release
  lands. Sealing currently rests on a self-declared `registered_at_utc`
  and the untagged commit `f1eba9a2`; after this pack is executed, a
  skeptic can verify sealing from the tag, the GitHub Release, and the
  Zenodo deposit without trusting branch history.
- Non-claims: the capsule re-packages already-committed artifacts.
  Registration is not a reveal result and not a success verdict; no
  interval, uncertainty, coverage, or prediction-readiness claim exists
  (TASK-0899 calibration failure stands). Nothing in this pack changes any
  PRED payload, registry entry, RESULT, or CLAIM.

## Frozen inputs (verified pins)

Freeze commit: `f1eba9a2` ("feat(task-0933): freeze NMD-0003 tier-1 point
forecasts"); the five anchored files are byte-identical between that
commit and current `main` (verified via `git diff f1eba9a2 -- <paths>`).

| # | Path | Bytes | SHA-256 |
| --- | --- | --- | --- |
| 1 | `prediction_registry/nuclear_masses/PRED-0069.yaml` | 26,856 | `1f25c093d18fe7076ae4ac8fb49266b0a93089b37379743ce7497658e6d585d9` |
| 2 | `prediction_registry/nuclear_masses/PRED-0070.yaml` | 27,076 | `04a9072f5f6836d63c623271b9addd1a25ee94b94574e4a378973ff77cc50de1` |
| 3 | `prediction_registry/nuclear_masses/PRED-0071.yaml` | 27,467 | `a8e685f5c863797ea93e8564dac314ca368b8961d3a15f378ff5451931065eca` |
| 4 | `prediction_registry/nuclear_masses/PRED-0072.yaml` | 26,450 | `9aa16f6b676b093138471f5f8755d5e90ee385208624e39eb32e64924a17322c` |
| 5 | `docs/reviews/nmd0003-tier1-point-only-frontier-freeze.md` | 18,862 | `360ac6dba379d96c07fea65b56f64e5d5911a4b1f0a0791f4cb0ac6ff04159c3` |

## Deterministic capsule (built and verified)

- Builder: `scripts/package_nmd0003_tier1_anchor_capsule.py`
  (`--output-dir <external dir>`; verifies every pin, ZIP_STORED, fixed
  1980-01-01 timestamps; rebuild reproduces the archive byte-for-byte —
  verified twice locally).
- Capsule: `nmd0003-tier1-anchor-v1.0.0.zip`, **127,617 bytes**, SHA-256
  `82e3a872ad5e3fb1cd7841d29ed53ef3223945a73ba64e71866f0de209804272`.
- The builder writes a JSON manifest beside the archive recording pins,
  policy flags, and the freeze commit.

## Maintainer step 1 — annotated tag (required; signature optional)

```bash
git tag -a pred-nmd0003-tier1-20260705 f1eba9a2 -m "NMD-0003 tier-1 point-only frontier freeze anchor

Seals PRED-0069..0072 (37 no-peek frontier targets, point forecasts only)
as frozen on 2026-07-05T19:35:00Z under TASK-0933. Capsule sha256:
82e3a872ad5e3fb1cd7841d29ed53ef3223945a73ba64e71866f0de209804272.
Not a reveal result; no interval/uncertainty claim exists (TASK-0899)."
git push origin pred-nmd0003-tier1-20260705
```

Use `git tag -s` instead of `-a` if a signing key is available; the
signature is optional and must not delay the anchor.

## Maintainer step 2 — GitHub Release (on the tag)

- Title: `NMD-0003 tier-1 point-only freeze anchor (PRED-0069..0072)`
- Attach: `nmd0003-tier1-anchor-v1.0.0.zip` (from the builder output).
- Body (paste):

> Anchor release for the sealed NMD-0003 tier-1 point-only frontier
> forecasts PRED-0069..0072 (37 no-peek targets, frozen
> 2026-07-05T19:35:00Z, TASK-0933, commit f1eba9a2). The attached capsule
> re-packages the four sealed registry entries and the freeze review note;
> capsule SHA-256
> `82e3a872ad5e3fb1cd7841d29ed53ef3223945a73ba64e71866f0de209804272`.
> Point forecasts only: no interval, uncertainty, coverage, or
> prediction-readiness claim exists or may be derived from this freeze.
> Registration is not a reveal result. Scoring waits for an admissible
> post-freeze source (see the reveal-source watch note in the repository).

## Maintainer step 3 — Zenodo deposit (copy-paste metadata)

- Upload type: Dataset. File: `nmd0003-tier1-anchor-v1.0.0.zip`.
- Title: `NMD-0003: Sealed tier-1 point-only nuclear mass frontier
  forecasts (PRED-0069..0072) — freeze anchor capsule`
- Creators: `Hladun, Roman` (ORCID `0009-0004-4853-5212`).
- Version: `1.0.0`. License: `CC BY 4.0`.
- Keywords: `nuclear masses`, `sealed predictions`, `pre-registration`,
  `Gaussian process`, `autonomous research agents`, `open science`.
- Related identifiers: `IsSupplementTo` ->
  `https://github.com/open-agent-science/autonomous-physics-lab`.
- Description (paste):

> Deterministic anchor capsule for the sealed NMD-0003 tier-1 point-only
> nuclear mass frontier forecasts PRED-0069..0072 of the Autonomous
> Physics Lab (APL): 37 no-peek frontier targets frozen on
> 2026-07-05T19:35:00Z at repository commit f1eba9a2 and release tag
> pred-nmd0003-tier1-20260705. The capsule contains the four sealed
> prediction-registry entries and the freeze review note, packaged
> deterministically (ZIP_STORED, fixed timestamps); capsule SHA-256
> 82e3a872ad5e3fb1cd7841d29ed53ef3223945a73ba64e71866f0de209804272.
> This deposit exists to give the sealing a third-party timestamp before
> the next AME/NUBASE-class evaluation. It is a pre-registration anchor,
> not a scientific result: point forecasts only, no interval, uncertainty,
> coverage, or prediction-readiness claim exists or may be derived from
> it, and registration is not a success verdict. Scoring is defined in
> the freeze note (MAE in MeV and rank against three frozen comparators
> over revealed targets only) and waits for an admissible post-freeze
> source.

## Record-Back Checklist (after Publish)

- [ ] Tag `pred-nmd0003-tier1-20260705` pushed at `f1eba9a2`.
- [ ] GitHub Release created with the capsule attached.
- [ ] Zenodo record published; version DOI + record URL recorded back into
      the freeze review note and this pack; anchor pointers added to the
      PRED-0069..0072 documentation trail.
- [ ] Reveal-source watch note updated to reference the anchor (a revealed
      grading must cite the anchored capsule checksum).
