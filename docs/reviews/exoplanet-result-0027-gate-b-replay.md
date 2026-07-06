# RESULT-0027 Exoplanet Null-Baseline Gate B Replay

- Task: `TASK-0935`
- Result: `RESULT-0027`
- Artifact: `results/EXP-0021/RUN-0001/result.yaml`
- Helper: `scripts/apl_validate_agent_published_result.py`
- Gate B engine: `physics_lab/registry/agent_replay_validation.py`
- Original publisher: `akutenyov` (agent tool Codex, GPT-5), task `TASK-0919`
- Replayer: `gladunrv` (agent tool Claude Code, Claude Fable 5)
- Formal Gate B helper status: **`BLOCKED` (`unsupported-command`)**
- Justified deterministic repackage replay: **byte-identical, zero drift**
- Tier decision this task: **no change.** RESULT-0027 stays at
  `AGENT_PUBLISHED`; the task permits a metadata-only tier update only when the
  formal helper path passes, and it does not.

## Scope

This task replays the already packaged RESULT-0027 negative/control artifact
from committed inputs only and records a Gate B determination. It does **not**
fetch live NASA Exoplanet Archive data, create `EXO-0003` rows, change
source-version triggers, rerun residual scoring, refit Chen–Kipping-style
baselines, create a positive mass–radius law, or create or promote `CLAIM-*`,
`KNOW-*`, or `PRED-*` artifacts. The committed RESULT-0027 package is
byte-unchanged by this task.

## Formal Gate B Helper Run

The canonical Gate B helper was run against the unmodified committed artifact:

```bash
python3 scripts/apl_validate_agent_published_result.py \
  results/EXP-0021/RUN-0001/result.yaml \
  --root . \
  --validator-contributor-id gladunrv \
  --validator-github-username gladunrv \
  --validator-agent-tool "Claude Code" \
  --validator-model "Claude Fable 5" \
  --json
```

Outcome:

- Status: **`BLOCKED`**, `ok: false`.
- Sole issue: `unsupported-command` — "Gate B only supports safe physics-lab
  run commands, not arbitrary shell commands."
- No metric deltas were computed and no validation record was emitted.

The blocker is structural, not scientific: RESULT-0027's recorded command is

```bash
python3 scripts/package_exoplanet_null_baseline_result.py --write
```

which is not in the Gate B engine's `SAFE_RESULT_COMMANDS` allowlist
(`physics-lab run ...` / `python(3) -m physics_lab.cli run ...`). The formal
helper therefore cannot re-execute this result regardless of its content.

## Justified Replay Path: Deterministic Repackage Comparison

Because the packager is deterministic from committed inputs (it reads the
frozen `agent_runs/AGENT-RUN-0050/metrics.json` at a pinned commit via
`git show`, enforces the packaged invariants, and uses a constant
`generated_at`), the packaged artifact can still be independently replayed by
re-running the packager into a disposable directory pinned to the recorded
result commit:

```bash
python3 scripts/package_exoplanet_null_baseline_result.py \
  --output-dir <disposable-replay-dir>/RUN-0001 \
  --git-commit 7d0be449044f0a693c4e54b81b9c2e1c80c2c1b4 \
  --write
diff -r results/EXP-0021/RUN-0001 <disposable-replay-dir>/RUN-0001
```

Outcome: `diff -r` reported **no differences**. The regenerated package is
**byte-identical** to the committed one across all eleven artifacts
(`result.yaml`, `metrics.json`, `report.md`, `gate_a_report.md`,
`review_metadata.yaml`, `review_summary.md`, `claim_update.md`,
`claim_update.patch.md`, `knowledge_update.md`, `knowledge_update.patch.md`)
and the full `inputs/` snapshot directory. Byte identity subsumes every
comparison the task requires: true-mass slice classifications, nearest-radius
null-control values, the underpowered minimum-mass boundary, result metadata,
and all five recorded input hashes.

## Drift Table

All values below reproduce exactly (drift `0`, byte-identical files).

| Axis | Slice | Rows | CK17 frozen RMSE (dex) | Nearest-radius null RMSE (dex) | Classification | Drift |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| `true_mass_with_transit_radius` | `compact_radius_lt1p5Re` | 92 | 0.263350 | 0.019905 | `null_family_matches_or_beats_ck17` | 0 |
| `true_mass_with_transit_radius` | `sub_neptune_radius_1p5_4Re` | 340 | 0.204175 | 0.000858 | `null_family_matches_or_beats_ck17` | 0 |
| `true_mass_with_transit_radius` | `jovian_radius_8_16Re` | 567 | 0.083354 | 0.000432 | `null_family_matches_or_beats_ck17` | 0 |
| `true_mass_with_transit_radius` | `hot_jupiter_period_lt10d_radius_ge8Re` | 445 | 0.069788 | 0.000349 | `null_family_matches_or_beats_ck17` | 0 |
| `minimum_mass_with_transit_radius` | `compact_radius_lt1p5Re` | 0 | n/a | n/a | `underpowered_slice` | 0 |
| `minimum_mass_with_transit_radius` | `sub_neptune_radius_1p5_4Re` | 2 | n/a | n/a | `underpowered_slice` | 0 |
| `minimum_mass_with_transit_radius` | `jovian_radius_8_16Re` | 0 | n/a | n/a | `underpowered_slice` | 0 |
| `minimum_mass_with_transit_radius` | `hot_jupiter_period_lt10d_radius_ge8Re` | 0 | n/a | n/a | `underpowered_slice` | 0 |

Recorded input hashes (full values in `result.yaml`) reproduce identically:

| Input | SHA-256 (first 16) | Identical |
| --- | --- | --- |
| `inputs/config.yaml` | `d17da7a9c9c527b6` | yes |
| `inputs/fixture.json` | `d3478e9ec9df18f0` | yes |
| `inputs/experiment.yaml` | `f8eb4ce2c0590687` | yes |
| `inputs/hypothesis.yaml` | `de65dd2207a0a27f` | yes |
| `inputs/task.yaml` | `563487095e46f8bb` | yes |

`best_verdict` unchanged: `INCONCLUSIVE`. `review_tier` unchanged:
`AGENT_PUBLISHED`.

## Independence Assessment

| Independence axis | Original party | This replay | Independent? |
| --- | --- | --- | --- |
| RESULT-0027 publisher and packager author (`TASK-0919`) | `akutenyov` / Codex / GPT-5 | `gladunrv` / Claude Code / Claude Fable 5 | Yes (different contributor, different agent tool, different model) |

Unlike the RESULT-0020 case, no same-identity conflict exists here: the
packaging script and the published artifact both come from `akutenyov` / Codex,
and the replay identity differs on every axis. If the formal-path blocker below
is cleared, this result has no known validation-independence obstacle.

## Determination and Path to Clear the Blocker

Gate B determination: **`BLOCKED`** on the formal path (`unsupported-command`).
The justified deterministic repackage replay is byte-identical, so the content
of RESULT-0027 is fully reproducible from committed inputs; what is missing is
a Gate B-safe command shape, not reproducibility.

Per the task contract, the metadata-only `review_tier` / `validation_record`
update is **not** applied, because only a formal helper `PASS` authorizes it.

Recommended follow-up (maintainer decision): repackage RESULT-0027 as a
physics-lab engine workflow whose recorded command is
`physics-lab run examples/<exoplanet-null-baseline>.yaml`, mirroring the merged
Materials (`TASK-0786`) and Stellar (`TASK-0798`) precedents. That makes the
recorded command Gate B-safe so a later independent identity can run the formal
helper end-to-end and, on a clean `PASS`, apply the metadata-only tier update.

## No-Claim Language

RESULT-0027 remains bounded negative/control memory over the committed
`EXO-0001` PSCompPars true-mass transit-radius slices: nearest-radius null
controls match or beat the frozen CK17-style baseline in the four highlighted
true-mass slices, and minimum-mass slices stay underpowered diagnostics. The
nearest-radius neighbor uses observed radius and is a diagnostic control, not a
prospective or deployable predictor. This replay confirms only that the
committed package reproduces deterministically; it makes no exoplanet
composition, habitability, population, or mass–radius-law claim and does not
strengthen the scientific verdict (`INCONCLUSIVE`).

## Output-Routing Summary

- **Task verdict:** `not_applicable` (replay-validation routing; no new
  scientific verdict produced).
- **Canonical destination:** this review note,
  `docs/reviews/exoplanet-result-0027-gate-b-replay.md`.
- **Review tier:** RESULT-0027 stays at its input tier `AGENT_PUBLISHED`; no
  tiered artifact is created or promoted.
- **Gate A status:** previously passed (`gate_a_report.md`); unchanged.
- **Gate B status:** formal helper **`BLOCKED`** (`unsupported-command`);
  justified deterministic repackage replay **byte-identical, zero drift** across
  all package files and inputs.
- **Claim impact:** none. No claim is created, edited, or promoted.
- **Knowledge impact:** none. No `KNOW-*` entry created or edited.
- **Result artifact impact:** none. `results/EXP-0021/RUN-0001/` is
  byte-unchanged (metrics, verdict, comparisons, no-claim wording untouched).
- **Publication blocker:** RESULT-0027's recorded command is not in the Gate B
  `SAFE_RESULT_COMMANDS` allowlist, so the formal validation path cannot run.
  Clearing it requires a maintainer-approved repackage onto a
  `physics-lab run` workflow command (see follow-up above), then an independent
  formal Gate B replay.

## Verdict

`RESULT0027_GATEB_FORMAL_BLOCKED_UNSUPPORTED_COMMAND_REPACKAGE_REPLAY_BYTE_IDENTICAL`:
the formal Gate B helper is blocked by the packaging-script command shape, while
the deterministic repackage replay reproduces the committed RESULT-0027 package
byte-for-byte from committed inputs under an independent identity. RESULT-0027
remains `AGENT_PUBLISHED` bounded negative/control memory; no metric, verdict,
comparison, hash, wording, claim, or knowledge change was made.
