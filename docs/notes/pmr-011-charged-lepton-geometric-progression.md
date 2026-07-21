# PMR-011 Charged-Lepton Geometric-Progression Attempt

**Run:** `MICROTASK-RUN-0035`
**Verdict:** `FALSIFIED`

## Relation And Inputs

The predeclared zero-parameter relation is

`m_mu^2 = m_e * m_tau`.

It asks whether the electron, muon, and tau pole masses form an exact geometric
progression, or equivalently whether their adjacent logarithmic spacings are
equal. Inputs are the three MeV values and one-sigma uncertainties in
`data/particle_masses/charged_leptons.yaml` (PDG 2025 update metadata). No live
source was fetched and no mass value was fitted.

The pass condition was fixed before calculation:

`abs(m_mu^2/(m_e*m_tau) - 1) <= 0.01`.

## Method

The deterministic calculation used the dimensionless ratio

`R = m_mu^2/(m_e*m_tau)`

and the independent diagnostic

`Delta_log = abs(log(m_mu/m_e) - log(m_tau/m_mu))`.

It also inverted the relation to predict `m_mu = sqrt(m_e*m_tau)`. First-order
independent uncertainty propagation was applied to `R`; this uncertainty is
reported only as a scale check because the central mismatch already dominates.

## Metrics

| Quantity | Value |
| --- | ---: |
| `R` | `12.294688527629699` |
| `abs(R-1)` | `11.294688527629699` |
| percent residual from unity | `1129.4688527629698%` |
| logarithmic-spacing mismatch | `2.509167342092258` |
| predicted muon mass | `30.133193727573914 MeV` |
| observed muon mass | `105.6583755 MeV` |
| muon prediction relative error | `0.7148054417363826` |
| propagated one-sigma uncertainty of `R` | `0.0006227157942568286` |

The relation fails the 1% gate by a wide margin.

## Interpretation

Equal logarithmic spacing is falsified for this pinned charged-lepton pole-mass
triplet. This is a negative test of one simple relation, not evidence for an
alternative mass law. It neither weakens nor strengthens the separate Koide
reproduction and holdout records.

## Novelty And Limitations

The earlier `PMR-011` attempt evaluated up-type quark Koide `Q`; it did not test
this relation. The particle AHS diagnostic uses common-scale Yukawa inputs and
a different target surface, so it is not treated as the same experiment.

The candidate was hand-declared and tested once. A failed arbitrary relation is
useful only as scoped negative memory; it does not establish that other
relations fail, explain the mass hierarchy, or justify a search over many
unreported alternatives. No `RESULT`, `CLAIM`, or `KNOW` artifact is changed.

## Output Routing

- Destination: this note and `MICROTASK-RUN-0035`.
- Gate A / Gate B: not attempted.
- Claim and knowledge impact: none.
- Publication blocker: human review remains required.
