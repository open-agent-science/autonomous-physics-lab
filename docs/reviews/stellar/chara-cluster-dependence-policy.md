# TASK-1041: CHARA cluster-dependence policy

## Scope

This review freezes a value-blind environment-grouping policy for the thirteen
TASK-1025 CHARA candidates before any CHARA measurement, row assignment,
residual, or model output is inspected. The machine-readable contract is
[chara_cluster_dependence_ledger.yaml](../../../data/textbook_formula_audit/stellar_ml/chara_cluster_dependence_ledger.yaml).

No CHARA value surface was created or edited. The TASK-1025 alias ledger and
the frozen DEBCat component surface were not modified.

## Frozen inputs and sources

- TASK-1025 CHARA identity ledger: 13 systems, SHA-256
  `9ba15da828381841914b7e848f2d9e9235aa7237d6ecf513a795dfa6b2ec8613`.
- DEBCat development surface: 373 `system_id` values, SHA-256
  `7e8fe4a2359f53f7fd7c80cdba5f56dc024fa45f985879d3faecb8bc8398db08`.
  Only `system_id` fields were inspected.
- Candidate memberships use the checksum-pinned SIMBAD TAP alias and
  hierarchy responses already recorded by TASK-1025. The six-system Hyades
  source is arXiv `2406.01674`; the seventh member, HD 284163, is pinned by
  DOI `10.1093/mnras/stad3803` and arXiv `2312.05301`.
- The DEBCat overlap check used fresh identifier-only SIMBAD TAP responses on
  2026-07-13. `V818 Tau` resolves to `HD 27130`, whose hierarchy has direct
  parents `Cl Melotte 25` and `NAME Hyades Moving Group`. Response digests are
  recorded in the ledger; raw responses are not committed.

SIMBAD content remains subject to ODbL 1.0 and is used with attribution.

## Dependence audit

Seven candidates share the single `melotte-25` environment group:
HD 27483, HD 283882, HD 26874, HD 27149, HD 30676, HD 28545, and HD 284163.
They are distinct physical systems, but not seven independent draws of cluster
environment.

The other six candidates have no cluster/group parent in the pinned TASK-1025
hierarchy responses. Each is therefore a **provisional** singleton group. This
is an operational pre-value classification, not a claim that the objects are
scientifically proven field-independent.

The frozen DEBCat development list contains `V818_Tau`. Its stable alias
`HD 27130` is a direct Melotte 25/Hyades member in the pinned SIMBAD hierarchy.
That one confirmed overlap is sufficient to disqualify the whole
`melotte-25` CHARA group from acting as an independent holdout against this
DEBCat development surface.

## Frozen split rule

1. One physical cluster or explicitly linked environment is one atomic group.
2. Every member of a group must remain in the same partition.
3. If DEBCat contains any member of a group, no CHARA member of that group may
   be labelled an independent holdout.
4. Components and unresolved hierarchy members inherit their system group and
   never increase the independent-group count.
5. Unlinked candidates remain provisional singletons and must be regrouped if
   later identifier-level evidence establishes a shared environment.

Before values, the minimum acceptable independent holdout size is frozen at
**five effective groups**. The prospective set has seven groups before the
DEBCat overlap; blocking Melotte 25 leaves six provisional eligible groups.
The threshold therefore passes now. It must not be lowered after values or
metrics are observed; any later regrouping below five returns
`HOLD_UNDERPOWERED`.

## Verdict

**`DEPENDENCE_POLICY_READY`.** The cluster leakage control, DEBCat environment
overlap, partition rule, and minimum effective-group gate are all frozen before
value access. This verdict authorizes only a future grouped holdout design. It
does not assert a stellar-population result and does not authorize row curation,
an actual split, fitting, scoring, or RESULT/PRED/CLAIM/KNOW promotion.

## Limitations and routing

- Six singleton groups are provisional because absence of a pinned hierarchy
  link is not proof of environmental independence.
- The audit proves at least one DEBCat Melotte 25 overlap; it does not publish
  an astrophysical census of every cluster represented by DEBCat.
- Actual row-level grouping and split assignment remain a separate task after
  source and row review.
- Gate A and Gate B are not attempted because no scientific result or replay
  artifact exists.

Output route: prospective holdout policy only; zero measurement rows, actual
splits, metrics, fits, results, predictions, claims, or knowledge mutations.
