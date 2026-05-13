# Nuclear Prediction Registry Entry Review

Task: `TASK-0205`

## Verdict

`PRED-0001` through `PRED-0020` create a first prospective nuclear-mass
prediction slate for scalable parallel testing.

The slate is intentionally conservative. It registers frozen variants and
control hypotheses for later reveal, but it does not promote a nuclear-mass
claim, canonical result, or accepted knowledge.

## Frozen Quantity

All entries predict:

```text
quantity: mass_excess_mev
unit: MeV
```

The registered values are deterministic point estimates. Each value starts from
a semi-empirical binding-energy prediction, converts that prediction to atomic
mass, and then converts atomic mass to mass excess using the repository helper
functions in `physics_lab.engines.nuclear_mass_baselines` and
`physics_lab.engines.nuclear_masses`.

## Parallel Variant Slate

The first slate contains 20 runs:

```text
4 frozen model/control variants x 5 repo-prospective target batches = 20 entries
```

Model/control variants:

| Variant | Registry model id | Role |
| --- | --- | --- |
| Fitted semi-empirical baseline | `RESULT-0015::model_fitted_semi_empirical` | Primary conservative baseline |
| Reference semi-empirical control | `RESULT-0015::model_reference_semi_empirical` | Literature-style coefficient control |
| Reference no-pairing control | `RESULT-0015::model_reference_liquid_drop_no_pairing` | Pairing ablation control from RESULT-0015 |
| Fitted no-pairing ablation | `RESULT-0015::model_fitted_semi_empirical::pairing_ablation_zero` | Derived control: fitted coefficients with pairing forced to zero |

Target batches:

| Batch | Targets |
| --- | --- |
| `frontier-next-row` | `Ca-55`, `Ni-76`, `Zn-80`, `Ga-85` |
| `n50-forward-row` | `Ge-88`, `As-90`, `Se-92`, `Br-94` |
| `n82-neighborhood-row` | `Cd-126`, `In-135`, `Sn-136`, `Sb-138` |
| `heavy-extension-row` | `Te-142`, `I-144`, `Xe-146`, `Cs-148` |
| `odd-even-stress-row` | `K-55`, `Ca-56`, `Sc-62`, `Ti-64` |

The target set is repo-prospective only: tests assert that these nuclides do
not appear in the committed `NMD-0002` measured slice or the committed
post-AME2020 holdout dataset. No live external data was fetched while
registering the slate.

## Agent Use

Agents can use this slate in two ways:

1. Run later reveal comparisons against the frozen entries when future reviewed
   measurements are committed.
2. Add their own `PRED-0021+` variants in separate PRs, provided each variant
   freezes its model, target list, prediction values, source state, uncertainty
   semantics, and reveal conditions before any later measurement comparison.

Agent-proposed variants should keep the same boundary:

- no live external fetch during registration;
- no claim promotion before reveal;
- no retrospective time-split result described as a blind prediction;
- no mutation of registered values after reveal-trigger data exists;
- deterministic code or artifact reference for the prediction calculation.

## Reveal Conditions

Reveal is triggered only when a future maintainer-reviewed nuclear-mass dataset
or source manifest is committed after the registry timestamp and contains
measured or reviewably convertible values for one or more target nuclides.

Reveal can happen per target or per batch, but comparison must be a separate
reviewed task. The original `PRED-XXXX` entries stay unchanged.

## Limitations

- The fitted baseline is trained on a small pinned measured slice.
- The ablation variant is a control hypothesis, not a promoted model.
- Absence from committed repository datasets is not proof of absence from the
  external scientific record.
- The entries contain point estimates only; `uncertainty_mev` is intentionally
  null.
