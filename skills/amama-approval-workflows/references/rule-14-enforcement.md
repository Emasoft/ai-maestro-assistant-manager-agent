# RULE 14: User Requirements Are Immutable

## Contents

- 1.1 When handling user requirements in any workflow
- 1.2 When detecting potential requirement deviations
- 1.3 When a technical constraint conflicts with a requirement
- 1.4 When documenting requirement compliance
- 1.5 RULE 14 enforcement via GovernanceRequest types

## 1.1 Core Rule

**RULE 14: User requirements are immutable.** No agent may modify, reinterpret, downgrade, or omit any user requirement without explicit written approval from the user.

This applies to:
- Functional requirements (what the system must do)
- Non-functional requirements (performance, security, scale targets)
- Constraints (technology choices, budget limits, timeline)
- Success criteria (acceptance conditions)

## 1.2 Detecting Deviations

A requirement deviation occurs when:
- An implementation does not match the requirement specification
- A workaround is applied that changes the expected behavior
- A requirement is marked as "out of scope" without user approval
- A requirement is reinterpreted to mean something different
- A partial implementation is accepted as "complete"

**Action on deviation detected:**
1. STOP the current task
2. Document the deviation in a Requirement Issue Report
3. Escalate to AMCOS (or directly to the user if AMCOS is unavailable)
4. BLOCK progress on the affected requirement until user decides

## 1.3 When Technical Constraints Conflict

If a technical constraint makes a requirement infeasible:
1. Document the constraint clearly (what, why, evidence)
2. Propose alternatives that satisfy the requirement intent
3. Send escalation to AMCOS with `priority: "urgent"`
4. Wait for user decision — do NOT proceed with a workaround

**Forbidden actions:**
- Silently dropping a requirement
- Implementing a "close enough" alternative without approval
- Marking a requirement as "done" when it was modified

## 1.4 Requirement Compliance Documentation

Every workflow output MUST include requirement compliance status:

```markdown
## Requirement Compliance
- Requirements addressed: X/Y
- Deviations: [list or NONE]
- Pending user decisions: [list or NONE]
```

## 1.5 RULE 14 Enforcement via GovernanceRequest Types

Every governance operation that could affect user requirements MUST be routed through the GovernanceRequest API. The following table maps RULE 14 protected operations to their corresponding GovernanceRequestType. Any attempt to perform these operations without a `dual-approved` GovernanceRequest is a RULE 14 violation.

### Operation-to-GovernanceRequestType Mapping

| RULE 14 Protected Operation | GovernanceRequestType | Why RULE 14 Applies |
|-----------------------------|----------------------|---------------------|
| Adding an agent to a team changes team composition, which may affect delivery capacity and requirement timelines | `add-to-team` | Team composition is a constraint the user sets; changing it without approval could compromise delivery commitments |
| Removing an agent from a team reduces capacity | `remove-from-team` | May cause requirement delays or scope gaps that violate the user's timeline constraints |
| Assigning a COS changes the authority structure (USER-ONLY) | `assign-cos` | COS has approval power over team operations; only the USER can assign COS -- AMAMA cannot approve or execute this operation |
| Removing a COS removes a governance checkpoint (USER-ONLY) | `remove-cos` | Weakens the approval chain that protects requirement immutability; only the USER can remove COS -- AMAMA cannot approve or execute this operation |
| Transferring an agent between teams | `transfer-agent` | Affects both source team capacity (may block requirements) and destination team dynamics (may alter priorities) |
| Creating a new agent provisions new capabilities | `create-agent` | New agents consume resources and may shift team focus away from existing requirements |
| Deleting an agent removes capabilities permanently | `delete-agent` | May destroy institutional knowledge or capability needed for current requirements |
| Reconfiguring an agent changes its behavior | `configure-agent` | Configuration changes can alter how an agent fulfills its assigned requirements |

### Enforcement Rules

1. **No bypass**: An agent MUST NOT perform any operation listed above without a GovernanceRequest in `dual-approved` or `executed` status
2. **No self-approval**: The agent requesting the operation MUST NOT be the same entity that approves it
3. **Audit trail**: Every GovernanceRequest creates an immutable audit record linking the operation to MANAGER's explicit approval
4. **Rejection is final**: A `rejected` GovernanceRequest means the operation is blocked; a new request must be submitted with additional justification if the agent still believes it is necessary
5. **Expiry preserves immutability**: Auto-rejected (expired) requests default to "no change", which preserves the current state and thus the user's requirements

### Deviation Detection for Governance Operations

If an agent performs a governance-protected operation WITHOUT a corresponding `dual-approved` GovernanceRequest:

1. **STOP** all operations by the violating agent
2. **REVERT** the unauthorized change if possible
3. **Create a Requirement Issue Report** documenting:
   - Which operation was performed without approval
   - Which GovernanceRequestType should have been used
   - The impact on user requirements
4. **Escalate** to MANAGER with `priority: "urgent"`
5. **BLOCK** the violating agent from further governance operations until MANAGER reviews

## Quick Reference

| Situation | Action |
|-----------|--------|
| Requirement clear and feasible | Implement as specified |
| Requirement ambiguous | Escalate for clarification, BLOCK until resolved |
| Requirement infeasible | Document constraint, propose alternatives, escalate |
| Requirement conflicts with another | Escalate both, let user prioritize |
| Implementation deviates | Stop, document, escalate |
| Governance operation without GovernanceRequest | RULE 14 violation -- stop, revert, escalate |
| GovernanceRequest rejected | Operation blocked; new request needed with justification |
| GovernanceRequest expired | Defaults to no-change; agent may resubmit |
