# Error Handling for GitHub Operation Routing

## Table of Contents
- [Ambiguous Routing](#ambiguous-routing)
- [Missing Context](#missing-context)
- [Missing Team Label](#missing-team-label)
- [Agent Unavailable](#agent-unavailable)
- [Task Sync Failures](#task-sync-failures)
- [Cross-Team Boundary Violation](#cross-team-boundary-violation)

## Ambiguous Routing

If operation could go to multiple agents:
1. Default to AMIA (most GitHub operations)
2. Ask user for clarification if design/module context unclear
3. Log routing decision for audit

## Missing Context

If handoff lacks required information:
1. Query user for missing details
2. Search locally (design search) before asking
3. Include "INCOMPLETE" flag in handoff for receiving agent

## Missing Team Label

If an issue has no team label:
1. Check the module/design ownership for team inference
2. Check the requesting agent's team affiliation
3. If still ambiguous, ask the user to assign a team
4. Do NOT route until a team label is applied

## Agent Unavailable

If target agent is not responding:
1. Queue the handoff
2. Notify user of delay
3. Retry after configured interval
4. Escalate to user if repeated failures

## Task Sync Failures

If task file sync fails:
1. Log the failure with timestamp and intended state change
2. Queue the sync for retry
3. On next successful operation, reconcile queued syncs
4. If task file is corrupted, rebuild from GitHub issue state using `gh issue list --repo "$OWNER/$REPO" --label "team:${TEAM_ID}" --state all --json` and jq

## Cross-Team Boundary Violation

If an agent attempts to modify an issue outside its team:
1. Block the operation
2. Log the violation attempt
3. Notify AMAMA for escalation
4. AMAMA may approve the cross-team operation or redirect
