# AGENT-RUN-0077 Preflight

- Task: `TASK-0816`
- Dataset: `data/quantum_dots/qd-0003-almeida-2023-inp-optical.yaml`
- Rows: the six committed Almeida 2023 InP `absorption_peak_eV` rows only.
- Diagnostic family: `E = E_Almeida_fixed(L) + b_train`, where `b_train` is one
  fitted additive offset per training fold.
- Negative control: `E = mean(E_train)`.
- Complexity cap: one fitted parameter for the diagnostic and one for the
  negative control.
- Forbidden in this run: new rows, open-ended formula search, TASK-0226
  unblock, RESULT/PRED/CLAIM/KNOW creation, and transfer/generalization claims.
