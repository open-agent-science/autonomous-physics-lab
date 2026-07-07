# Decision Autonomy — Dry-Run Plan and Retro-Calibration (TASK-0952)

- Policy under test: `docs/decision-autonomy-policy.md` +
  `policy/decision-autonomy.yaml` (v0, `can_apply_now: false` everywhere).
- Duration: 1-2 weeks from the policy merge.
- Non-claims: dry-run packets change nothing; every actual change still goes
  through the normal task/PR/maintainer gates.

## Dry-run protocol

1. For every routing decision that arises, the acting agent files a
   `decisions/DEC-*.yaml` packet (template committed, or `python3 scripts/apl_decision.py propose`): classification,
   quorum votes from separate sessions, formal devil's-advocate block,
   `decision_record.status: dry_run_only`.
2. Packets are checked with `python3 scripts/apl_decision.py validate decisions/DEC-*.yaml` (unknown decision types fail — default-deny). Nothing auto-applies — including Class 0; `apply` refuses in v0. The maintainer decides as
   before; the packet records what the policy *would* have done
   (`would_apply` note in `recommended_action` basis when relevant).
3. The maintainer reads a periodic summary (director cycle), not individual
   pings; the expedite path applies to anything blocking a high-priority
   lane.

## Success criteria to enable Phase 2 (auto-apply Class 0)

- `wrong_classification_count = 0` on the retro set below AND on all live
  dry-run packets (a wrong classification is one the maintainer relabels).
- Every Class 2 situation in the period was correctly kept maintainer-only.
- At least 6 live packets filed, with quorum + devil's-advocate blocks
  complete.
- Veto/disagreement rate on would-apply Class 0/1 recommendations low
  enough that the maintainer signs the Phase 2 matrix flip (his call).

## Retro-calibration

The fixed calibration set (the eight Decision Day #2 decisions) lives in
`docs/reviews/decision-autonomy-retrotest-20260706.md` (verdict:
RETROTEST_PASS — 6 of 8 quorum-routable, 2 of 2 human-mandatory kept
maintainer-only) and is enforced by
`tests/test_decision_autonomy_policy.py`.

## Enforcement notes

- `policy/`, this policy doc, and `.github/CODEOWNERS` are Class 2 surfaces
  (`autonomy_policy_change`); CODEOWNERS assigns them to the maintainer. To
  make GitHub enforce it, enable "require review from Code Owners" in branch
  protection (maintainer toggle).
- Unknown decision types are default-deny (treated as class_2) — an agent
  cannot invent a permissive category.
