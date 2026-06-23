# RESULT-0019 Exact-Reference Maintainer Review Packet

- Task: `TASK-0813`
- Result: `RESULT-0019` (`results/EXP-0013/RUN-0001/result.yaml`)
- Campaign: Textbook Formula Audit
- Current review tier: `AGENT_VALIDATED`
- Result verdict: `VALID_IN_RANGE`
- Requested decision: approve, defer, or restrict public wording
- Artifact changes requested by this packet: none

## Executive Recommendation

Approve the safe wording in this packet for public reuse as a description of a
deterministic software/convention check. Keep `RESULT-0019` unchanged in this
task. In particular, do not infer an empirical result, create a claim, or create
knowledge from this review packet.

No campaign-page or dashboard change is recommended. The existing Textbook
Formula Audit campaign page and Public Science Dashboard already state that
`RESULT-0019` is a Gate-B-validated exact-reference software/convention result,
not an empirical-law validation. Adding another capsule there would duplicate
the current boundary rather than correct stale wording.

## Scope

`RESULT-0019` records a synthetic Stefan-Boltzmann exact-reference fixture for
`EXP-0013` / `HYP-0013`. The fixture checks that the committed APL
implementation:

- applies the declared SI units and frozen CODATA 2022 constant convention;
- reproduces values generated from the declared reference relation;
- preserves the expected `T^4`, `R^2`, and monotonic behavior;
- rejects the declared wrong-temperature-exponent and wrong-area controls; and
- can be replayed deterministically through the repository command path.

The result is a quality-floor check for software, fixture metadata, units, and
conventions. It is not an observation of a physical emitter and is not an
independent test of the physical law used to construct the expected values.

## Exact-Reference Semantics

Here, "exact reference" means that expected fixture values are generated from
the same frozen mathematical relation and constant convention that the
implementation is expected to reproduce. Agreement therefore answers:

> Does the software implement the declared arithmetic, units, scaling, and
> convention consistently on the synthetic fixture?

It does not answer:

> Does independent laboratory or astronomical evidence support the physical
> law?

The zero relative error is meaningful as an implementation regression result,
but not as empirical accuracy. Because the expected rows are synthetic and
formula-derived, they carry no measurement uncertainty, source-calibration
uncertainty, emitter non-ideality, or model-discrepancy test.

## Command And Code Path

The RESULT records this canonical replay command:

```text
physics-lab run examples/textbook_stefan_boltzmann_exact_reference.yaml
```

The equivalent module entrypoint is:

```text
python3 -m physics_lab.cli run examples/textbook_stefan_boltzmann_exact_reference.yaml
```

The command routes through:

1. `examples/textbook_stefan_boltzmann_exact_reference.yaml`;
2. the pinned `EXP-0013`, `HYP-0013`, and fixture inputs copied under
   `results/EXP-0013/RUN-0001/inputs/`;
3. `physics_lab/workflows/textbook_exact_reference.py`; and
4. the deterministic Stefan-Boltzmann fixture engine and result writer.

Gate B used:

```text
python3 scripts/apl_validate_agent_published_result.py \
  results/EXP-0013/RUN-0001/result.yaml \
  --output-dir <temporary-gate-b-output-dir> \
  --validator-contributor-id roman \
  --validator-github-username gladunrv \
  --validator-agent-tool Codex \
  --validator-model "GPT-5 Codex" \
  --json
```

That helper replayed the RESULT's recorded command, compared the regenerated
numeric metrics with the published artifact, and did not rewrite the result
metrics or verdict.

## Gate Status

### Gate A: PASS

`TASK-0634` published the scoped software result after the result-publication
check passed. Its review records all nine Gate A checks as satisfied:

- deterministic run;
- populated verification block;
- recorded input hashes;
- explicit limitations;
- pinned engine version and git commit;
- schema validation;
- no protected-result rewrite;
- no forbidden overclaim wording; and
- valid provenance for the synthetic fixture inputs.

The recorded run contains 16 rows: 8 reference rows and 8 holdout rows. Maximum
relative error is `0.0` under a declared `1e-12` tolerance. Both declared
negative controls were rejected.

### Gate B: PASS With A Limitation

`TASK-0635` replayed 13 numeric metrics with maximum absolute drift `0.0` at
`1e-09` tolerance. The verdict remained `VALID_IN_RANGE`, and no contested
report was produced.

The publication and replay used different agent tools (`Claude Code` and
`Codex`) but the same contributor id (`roman`). This satisfies the recorded
maintainer-directed Gate B route, while remaining weaker than external
replication or an independent-contributor empirical audit.

### Gate C: Not Performed By This Task

This packet does not change `review_tier`, result metrics, claim status,
knowledge, or golden-result pinning. Any move to `MAINTAINER_REVIEWED` remains a
separate maintainer decision and artifact edit under Gate C.

## Maintainer Decision Options

### Option 1: Leave At `AGENT_VALIDATED`

Keep the result and current public pages unchanged. Cite it only with the
`AGENT_VALIDATED` qualifier and the software/convention boundary.

Use this option if the current tier already provides enough visibility for an
internal quality-floor fixture.

### Option 2: Approve Safe Public Wording

Approve the wording below for README text, public status summaries, issue
comments, or campaign discussion. This approval does not itself modify the
RESULT tier and does not authorize empirical interpretation.

This is the recommended option because the wording is useful, reproducible,
and bounded by the evidence. The existing campaign pages already carry this
meaning, so approval requires no page edit in this task.

If the maintainer also wants to change `RESULT-0019` to
`MAINTAINER_REVIEWED`, perform that Gate C artifact change separately and
review the scope wording attached to the RESULT.

### Option 3: Keep As Internal Quality-Floor Evidence

Do not use the result in general public summaries. Retain it only as a
regression fixture and prerequisite for later empirical lanes.

Use this option if same-contributor Gate B validation is considered
insufficient for public citation, even with the software-only qualifier.

## Safe Public Wording

Recommended short wording:

> APL's synthetic Stefan-Boltzmann exact-reference fixture reproduced all
> declared software/convention checks with zero numeric drift in an independent
> cross-tool replay. This validates the committed implementation, units, and
> frozen constant convention only; it is not an empirical test of blackbody
> physics.

Recommended compact wording:

> `RESULT-0019` is an `AGENT_VALIDATED` deterministic software/convention
> fixture. It is not empirical validation of Stefan-Boltzmann, Wien
> displacement, blackbody radiation, or a universal physical law.

Required qualifier when only the metric is cited:

> Zero relative error refers to synthetic exact-reference arithmetic under the
> declared convention, not agreement with laboratory or astronomical data.

## Wording That Is Not Supported

Do not state or imply that:

- APL validated or proved the Stefan-Boltzmann law;
- the result confirms blackbody radiation against observations;
- the result establishes a universal physical law;
- the result validates Wien displacement or FIRAS data;
- zero fixture error is a physical measurement accuracy;
- Gate B is external replication; or
- the result supports a promoted scientific claim or knowledge entry.

## Limitations

- All rows are synthetic and derived from the declared reference relation.
- No laboratory, stellar, FIRAS, or other empirical blackbody data were used.
- The fixture has no measurement-uncertainty model.
- The frozen constant and unit convention are tested for consistency, not
  independently estimated.
- Gate B was cross-tool but used the same contributor id as publication.
- Passing the fixture cannot expose model inadequacy shared by both the
  reference generator and implementation.
- `RESULT-0019` is not pinned in `results/golden-results.yaml`.
- The packet runs no new metric and does not assess the separate empirical
  Wien/FIRAS source lane.

## No-Claim Statement

This task creates no `CLAIM-*`, changes no claim status, creates no `KNOW-*`,
and requests no interpretation promotion. `review_metadata.yaml` records
`claim_id: null`, `knowledge_id: null`, and `proposed_claim_status: null`.
`RESULT-0019` remains evidence about deterministic repository behavior within
its synthetic fixture scope.

## Output Routing

- Task verdict: `not_applicable` (maintainer decision packet; no new run).
- Canonical destination:
  `docs/reviews/result-0019-exact-reference-maintainer-review-packet.md`.
- Existing result destination:
  `results/EXP-0013/RUN-0001/result.yaml` (read-only in this task).
- Review tier: `AGENT_VALIDATED`, unchanged.
- Gate A: `PASS` under `TASK-0634`.
- Gate B: `PASS` under `TASK-0635`, with same-contributor limitation.
- Gate C: not attempted; maintainer-only.
- Claim impact: none.
- Knowledge impact: none.
- Result artifact impact: none.
- Campaign/public-page impact: no change recommended; existing wording is
  sufficient.
- Publication blocker: empirical or universal-law wording remains blocked
  because no empirical dataset was tested; external-replication wording is
  blocked because Gate B was not external replication.

## Maintainer Checklist

- [ ] Confirm the software/convention scope is accurate.
- [ ] Choose Option 1, 2, or 3.
- [ ] If choosing Option 2, approve the safe wording without empirical
      expansion.
- [ ] Decide separately whether a Gate C `review_tier` change is warranted.
- [ ] Keep CLAIM, KNOW, golden-result, and empirical Wien/FIRAS actions outside
      this task.
