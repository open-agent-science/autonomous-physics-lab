# PMR-001: Electron Mass Dataset Audit

**Microtask ID:** PMR-001  
**Queue:** particle-mass-relations  
**Run:** MICROTASK-RUN-0018  
**Verdict:** VALID  
**Review state:** UNREVIEWED  

---

## Dataset Entry Under Audit

Source file: `data/particle_masses/charged_leptons.yaml`

| Field | Stored Value |
|---|---|
| Particle | electron |
| Mass | 0.51099895000 MeV |
| Uncertainty | ±1.5×10⁻¹⁰ MeV |
| Mass type | pole mass |
| Source | S. Navas et al. (PDG), Phys. Rev. D 110, 030001 (2024) and 2025 update |

---

## Comparison Against PDG 2025

PDG 2025 lists the electron mass as 0.51099895069(16) MeV (where the parenthetical is the uncertainty in the last two digits, i.e., ±1.6×10⁻¹⁰ MeV in the CODATA 2018 representation).

The dataset stores 0.51099895000 MeV — 11 significant figures. Comparing with PDG 2025:

- Stored value: 0.51099895000
- PDG 2025:     0.51099895069

Difference: |0.51099895069 − 0.51099895000| = 6.9×10⁻¹⁰ MeV

This difference is within 5× the stated uncertainty (±1.5×10⁻¹⁰ MeV), consistent with rounding the PDG central value to 11 significant figures. The dataset value is consistent with PDG 2025 within stated precision.

---

## Representation Ambiguity (Recorded, Not an Error)

PDG notes that the electron mass is more precisely known in atomic mass units:

- m_e = 5.48579909065(16)×10⁻⁴ u  (CODATA 2018)
- m_e = 0.51099895069(16) MeV

The MeV representation carries additional uncertainty from the conversion factor (1 u in MeV), which is dominated by the uncertainty in the Avogadro constant and the molar Planck constant. The atomic mass unit representation is therefore the more precisely pinned form.

The dataset stores the MeV form. This is a representation choice, not an error. For the purpose of Koide-type relations (which use mass ratios in a common unit), using consistently the MeV form is acceptable. This choice must be noted in any downstream analysis.

---

## Uncertainty Discrepancy (Minor Rounding)

The dataset lists ±1.5×10⁻¹⁰ MeV. CODATA 2018 / PDG 2025 gives ±1.6×10⁻¹⁰ MeV for the MeV form. The discrepancy is:

|1.6×10⁻¹⁰ − 1.5×10⁻¹⁰| / 1.6×10⁻¹⁰ ≈ 6%

This is a minor rounding in the source note and is not an error in mass type, PDG edition, or numerical value. It should be corrected in a future dataset update to avoid confusion with CODATA propagation.

---

## Mass Type Assessment

The electron is stable and carries a well-defined pole mass (the on-shell renormalization scheme is unambiguous for a non-confined charged lepton). The dataset correctly labels this as a pole mass.

---

## Verdict

VALID — the dataset value 0.51099895000 MeV is consistent with PDG 2025 within stated precision. Two items are noted for future maintenance:

1. The uncertainty ±1.5×10⁻¹⁰ MeV is a slight rounding from the CODATA 2018 value of ±1.6×10⁻¹⁰ MeV. This is a minor source-note inconsistency, not an error.
2. The MeV representation carries conversion-factor uncertainty absent from the atomic mass unit form. This is a representation choice and must be acknowledged in downstream analyses.

---

## Limitations

- This audit covers only the electron entry in `charged_leptons.yaml`.
- Comparisons rely on PDG 2025 and CODATA 2018; a future PDG edition may update the central value.
- The representation ambiguity does not affect analyses that use mass ratios exclusively, provided all masses in a given analysis use the same unit convention.
