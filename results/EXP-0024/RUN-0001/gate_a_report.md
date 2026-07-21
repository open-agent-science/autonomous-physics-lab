# Gate A Report — RESULT-0032

Gate A mechanical fields are populated for an `AGENT_PUBLISHED` negative/control result. Verify with:

```text
python scripts/apl_check_result_publication.py results/EXP-0024/RUN-0001/result.yaml --root .
python -m physics_lab.cli validate-repo . --strict --fail-on-warnings
```

Expected publication-gate verdict: `PASS`. Gate B is not attempted.
