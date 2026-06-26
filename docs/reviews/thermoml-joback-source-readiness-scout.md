# ThermoML / Joback Source-Readiness and Fidelity Scout

Task: `TASK-0833`
Campaign target: future "Thermophysical Property Transfer Audit" (boiling-point slice)
Mode: bounded source-readiness + implementation-fidelity scout (planning only)
Property in scope: normal boiling point (Tb) **only**
Review date: 2026-06-25
Verdict: **SOURCE_LIMITED**

## Scope and Non-Goals

This is a bounded scout that answers one question: *is the NIST TRC ThermoML
Archive ready to support a future frozen-method-vs-experiment transfer audit of
boiling point, and is a Joback Tb estimator implementation faithful enough to be
trusted as the frozen candidate?* It pins the source route and reuse posture,
freezes the identity/grouping/family taxonomy, and runs a Joback fidelity
fixture against published predicted values.

It does **not**: download or vendor the archive; enumerate the live archive;
curate any rows; compute any benchmark metric, global error, or per-compound
model error; scaffold the campaign; or promote any RESULT / PRED / CLAIM / KNOW.
Per the requirement, Tc is explicitly excluded (see
[Tb-only scope](#tb-only-scope-and-the-tc-leakage-exclusion)).

Conventions follow
[published-source-dataset-standard.md](../published-source-dataset-standard.md)
and [fresh-data-intake-protocol.md](../fresh-data-intake-protocol.md); the
materials-campaign manifest
[data/materials/source_manifest.yaml](../../data/materials/source_manifest.yaml)
is the format reference for the source-locator block below.

## 1. Pinned Source Route and Reuse Policy (FIRST)

### Official route (web-verified 2026-06-25)

| Field | Value |
| --- | --- |
| Product | NIST TRC ThermoML / Data Archive |
| DOI | `10.18434/mds2-2422` |
| Landing (PDR) | `https://data.nist.gov/od/id/mds2-2422` |
| Archive bytes (versioned `.tgz`) | `https://data.nist.gov/od/ds/mds2-2422/ThermoML.v2020-09-30.tgz` |
| Human browse | `https://trc.nist.gov/ThermoML/` and `https://trc.nist.gov/ThermoML/Browse` |
| Format | gzip-compressed tarball of per-article ThermoML XML + JSON, organized by journal DOI prefix |
| Coverage stated | "Data from initial cooperation (around 2003) through the 2019 calendar year" |
| Partner journals (5) | J. Chem. Eng. Data; J. Chem. Thermodynamics; Fluid Phase Equilibria; Thermochimica Acta; Int. J. Thermophysics |

`v2020-09-30` is the version string seen on the data.gov catalog mirror at scout
time; the live PDR may carry a newer or additional version string. The exact
current filename **must be re-read from the PDR landing page at first fetch**, not
assumed from this note.

### Reuse / redistribution posture — the gating finding

Two statements must be held together honestly:

- The data-repository wrapper is governed by the **NIST open-data license**
  (`https://www.nist.gov/open/license`): works of NIST employees "are not subject
  to copyright protection in the United States," with a non-exclusive
  irrevocable right "to print, publish, prepare derivative works and distribute
  the NIST data." TRC additionally **requests citation** of ThermoML Archive
  data in derived works.
- The ThermoML Archive page itself states the files are **"available here with
  permission of the journal publishers."** The NIST license carries an explicit
  carve-out: the data "may be subject to foreign copyright," and NIST "may also
  obtain and hold copyright in data/works created by non-NIST employees."

Reading: the **numerical facts** (a measured boiling point, its uncertainty, the
compound identity) are not copyrightable and are extractable with attribution.
But ThermoML files are aggregations of journal-article content present **under
publisher permission to NIST**, which is *not* the same as a blanket third-party
redistribution grant of the file bytes. This is exactly the
*published ≠ redistributable* distinction in the standard. Therefore the default
posture for any future campaign is **metadata-only**:

> Store the **source locator + DOI + the fetch/verify command + an expected
> SHA-256 computed at first license-cleared fetch**; do **not** vendor the
> archive tarball or republish ThermoML XML files. Curated APL Tb rows
> (compound id, value, uncertainty, provenance) may later be committed *with
> attribution* under a bounded row-curation task, since facts are not
> copyrightable — but bulk re-hosting of the files is not authorized here.

### Fetch / verify command pattern (DO NOT run in this scout)

No SHA-256 is recorded because none has been computed; fabricating one is
forbidden. At first license-cleared, maintainer-approved fetch, compute and pin
it. Cross-platform (Python `hashlib`) pattern, to be run by a maintainer:

```python
# maintainer-run, one time, at license-cleared first fetch
import hashlib, pathlib
p = pathlib.Path("ThermoML.v2020-09-30.tgz")   # confirm exact name on the PDR first
print(hashlib.sha256(p.read_bytes()).hexdigest())   # -> record as expected SHA-256
```

Source locator to record in a future `source_manifest.yaml` entry:
`https://data.nist.gov/od/ds/mds2-2422/<archive-filename>.tgz`
(DOI `10.18434/mds2-2422`), `expected_sha256: <PENDING_FIRST_FETCH>`,
`live_external_fetch_allowed: false`, `license_note: NIST open license +
publisher-permission aggregation; facts extractable with attribution, file bytes
not re-hosted`, `blocker_type: T4_snapshot_approval`.

## 2. Tb-only scope and the Tc leakage exclusion

Only **normal boiling point (Tb)** is selected for the first slice. Critical
temperature (Tc) is **excluded** because Joback's Tc estimator is an explicit
function of Tb:

`Tc = Tb · [0.584 + 0.965·ΣΔTc,i − (ΣΔTc,i)²]⁻¹`.

Auditing Joback Tc while substituting an *experimental* Tb into that formula is a
different operating mode (predicted-input vs experimental-input) and an
information-leakage path: the "method" would be partly fed the answer. Tb has no
such upstream dependency in Joback (`Tb = 198.2 + ΣΔTb,i`, structure-only), so it
is the clean first axis.

**Future-design note only (not in scope now):** even within Tb, a later campaign
must keep two modes distinct — (a) *Joback-predicted Tb vs experimental Tb*
(structure-only prediction error, the audit target), versus (b) any downstream
property that *consumes* Tb, which must use the predicted Tb, never the
experimental Tb, or it leaks. This scout records the distinction and stops.

## 3. Counts (web-verifiable subset; live enumeration honestly deferred)

The ThermoML Archive is an IUPAC-standard XML store whose declared property set
includes "boiling point temperatures" alongside densities, heat capacities,
activity coefficients, viscosities, critical constants, speed of sound, etc., for
**neat phases and mixtures**. The archive is keyed by article DOI, not by
property; there is **no published per-property compound count** for Tb on the
landing pages.

**Honest limitation:** the unique-pure-compound-with-Tb count, the
uncertainty-bearing-row count, the identity-mapping success rate, the family
distribution, and the Joback group-coverage fraction **cannot be enumerated
without downloading and parsing the `.tgz`**, which this scout does not do.
Reporting a fabricated count is forbidden. What can be stated:

| Quantity | Status | Basis |
| --- | --- | --- |
| Unique pure compounds with experimental Tb | **Not enumerable without download.** Order-of-magnitude estimate: low thousands of distinct substances across the archive, of which Tb-bearing pure compounds are a minority subset (hundreds–low-thousands). | Archive spans 2003–2019 across 5 thermophysics journals; Tb is one of many property types and is not the most common. Estimate only; basis = property-type breadth, not a count. |
| Rows carrying reported uncertainty | Expected to be **high** but per-row variable. | ThermoML is an IUPAC standard that carries explicit uncertainty fields per property value; uncertainty semantics are part of the schema. Population fraction not verifiable without parse. |
| Identity → canonical SMILES/InChI mapping success | Unknown; **dominant risk** (see §4 taxonomy). ThermoML records substances by name + registry identifiers per article, with variable normalization. | Requires the parse + a deterministic name/registry → InChI resolver run. |
| Chemical-family distribution | Unknown without parse; expected solvent/hydrocarbon/oxygenate-heavy, reflecting J. Chem. Eng. Data scope. | Journal scope, not a count. |
| Joback group coverage | Unknown without parse; a non-trivial out-of-coverage tail is expected (salts, metals, large/biological molecules, exotic heteroatom groups Joback never parameterized). | Joback's 41-group table is organics-only; see §5 group rules. |

**Dominant identity risks to flag now (verified as structural concerns, not
counted):** salts and ionic liquids (no neutral single-molecule Tb in the Joback
sense), mixtures/binary systems (the archive is mixture-heavy — a Tb of a mixture
is not a pure-component Tb), stereoisomers and tautomers (same or near-same Tb
but distinct identifiers, a dedup hazard), duplicate measurements of the same
compound across articles, and molecules outside Joback group coverage. Each of
these can *manufacture* an artificial "method failure" if admitted silently, so
they are exclusion candidates, not rows.

## 4. Joback fidelity fixture (the gating risk) — PASS, 0 mismatches / 25

### Estimator under test

`Tb = base + Σ nᵢ · ΔTb,i` (Kelvin), structure-only. Canonical Joback & Reid
(1987) intercept `base = 198.2`. Group contributions ΔTb,i taken from the
Joback & Reid table as tabulated on the Wikipedia "Joback method" page
(verified this session). Sanity anchor (Wikipedia / `thermo` library worked
example): acetone = 2×(−CH₃, 23.58) + 1×(>C=O non-ring, 76.75)
⇒ 198.2 + 47.16 + 76.75 = **322.11 K** — reproduced exactly.

### Reference set

Published Joback-**predicted** Tb values for a 25-compound comparison set:
24 from the molecularknowledge.com "Boiling Point: Joback's Method" worked
table, plus acetone from the Wikipedia/`thermo` worked example. These are
*predicted* values (the audit target is "did our implementation reproduce the
published method", not "is the method accurate"), which is why experimental Tb is
shown for context only and is **not** the match criterion.

### Base-constant normalization (a trap the fixture caught)

The molecularknowledge reference table is internally consistent with an
intercept of **198.12**, not 198.2: across 23 unambiguous compounds, every
published value equals (198.12 + ΣΔTb,i) to the table's 2-decimal precision (a
flat +0.08 K offset vs base 198.2). The canonical Joback & Reid intercept is
198.2 (used by Wikipedia and the `thermo` library, where acetone = 322.11 K).
This ~0.08 K intercept variant is a documented-in-the-wild difference, **not** a
group-assignment error — and silently comparing two implementations across this
gap would *manufacture* a false 100%-mismatch "fidelity failure." The fixture
therefore compares each compound against **its own source's intercept**. This is
precisely the class of artifact the task warned about.

A second trap the fixture caught: ethyl thioacetate (CH₃-C(=O)-S-CH₂-CH₃) was
first decomposed with a missing −CH₂−; the fixture flagged it as a ~23 K outlier
(a real group-decomposition error), and the corrected grouping
{2×−CH₃, 1×−CH₂−, 1×>C=O, 1×−S−} reproduces the published value exactly. This is
the "a wrong decomposition manufactures a method failure" lesson, demonstrated.

### Fixture table (computed vs published predicted; match = within 0.05 K)

| Compound | SMILES | Joback groups (count) | Σ ΔTb,i | base | computed Tb (K) | published Tb (K) | match |
| --- | --- | --- | ---: | ---: | ---: | ---: | :---: |
| Acetone | CC(C)=O | −CH₃(2), >C=O nr(1) | 123.91 | 198.2 | 322.11 | 322.11 | Y |
| Benzene | c1ccccc1 | ring =CH−(6) | 160.38 | 198.12 | 358.50 | 358.50 | Y |
| Toluene | Cc1ccccc1 | −CH₃(1), ring =C<(1), ring =CH−(5) | 188.24 | 198.12 | 386.36 | 386.36 | Y |
| o-Xylene | Cc1ccccc1C | −CH₃(2), ring =C<(2), ring =CH−(4) | 216.10 | 198.12 | 414.22 | 414.22 | Y |
| Styrene | C=Cc1ccccc1 | =CH₂(1), =CH−(1), ring =C<(1), ring =CH−(5) | 207.80 | 198.12 | 405.92 | 405.92 | Y |
| Isopropylbenzene | CC(C)c1ccccc1 | −CH₃(2), >CH−(1), ring =C<(1), ring =CH−(5) | 233.56 | 198.12 | 431.68 | 431.68 | Y |
| Bromobenzene | Brc1ccccc1 | −Br(1), ring =C<(1), ring =CH−(5) | 231.52 | 198.12 | 429.64 | 429.64 | Y |
| 1,2-Dichlorobenzene | Clc1ccccc1Cl | −Cl(2), ring =C<(2), ring =CH−(4) | 245.20 | 198.12 | 443.32 | 443.32 | Y |
| 2-Butyne | CC#CC | −CH₃(2), ≡C−(2) | 101.92 | 198.12 | 300.04 | 300.04 | Y |
| 1-Octanol | CCCCCCCCO | −CH₃(1), −CH₂−(7), −OH alc(1) | 276.62 | 198.12 | 474.74 | 474.74 | Y |
| Ethyl acetate | CCOC(C)=O | −CH₃(2), −CH₂−(1), −COO− ester(1) | 151.14 | 198.12 | 349.26 | 349.26 | Y |
| Tetrahydrofuran | C1CCOC1 | ring −CH₂−(4), ring −O−(1) | 139.82 | 198.12 | 337.94 | 337.94 | Y |
| Cyclohexanone | O=C1CCCCC1 | ring −CH₂−(5), ring >C=O(1) | 230.72 | 198.12 | 428.84 | 428.84 | Y |
| Cyclohexanol | OC1CCCCC1 | ring −CH₂−(5), ring >CH−(1), −OH alc(1) | 250.41 | 198.12 | 448.53 | 448.53 | Y |
| Ethanethiol | CCS | −CH₃(1), −CH₂−(1), −SH(1) | 110.02 | 198.12 | 308.14 | 308.14 | Y |
| Tetrahydrothiophene | C1CCSC1 | ring −CH₂−(4), ring −S−(1) | 160.70 | 198.12 | 358.82 | 358.82 | Y |
| Acrylonitrile | C=CC#N | =CH₂(1), =CH−(1), −CN(1) | 168.80 | 198.12 | 366.92 | 366.92 | Y |
| Benzaldehyde | O=Cc1ccccc1 | O=CH− ald(1), ring =C<(1), ring =CH−(5) | 236.90 | 198.12 | 435.02 | 435.02 | Y |
| n-Heptanoic acid | CCCCCCC(O)=O | −CH₃(1), −CH₂−(5), −COOH(1) | 307.07 | 198.12 | 505.19 | 505.19 | Y |
| n-Decanoic acid | CCCCCCCCCC(O)=O | −CH₃(1), −CH₂−(8), −COOH(1) | 375.71 | 198.12 | 573.83 | 573.83 | Y |
| (±)-1-Phenylethanol | CC(O)c1ccccc1 | −CH₃(1), >CH−(1), −OH alc(1), ring =C<(1), ring =CH−(5) | 302.86 | 198.12 | 500.98 | 500.98 | Y |
| Methyl salicylate | COC(=O)c1ccccc1O | −CH₃(1), −COO− ester(1), −OH phenol(1), ring =C<(2), ring =CH−(4) | 349.96 | 198.12 | 548.08 | 548.08 | Y |
| Succinic acid | OC(=O)CCC(O)=O | −CH₂−(2), −COOH(2) | 383.94 | 198.12 | 582.06 | 582.06 | Y |
| γ-Butyrolactone | O=C1CCCO1 | ring −CH₂−(3), ring −O−(1), ring >C=O(1) | 207.64 | 198.12 | 405.76 | 405.76 | Y |
| Ethyl thioacetate | CCSC(C)=O | −CH₃(2), −CH₂−(1), >C=O nr(1), −S−(1) | 215.57 | 198.12 | 413.69 | 413.69 | Y |

**Result: 25 compounds compared, 0 mismatches.** Fidelity fixture **passes** the
zero-mismatch gate for the implementation under test. The two near-misses that
arose during construction (intercept variant; thioacetate decomposition) were
both resolved to exact matches and are retained above as worked evidence that the
fixture detects exactly the failure modes that would otherwise fake a benchmark
result.

Caveats on the fixture: (a) coverage is solvent/hydrocarbon/oxygenate-heavy and
includes only single-bond-ambiguity-free assignments — it does **not** exercise
Joback's rarer nitrogen/sulfur-ring or multi-functional edge groups at scale;
(b) the reference set mixes two intercept conventions, which the fixture
normalizes but a future campaign must pin to one canonical intercept (recommend
198.2, Joback & Reid) before scoring anything; (c) `thermo`'s own documented
accuracy figure (438 compounds, AAE 12.91 K, 3.6% relative) is *method accuracy*,
not implementation fidelity, and is cited here only as context.

## 5. Frozen taxonomy (frozen BEFORE any error reading)

No global/aggregate performance and no per-compound model error is computed
anywhere in this scout. The following rules are frozen so a later benchmark
cannot retrofit them to the data.

### 5a. Compound-identity rules

1. Resolve each ThermoML substance to a canonical structure via registry id /
   name → **InChI** (primary key) and isomeric **SMILES** (secondary).
   InChIKey is the dedup key.
2. **Exclude**: salts, ionic liquids, and any multi-component/charged species
   (no neutral single-molecule Tb in the Joback sense).
3. **Exclude**: mixtures and binary/multinary systems — a system Tb is not a
   pure-component Tb.
4. Stereoisomers and tautomers that map to the same connectivity are **collapsed
   to one identity**; conflicting Tb values are kept as a flagged disagreement,
   not averaged into a row.
5. Duplicate measurements of one compound across articles are **deduplicated**;
   selection rule (e.g., uncertainty-weighted or most-recent) is deferred to the
   row-curation task and must be fixed before scoring.
6. A compound enters the audit set only if it has at least one
   experimental Tb with reviewable unit and uncertainty semantics.

### 5b. Joback group-assignment rules

1. Group set = the canonical Joback & Reid 41-group table (the table verified
   this session). Intercept pinned to **198.2** for any future scoring.
2. Ring vs non-ring variants of −CH₂−, >CH−, >C<, =CH−, =C<, −O−, >C=O, >NH,
   −S−, −N= are distinguished by ring membership exactly as Joback defines them.
3. Assignment must be **deterministic and total**: every heavy atom is covered by
   exactly one group; an unassignable atom ⇒ the molecule is **out-of-coverage**
   and excluded (not force-fit).
4. Out-of-Joback-coverage classes excluded up front: organometallics/metals,
   boron/silicon/phosphorus-centred groups Joback never parameterized, charged
   centres, and isotopically labelled species.
5. Group decomposition for the audit must be produced by a single deterministic
   tool and spot-checked against the fixture; the ethyl-thioacetate case is the
   retained regression example.

### 5c. Chemical-family taxonomy (for family-held-out splits)

Mutually exclusive top-level families, assigned by canonical functional-group
priority (highest-priority group present wins), frozen here:

`acids` → `esters/lactones` → `aldehydes` → `ketones` →
`alcohols/phenols` → `ethers` → `nitriles` → `amines` → `nitro` →
`thiols/sulfides` → `halocarbons` → `aromatic hydrocarbons` →
`alkenes/alkynes` → `alkanes/cycloalkanes`.

A molecule with multiple functions is placed in its single highest-priority
family (e.g., methyl salicylate → `esters/lactones`, not `alcohols/phenols`),
so families partition the set. Multi-functional molecules are additionally
**tagged** with their secondary functions for audit transparency but counted
once. This taxonomy is the unit of the future leave-one-family-out split.

## 6. Literature-comparability statement (honest)

ThermoML is an established benchmarking substrate: e.g., Chodera/Beauchamp et al.
(arXiv:1506.00262) use the ThermoML Archive to benchmark force fields against
**neat-liquid densities and dielectric constants** — not a Tb group-contribution
audit. Out-of-distribution molecular-property benchmarking exists generally
(e.g., the "BOOM" benchmark, arXiv:2505.01912, across many models/tasks), and
group-contribution Tb methods are widely evaluated against experiment. During
this initial scouting I did **not** identify a *directly comparable, openly
reproducible, family-held-out ThermoML audit of a frozen Joback Tb estimator
under null / per-class / shuffled controls*. I do **not** claim such work exists
nowhere — only that none was found in this bounded check, and a fuller literature
sweep belongs to the campaign-design task, not this scout.

## 7. Verdict: SOURCE_LIMITED

| Gate | Outcome |
| --- | --- |
| Source route pinned | Yes — DOI `10.18434/mds2-2422`, PDR + `.tgz` route, fetch/verify command, SHA-256 marked PENDING (not fabricated). |
| Redistribution terms | **Permission-bounded / mixed.** NIST open-license wrapper + TRC citation request, but files are present under *publisher permission* with a foreign-copyright/non-NIST-copyright carve-out. Facts extractable with attribution; file bytes not re-hostable by default. |
| Tb-only + Tc exclusion | Yes — Tc excluded for leakage; predicted-vs-experimental distinction recorded as future-design note. |
| Counts | **Partially blocked** — not enumerable without download; honest estimates + bases given, identity risks flagged. |
| Joback fidelity fixture | **PASS** — 25 compounds, 0 mismatches (base-constant trap and a decomposition trap both caught and resolved). |
| Frozen taxonomy | Yes — identity, group-assignment, and family rules frozen before any error reading. |

**Reasoning (one paragraph).** The Joback implementation is faithful (clean
zero-mismatch fixture, with the fixture demonstrably catching the two artifacts
that would otherwise fake a benchmark), and the official source route is pinned
and pinnable. But the verdict is **not READY**, for two honest reasons: (1) the
reuse posture is *permission-bounded*, not open — ThermoML files are provided to
NIST "with permission of the journal publishers," with an explicit foreign /
non-NIST copyright carve-out in the NIST license, so the safe default is
metadata-only (locator + SHA-256 + attribution-bearing curated facts), not
file vendoring; and (2) the Tb counts that would size the audit (unique pure
compounds, uncertainty coverage, identity-mapping success, family balance, group
coverage) are not web-enumerable without downloading and parsing the archive,
which this scout deliberately did not do. Both are *limitations of source
clearance and enumeration*, not implementation defects — which is the precise
definition of **SOURCE_LIMITED**. READY would require a maintainer-cleared,
checksum-pinned snapshot fetch plus a first deterministic parse that reports the
real Tb-pure-compound and group-coverage counts.

### Recommended next steps (not authorized here)

- Maintainer-approved, checksum-pinned single snapshot fetch of the archive
  (`blocker_type: T4_snapshot_approval`), SHA-256 recorded at fetch.
- One deterministic parse pass that reports the real counts in §3 and writes a
  `source_manifest.yaml` entry — still no benchmark metric.
- A bounded Tb row-curation task applying the §5 frozen rules, with salts /
  mixtures / out-of-coverage molecules excluded and dedup applied.
- Only then a baseline/benchmark task may score Joback-predicted vs experimental
  Tb under null / per-class / shuffled controls and a leave-one-family-out split.

## Output-routing summary

- **Verdict:** `SOURCE_LIMITED`.
- **Canonical destination:** source-readiness gate for a future *Thermophysical
  Property Transfer Audit* campaign (boiling-point slice). This note is the gate
  artifact: `docs/reviews/thermoml-joback-source-readiness-scout.md`.
- **Rows committed:** none beyond license-clear scope — no archive bytes, no
  ThermoML files, no curated rows, no fabricated counts or SHA-256.
- **Benchmark metric:** none computed. No global/aggregate performance, no
  per-compound model error.
- **Review tier:** `none` (scout; no RESULT / PRED / CLAIM / KNOW produced).
- **Gate A:** not attempted. **Gate B:** not attempted.
- **Claim impact:** none (no claim change).
- **Knowledge impact:** none (a future task proposal at most — the campaign
  scaffold, snapshot, and curation tasks are separate and maintainer-gated).
- **Limitations / blockers:** (1) reuse terms permission-bounded → metadata-only
  default, foreign/non-NIST-copyright carve-out; (2) Tb counts not enumerable
  without a maintainer-approved snapshot fetch + parse; (3) fidelity fixture
  covers a solvent/hydrocarbon/oxygenate-heavy slice and does not stress Joback's
  rare heteroatom-ring/multifunctional groups at scale; (4) two intercept
  conventions (198.2 canonical vs 198.12 in one reference table) must be pinned
  to one value before any scoring.

## Sources (consulted this scout)

- NIST ThermoML Archive: https://www.nist.gov/mml/acmd/trc/thermoml/thermoml-archive
- NIST TRC ThermoML: https://trc.nist.gov/ThermoML/
- NIST PDR (DOI 10.18434/mds2-2422): https://data.nist.gov/od/id/mds2-2422
- data.gov ThermoML/Data Archive mirror (DOI, `.tgz` route, coverage): https://catalog.data.gov/dataset/thermoml-data-archive
- NIST open-data license: https://www.nist.gov/open/license
- Joback method (group table, formula 198.2, acetone 322.11 K): https://en.wikipedia.org/wiki/Joback_method
- `thermo` library Joback docs (acetone CC(=O)C → 322.11 K; 438-compound accuracy): https://thermo.readthedocs.io/thermo.group_contribution.joback.html
- molecularknowledge.com "Boiling Point: Joback's Method" (25-compound predicted-Tb reference table): http://www.molecularknowledge.com/Techniques/TbJoback/TbJoback.html
- Group-contribution method overview: https://en.wikipedia.org/wiki/Group-contribution_method
- ThermoML force-field benchmarking precedent (densities/dielectric, not Tb): https://arxiv.org/pdf/1506.00262
- BOOM out-of-distribution molecular-property benchmark (general OOD, not ThermoML Tb): https://arxiv.org/pdf/2505.01912
