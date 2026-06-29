# ThermoML Tb Corpus-Expansion Preflight

**Task:** `TASK-0895`
**Campaign:** `thermophysical-property-residuals`
**Verdict:** `NEEDS_MAINTAINER_SOURCE_DECISION`
**Review date:** 2026-06-29

## Scope

This value-free preflight defines the source, rights, identity, row-class,
duplicate, family, and size contract for a possible expansion of the committed
40-row ThermoML normal-boiling-temperature audit fixture.

It uses only committed manifests, metadata, code, and review artifacts. It does
not fetch or parse the archive, inspect uncommitted values, add rows, vendor
source bytes, rerun `RESULT-0026`, or authorize another thermophysical
property.

## Current Readiness

The repository already has a strong local-analysis route:

| Surface | Current state |
| --- | --- |
| Product | NIST TRC ThermoML Archive |
| DOI | `10.18434/mds2-2422` |
| Product version | `1.2.6`, archive dated `2020-09-30` |
| Archive filename | `ThermoML.v2020-09-30.tgz` |
| Archive SHA-256 | `231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2` |
| Local verification | completed by `TASK-0851`; checksum matched |
| Raw-byte redistribution | forbidden by current policy |
| Local analysis | allowed |
| Derived-row publication | conditional, bounded factual extract only |
| Existing public fixture | 40 rows, 5 rows in each of 8 families |

The source route and parser are therefore technically ready for a bounded local
expansion. Publication of a larger row extract is not yet authorized because
the manifest requires review for any substantial extraction and does not
define a larger row-count ceiling.

## Expansion Decision

Decision: `NEEDS_MAINTAINER_SOURCE_DECISION`.

The repository can define a deterministic candidate contract, but it cannot
decide that an 80-row factual extract is acceptable under the current rights
posture. The maintainer must choose one of two routes before row curation:

1. **Bounded public extract:** approve the candidate 80-row ceiling below and
   record that this size remains a bounded factual extract with attribution.
2. **Local-only expansion:** allow local parsing and analysis while committing
   no new value-bearing rows; only code, metadata, hashes, counts, and blocker
   memory may be published.

No larger or open-ended normalized corpus is proposed.

## Frozen Candidate Contract

### Source And Snapshot

- Use only `ThermoML.v2020-09-30.tgz`, product version `1.2.6`.
- Verify both size `189433115` bytes and the committed SHA-256 before parsing.
- Do not silently move to a newer PDR release. A changed filename, size, hash,
  schema, or coverage year requires a new source-version review.
- Archive acquisition is a maintainer-run, one-time local action. Agent task
  PRs must not perform a live fetch.
- Do not commit archive bytes, extracted archive trees, or a normalized mirror.

### Property Boundary

Admit only:

- `Normal boiling temperature, K`;
- experimental pure-component observations;
- explicit Kelvin values with recoverable source DOI and uncertainty metadata.

Exclude:

- `Tc` and every other property;
- vapor pressure, heat capacity, critical properties, phase equilibria, and
  multi-property records;
- estimates, correlations, calculated values, and review-only values unless a
  separate row class and task explicitly admit them.

`Tc` remains prohibited because the Joback `Tc` path depends on `Tb` and
would create upstream-property leakage in this campaign.

### Identity Resolution

Every candidate compound must satisfy all of these checks:

1. exactly one ThermoML component;
2. standard InChI and standard InChIKey present;
3. structure parses deterministically under the pinned RDKit version;
4. one molecular fragment and formal charge zero;
5. no salts, ionic liquids, mixtures, coordination compounds, or ambiguous
   multi-component systems;
6. every atom and Joback group is covered by the frozen implementation;
7. InChIKey is the primary identity and source DOI/member remain attached.

Common names and formulas are descriptive metadata, not identity keys.

### Row Classes

The future extraction must assign one of these non-overlapping classes:

| Row class | Rule | Public-fixture status |
| --- | --- | --- |
| `experimental_tb_representative` | one selected source observation for an admitted pure compound | eligible after rights approval |
| `experimental_tb_conflict_flagged` | multiple observations span more than the frozen conflict threshold | excluded from scoring by default |
| `missing_uncertainty` | no selected observation has usable uncertainty semantics | excluded from uncertainty-aware benchmark |
| `identity_blocked` | standard identity absent, ambiguous, charged, or multi-fragment | excluded |
| `joback_out_of_coverage` | deterministic group decomposition fails | excluded |
| `non_tb_or_nonexperimental` | wrong property or nonexperimental value class | excluded |

Rows must not be relabelled as critically evaluated NIST recommendations. The
archive is an experimental compilation and NIST does not critically evaluate
the deposited values.

### Duplicate And Conflict Policy

- Group all observations by standard InChIKey.
- Select one representative by smallest reported expanded uncertainty.
- Break an uncertainty tie by source DOI, then the source-reported value only
  as a deterministic final ordering rule.
- Do not average repeated observations.
- Record observation count, selected DOI/member, uncertainty availability, and
  full observed span.
- Preserve the existing conflict threshold of `span > 1 K`.
- Exclude conflict-flagged compounds from the scored expansion unless a
  separate predeclared sensitivity task admits them.
- Never choose a representative by Joback error or any model residual.

### Family Taxonomy

Keep the committed highest-priority functional-family taxonomy and its order.
The first expansion must remain limited to the same eight families:

1. acids;
2. esters/lactones;
3. ketones;
4. alcohols/phenols;
5. ethers;
6. halocarbons;
7. aromatic hydrocarbons;
8. alkanes/cycloalkanes.

Adding aldehydes, nitriles, amines, nitro compounds, sulfur families, or
alkenes/alkynes requires a separate source/baseline task because it changes the
transfer surface and family-balance contract.

### Candidate Bounded-Extract Limit

Proposed ceiling: **80 rows total**, exactly **10 rows per existing family**.

Selection must be value-blind to Joback error:

- sort admitted representatives within each family by molecular weight and
  InChIKey;
- select ten deterministic molecular-weight quantile positions;
- freeze the candidate counts and selected identities before any benchmark
  metric is run;
- stop if any family has fewer than ten admissible non-conflict
  representatives.

The 80-row ceiling is a scientific and operational proposal, not a legal
conclusion. It doubles the current per-family coverage without changing the
family taxonomy or creating an open-ended corpus. It becomes executable only
after a maintainer records that this extract size is acceptable.

## Rights And Publication Matrix

| Artifact | Allowed now | Maintainer decision required |
| --- | --- | --- |
| Source locator, checksum, schema, code references | yes | no |
| Local archive bytes outside repository | yes, maintainer-controlled | archive access |
| Archive bytes or extracted tree in Git | no | cannot be waived by this task |
| Local-only normalized candidate table | not created here | yes |
| Public 80-row factual fixture | no | explicit bounded-extract approval |
| Open-ended or substantial normalized corpus | no | outside current campaign policy |
| Counts and exclusion summaries without values | yes after deterministic run | source access only |

Attribution must retain the NIST TRC archive DOI, archive version, publisher
permission caveat, and statement that NIST does not critically evaluate the
deposited values.

## Reproducibility Contract

A future row-curation task must pin:

- archive size and SHA-256;
- extractor commit;
- Python, RDKit, `thermo`, and PyYAML versions;
- ThermoML property-name matcher;
- identity, element, charge, fragment, and Joback coverage filters;
- family SMARTS and priority;
- duplicate/conflict rules;
- row ceiling and quantile indices;
- output fixture hash;
- a test proving regeneration from the local verified archive.

The current reference runtime is RDKit `2025.09.3` and `thermo 0.6.0`.
Version changes require a parity report because structure parsing and Joback
group assignment may change selected rows.

## Exact Future Task Shape

Only after bounded-extract rights approval:

> Build a checksum-pinned 80-row ThermoML `Tb` expansion fixture from the
> locally verified version 1.2.6 archive. Select ten molecular-weight-quantile
> representatives in each of the existing eight families under the frozen
> identity, row-class, duplicate, conflict, and Joback coverage rules. Commit
> no archive bytes or normalized corpus. Add deterministic regeneration and
> schema tests. Do not run benchmark metrics or edit `RESULT-0026`.

If the maintainer selects local-only analysis, the future task must instead
write only code, non-value metadata, aggregate counts, hashes, and a blocker
note; no public fixture may be committed.

## Stop Conditions

Stop before row extraction or publication if:

1. the archive size or hash does not match;
2. archive access or larger-extract rights are not explicitly approved;
3. any value is obtained through a live agent fetch;
4. identity, uncertainty, row class, duplicate, or conflict semantics are
   missing;
5. a family has fewer than ten admissible representatives;
6. selection uses Joback errors or post-score knowledge;
7. the task mixes properties, mixtures, charged species, or out-of-coverage
   structures;
8. the proposed output resembles a substantial normalized corpus;
9. the task expands into process, chemical, synthesis, or safety guidance.

## Output Routing

- Task verdict: `NEEDS_MAINTAINER_SOURCE_DECISION`.
- Canonical destination: this source-readiness preflight.
- Review tier: `none`.
- Gate A status: not attempted; no result or prediction artifact.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Result impact: none; `RESULT-0026` is unchanged.
- Dataset impact: no new values, rows, archive bytes, or corpus.
- Blocker: maintainer approval of the 80-row bounded-extract rights posture or
  selection of the local-only route.

## Limitations

- Committed repository evidence only; no live source access.
- The 80-row ceiling is unexecuted and may fail family-count or conflict gates.
- This task does not determine whether the expanded surface would preserve the
  current Joback result.
- No property beyond normal boiling temperature is authorized.
