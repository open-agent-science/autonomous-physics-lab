# Prospective Reveal Source Admissibility — Shared Policy

- Applies to EVERY sealed-prediction surface: the nuclear mass registry, the
  FRB repeater-propensity registry, and any future prospective registry.
  Domain protocols (nuclear, FRB) reference this document; they may add
  stricter domain rules but may not relax these.
- Origin: generalized from the 2026-07-13 no-peek incident (TASK-1023 scout,
  PR #1534, verdict `BLOCKED_NO_PEEK_AUDIT`), where a general web search
  surfaced target-related values in result snippets before any source
  manifest existed. The executor stopped honestly; this policy makes that
  outcome a rule instead of a judgment call.
- Governance guardrail: incidents generalize into policy ONLY through
  maintainer-reviewed changes like this one (incident -> generalized
  invariant -> regression test). Agents do not extend or relax this policy
  autonomously.

## The rule

After a prediction registry entry is registered/frozen for a surface:

1. **Source admissibility scouting** for that surface uses ONLY direct
   official metadata surfaces (publisher/collaboration release pages,
   registrar records) or a pre-approved locator allowlist.
2. **General web search, AI search summaries, and search-result snippets are
   forbidden** for target-aware scouting: a snippet can surface target
   values before any manifest exists.
3. Phase one may record ONLY: source title, publishing organization, release
   date, DOI/URL, license, immutable locator, and checksum feasibility.
   No measured values, tables, or per-target content.
4. **Target identifier matching** is allowed only AFTER the source manifest
   is reviewed and approved.
5. **Target values** may be read only inside a separate, approved reveal
   task, after the source-manifest and no-peek gates.
6. Any unintended exposure of a target value:
   - immediate stop;
   - verdict `BLOCKED_NO_PEEK_AUDIT`;
   - no manifest is created and no scoring occurs in that context;
   - the retry runs in a fresh clean session — preferably a different
     contributor lane; the contaminated context never continues the scout.

## Machine-readable task fields

Reveal-scout tasks on sealed surfaces declare:

```yaml
source_discovery_mode: official_metadata_only
search_result_snippets_allowed: false
target_matching_requires_manifest_approval: true
value_access_requires_reveal_task: true
no_peek_context_status: clean
```

On contamination the executor records:

```yaml
no_peek_context_status: contaminated
prospective_reveal_eligibility: false
```

## Domain protocol references

- Nuclear: `docs/nuclear-prediction-reveal-protocol.md`,
  `docs/nuclear-reveal-source-readiness-checklist.md`.
- FRB: `docs/reviews/frb-reveal-source-admissibility-contract.md`
  (TASK-0995 contract; its admissible/inadmissible source classes remain the
  domain layer on top of this shared policy).
