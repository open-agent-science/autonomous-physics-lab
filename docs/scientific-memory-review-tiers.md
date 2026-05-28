# Scientific Memory Review Tiers

> Generated from canonical scientific-memory artifacts. Refresh with
> `python3 scripts/apl_scientific_memory_index.py --write`.

This index separates publication and review tiers so `AGENT_PUBLISHED`
evidence is not mistaken for maintainer-endorsed claims. It is a
visibility layer only: it does not promote, re-tier, or edit canonical
scientific artifacts.

## Tier Meaning

| Tier | Meaning | Default next action |
| --- | --- | --- |
| `AGENT_PUBLISHED` | Agent-created canonical evidence after Gate A. | Independent replay or maintainer review, depending on artifact class. |
| `AGENT_VALIDATED` | A different agent reproduced the artifact through Gate B. | Maintainer review before stronger interpretation. |
| `MAINTAINER_REVIEWED` | Maintainer endorsed the artifact tier/scope. | External replication or monitored reveal when relevant. |
| `EXTERNAL_REPLICATED` | External source, contributor, or reveal independently replicated the artifact. | Preserve as strongest public memory. |
| `LEGACY_UNTIERED` | Artifact predates the review-tier protocol. | Do not infer endorsement; triage only when a new promotion task asks for it. |

## Counts

| Tier | RESULT | PRED | CLAIM | KNOW | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| `AGENT_PUBLISHED` | 1 | 0 | 0 | 0 | 1 |
| `AGENT_VALIDATED` | 1 | 0 | 0 | 0 | 1 |
| `MAINTAINER_REVIEWED` | 0 | 0 | 0 | 0 | 0 |
| `EXTERNAL_REPLICATED` | 0 | 0 | 0 | 0 | 0 |
| `LEGACY_UNTIERED` | 15 | 60 | 10 | 9 | 94 |

## AGENT_PUBLISHED

| Class | Artifact | Status | Next action | Path |
| --- | --- | --- | --- | --- |
| `RESULT` | `RESULT-0017` - Pendulum Formula Discovery — Gauntlet (101 Candidates) | `OVERFITTED` | `replay-needed` | [`results/EXP-0001/RUN-0006/result.yaml`](../results/EXP-0001/RUN-0006/result.yaml) |

## AGENT_VALIDATED

| Class | Artifact | Status | Next action | Path |
| --- | --- | --- | --- | --- |
| `RESULT` | `RESULT-0016` - Anharmonic Oscillator Period Benchmark | `VALID_IN_RANGE` | `maintainer-review-needed` | [`results/EXP-0011/RUN-0002/result.yaml`](../results/EXP-0011/RUN-0002/result.yaml) |

## MAINTAINER_REVIEWED

_No artifacts in this tier._

## EXTERNAL_REPLICATED

_No artifacts in this tier._

## LEGACY_UNTIERED

| Class | Artifact | Status | Next action | Path |
| --- | --- | --- | --- | --- |
| `CLAIM` | `CLAIM-0001` - Pendulum Period Depends on Amplitude | `DRAFT` | `legacy-triage-only` | [`claims/CLAIM-0001-pendulum-period-amplitude.md`](../claims/CLAIM-0001-pendulum-period-amplitude.md) |
| `CLAIM` | `CLAIM-0002` - Damped Oscillator Regime Structure | `DRAFT` | `legacy-triage-only` | [`claims/CLAIM-0002-damped-oscillator-regimes.md`](../claims/CLAIM-0002-damped-oscillator-regimes.md) |
| `CLAIM` | `CLAIM-0003` - Charged-Lepton Koide Reproduction | `DRAFT` | `legacy-triage-only` | [`claims/CLAIM-0003-koide-charged-lepton-reproduction.md`](../claims/CLAIM-0003-koide-charged-lepton-reproduction.md) |
| `CLAIM` | `CLAIM-0004` - Historical Tau Holdout Benchmark | `DRAFT` | `legacy-triage-only` | [`claims/CLAIM-0004-koide-tau-holdout.md`](../claims/CLAIM-0004-koide-tau-holdout.md) |
| `CLAIM` | `CLAIM-0005` - Dimensional Analysis Validator Correctly Classifies Physics Formulas | `DRAFT` | `legacy-triage-only` | [`claims/CLAIM-0005-dimensional-analysis-validator.md`](../claims/CLAIM-0005-dimensional-analysis-validator.md) |
| `CLAIM` | `CLAIM-0006` - Quark-Sector Koide Follow-up Fails in Scope | `DRAFT` | `legacy-triage-only` | [`claims/CLAIM-0006-koide-quark-falsification.md`](../claims/CLAIM-0006-koide-quark-falsification.md) |
| `CLAIM` | `CLAIM-0007` - Fixed Standard Koide Target Fails Cross-Family Survival in the Falsifier MVP | `DRAFT` | `legacy-triage-only` | [`claims/CLAIM-0007-particle-mass-falsifier-mvp.md`](../claims/CLAIM-0007-particle-mass-falsifier-mvp.md) |
| `CLAIM` | `CLAIM-0008` - Muon g-2 stress test finds one first-pass lepton-cascade hit within 1σ | `DRAFT` | `legacy-triage-only` | [`claims/CLAIM-0008-muon-g2-lepton-cascade-empirical.md`](../claims/CLAIM-0008-muon-g2-lepton-cascade-empirical.md) |
| `CLAIM` | `CLAIM-0009` - Anharmonic Oscillator Period Benchmark | `DRAFT` | `legacy-triage-only` | [`claims/CLAIM-0009-anharmonic-oscillator-period.md`](../claims/CLAIM-0009-anharmonic-oscillator-period.md) |
| `CLAIM` | `CLAIM-0010` - Nuclear Mass Baseline Residual Benchmark | `DRAFT` | `legacy-triage-only` | [`claims/CLAIM-0010-nuclear-mass-baseline.md`](../claims/CLAIM-0010-nuclear-mass-baseline.md) |
| `KNOW` | `KN-0006` - Quark Running Masses — PDG 2024 MS-bar Scheme | `n/a` | `legacy-triage-only` | [`knowledge/particle_physics/quark_masses.yaml`](../knowledge/particle_physics/quark_masses.yaml) |
| `KNOW` | `KNOW-0001` - Pendulum | `n/a` | `legacy-triage-only` | [`knowledge/classical_mechanics/pendulum.md`](../knowledge/classical_mechanics/pendulum.md) |
| `KNOW` | `KNOW-0002` - Damped Oscillator | `n/a` | `legacy-triage-only` | [`knowledge/classical_mechanics/damped_oscillator.md`](../knowledge/classical_mechanics/damped_oscillator.md) |
| `KNOW` | `KNOW-0003` - Koide Relation | `n/a` | `legacy-triage-only` | [`knowledge/particle_physics/koide_relation.md`](../knowledge/particle_physics/koide_relation.md) |
| `KNOW` | `KNOW-0003` - Units and Dimensions Reference | `n/a` | `legacy-triage-only` | [`knowledge/reference/units-and-dimensions.md`](../knowledge/reference/units-and-dimensions.md) |
| `KNOW` | `KNOW-0004` - Dimensional Analysis Validator | `n/a` | `legacy-triage-only` | [`knowledge/physics_validation/dimensional_analysis_validator.md`](../knowledge/physics_validation/dimensional_analysis_validator.md) |
| `KNOW` | `KNOW-0007` - Muon g-2 discrepancy stress-test target and formula-search constants | `REVIEW_NEEDED` | `legacy-triage-only` | [`knowledge/particle_physics/muon_g2.yaml`](../knowledge/particle_physics/muon_g2.yaml) |
| `KNOW` | `KNOW-0008` - Anharmonic Oscillator | `n/a` | `legacy-triage-only` | [`knowledge/classical_mechanics/anharmonic_oscillator.md`](../knowledge/classical_mechanics/anharmonic_oscillator.md) |
| `KNOW` | `KNOW-0009` - Nuclear Mass Baseline | `n/a` | `legacy-triage-only` | [`knowledge/nuclear_physics/nuclear_mass_baseline.md`](../knowledge/nuclear_physics/nuclear_mass_baseline.md) |
| `PRED` | `PRED-0001` - Prospective nuclear mass slate: fitted semi-empirical baseline on frontier next-row controls | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0001.yaml`](../prediction_registry/nuclear_masses/PRED-0001.yaml) |
| `PRED` | `PRED-0002` - Prospective nuclear mass slate: fitted semi-empirical baseline on N=50 forward-row stress targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0002.yaml`](../prediction_registry/nuclear_masses/PRED-0002.yaml) |
| `PRED` | `PRED-0003` - Prospective nuclear mass slate: fitted semi-empirical baseline on N=82 neighborhood extension targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0003.yaml`](../prediction_registry/nuclear_masses/PRED-0003.yaml) |
| `PRED` | `PRED-0004` - Prospective nuclear mass slate: fitted semi-empirical baseline on heavy neutron-rich extension targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0004.yaml`](../prediction_registry/nuclear_masses/PRED-0004.yaml) |
| `PRED` | `PRED-0005` - Prospective nuclear mass slate: fitted semi-empirical baseline on odd-even pairing stress targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0005.yaml`](../prediction_registry/nuclear_masses/PRED-0005.yaml) |
| `PRED` | `PRED-0006` - Prospective nuclear mass slate: reference semi-empirical control on frontier next-row controls | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0006.yaml`](../prediction_registry/nuclear_masses/PRED-0006.yaml) |
| `PRED` | `PRED-0007` - Prospective nuclear mass slate: reference semi-empirical control on N=50 forward-row stress targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0007.yaml`](../prediction_registry/nuclear_masses/PRED-0007.yaml) |
| `PRED` | `PRED-0008` - Prospective nuclear mass slate: reference semi-empirical control on N=82 neighborhood extension targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0008.yaml`](../prediction_registry/nuclear_masses/PRED-0008.yaml) |
| `PRED` | `PRED-0009` - Prospective nuclear mass slate: reference semi-empirical control on heavy neutron-rich extension targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0009.yaml`](../prediction_registry/nuclear_masses/PRED-0009.yaml) |
| `PRED` | `PRED-0010` - Prospective nuclear mass slate: reference semi-empirical control on odd-even pairing stress targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0010.yaml`](../prediction_registry/nuclear_masses/PRED-0010.yaml) |
| `PRED` | `PRED-0011` - Prospective nuclear mass slate: reference no-pairing control on frontier next-row controls | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0011.yaml`](../prediction_registry/nuclear_masses/PRED-0011.yaml) |
| `PRED` | `PRED-0012` - Prospective nuclear mass slate: reference no-pairing control on N=50 forward-row stress targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0012.yaml`](../prediction_registry/nuclear_masses/PRED-0012.yaml) |
| `PRED` | `PRED-0013` - Prospective nuclear mass slate: reference no-pairing control on N=82 neighborhood extension targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0013.yaml`](../prediction_registry/nuclear_masses/PRED-0013.yaml) |
| `PRED` | `PRED-0014` - Prospective nuclear mass slate: reference no-pairing control on heavy neutron-rich extension targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0014.yaml`](../prediction_registry/nuclear_masses/PRED-0014.yaml) |
| `PRED` | `PRED-0015` - Prospective nuclear mass slate: reference no-pairing control on odd-even pairing stress targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0015.yaml`](../prediction_registry/nuclear_masses/PRED-0015.yaml) |
| `PRED` | `PRED-0016` - Prospective nuclear mass slate: fitted no-pairing ablation control on frontier next-row controls | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0016.yaml`](../prediction_registry/nuclear_masses/PRED-0016.yaml) |
| `PRED` | `PRED-0017` - Prospective nuclear mass slate: fitted no-pairing ablation control on N=50 forward-row stress targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0017.yaml`](../prediction_registry/nuclear_masses/PRED-0017.yaml) |
| `PRED` | `PRED-0018` - Prospective nuclear mass slate: fitted no-pairing ablation control on N=82 neighborhood extension targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0018.yaml`](../prediction_registry/nuclear_masses/PRED-0018.yaml) |
| `PRED` | `PRED-0019` - Prospective nuclear mass slate: fitted no-pairing ablation control on heavy neutron-rich extension targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0019.yaml`](../prediction_registry/nuclear_masses/PRED-0019.yaml) |
| `PRED` | `PRED-0020` - Prospective nuclear mass slate: fitted no-pairing ablation control on odd-even pairing stress targets | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0020.yaml`](../prediction_registry/nuclear_masses/PRED-0020.yaml) |
| `PRED` | `PRED-0021` - Prospective nuclear mass slate: fitted/reference 50-50 coefficient blend on frontier next-row controls | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0021.yaml`](../prediction_registry/nuclear_masses/PRED-0021.yaml) |
| `PRED` | `PRED-0022` - Prospective nuclear mass slate: fitted volume +1% perturbation control on frontier next-row controls | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0022.yaml`](../prediction_registry/nuclear_masses/PRED-0022.yaml) |
| `PRED` | `PRED-0023` - Prospective nuclear mass slate: pairing-enhanced control (+10% pairing coefficient) on odd-even sensitivity probe | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0023.yaml`](../prediction_registry/nuclear_masses/PRED-0023.yaml) |
| `PRED` | `PRED-0024` - Prospective nuclear mass slate: null-pairing control (pairing coefficient = 0) on odd-even sensitivity probe | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0024.yaml`](../prediction_registry/nuclear_masses/PRED-0024.yaml) |
| `PRED` | `PRED-0025` - Prospective nuclear mass slate: shell Gaussian proximity (Z+N) negative control on shell-magic probe | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0025.yaml`](../prediction_registry/nuclear_masses/PRED-0025.yaml) |
| `PRED` | `PRED-0026` - Prospective nuclear mass slate: shell Gaussian proximity (N only) negative control on shell-magic probe | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0026.yaml`](../prediction_registry/nuclear_masses/PRED-0026.yaml) |
| `PRED` | `PRED-0027` - Prospective nuclear mass slate: quartic asymmetry negative control on neutron-excess probe | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0027.yaml`](../prediction_registry/nuclear_masses/PRED-0027.yaml) |
| `PRED` | `PRED-0028` - Prospective nuclear mass slate: asymmetric neutron-excess near-null control on neutron-excess probe | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0028.yaml`](../prediction_registry/nuclear_masses/PRED-0028.yaml) |
| `PRED` | `PRED-0029` - Prospective nuclear mass slate: base fitted semi-empirical extrapolation along Tin isotope chain beyond Sn-120 | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0029.yaml`](../prediction_registry/nuclear_masses/PRED-0029.yaml) |
| `PRED` | `PRED-0030` - Prospective nuclear mass slate: asymmetry-enhanced (+15%) fitted model on Zinc isotope chain mid-mass neutron-rich extrapolation | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0030.yaml`](../prediction_registry/nuclear_masses/PRED-0030.yaml) |
| `PRED` | `PRED-0037` - Prospective nuclear mass slate: fitted SEMF with Coulomb Z^2 form simplification on frontier next-row controls | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0037.yaml`](../prediction_registry/nuclear_masses/PRED-0037.yaml) |
| `PRED` | `PRED-0038` - Prospective nuclear mass slate: fitted SEMF with pairing 1/A scaling simplification on frontier next-row controls | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0038.yaml`](../prediction_registry/nuclear_masses/PRED-0038.yaml) |
| `PRED` | `PRED-0041` - Prospective nuclear mass factory selection: blend-with-reference-10-frontier | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0041.yaml`](../prediction_registry/nuclear_masses/PRED-0041.yaml) |
| `PRED` | `PRED-0042` - Prospective nuclear mass factory selection: blend-with-reference-50-frontier | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0042.yaml`](../prediction_registry/nuclear_masses/PRED-0042.yaml) |
| `PRED` | `PRED-0043` - Prospective nuclear mass factory selection: blend-with-reference-50-mid-mass-stable | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0043.yaml`](../prediction_registry/nuclear_masses/PRED-0043.yaml) |
| `PRED` | `PRED-0044` - Prospective nuclear mass factory selection: pairing-scale-plus-5pct-odd-even | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0044.yaml`](../prediction_registry/nuclear_masses/PRED-0044.yaml) |
| `PRED` | `PRED-0045` - Prospective nuclear mass factory selection: pairing-scale-minus-5pct-odd-even | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0045.yaml`](../prediction_registry/nuclear_masses/PRED-0045.yaml) |
| `PRED` | `PRED-0046` - Prospective nuclear mass factory selection: pairing-zero-ablation-odd-even | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0046.yaml`](../prediction_registry/nuclear_masses/PRED-0046.yaml) |
| `PRED` | `PRED-0047` - Prospective nuclear mass factory selection: coulomb-scale-plus-1pct-frontier | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0047.yaml`](../prediction_registry/nuclear_masses/PRED-0047.yaml) |
| `PRED` | `PRED-0048` - Prospective nuclear mass factory selection: coulomb-scale-minus-1pct-frontier | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0048.yaml`](../prediction_registry/nuclear_masses/PRED-0048.yaml) |
| `PRED` | `PRED-0049` - Prospective nuclear mass factory selection: asymmetry-scale-plus-1pct-frontier | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0049.yaml`](../prediction_registry/nuclear_masses/PRED-0049.yaml) |
| `PRED` | `PRED-0050` - Prospective nuclear mass factory selection: asymmetry-scale-minus-1pct-frontier | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0050.yaml`](../prediction_registry/nuclear_masses/PRED-0050.yaml) |
| `PRED` | `PRED-0051` - Selected nuclear mass feature-term prediction: shell-zn-reviewed-coefficients-shell-magic on shell-magic-probe | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0051.yaml`](../prediction_registry/nuclear_masses/PRED-0051.yaml) |
| `PRED` | `PRED-0052` - Selected nuclear mass feature-term prediction: shell-zn-sign-inverted-shell-magic on shell-magic-probe | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0052.yaml`](../prediction_registry/nuclear_masses/PRED-0052.yaml) |
| `PRED` | `PRED-0053` - Selected nuclear mass feature-term prediction: shell-n-reviewed-coefficient-shell-magic on shell-magic-probe | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0053.yaml`](../prediction_registry/nuclear_masses/PRED-0053.yaml) |
| `PRED` | `PRED-0054` - Selected nuclear mass feature-term prediction: shell-n-sign-inverted-shell-magic on shell-magic-probe | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0054.yaml`](../prediction_registry/nuclear_masses/PRED-0054.yaml) |
| `PRED` | `PRED-0055` - Selected nuclear mass feature-term prediction: asymmetric-neutron-excess-plus-neutron-rich on neutron-rich-stress | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0055.yaml`](../prediction_registry/nuclear_masses/PRED-0055.yaml) |
| `PRED` | `PRED-0056` - Selected nuclear mass feature-term prediction: asymmetric-neutron-excess-minus-neutron-rich on neutron-rich-stress | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0056.yaml`](../prediction_registry/nuclear_masses/PRED-0056.yaml) |
| `PRED` | `PRED-0057` - Selected nuclear mass feature-term prediction: asymmetric-neutron-excess-cubic-plus-neutron-rich on neutron-rich-stress | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0057.yaml`](../prediction_registry/nuclear_masses/PRED-0057.yaml) |
| `PRED` | `PRED-0058` - Selected nuclear mass feature-term prediction: asymmetric-neutron-excess-cubic-minus-neutron-rich on neutron-rich-stress | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0058.yaml`](../prediction_registry/nuclear_masses/PRED-0058.yaml) |
| `PRED` | `PRED-0059` - Selected nuclear mass feature-term prediction: shell-n-reviewed-nickel-chain on nickel-isotope-chain | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0059.yaml`](../prediction_registry/nuclear_masses/PRED-0059.yaml) |
| `PRED` | `PRED-0060` - Selected nuclear mass feature-term prediction: shell-n-sign-inverted-nickel-chain on nickel-isotope-chain | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0060.yaml`](../prediction_registry/nuclear_masses/PRED-0060.yaml) |
| `PRED` | `PRED-0061` - Selected nuclear mass feature-term prediction: asymmetric-neutron-excess-plus-nickel-chain on nickel-isotope-chain | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0061.yaml`](../prediction_registry/nuclear_masses/PRED-0061.yaml) |
| `PRED` | `PRED-0062` - Selected nuclear mass feature-term prediction: asymmetric-neutron-excess-minus-nickel-chain on nickel-isotope-chain | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0062.yaml`](../prediction_registry/nuclear_masses/PRED-0062.yaml) |
| `PRED` | `PRED-0063` - Nuclear shell-axis prospective mini-wave: proton-axis Gaussian on shell-axis-balanced-001 | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0063.yaml`](../prediction_registry/nuclear_masses/PRED-0063.yaml) |
| `PRED` | `PRED-0064` - Nuclear shell-axis prospective mini-wave: proton-neutron product on shell-axis-balanced-001 | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0064.yaml`](../prediction_registry/nuclear_masses/PRED-0064.yaml) |
| `PRED` | `PRED-0065` - Nuclear shell-axis prospective mini-wave: neutron-axis Gaussian on shell-axis-balanced-001 | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0065.yaml`](../prediction_registry/nuclear_masses/PRED-0065.yaml) |
| `PRED` | `PRED-0066` - Nuclear shell-axis prospective mini-wave: sign-inverted proton-axis control on shell-axis-balanced-001 | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0066.yaml`](../prediction_registry/nuclear_masses/PRED-0066.yaml) |
| `PRED` | `PRED-0067` - Nuclear shell-axis prospective mini-wave: near-null control on shell-axis-balanced-001 | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0067.yaml`](../prediction_registry/nuclear_masses/PRED-0067.yaml) |
| `PRED` | `PRED-0068` - Nuclear shell-axis prospective mini-wave: frozen baseline reference on shell-axis-balanced-001 | `REGISTERED` | `legacy-triage-only` | [`prediction_registry/nuclear_masses/PRED-0068.yaml`](../prediction_registry/nuclear_masses/PRED-0068.yaml) |
| `RESULT` | `RESULT-0001` - Pendulum Formula Discovery | `VALID_IN_RANGE` | `legacy-triage-only` | [`results/EXP-0001/RUN-0001/result.yaml`](../results/EXP-0001/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0002` - Damped Oscillator Regime Verification | `VALID_IN_RANGE` | `legacy-triage-only` | [`results/EXP-0002/RUN-0001/result.yaml`](../results/EXP-0002/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0003` - Pendulum Formula Discovery | `VALID_IN_RANGE` | `legacy-triage-only` | [`results/EXP-0001/RUN-0002/result.yaml`](../results/EXP-0001/RUN-0002/result.yaml) |
| `RESULT` | `RESULT-0004` - Pendulum Formula Discovery — Gauntlet (100 Candidates) | `VALID_IN_RANGE` | `legacy-triage-only` | [`results/EXP-0001/RUN-0003/result.yaml`](../results/EXP-0001/RUN-0003/result.yaml) |
| `RESULT` | `RESULT-0005` - Charged-Lepton Koide Reproduction | `VALID` | `legacy-triage-only` | [`results/EXP-0004/RUN-0004/result.yaml`](../results/EXP-0004/RUN-0004/result.yaml) |
| `RESULT` | `RESULT-0006` - Historical Tau Holdout Prediction | `VALID_IN_RANGE` | `legacy-triage-only` | [`results/EXP-0005/RUN-0005/result.yaml`](../results/EXP-0005/RUN-0005/result.yaml) |
| `RESULT` | `RESULT-0007` - Dimensional Analysis Validator MVP Benchmark | `VALID` | `legacy-triage-only` | [`results/EXP-0006/RUN-0006/result.yaml`](../results/EXP-0006/RUN-0006/result.yaml) |
| `RESULT` | `RESULT-0008` - Pendulum Formula Discovery — Gauntlet (100 Candidates) | `OVERFITTED` | `legacy-triage-only` | [`results/EXP-0001/RUN-0004/result.yaml`](../results/EXP-0001/RUN-0004/result.yaml) |
| `RESULT` | `RESULT-0009` - Neutrino Koide Consistency Test — Neutrino Koide Consistency Test | `INVALID` | `legacy-triage-only` | [`results/EXP-0007/RUN-0001/result.yaml`](../results/EXP-0007/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0010` - Quark Koide Cascade — Brannen Phase Extension Test | `INVALID` | `legacy-triage-only` | [`results/EXP-0008/RUN-0001/result.yaml`](../results/EXP-0008/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0011` - Particle-Mass Relation Falsifier MVP | `INVALID` | `legacy-triage-only` | [`results/EXP-0009/RUN-0001/result.yaml`](../results/EXP-0009/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0012` - Muon g-2 Formula-Search Stress Test | `INCONCLUSIVE` | `legacy-triage-only` | [`results/EXP-0010/RUN-0001/result.yaml`](../results/EXP-0010/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0013` - Pendulum Formula Discovery — Gauntlet (102 Candidates) | `VALID_IN_RANGE` | `legacy-triage-only` | [`results/EXP-0001/RUN-0005/result.yaml`](../results/EXP-0001/RUN-0005/result.yaml) |
| `RESULT` | `RESULT-0014` - Anharmonic Oscillator Period Benchmark | `VALID_IN_RANGE` | `legacy-triage-only` | [`results/EXP-0011/RUN-0001/result.yaml`](../results/EXP-0011/RUN-0001/result.yaml) |
| `RESULT` | `RESULT-0015` - Nuclear Mass Baseline Residual Benchmark | `PARTIALLY_VALID` | `legacy-triage-only` | [`results/EXP-0012/RUN-0001/result.yaml`](../results/EXP-0012/RUN-0001/result.yaml) |

## Notes

- Missing `review_tier` fields are displayed as `LEGACY_UNTIERED` for
  visibility only; this task intentionally leaves canonical artifacts
  unchanged.
- `PRED` entries often need reveal or source-state review rather than Gate B
  replay.
- `CLAIM` and `KNOW` artifacts remain maintainer-sensitive in Phase 1 even
  when a future agent creates draft supporting material.
