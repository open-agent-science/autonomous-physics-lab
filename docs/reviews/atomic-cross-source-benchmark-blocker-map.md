# Atomic Cross-Source Benchmark Blocker Map

**Task:** `TASK-0653`
**Campaign:** `atomic-clock-residuals`
**Mode:** planning only (research quality gate)
**Verdict:** `NO_BENCHMARK_TASK_SHOULD_RUN_YET`

## Scope

This note maps the blocker state of the four named Atomic source candidates
(Beloy, Nemitz, Pizzocaro, Lange/PTB) and recommends the next one or two tasks
that could actually unlock the first Atomic cross-source benchmark. It reads
only committed repository evidence and live PR/task status. It fits no
constants drift, adds no rows, fetches no data, creates no result/prediction,
and promotes no claim.

The first intended benchmark is a **narrow Yb/Sr cross-source consistency
check**: the pinned Beloy 2021 rows as `cross_source_reference` bound to a second
value-bearing Yb/Sr source as `cross_source_target`, scored under the
first-benchmark covariance policy. The load-bearing blocker for that benchmark is
that **no second value-bearing Yb/Sr direct row is committed**, so Atomic remains
`PINNED_DATASET`, not `BASELINE_READY`
(`docs/reviews/atomic-baseline-readiness-gate-after-nemitz-loader-holdout.md`).

## Blocker Map

| Candidate | Family | Current state | Load-bearing blocker | Benchmark role |
| --- | --- | --- | --- | --- |
| Beloy 2021 / BACON (`ACR-0001`) | Yb/Sr direct ratio | Pinned; 3 committed sandbox rows; manifest row-roles assigned; source-derived PSD covariance approximation (sensitivity-only) | Single source — needs a second Yb/Sr row to bind a comparison; covariance is approximate, not exact | `cross_source_reference` (ready as the anchor) |
| Nemitz 2016 / RIKEN Yb/Sr | Yb/Sr direct ratio | Source artifact pinned (`arXiv:1601.04582`) with checksum/provenance; no `ACR-0002` row | Version-of-record (arXiv vs Nature) table review, campaign-window lock, row-level uncertainty transcription | Candidate `cross_source_target` (independent of Pizzocaro) |
| Pizzocaro 2020 / INRIM Yb/Sr (VLBI) | Yb/Sr direct ratio | Source artifacts pinned; 10-window per-window diagnostic ledger committed; covariance feasible as `COV_SOURCE_DERIVED_PSD_APPROX`, under-specified for exact | `COV_BLOCKED_SHARED_SYSTEMATICS`: windows share clocks/links/campaign systematics; no frozen aggregation + covariance recipe for a single summary row | Most-developed `cross_source_target` candidate; **active** in PR #982 (`TASK-0666`) |
| Lange et al. 2021 / PTB Yb+ E3/Cs | Yb+ (E3/Cs, E3/E2) — **separate family** | Metadata pinned (`TASK-0652`); license/reuse + artifact-retrieval route undecided (`TASK-0669` READY) | Not a Yb/Sr ratio; license/reuse gate before any artifact commit | **Does not unblock the Yb/Sr benchmark**; breadth fallback for a future Yb+ benchmark |

## Candidate Detail

### Beloy 2021 / BACON — anchor, not the blocker

Beloy is the readiest surface: three committed sandbox-only direct Yb/Sr
frequency-ratio rows with manifest-assigned row roles and a reconstructed
positive-semidefinite source-derived covariance approximation. Per the
first-benchmark covariance policy that approximation is **sensitivity-only**: any
benchmark consuming it must report a diagonal-only comparator and label the
correlated metric approximate. Beloy can serve as `cross_source_reference` today;
it cannot, by itself, produce a cross-source consistency result without a second
Yb/Sr source.

### Nemitz 2016 / RIKEN Yb/Sr — source-ready, row-blocked

The correct Nemitz arXiv artifact is pinned with checksum and provenance, but no
value-bearing row exists. Row curation is blocked on three independent gates:
arXiv-vs-version-of-record table reconciliation (`SOURCE_ARTIFACT_VERSION_DRIFT`
discipline), campaign-window lock, and row-level uncertainty transcription. Nemitz
is a direct Yb/Sr ratio (the same observable as Beloy), so it is the cleanest
conceptual `cross_source_target` — its blocker is row-curation discipline, not
covariance ambiguity. This path is **independent** of the Pizzocaro covariance
work and could proceed in parallel.

### Pizzocaro 2020 / INRIM Yb/Sr — most active, covariance-blocked

Pizzocaro is the most-developed second-source path: source artifacts are pinned,
and a deterministic per-window diagnostic ledger for 10 VLBI campaign windows is
committed (`TASK-0636`). The row-aggregation covariance gate (`TASK-0627`)
preserved `COV_BLOCKED_SHARED_SYSTEMATICS`: the 10 windows share clocks, links,
campaign systematics, and deadtime/drift components, so they cannot be treated as
independent rows, and collapsing them into one summary row needs a frozen
aggregation + covariance recipe that was not yet committed. `TASK-0651` found that
recipe feasible as a `COV_SOURCE_DERIVED_PSD_APPROX` (not an exact committed
matrix). **`TASK-0666` (open PR #982, currently in review) is the live attempt** to
build and test exactly that PSD covariance approximation without aggregating
windows into benchmark rows. Even if it lands, the covariance policy keeps the
result sensitivity-only — a correlated *diagnostic*, not a full-covariance claim.

### Lange/PTB Yb+ E3/Cs — separate family, not a Yb/Sr unblocker

Lange/PTB metadata is pinned, but it is an Yb+ optical-clock comparison
(E3/Cs and E3/E2), a **different source family** from the Yb/Sr ratio. It cannot
serve as the `cross_source_target` for the first Yb/Sr consistency benchmark.
`TASK-0669` (READY) decides its artifact-retrieval and reuse route. That work is
valuable for breadth (a future Yb+ benchmark lane) and can proceed in parallel,
but it must not be presented as unblocking the first Yb/Sr benchmark.

## Shortest Unblock Path

The first Yb/Sr benchmark needs exactly one thing: a defensible second Yb/Sr
surface bound to Beloy. Two independent routes lead there; recommend pursuing the
active one first and keeping the second as a parallel hedge.

1. **Primary — finish and gate the Pizzocaro PSD covariance approximation.**
   `TASK-0666` (PR #982) is already in review. The next task that can move the
   benchmark is a **post-`TASK-0666` baseline-readiness gate rerun** that decides
   whether the landed PSD approximation lets a single Pizzocaro summary row (or a
   per-window consistency surface) bind as a sensitivity-only `cross_source_target`,
   or whether Pizzocaro stays diagnostic-only. This is the campaign's own stated
   sequence ("rerun the baseline-readiness gate only after a second value-bearing
   source row is committed or explicitly waived"). It should not start before
   `TASK-0666` merges.

2. **Secondary / parallel — a Nemitz 2016 row-curation gate.** Independent of the
   Pizzocaro covariance question, a Nemitz row-curation task could clear the
   version-of-record, campaign-window, and uncertainty-transcription gates and
   commit an `ACR-0002` Yb/Sr row. If Pizzocaro stays diagnostic, this becomes the
   primary second source; if Pizzocaro lands, the two provide a stronger
   cross-source picture.

`TASK-0669` (Lange/PTB retrieval route) may proceed in parallel for breadth but is
**not** on the Yb/Sr benchmark critical path.

## No Benchmark Task Should Run Yet

The Yb/Sr cross-source consistency benchmark must **not** run now. Atomic is
`PINNED_DATASET`: only Beloy carries committed rows, Nemitz and Pizzocaro have no
admissible second row, and the campaign already lists running the benchmark before
a `BASELINE_READY` declaration as an explicitly unsafe task. No constants-drift
fit, cross-source metric, prediction, result, or claim is authorized by this map.

## Campaign Page Decision

`docs/campaigns/atomic-clock-residuals.md` is **not** updated. Its current wording
is already conservative and source-first: it names `TASK-0666` as the immediate
path, marks Lange/PTB as a separate Yb+ family rather than a Yb/Sr unblocker, and
explicitly lists the Yb/Sr cross-source benchmark under "Unsafe next tasks" until a
later readiness gate declares `BASELINE_READY`. Nothing in the page points agents
toward an unsafe benchmark, so the optional update is not warranted.

## Limitations

- Uses committed repository evidence plus live PR/task status only; no papers,
  supplements, or external datasets were fetched, and no values were transcribed.
- The Pizzocaro recommendation depends on the outcome of `TASK-0666` (PR #982),
  which is still in review; if it fails or is revised, the Nemitz route becomes
  primary.
- This map does not assign canonical task ids, create the recommended follow-up
  tasks, or change any task status other than this task's own.
- It does not re-evaluate the Beloy covariance approximation or re-derive any
  covariance state.

## Output Routing Summary

- **Task verdict:** `not_applicable` for a scientific claim; benchmark-readiness
  classification is `NO_BENCHMARK_TASK_SHOULD_RUN_YET`.
- **Canonical destination:** this review note,
  `docs/reviews/atomic-cross-source-benchmark-blocker-map.md`.
- **Review tier:** `none`; no `RESULT-*` or `PRED-*` artifact is proposed.
- **Gate A status:** not attempted (no rows or metrics produced).
- **Gate B status:** not applicable.
- **Claim impact:** no claim change; no constants-drift, consistency, or anomaly
  statement is made.
- **Knowledge impact:** no knowledge change.
- **Result artifact impact:** no `results/` artifact created or modified.
- **Publication blocker:** the first Yb/Sr cross-source benchmark stays blocked on
  a second admissible Yb/Sr row — Pizzocaro covariance aggregation (active in
  `TASK-0666`/PR #982) or Nemitz row curation (version-of-record, campaign-window,
  uncertainty gates). Lange/PTB is a separate Yb+ family and does not unblock it.
