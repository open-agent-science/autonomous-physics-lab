# Nuclear Prediction Synthetic Reveal Dry-Run

**Task:** TASK-0273
**Harness:** `physics_lab/engines/nuclear_prediction_reveal.py`
**Fixture:** `examples/nuclear_prediction_synthetic_reveal.yaml`
**Mode:** synthetic/toy source only

This review note documents a dry-run harness for future nuclear prediction
reveal work. It does not fetch live measurements, compare against real nuclear
data, score real predictions, or promote any claim. The fixture values are
fabricated toy rows used only to exercise protocol plumbing.

## Method

The harness reads a frozen prediction registry snapshot and a synthetic source
fixture:

```bash
python3 - <<'PY'
from pathlib import Path
from physics_lab.engines.nuclear_prediction_reveal import run_synthetic_reveal_dry_run

result = run_synthetic_reveal_dry_run(
    Path("."),
    Path("examples/nuclear_prediction_synthetic_reveal.yaml"),
)
print(result["coverage"])
print(result["verdict"])
PY
```

The fixture must explicitly declare:

- `source_kind: synthetic_toy_measurement`
- `synthetic_source: true`
- `real_measurement_source: false`
- a human-readable fake-source warning

The helper rejects sources that do not carry those labels. It loads committed
`PRED-*.yaml` files through the existing nuclear prediction registry validator
and never writes back to `prediction_registry/nuclear_masses/`.

## Dry-Run Shape

The committed fixture uses `PRED-0041` and four target rows:

| Target | Synthetic fixture state | Dry-run status |
| --- | --- | --- |
| `Ni-76` | fake measured-synthetic row after registration | `ELIGIBLE_SYNTHETIC` |
| `Ca-55` | absent from fake source | `TARGET_NOT_REVEALED` |
| `Zn-80` | fake extrapolated-synthetic row | `NON_MEASURED_VALUE_ONLY` |
| `Ga-85` | fake measured-synthetic row before registration | `SOURCE_PREDATES_REGISTRATION` |

Coverage from the dry-run:

| Metric | Value |
| --- | ---: |
| Target rows | 4 |
| Eligible synthetic rows | 1 |
| Unrevealed rows | 1 |
| Ineligible rows | 2 |
| Partial reveal fraction | 0.25 |

The toy metric path intentionally scores only the one eligible synthetic row.
Those values test table generation and exclusion behavior only; they are not
scientific evidence.

## Protocol Behaviors Exercised

- Registry snapshot handling: selected `PRED` entries are loaded read-only from
  committed files.
- Eligibility screening: eligible, unrevealed, and ineligible rows remain in
  one comparison table with explicit statuses.
- Partial reveal handling: unrevealed targets are preserved as unscored rows.
- Source labeling: the fixture must be marked synthetic and non-real.
- Conservative verdict wording: the harness returns
  `INCONCLUSIVE_SYNTHETIC_DRY_RUN`.
- No registry mutation: tests verify the frozen registry input file is
  unchanged by the dry-run call.

## Limitations

- The fixture contains fake toy values and must not be cited as measured,
  evaluated, extrapolated, or reviewed nuclear data.
- No source manifest, checksum record, or real parser is introduced here.
- No no-peek audit over GitHub/task history is automated beyond synthetic row
  labels.
- No baseline-relative real reveal scoring is attempted.
- Claim promotion remains out of scope and would require a separate
  maintainer-reviewed task.

## Validation

Targeted validation:

```bash
python3 -m pytest tests/test_nuclear_prediction_reveal.py
```

Full handoff validation should also include the repository protocol commands:

```bash
python3 -m ruff check .
python3 -m pytest
python3 -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

## Verdict

`REVIEW_READY` as synthetic reveal tooling.

No scientific validation verdict is assigned. The harness is a guardrail and
workflow test for future reviewed reveal tasks only.
