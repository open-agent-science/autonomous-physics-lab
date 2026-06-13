# Public-Launch Git-History Source-Artifact Scan And Cleanup Runbook

**Task:** `TASK-0732`
**Type:** repository hardening / release readiness
**Mode:** scan + runbook only — **no `git filter-repo`, no force-push, no ref deletion, no history rewrite is performed by this task**
**Scanned ref:** `origin/main` @ `a92f2f4e` (2026-06-13)
**Verdict:** `REMOVE_TWO_ARXIV_PDFS_AT_FREEZE_TIME; ALL_OTHER_LARGE_ARTIFACTS_KEPT`

## Scope

`TASK-0731` removed two non-redistributable arXiv preprint PDFs from the working
tree and added guards against reintroducing them; `TASK-0733` declared the
redistribution basis of every committed third-party dataset and added a CI guard.
Public launch still requires a Phase B history cleanup because removed-from-HEAD
blobs remain reachable in history. This document records the full-history scan,
the candidate removal list with evidence, and the freeze-time rewrite runbook.
Execution is a separate maintainer-approved, freeze-time step.

This is a **redistribution-hygiene** cleanup (keep the public clone free of
non-redistributable publisher artifacts), not a secret/credential leak; the bar
is "clean clonable history", not forensic eradication of server-side refs.

## Scan Commands (reproducible)

```bash
# A. Largest blobs reachable from origin/main
git rev-list --objects origin/main \
  | git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' \
  | awk '$1=="blob" && $2>200000 {print $2, $3}' | sort -rn | head -25

# B. Every path ever ADDED on origin/main with a risky binary/document/archive ext
git log origin/main --diff-filter=A --name-only --pretty=format: \
  | grep -iE '\.(pdf|zip|tar|gz|tgz|7z|rar|xlsx|xls|docx|doc|pptx|ppt|fits|fit|h5|hdf5|parquet|nc|db|sqlite)$' \
  | sort -u

# C. Add/remove history of each candidate path
git log origin/main --oneline --diff-filter=AD --name-status -- <path>

# D. Confirm a path is NOT reachable from origin/main
git log origin/main --oneline -- <path>

# E. Currently tracked PDFs at HEAD (expect none)
git ls-tree -r --name-only origin/main | grep -iE '\.pdf$'
```

## Inventory Results (origin/main @ a92f2f4e)

- **Risky-extension sweep (B):** the only files ever added with a
  PDF/archive/document/spreadsheet/database extension are the two arXiv PDFs
  below. No hidden archives, office documents, or databases exist in history.
- **Largest blobs (A):** all other large blobs are either APL-authored
  (`docs/figures/*.png`, `agent_runs/*/metrics.json`) or redistributable
  third-party data declared in `data/DATA_LICENSES.yaml` (NASA Exoplanet Archive
  snapshots/CSVs, AME2020 YAML, Pizzocaro/Zenodo CSV).
- **DEBCat (D):** the full normalized DEBCat dataset
  (`debcat_component_rows.yaml` / `debcat_holdout_manifest.yaml`) is **not**
  reachable from `origin/main` — the `TASK-0708` branch was repacked and
  squash-merged, so the blob never entered main history.
- **HEAD (E):** no `.pdf` is tracked at `origin/main` HEAD.

## Candidate Paths To Remove (and evidence)

Listed in `docs/reviews/public-launch-history-paths-to-remove.candidate.txt`.

| Path | Size | Added | Removed-from-HEAD | Why remove |
| --- | --- | --- | --- | --- |
| `data/atomic_clocks/source_artifacts/2016-nemitz-riken/arxiv-1601.04582.pdf` | 1.6 MB | `b91ff161` (TASK-0452) | `27088f32` (TASK-0731 / #1052) | arXiv.org perpetual non-exclusive licence grants distribution to arXiv only, not third parties; not Creative Commons → not redistributable in a public repo. |
| `data/atomic_clocks/source_artifacts/2021-beloy-bacon/arxiv-2005.14694.pdf` | 10.6 MB | `cb16b241` (TASK-0371 / #556) | `27088f32` (TASK-0731 / #1052) | Same arXiv non-exclusive licence; not redistributable. |

Both blobs are still reachable in history and must be purged before public
launch. The numeric facts, checksums, locators, and the fetch helper that
replace them are already committed (`TASK-0731`), so no scientific content is
lost by purging the PDFs.

## What Is KEPT, And Why (evidence it does NOT need removal)

| Artifact(s) in history | Basis to keep |
| --- | --- |
| NASA Exoplanet Archive snapshots + raw CSVs | Open/unrestricted access + acknowledgement (declared in `data/DATA_LICENSES.yaml`). |
| AME2020 nuclear-mass YAML | CC BY 3.0 (Chinese Physics C OA / SCOAP3), attribution declared. |
| Materials Project, Pizzocaro/Zenodo data | CC BY 4.0, attribution declared. |
| DEBCat sample + extractor | Sample-only / extractor; full set not committed (`TASK-0708`). |
| `docs/figures/*.png`, `agent_runs/*/metrics.json`, all other blobs | APL-authored outputs. |

All third-party keepers are enforced by
`tests/test_data_redistribution_declarations.py` (`TASK-0733`).

## Freeze-Time Rewrite Runbook (execute only under a maintainer-declared freeze)

### Prerequisites
1. Maintainer declares a **merge freeze**; resolve or accept rebasing of any
   open PRs first.
2. Create a full **backup mirror** for rollback:
   `git clone --mirror <origin> apl-prelaunch-backup.git`.
3. Re-confirm the candidate list still matches a fresh scan (commands above);
   re-run if `main` advanced.

### Rewrite
```bash
# from a fresh mirror/working clone, with git-filter-repo installed:
git filter-repo --invert-paths \
  --paths-from-file docs/reviews/public-launch-history-paths-to-remove.candidate.txt
# (filter-repo ignores blank lines and # comments in the paths file)
```

### Verification (all must pass before force-push)
```bash
git log --all --oneline -- data/atomic_clocks/source_artifacts/2016-nemitz-riken/arxiv-1601.04582.pdf   # empty
git log --all --oneline -- data/atomic_clocks/source_artifacts/2021-beloy-bacon/arxiv-2005.14694.pdf    # empty
git rev-list --objects --all \
  | git cat-file --batch-check='%(objecttype) %(objectsize) %(rest)' \
  | awk '$1=="blob"' | grep -iE '\.pdf$'                                                                 # empty
python3 -m pytest tests/test_source_artifact_publication_guard.py tests/test_data_redistribution_declarations.py
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

### Publish + collaborator recovery
1. Force-push the rewritten `main` (maintainer action; the only sanctioned
   force-push to `main`, under the declared freeze).
2. The PDFs were added early (`TASK-0371` / `TASK-0452`), so the rewrite changes
   most commit hashes. **Every collaborator must re-clone** (preferred) or hard
   reset: `git fetch origin && git reset --hard origin/main`.
3. Any surviving feature branch must be rebased onto the rewritten `main` before
   pushing; **do not push an un-rebased old branch** — it would reintroduce the
   purged blobs.

### Recontamination risks
- Old local clones and any forks still contain the blobs; pushing from them
  reintroduces them. Mitigate with the re-clone instruction above and by
  deleting stale branches.
- GitHub retains pre-rewrite commits in `refs/pull/*` and force-push events
  server-side until garbage collection; these are not part of a fresh clone, so
  a public clone is clean. (No credential/secret is involved, so server-side GC
  is sufficient; escalate to GitHub support only if a stricter purge is later
  required.)

### Rollback / fallback
- **Rollback:** if the rewrite or force-push is wrong, restore from
  `apl-prelaunch-backup.git` and force-push it back.
- **Fallback (last resort):** if history rewrite is judged too risky, publish a
  fresh public repository seeded from a squashed snapshot of `main`. This loses
  commit history and the task-trail (which APL values via `git log`), so prefer
  the targeted rewrite above.

## Output-Routing Summary (`docs/result-promotion-protocol.md`)

- **Task verdict:** `not_applicable` (planning/scan gate); decision
  `REMOVE_TWO_ARXIV_PDFS_AT_FREEZE_TIME`.
- **Canonical destination:** this review note + the candidate paths file. No data
  rows, results, predictions, claims, or knowledge change. **No history was
  rewritten.**
- **Review tier:** `none`. **Gate A / Gate B:** not applicable.
- **Limitations / blockers:** the destructive rewrite + force-push remain a
  separate maintainer-approved, freeze-time step. Recommended follow-up: a
  dedicated freeze-time execution task created only when the maintainer declares
  the public-launch freeze.
