# Operational Approval Types Reference

## Table of Contents
- [Push Approval](#push-approval)
- [Merge Approval](#merge-approval)
- [Publish Approval](#publish-approval)
- [Security Approval](#security-approval)
- [Design Approval](#design-approval)

These are **operational** approvals (deploys, merges, pushes, releases, design
sign-off) — distinct from the governance lifecycle ops handled via the
GovernanceRequest API. They travel on the AMP messaging system, arriving from
the team's **CHIEF-OF-STAFF** (R6 v3 — a team member never messages you directly;
the COS is the sole entry point) and surfaced by you to the user. Publish,
deploy, and security actions are **hard-floor escalations to the USER** (Tier 3,
`trdd-approval-tiers.md` / `manager-approval-defaults.md`) regardless of any
autonomous-fallback verdict.

## Push Approval

**Trigger**: Code is ready to be pushed to remote repository

**Workflow**:
1. Receive approval request via the team's CHIEF-OF-STAFF
2. Present to user:
   ```
   ## Push Approval Requested

   **Branch**: {branch_name}
   **Changes**: {summary_of_changes}
   **Files Modified**: {count}
   **Tests Status**: {passed/failed}

   Do you approve pushing these changes?
   - [Approve] - Push to remote
   - [Reject] - Cancel push
   - [Review] - Show me the changes first
   ```
3. Record user decision
4. Send approval response back via the CHIEF-OF-STAFF

## Merge Approval

**Trigger**: PR is ready to be merged

**Workflow**:
1. Receive approval request via the CHIEF-OF-STAFF (originated by the INTEGRATOR)
2. Present to user:
   ```
   ## Merge Approval Requested

   **PR**: #{pr_number} - {pr_title}
   **Branch**: {source} -> {target}
   **Reviews**: {review_status}
   **CI Status**: {ci_status}
   **Conflicts**: {yes/no}

   Do you approve merging this PR?
   - [Approve] - Merge PR
   - [Reject] - Close without merging
   - [Request Changes] - Add comments
   ```
3. Record user decision
4. Send approval response back via the CHIEF-OF-STAFF

## Publish Approval

**Trigger**: Package/release is ready to be published

**Workflow**:
1. Receive approval request via the CHIEF-OF-STAFF (originated by the INTEGRATOR)
2. Present to user:
   ```
   ## Publish Approval Requested

   **Package**: {package_name}
   **Version**: {version}
   **Target**: {npm/pypi/github releases/etc}
   **Changelog**: {summary}
   **Breaking Changes**: {yes/no}

   Do you approve publishing this release?
   - [Approve] - Publish
   - [Reject] - Cancel
   - [Review] - Show release notes
   ```
3. Record user decision
4. Send approval response back via the CHIEF-OF-STAFF

## Security Approval

**Trigger**: Action with security implications requires authorization

**Workflow**:
1. Receive approval request via the CHIEF-OF-STAFF (originated by any team role)
2. Present to user:
   ```
   ## Security Approval Required

   **Action**: {action_description}
   **Risk Level**: {low/medium/high/critical}
   **Affected Systems**: {list}
   **Justification**: {reason_for_action}
   **Rollback Plan**: {description}

   This action has security implications. Do you authorize it?
   - [Authorize] - Proceed with action
   - [Deny] - Block action
   - [More Info] - Explain risks in detail
   ```
3. Record user decision with timestamp
4. Send authorization response

## Design Approval

**Trigger**: the ARCHITECT has completed a design document

**Workflow**:
1. Receive the completion signal via the CHIEF-OF-STAFF
2. Present to user:
   ```
   ## Design Approval Requested

   **Design**: {design_name}
   **Document**: {path_to_design_doc}
   **Modules**: {count} modules defined
   **Estimated Scope**: {scope_summary}

   Review the design document and approve to proceed with implementation.
   - [Approve] - Proceed to orchestration
   - [Request Changes] - Send back to the ARCHITECT (via the COS)
   - [Discuss] - I have questions
   ```
3. Record user decision
4. If approved, relay the go-ahead to the team via the CHIEF-OF-STAFF
