# Subprocess Environment Guardrail Audit

**Task:** `TASK-0623`
**Status:** workflow guardrail, no production behavior change except a new helper
**Verdict:** `ENV_OVERRIDE_GUARDRAIL_ADDED`

## Scope

This audit checked subprocess environment usage in tests, scripts, and registry
helpers for replacement environments such as `env={...}` that can accidentally
drop Python dependency discovery, `PATH`, virtual-environment metadata, or
GitHub/proxy context.

The concrete repeated failure mode came from a test launching a helper CLI with a
replacement environment containing only a proxy override. That pattern can pass
locally and fail in CI when the subprocess loses dependency discovery.

## Change

The PR adds `physics_lab.registry.pr_capability.env_with_overrides(...)` as the
canonical small helper for child-process overrides. It starts from the inherited
environment by default, then applies explicit key overrides or removals.

`tests/test_task_claiming.py` now uses the helper when launching
`scripts/apl_task_occupancy.py` with a suspicious-proxy and `PATH` override. The
regression asserts the helper CLI still starts cleanly and does not fail with a
dependency import error.

`tests/test_pr_capability.py` adds direct coverage for inherited-env preservation
and explicit key removal.

## Audit Notes

- Intentional minimal-env unit tests remain allowed when the test scenario is
  missing-tool, missing-token, dependency-loss, or minimal-environment behavior.
- Existing production helper paths that already build child environments from
  inherited env maps were left unchanged.
- No CI requirement, dependency requirement, or repository validation rule was
  relaxed.
- No scientific rows, metrics, results, claims, or knowledge entries were
  touched.

## Documentation

`docs/cross-platform-compatibility.md` now tells agents to use inherited
environment overrides for subprocesses and reserve tiny replacement env dicts
for explicitly named/commented minimal-env tests.

## Output Routing Summary

- Task verdict: `ENV_OVERRIDE_GUARDRAIL_ADDED`.
- Canonical destination: helper, tests, documentation, and this audit note.
- Review tier: `none`.
- Gate A status: `not_applicable`.
- Gate B status: `not_applicable`.
- Claim impact: `none`.
- Knowledge impact: reusable developer workflow convention only.
- Publication blocker: none for this infrastructure guardrail.
