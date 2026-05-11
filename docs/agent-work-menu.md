# Agent Work Menu

This is the support and short-session menu.

For the default Agent First research path, start with:

```bash
python3 scripts/apl_mission.py
```

Use this menu when you intentionally want support work, microtasks, docs,
packaging, or a narrow queue item that matches your available time budget.

All options here are safe, reviewable, and scoped to one session.
None require new engine code or large-scope implementation.

Follow `docs/agent-task-protocol.md` for branch, commit, PR, and validation rules.

---

## 30 minutes

### Challenge-set entry (Dimensional Analysis)

Add one entry to `knowledge/challenge_sets/dimensional_analysis_challenge_set.yaml`.

- VALID entry: pick a well-known SI formula, show the dimension balance explicitly.
- INVALID entry: invent or find a formula with a clear dimension mismatch.
- SUSPICIOUS entry: a formula that is dimensionally balanced but physically questionable.

Queue: `tasks/microtasks/dimensional-analysis-validator.yaml` → DAV-001 / DAV-002 / DAV-003  
Effort: 10–20 min · Risk: low · autonomy: agent_can_complete

### Narrow Koide Q computation (Particle Mass)

Compute one Q value for a specified charged-lepton or quark triplet.  
Report the triplet, Q value, uncertainty, and interpretation ceiling.

Queue: `tasks/microtasks/particle-mass-relations.yaml` → PMR-002  
Effort: 10–20 min · Risk: low · autonomy: agent_can_complete

---

## 1 hour

### Small DA microtask batch (3–5 entries)

Complete a tightly related batch of dimensional-analysis challenge entries.  
Stick to one type per batch (all VALID, all INVALID, or a mixed but coherent set).  
Add a batch summary note under `docs/notes/`.

Queue: `tasks/microtasks/dimensional-analysis-validator.yaml`  
Effort: 30–50 min · Risk: low · Batch size: 3–5 items

### Pendulum failure-mode note

Pick one candidate family from the gauntlet leaderboard.  
Classify its failure mode at large amplitude or near the separatrix.  
Write a narrow note in `docs/notes/`.

Queue: `tasks/microtasks/pendulum-formula-falsification.yaml` → PFF-002 / PFF-003  
Effort: 20–40 min · Risk: low · autonomy: agent_can_complete

### Dataset audit (Particle Mass)

Audit one entry in `knowledge/datasets/` against its stated source.  
Record mass value, mass type, units, and any ambiguity as `REVIEW_NEEDED`.

Queue: `tasks/microtasks/particle-mass-relations.yaml` → PMR-001  
Effort: 15–30 min · Risk: medium · autonomy: agent_can_complete

---

## 2 hours

### Canonical READY task (low difficulty)

Open [`tasks/ACTIVE.md`](../tasks/ACTIVE.md) and pick any task where:
- `status: READY`
- `difficulty: low`

Good filters to apply: `priority: high` first, then `priority: medium`.

Full lifecycle: create branch → implement → validate → open PR → wait for review.  
Do not merge your own PR.

### Formula-family proposal (Pendulum)

Propose one new even candidate family using `x = sin^2(theta/2)`.  
Justify why it is even in theta and state at least one expected failure regime.

Queue: `tasks/microtasks/pendulum-formula-falsification.yaml` → PFF-001  
Effort: 15–30 min + note writing

### Koide triplet scope probe (Particle Mass)

Pick one non-charged-lepton triplet (e.g. up/down/strange quarks).  
Compute Q, compare to charged-lepton baseline, and document why the result is
narrowly scoped with `REVIEW_NEEDED` if any interpretation is uncertain.

Queue: `tasks/microtasks/particle-mass-relations.yaml` → PMR-003 / PMR-004

---

## Safety Rules (all sessions)

- No claim promotion without explicit maintainer review.
- No discovery framing ("we found", "this proves").
- No engine implementation hidden inside a short-session suggestion.
- Mark uncertain outputs as `REVIEW_NEEDED`.
- State limitations explicitly in every output.
- Keep PRs to one campaign per session.

---

## Navigation

- [tasks/ACTIVE.md](../tasks/ACTIVE.md) — canonical task board
- [tasks/microtasks/README.md](../tasks/microtasks/README.md) — all campaign queues
- [docs/agent-scientific-work-mode.md](./agent-scientific-work-mode.md) — spare-budget mode details
- [docs/scientific-micro-task-protocol.md](./scientific-micro-task-protocol.md) — queue and batching rules
- [docs/agent-task-protocol.md](./agent-task-protocol.md) — branch, commit, PR protocol
- [docs/mission-control.md](./mission-control.md) — project overview and campaign map
