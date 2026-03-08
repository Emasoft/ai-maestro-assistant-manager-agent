# Legacy Approval Types Reference

## Table of Contents
- [Push Approval](#push-approval)
- [Merge Approval](#merge-approval)
- [Publish Approval](#publish-approval)
- [Security Approval](#security-approval)
- [Design Approval](#design-approval)

The following approval types from v1 are still supported for backward compatibility with non-governance workflows. These use the standard AI Maestro messaging system rather than the GovernanceRequest API.

## Push Approval

**Trigger**: Code is ready to be pushed to remote repository

**Workflow**:
1. Receive approval request from AMOA/AMIA
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
4. Send approval response to requesting role

## Merge Approval

**Trigger**: PR is ready to be merged

**Workflow**:
1. Receive approval request from AMIA
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
4. Send approval response to AMIA

## Publish Approval

**Trigger**: Package/release is ready to be published

**Workflow**:
1. Receive approval request from AMIA
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
4. Send approval response to AMIA

## Security Approval

**Trigger**: Action with security implications requires authorization

**Workflow**:
1. Receive approval request from any role (AMAA/AMOA/AMIA)
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

**Trigger**: AMAA (Architect) has completed design document

**Workflow**:
1. Receive completion signal from AMAA
2. Present to user:
   ```
   ## Design Approval Requested

   **Design**: {design_name}
   **Document**: {path_to_design_doc}
   **Modules**: {count} modules defined
   **Estimated Scope**: {scope_summary}

   Review the design document and approve to proceed with implementation.
   - [Approve] - Proceed to orchestration
   - [Request Changes] - Send back to AMAA
   - [Discuss] - I have questions
   ```
3. Record user decision
4. If approved, create handoff to AMOA
