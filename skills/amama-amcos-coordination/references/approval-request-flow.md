# Approval Request Flow from COS-Assigned Agent to AMAMA

<!-- TOC -->
- [When COS-Assigned Agent Sends Approval Requests](#when-cos-assigned-agent-sends-approval-requests)
- [Request Categories](#request-categories)
- [Related Documents](#related-documents)
<!-- /TOC -->

## When COS-Assigned Agent Sends Approval Requests

A COS-assigned agent sends approval requests to AMAMA when:

1. **Critical Operations**: Actions that affect production, security, or user data
2. **Policy Exceptions**: Operations outside delegated autonomy boundaries
3. **Resource Allocation**: Major resource commitments (time, budget, infrastructure)
4. **Conflict Resolution**: When specialized roles disagree on approach
5. **User-Impacting Changes**: Any change that affects user experience

## Request Categories

| Category | Description | Default: Requires AMAMA Approval |
|----------|-------------|--------------------------------|
| `critical-operation` | Production deployments, database migrations | Always |
| `policy-exception` | Deviation from standard procedures | Always |
| `resource-allocation` | Budget, infrastructure, timeline changes | Always |
| `conflict-resolution` | Inter-role disagreements | Always |
| `routine-operation` | Standard development tasks | Delegatable |
| `minor-decision` | Low-impact choices | Delegatable |

## Related Documents

- [approval-response-workflow.md](approval-response-workflow.md) - How AMAMA responds to approval requests
- [delegation-rules.md](delegation-rules.md) - When operations can be delegated (autonomy mode)
- [message-formats.md](message-formats.md) - Message format for approval requests
