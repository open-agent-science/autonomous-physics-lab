# Nuclear Reveal-Source Watch — Bounded Definition (TASK-0946)

- Task: TASK-0946, executing Decision Day #2
  (`docs/reviews/maintainer-decision-day-2026-07-06.md`).
- Purpose: the prediction registry holds sealed reveal-blocked entries,
  including the tier-1 point-only set PRED-0069..0072
  (`docs/reviews/nmd0003-tier1-point-only-frontier-freeze.md`). Their value
  is realized only at reveal, and until now no task watched for admissible
  reveal sources. This note converts the passive "wait for AME" into an
  active, bounded watch with an explicit hit protocol.
- Non-claims: this note performs no reveal, no scoring, and changes no
  PRED, registry, RESULT, or CLAIM artifact. A watch hit produces a
  maintainer decision packet, never an automatic reveal.

## External anchor to cite on any hit

The PRED-0069..0072 tier-1 point-only freeze is externally anchored by
TASK-0945:

- GitHub Release:
  <https://github.com/open-agent-science/autonomous-physics-lab/releases/tag/pred-nmd0003-tier1-20260705>.
- Zenodo record: <https://zenodo.org/records/21240451>.
- Version DOI: <https://doi.org/10.5281/zenodo.21240451>.
- Concept DOI: <https://doi.org/10.5281/zenodo.21240450>.
- Capsule SHA-256:
  `82e3a872ad5e3fb1cd7841d29ed53ef3223945a73ba64e71866f0de209804272`.
- Zenodo MD5: `af2c3234796f0357c6a4263ffc04b1ab`.

Any future watch hit or reveal decision packet must cite this external anchor
before scoring, and must preserve the point-only/no-interval/no-success
boundaries recorded in the freeze note.

## Admissible source classes (verbatim scope from the freeze note)

- **Class A:** the next AME/NUBASE-class evaluation published after
  `2026-07-05T19:35:00Z`.
- **Class B:** a qualifying flagged Penning-trap / storage-ring measurement
  subset in a watched frontier region.
- Each source is admitted only by a separate maintainer-reviewed reveal
  task with its own source manifest, checksum record, registry snapshot,
  and no-peek audit per the reveal protocol and
  `docs/nuclear-reveal-source-readiness-checklist.md`.

## Watch procedure

1. **What to check.**
   - Class A: the AMDC (Atomic Mass Data Center) publication surface for a
     new AME/NUBASE evaluation release (a successor to AME2020/NUBASE2020),
     including announcement pages and the associated journal publications
     (Chinese Physics C for recent editions).
   - Class B: new Penning-trap / storage-ring mass measurement publications
     covering isotopes inside the frozen frontier target set
     (`FRONTIER-PRED-TARGETS-0001`); candidate venues include the standard
     precision-mass literature streams the AMDC ingests.
2. **Cadence.** Once per director cycle, and at minimum monthly. The check
   is a lightweight source-surface scan, not a data download.
3. **Evidence to record on a hit.** Source name, publication date and
   venue, DOI/URL, claimed coverage (which nuclides / regions), and an
   explicit statement of whether the publication date is after the freeze
   timestamp `2026-07-05T19:35:00Z`. No mass values may be transcribed
   into the repo at watch time — value contact is deferred to the no-peek
   reveal task itself.
4. **Hit protocol.** A hit produces a maintainer decision packet
   referencing this note and the readiness checklist, proposing (not
   executing) the reveal task shape: source manifest, checksum record,
   registry snapshot, no-peek audit, and the frozen scoring rule (MAE in
   MeV per region and pooled, plus rank of the GP against the three frozen
   comparators — only; no interval metrics exist at tier-1).
5. **No-hit record.** A one-line "checked, no admissible source" entry in
   the director-cycle notes is sufficient; do not create per-cycle memo
   files.

## Stop conditions

- Stop the scan and escalate to a maintainer decision packet immediately
  on any Class A hit.
- Do not admit sources that predate the freeze timestamp, preprint-only
  evaluations, or partial datasets whose provenance the readiness
  checklist cannot pin — record them as watched-but-inadmissible with a
  one-line reason instead.
- This watch creates no recurring seeded tasks: it is a standing procedure
  executed inside existing director cycles, so the atomic-style scout-loop
  cost cap does not recur here.

## Watched artifacts

- `prediction_registry/nuclear_masses/` sealed entries, including
  PRED-0069..0072 (tier-1 point-only, frozen 2026-07-05).
- Reveal scoring rule and comparator set: frozen in
  `docs/reviews/nmd0003-tier1-point-only-frontier-freeze.md`; this note
  changes none of it.
