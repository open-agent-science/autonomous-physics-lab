# Nuclear Post-Registration Reveal-Source Trigger Ledger

**Task:** `TASK-1072`
**Campaign:** `nuclear-mass-surface`
**Task verdict:** `MONITOR_LEDGER_RATIFIED`
**Review date:** 2026-07-19

## Scope

This ledger converts the clean `TASK-1031` source-readiness outcome into an
event-triggered monitoring contract. The relevant prediction registration date
is `2026-05-20`. `TASK-1031` found only pre-registration AME2020/NUBASE2020
official records and recorded zero target-value or measured-status exposure.
That evidence is immutable here: this task did not repeat the search, browse
for a replacement source, open a source payload, query a target, or inspect a
value.

The standing posture is `MONITOR_ONLY_NO_SCOUT`. A calendar interval is never a
trigger. The absence of a new official event produces no task, no new review
note, and no recurring check record.

## Qualifying Official Signals

A signal may enter the ledger only through one of these classes:

| Signal class | Qualifying event | Required metadata |
| --- | --- | --- |
| `official_issuing_body_release_notice` | A direct notice from the Atomic Mass Data Center, IAEA Nuclear Data Services, the issuing laboratory/collaboration, or another maintainer-approved issuing body announcing a post-registration nuclear-mass evaluation or primary measurement release | Issuer, source class, publication or release date, version or edition, stable official locator, and a value-free reason the release may contain post-registration information |
| `official_repository_version_record` | A new versioned record on an official repository or edition page whose identity indicates a post-registration nuclear-mass evaluation or primary measurement release | Repository owner, record/version identity, release date, stable official locator, and source-class rationale |
| `official_doi_metadata_record` | DOI or registrar metadata that directly identifies a post-registration nuclear-mass evaluation or primary measurement release | Publisher or collaboration, DOI, publication date, version-of-record status, stable locator, and source-class rationale |

Every recorded signal must also include the observer, observation timestamp,
the route by which it became visible, and an attestation that no target values,
per-target measured status, tables, snippets, or payload content were exposed.
A title or locator that cannot establish the issuing body, release identity,
and post-registration timing is not qualifying evidence.

## Allowed Visibility Routes

The project may learn that a possible event exists only through:

- a maintainer-provided direct official release alert;
- an issuing-body notice already encountered through normal project
  monitoring; or
- another directly locatable official metadata signal with a stable issuer and
  version, release, or DOI identity.

These routes permit recording the metadata signal. They do not authorize an
agent to search target names, run periodic source scouts, inspect previews, or
open a value-bearing payload.

## Explicit Non-Triggers

The following must not create a task or reopen source scouting:

- a calendar interval, reminder, or elapsed month;
- generic web-search results, search snippets, AI summaries, news, or secondary
  reporting;
- theory, model, forecast, review, or phenomenology papers without an official
  evaluation or primary measurement release identity;
- unchanged AME2020 or NUBASE2020 mirrors, landing pages, or archive copies;
- preprints without an official issuing-body release, repository version, or
  version-of-record DOI identity;
- target-name, nuclide, isotope, prediction-id, or target-region searches;
- a preview, abstract, table of contents, snippet, or attachment that already
  exposes target values or per-target measured status; and
- an ambiguous date, issuer, version, source class, or locator.

Pre-registration sources remain `SOURCE_PREDATES_REGISTRATION`. Repeatedly
rediscovering them adds no evidence and must not be recorded as monitoring
activity.

## State Transition

The only allowed transition is:

1. `MONITOR_ONLY_NO_SCOUT`: no active search or periodic availability check.
2. `OFFICIAL_METADATA_SIGNAL_RECORDED`: a qualifying signal and all required
   evidence fields are recorded without value or target exposure.
3. `SOURCE_MANIFEST_DECISION_PENDING`: a fresh, independent, metadata-only
   source-manifest task is proposed and reviewed. It may verify identity,
   timing, source class, rights posture, immutable locator, and checksum
   feasibility only.
4. `SOURCE_MANIFEST_APPROVED` or `SOURCE_MANIFEST_REJECTED`: the maintainer
   accepts or rejects that manifest decision. Rejection returns the campaign to
   `MONITOR_ONLY_NO_SCOUT`.
5. Only after approval may a separate target-matching/no-peek task be opened.
6. Only after target matching and no-peek review may a separate reveal/scoring
   task be authorized.

No step may be skipped. A trigger never authorizes download, payload access,
target matching, measured-status inspection, or scoring.

## Stop And Session-Retirement Rule

If any target value, uncertainty, per-target measured status, table row, or
value-bearing preview appears before source-manifest approval:

1. stop immediately with `STOP_VALUE_EXPOSURE`;
2. do not create or approve a source manifest in that context;
3. record only the exposure class and stop point, never the exposed content;
4. retire the contaminated session from all source-scout, target-matching, and
   reveal work; and
5. preserve every frozen prediction payload and target identity unchanged.

Any retry requires a fresh clean context and explicit maintainer routing under
the shared prospective-reveal source-admissibility policy.

## Decision

`MONITOR_LEDGER_RATIFIED`

The event classes, evidence fields, non-triggers, state transitions, and
stop conditions are explicit. No unresolved policy choice requires a periodic
scout. The campaign remains `MONITOR_ONLY_NO_SCOUT` until a qualifying official
metadata signal is recorded.

## Output Routing

- Task verdict: `MONITOR_LEDGER_RATIFIED`
- Canonical destination: this trigger ledger, the synchronized Nuclear reveal
  protocol, and the Nuclear campaign pointer
- Review tier: `none`
- Gate A status: not attempted
- Gate B status: not attempted
- Claim impact: none
- Knowledge impact: none
- Prediction impact: none; no payload or target identity changed
- Result impact: none
- Limitations / blockers: no new source is asserted to exist; source-manifest
  approval, target matching, no-peek review, and reveal authorization remain
  separate future gates after a qualifying event
