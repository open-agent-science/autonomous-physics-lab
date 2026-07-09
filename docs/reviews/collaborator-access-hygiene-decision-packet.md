# Collaborator Access Hygiene Decision Packet

Task: `TASK-0962`
Claim issue: `#1448`
Decision packet: `decisions/DEC-20260709-collaborator-access-hygiene.yaml`

## Scope

This packet prepares a maintainer-only repository settings decision. It does
not change collaborator permissions, branch protection, repository visibility,
secrets, CODEOWNERS, or any scientific artifact.

Repo access review is a `repo_settings_change`, so it is Class 2 under
`docs/decision-autonomy-policy.md`: agents may prepare evidence and options,
but only the maintainer can inspect private collaborator settings and click the
final access changes.

## Evidence Access Status

The executor attempted the required local GitHub CLI path:

```bash
gh auth status
```

Observed status:

```text
github.com
  X Failed to log in to github.com account akutenyov (default)
  - Active account: true
  - The token in default is invalid.
```

The direct collaborator list is not a public repository artifact and the
available GitHub connector does not expose a collaborator-permission endpoint.
Therefore this packet does not invent collaborator names, roles, or activity
judgements. The maintainer should run the read-only evidence commands below
before applying any access change.

## Maintainer Evidence Commands

Run from the repository root with a maintainer-authorized GitHub CLI session:

```bash
gh api --paginate \
  repos/open-agent-science/autonomous-physics-lab/collaborators \
  -f affiliation=direct \
  --jq '.[] | [.login, .permissions.admin, .permissions.maintain, .permissions.push, .permissions.triage, .permissions.pull] | @tsv'
```

For each listed login, collect recent activity in the repository:

```bash
LOGIN=<github-login>
gh pr list --repo open-agent-science/autonomous-physics-lab --author "$LOGIN" --state all --limit 20 \
  --json number,title,state,mergedAt,updatedAt,headRefName,url
gh issue list --repo open-agent-science/autonomous-physics-lab --author "$LOGIN" --state all --limit 20 \
  --json number,title,state,updatedAt,url
gh api --paginate "repos/open-agent-science/autonomous-physics-lab/commits?author=$LOGIN&per_page=100" \
  --jq '.[0:10][] | [.sha[0:12], .commit.author.date, .commit.message] | @tsv'
```

Optional review participation check:

```bash
LOGIN=<github-login>
gh search prs --repo open-agent-science/autonomous-physics-lab --reviewed-by "$LOGIN" --limit 20 \
  --json number,title,state,updatedAt,url
```

## Decision Table Template

Fill this table from the commands above before taking any settings action.

| Collaborator | Current direct role evidence | Last activity | Artifacts touched | Options | Recommended default |
| --- | --- | --- | --- | --- | --- |
| `<login>` | `<pull/triage/push/maintain/admin booleans from API>` | `<latest PR/issue/review/commit>` | `<paths or artifact classes>` | keep write / downgrade to triage-read / remove | `keep current role until evidence is filled` |

## Recommended Defaults

Until the maintainer fills the table with verified role and activity evidence:

1. **No access changes.** Do not downgrade, remove, or grant access from this
   agent-prepared packet alone.
2. **Keep branch protection as the primary safety layer.** Current task/PR
   protocol and protected `main` already require review before merge.
3. **Apply least privilege after evidence is visible.** For each collaborator:
   choose the smallest role that matches recent repo activity and expected
   future contribution.

Suggested per-person rubric after evidence is collected:

| Evidence pattern | Maintainer option |
| --- | --- |
| Active maintainer or frequent reviewer/merger | keep current role if it matches operational need |
| Active task contributor who opens PRs but does not need direct pushes | downgrade to triage/read if write is not operationally needed |
| No recent PR, issue, review, or commit activity and no known upcoming role | remove direct access or downgrade to read/triage, at maintainer discretion |
| Unclear identity or unclear operational need | keep temporarily and ask the person before changing access |

## Maintainer Click Path

For each collaborator selected for a change:

1. GitHub repository -> `Settings`.
2. `Collaborators and teams`.
3. Locate the collaborator login from the evidence table.
4. Choose the maintainer-approved role change or removal.
5. Record the action in the decision packet or a follow-up closeout note.

Do not apply changes in bulk from stale screenshots or chat memory. Re-run the
read-only collaborator command immediately before clicking.

## Non-Goals

- No repository settings are changed by this PR.
- No access is removed or granted by this PR.
- No collaborator identity is inferred from branch names, PR authorship, or
  old docs alone.
- No scientific artifact, claim, prediction, knowledge entry, result, or source
  dataset is changed.

## Output Routing

- Task verdict: `MAINTAINER_PACKET_READY_WITH_PRIVATE_API_FILL_IN_REQUIRED`.
- Canonical destination: this review packet plus
  `decisions/DEC-20260709-collaborator-access-hygiene.yaml`.
- Review tier: `none`.
- Gate A status: not applicable.
- Gate B status: not applicable.
- Claim impact: none.
- Knowledge impact: none.
- Repository settings impact: none in this PR; any future action is
  maintainer-only.
- Blocker before applying changes: maintainer-authenticated collaborator API
  evidence must be collected and pasted into the decision table.
