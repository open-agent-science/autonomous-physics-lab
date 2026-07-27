# ThermoML Tb Feasible-Expansion Fixture

Task: `TASK-1091`

## Verdict

`FIXTURE_EXTRACTION_PASS`

The checksum-pinned ThermoML v1.2.6 archive supports the complete frozen
TASK-1084 fixture. The extraction retains all 38 eligible historical rows,
excludes both conflict-flagged historical identities, and adds 36 identities
without using target values, model errors, residuals, or prior family
performance for identity selection.

This is source-fixture readiness only. No Joback score, control comparison,
residual, `RESULT`, `PRED`, `CLAIM`, or `KNOW` artifact was created.

## Inputs And Method

The archive was resolved with `scripts/apl_local_artifacts.py locate` using:

- source id: `nist-trc-thermoml-archive`;
- filename: `ThermoML.v2020-09-30.tgz`;
- byte size: `189433115`;
- SHA-256:
  `231161b5e443dc1ae0e5da8429d86a88474cb722016e5b790817bb31c58d7ec2`;
- helper status: `FOUND`.

The resolved machine path is intentionally not recorded. Source bytes remained
read-only and outside git. Generated local work used the canonical TASK-1091
local-artifact workspace; the archive was streamed without unpacking an XML or
JSON tree.

Before row extraction, the count-only preflight independently reproduced the
frozen admissible non-conflict counts:

| Family | Frozen count | Replayed count | Retained | Added | Final |
| --- | ---: | ---: | ---: | ---: | ---: |
| acids | 6 | 6 | 5 | 1 | 6 |
| esters/lactones | 48 | 48 | 4 | 6 | 10 |
| ketones | 8 | 8 | 4 | 4 | 8 |
| alcohols/phenols | 29 | 29 | 5 | 5 | 10 |
| ethers | 12 | 12 | 5 | 5 | 10 |
| halocarbons | 15 | 15 | 5 | 5 | 10 |
| aromatic hydrocarbons | 20 | 20 | 5 | 5 | 10 |
| alkanes/cycloalkanes | 11 | 11 | 5 | 5 | 10 |

The deterministic extractor:

1. verifies archive size and SHA-256;
2. replays the frozen pure-component, identity, uncertainty, conflict, family,
   and Joback-coverage filters;
3. verifies the TASK-1084 contract and the original 40-row fixture hashes;
4. preserves the 38 non-conflict rows exactly;
5. excludes all 40 historical identities from the addition pool;
6. orders each family by molecular weight and InChIKey;
7. takes the frozen quantile positions, applying the five-row article cap
   across retained and added rows;
8. stops before output unless every information-floor condition passes.

## Extraction Ledger

| Check | Outcome |
| --- | ---: |
| Total fixture rows | 74 |
| Retained historical rows | 38 |
| New identities | 36 |
| Effective families | 8 |
| Equal-family weighted effective rows | 71.775701 |
| Minimum rows in a family | 6 |
| Distinct source articles | 52 |
| Maximum rows from one source article | 4 |
| Conflict-flagged historical rows retained | 0 |
| Quantile targets requiring article-cap fallback | 0 |

The article cap therefore did not alter any frozen quantile target. The
committed selection trace records every target and selected index so a later
review can detect selection drift without running a benchmark.

## Frozen Artifacts

| Artifact | SHA-256 |
| --- | --- |
| `data/thermophysical/thermoml_tb_feasible_expansion_contract.yaml` | `3b82ea5700a21213346e7201d52bb2065d6050e5abc53a08c15b1feca2ee18bc` |
| `data/thermophysical/thermoml_tb_audit_fixture.yaml` | `c96b33b60fc07ef78b71a188cb931bff34d443549f0517ce198b0f5049ccdc7c` |
| `data/thermophysical/thermoml_tb_feasible_expansion_fixture.yaml` | `06063d2690d903821e1740af29f5e13f94563bf2aff297d7ffb9d95d42d48a74` |

The release manifest additionally pins the extractor hash. Repeating the full
archive extraction after restoring the worktree reproduced the fixture
byte-for-byte with the same fixture SHA-256.

## Rights And Redistribution

The fixture remains inside the merged maintainer decision
`DEC-20260708-thermoml-option-a`:

- reuse status: `limited_factual_extract_with_attribution`;
- 74 rows, below the approved 80-row ceiling;
- at most 4 rows from one source article, below the approved cap of 5;
- attribution and source DOI retained on every row;
- `covered_by_repo_license: false`;
- no archive, extracted XML/JSON, normalized corpus, or substantial source
  layout committed;
- no external dataset release or DOI authorized.

The release manifest and fixture preserve these restrictions explicitly.

## Validation And Limitations

Tests verify archive fail-closed behavior, contract and legacy-fixture hashes,
exact retention of all eligible rows, exclusion of every historical identity
from additions, deterministic quantile and article-cap behavior, family and
information floors, rights metadata, and absence of machine-local paths.

Limitations:

- the fixture remains a narrow pure-component normal-boiling-temperature
  extract from eight predeclared families;
- denser within-family identity coverage does not create new independent
  family groups;
- source values are factual extracts under attribution, not relicensed
  repository data;
- fixture readiness says nothing about Joback accuracy or transfer behavior;
- scoring, thresholds, controls, and any scientific verdict belong only to
  the separately frozen benchmark task.

## Output Routing

- Canonical destination:
  `data/thermophysical/thermoml_tb_feasible_expansion_fixture.yaml`.
- Release identity:
  `data/thermophysical/thermoml_tb_feasible_expansion_release.yaml`.
- Source readiness: ready for the separately frozen TASK-1103 benchmark after
  maintainer review and merge.
- Benchmark scoring: not attempted.
- Gate A: not attempted.
- Gate B: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Existing results: unchanged.
- Publication blocker: the fixture and release hashes must be maintainer
  reviewed and merged before TASK-1103 may score the frozen benchmark.

Fixture extraction success is not evidence that Joback succeeds, fails
globally, supports production property estimation, or provides chemical
design, process, synthesis, or safety guidance.
