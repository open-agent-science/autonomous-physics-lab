# Science Wave — 2026-07-08 (artifact-weighted top-up)

- Seeded by: the Scientific Campaign Director lane after the external
  trust-infrastructure sequence closed (anchor + vitrine + software DOI,
  2026-07-07).
- Queue-throttle compliance: REVIEW_READY = 7 (< 8) at seed time; READY
  goes 4 -> 12, inside the 12-16 policy band. Evidence:
  `grep -c '^status: REVIEW_READY' tasks/TASK-*.yaml` = 7 and
  `grep -c '^status: READY' tasks/TASK-*.yaml` = 12 on this branch.
- Decision packet: `decisions/DEC-20260708-science-wave-topup.yaml`
  (queue_top_up, class 1, dry-run; quorum + devil's advocate recorded).
- The ThermoML Option A signature is deliberately NOT in this PR: the
  devil's advocate blocked bundling a Class 2 data-rights decision inside
  a composite wave diff, so the tick + its decision stub travel in a
  dedicated one-surface maintainer PR. TASK-0955 stays gated on that
  signature (its executor stops if the box is unticked).
- Non-claims: seeding only; no RESULT/PRED/CLAIM/KNOW change in this PR.

## Composition (artifact quota: 4 of 8 produce dataset/result artifacts)

| Task | Lane | Output class | Priority |
| --- | --- | --- | --- |
| TASK-0955 | ThermoML 80-row bounded public extraction (Option A) | dataset artifact | high |
| TASK-0956 | CLAIM-0005 evidence refresh (RESULT-0020 independent Gate B) | claim layer (no status change) | high |
| TASK-0957 | ZnSe contract transfer -> canonical Gate A RESULT (honest FAIL) | result artifact | high |
| TASK-0958 | First common-scheme baseline metric on the pinned AHS table | benchmark artifact | medium |
| TASK-0959 | RESULT-0027 workflow repackage + fair-null transparency + Gate B | result packaging + validation | high |
| TASK-0960 | Gate A safe-command packaging check | tooling guard | high |
| TASK-0961 | Ledger hygiene batch (hypotheses, EXP-0019, 4 knowledge entries) | ledger accounting | medium |
| TASK-0962 | Collaborator access hygiene decision packet | maintainer packet | low |

Carried READY (not new): TASK-0305 (scoring lane), TASK-0947/0949
(reserved akutenyov), TASK-0951 (in progress).

## Standing-directive traceability

- Artifact quota per the wave-composition rule (>= half produce
  RESULT/PRED/dataset artifacts): satisfied 4/8 + one claim-layer task.
- queue-throttle: satisfied (see above).
- campaign no-go respected: no atomic tasks (KEEP_MONITOR_ONLY terminal),
  no muon tasks (parked), no interval-bearing nuclear freeze (R2), no broad
  formula searches.
- Identity routing (R4): TASK-0959 explicitly excludes akutenyov
  (publisher); TASK-0947/0949 remain reserved for him.
