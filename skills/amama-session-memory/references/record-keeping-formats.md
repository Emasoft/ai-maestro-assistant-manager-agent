# Record-Keeping Formats


## Contents

- [Overview](#overview)
- [1. Project Registry](#1-project-registry)
- [Project: inventory-system](#project-inventory-system)
- [Project: data-pipeline](#project-data-pipeline)
- [2. Approval Log](#2-approval-log)
- [APPROVAL-2026-02-04-001](#approval-2026-02-04-001)
- [APPROVAL-2026-02-04-002](#approval-2026-02-04-002)
- [3. Active Orchestrator Sessions Log](#3-active-orchestrator-sessions-log)
- [Session: orchestrator-inventory-system](#session-orchestrator-inventory-system)
- [4. User Interactions Log](#4-user-interactions-log)
- [Interaction 2026-02-04-001](#interaction-2026-02-04-001)
- [Interaction 2026-02-04-002](#interaction-2026-02-04-002)
- [Record-Keeping Best Practices](#record-keeping-best-practices)
  - [1. Timestamps](#1-timestamps)
  - [2. Exact Quotes](#2-exact-quotes)
  - [3. Unique IDs](#3-unique-ids)
  - [4. Completeness](#4-completeness)
  - [5. Update Frequency](#5-update-frequency)
  - [6. File Locations](#6-file-locations)
- [Tools for Record-Keeping](#tools-for-record-keeping)
  - [Write Tool](#write-tool)
  - [Read Tool](#read-tool)
- [Session Memory Persistence](#session-memory-persistence)
- [Error Handling](#error-handling)
  - [Corrupted Log Files](#corrupted-log-files)
  - [Missing Log Files](#missing-log-files)
  - [Concurrent Access](#concurrent-access)
- [Audit Trail Requirements](#audit-trail-requirements)
- [APPROVAL-2026-02-04-001](#approval-2026-02-04-001)
  - [Correction (2026-02-04 18:00)](#correction-2026-02-04-1800)
- [Summary](#summary)

This reference documents the standard formats for session memory, state tracking, and audit logs used by the AI Maestro Assistant Manager Agent (AMAMA).

---

## Overview

AMAMA maintains accurate records of all activities for traceability and audit purposes. Four primary record types are maintained:

1. **Project Registry** - Track all projects and orchestrator instances
2. **Approval Log** - Audit trail of approval decisions
3. **Active Orchestrator Sessions Log** - Monitor running orchestrator instances
4. **User Interactions Log** - Record user requests and responses

---

## 1. Project Registry

**File**: `docs_dev/projects/project-registry.md`

**Purpose**: Track all projects and their orchestrator instances.

**Format**:
```markdown
# Project Registry

| Project Name | Path | Orchestrator Session | Created | Status |
|--------------|------|----------------------|---------|--------|
| inventory-system | /Users/user/Code/inventory-system | orchestrator-inventory-system | 2026-02-04 | active |
| data-pipeline | /Users/user/Code/data-pipeline | orchestrator-data-pipeline | 2026-02-03 | active |
| auth-service | /Users/user/Code/auth-service | orchestrator-auth-service | 2026-01-28 | archived |

## Project: inventory-system
- **Created**: 2026-02-04 14:30:22
- **Orchestrator**: orchestrator-inventory-system
- **Purpose**: REST API for inventory management
- **User Requirements**: "Build a REST API with CRUD operations for inventory tracking"
- **Status**: Active development

## Project: data-pipeline
...
```

**When to update**:
- After creating new project
- After creating orchestrator session
- When project status changes (active → paused → archived)

**Fields Explanation**:
- **Project Name**: Short identifier for the project
- **Path**: Absolute path to project directory
- **Orchestrator Session**: Name of the orchestrator tmux session managing this project
- **Created**: Date the project was created
- **Status**: `active`, `paused`, or `archived`

---

## 2. Approval Log

**File**: `docs_dev/approvals/approval-log.md`

**Purpose**: Audit trail of all approval decisions.

**Format**:
```markdown
# Approval Log

## APPROVAL-2026-02-04-001

- **Request ID**: ORCH-REQ-20260204-143022
- **From**: orchestrator-inventory-system
- **Timestamp**: 2026-02-04 14:30:22 UTC
- **Operation**: Deploy to staging environment
- **Risk Level**: Medium
- **Decision**: APPROVED (by user)
- **Approved By**: User (exact quote: "Yes, deploy to staging")
- **Justification**: Orchestrator needs to verify API in staging before production
- **Conditions**: None
- **Outcome**: Deployment successful

## APPROVAL-2026-02-04-002

- **Request ID**: ORCH-REQ-20260204-150033
- **From**: orchestrator-inventory-system
- **Timestamp**: 2026-02-04 15:00:33 UTC
- **Operation**: Delete all test data from database
- **Risk Level**: High (destructive)
- **Decision**: DENIED (by AMAMA)
- **Reason**: Operation is destructive and irreversible; user did not explicitly approve data deletion
- **Alternative Suggested**: Archive test data instead of deleting
- **Outcome**: Orchestrator acknowledged, will archive instead
```

**When to update**:
- After processing each approval request
- Include request details, decision, reason, outcome

**Fields Explanation**:
- **Request ID**: Unique identifier (format: `ORCH-REQ-YYYYMMDD-HHMMSS`)
- **From**: Which orchestrator session made the request
- **Timestamp**: When the request was received (UTC)
- **Operation**: What action is being requested
- **Risk Level**: `Low`, `Medium`, `High`, or `Critical`
- **Decision**: `APPROVED` or `DENIED`
- **Approved By**: `User` (with exact quote) or `AMAMA` (auto-approved)
- **Justification**: Why the decision was made
- **Conditions**: Any conditions attached to the approval
- **Outcome**: What happened after the decision

**Approval ID Format**: `APPROVAL-YYYY-MM-DD-###`

---

## 3. Active Orchestrator Sessions Log

**File**: `docs_dev/sessions/active-orchestrator-sessions.md`

**Purpose**: Track which orchestrator instances are currently running.

**Format**:
```markdown
# Active Orchestrator Sessions

| Session Name | Project | Working Directory | Launched | Last Ping | Status |
|--------------|---------|-------------------|----------|-----------|--------|
| orchestrator-inventory-system | inventory-system | /Users/user/Code/inventory-system | 2026-02-04 14:30 | 2026-02-04 16:15 | alive |
| orchestrator-data-pipeline | data-pipeline | /Users/user/Code/data-pipeline | 2026-02-03 10:22 | 2026-02-04 16:10 | alive |

## Session: orchestrator-inventory-system
- **Launched**: 2026-02-04 14:30:22
- **Plugins**: ai-maestro-assistant-manager
- **Working Dir**: /Users/user/Code/inventory-system
- **Last Health Check**: 2026-02-04 16:15:44 (ALIVE)
- **Active Specialists**: AMOA, AMIA
- **Current Tasks**: Implementing REST API (8/12 tasks complete)
```

**When to update**:
- After launching new orchestrator session
- After successful health check ping
- When orchestrator reports completion or shutdown

**Fields Explanation**:
- **Session Name**: tmux session name (format: `orchestrator-<project-name>`)
- **Project**: Associated project name
- **Working Directory**: Absolute path where the orchestrator operates
- **Launched**: When the orchestrator session was created
- **Last Ping**: Last successful health check response
- **Status**: `alive`, `stale`, or `dead`
- **Plugins**: Which plugins are loaded in this orchestrator session
- **Active Specialists**: Which specialist agents (AMAA, AMOA, AMIA) are currently working
- **Current Tasks**: Brief summary of work in progress

**Status Values**:
- `alive`: Responded to health check within expected interval
- `stale`: No response, but within grace period
- `dead`: No response beyond grace period

---

## 4. User Interactions Log

**File**: `docs_dev/sessions/user-interactions.md`

**Purpose**: Record all user requests and your responses for continuity.

**Format**:
```markdown
# User Interactions Log

## Interaction 2026-02-04-001

- **Timestamp**: 2026-02-04 14:28:15
- **User Request**: "Build a REST API for inventory management"
- **Your Response**: "I'll create a new project called 'inventory-system' and route this to AMOA via the orchestrator for implementation."
- **Actions Taken**:
  - Created project at /Users/user/Code/inventory-system
  - Launched orchestrator-inventory-system
  - Routed work request to AMOA
- **User Acknowledgment**: "Great, keep me posted on progress"
- **Follow-up**: Status update requested in 24 hours

## Interaction 2026-02-04-002

- **Timestamp**: 2026-02-04 15:45:30
- **User Request**: "What's the status of the API?"
- **Your Response**: "API implementation is 67% complete. 8 of 12 tasks done. Code review passed. All tests passing. AMOA estimates completion by end of day."
- **User Acknowledgment**: "Thanks"
```

**When to update**:
- After each user interaction
- Include request, response, actions, follow-up

**Fields Explanation**:
- **Timestamp**: When the user made the request
- **User Request**: Exact quote of what the user asked
- **Your Response**: Summary of AMAMA's response
- **Actions Taken**: Bulleted list of concrete actions performed
- **User Acknowledgment**: User's reaction or response
- **Follow-up**: Any pending actions or status check schedules

**Interaction ID Format**: `Interaction YYYY-MM-DD-###`

---

## Record-Keeping Best Practices

### 1. Timestamps
- Always use ISO 8601 format: `YYYY-MM-DD HH:MM:SS`
- Use UTC for approval logs and health checks
- Use local time for user interactions

### 2. Exact Quotes
- When recording user approval decisions, use exact quotes
- Example: `"Yes, deploy to staging"` not `User approved`
- This is critical for audit trail and dispute resolution

### 3. Unique IDs
- Each record must have a unique, sortable identifier
- Format includes date for easy chronological sorting
- Example: `APPROVAL-2026-02-04-001`, `Interaction 2026-02-04-002`

### 4. Completeness
- Always include all fields, even if value is "None" or "N/A"
- Never leave fields blank or omit them
- Incomplete records undermine audit trail

### 5. Update Frequency
- Update logs immediately after events, not in batches
- Stale logs create confusion and risk data loss
- Use atomic write operations (Write tool, not Edit)

### 6. File Locations
All record-keeping files live under `docs_dev/`:
```
docs_dev/
├── projects/
│   └── project-registry.md
├── approvals/
│   └── approval-log.md
└── sessions/
    ├── active-orchestrator-sessions.md
    └── user-interactions.md
```

---

## Tools for Record-Keeping

### Write Tool
Use the Write tool (not Edit) to append entries to logs. This ensures atomic operations and prevents corruption from concurrent access.

### Read Tool
Read logs before making decisions:
- Check project registry before creating new projects
- Review approval log before auto-approving similar requests
- Check active sessions before launching new orchestrator

---

## Session Memory Persistence

**Why records matter**:
- AMAMA has no persistent memory between Claude Code restarts
- All context is lost on session end
- Record-keeping files are the ONLY persistent state

**Recovery on restart**:
1. Read `active-orchestrator-sessions.md` to discover running orchestrator instances
2. Read `project-registry.md` to understand project structure
3. Read `approval-log.md` to understand past decisions
4. Read `user-interactions.md` to understand conversation history

**Without these files, AMAMA is blind to prior work.**

---

## Error Handling

### Corrupted Log Files
If a log file is corrupted or invalid:
1. DO NOT delete the file
2. Rename to `<filename>.corrupted.<timestamp>`
3. Create a new empty log with proper format
4. Report corruption to user
5. Attempt to extract valid entries from corrupted file

### Missing Log Files
If expected log files don't exist:
1. Create them with proper format
2. Add header comment: `# Created on <timestamp> (previous log missing)`
3. Report gap to user

### Concurrent Access
All logs are designed for single-writer (AMAMA). If you detect unexpected changes:
1. DO NOT overwrite
2. Read current state
3. Merge your changes
4. Report anomaly to user

---

## Audit Trail Requirements

For compliance and troubleshooting, all approval decisions must be:
1. **Traceable**: Clear chain from request → decision → outcome
2. **Timestamped**: Exact time of each event
3. **Attributed**: Who made the decision (user or AMAMA)
4. **Justified**: Why the decision was made
5. **Immutable**: Never edit past entries (append corrections instead)

**Example of appending a correction**:
```markdown
## APPROVAL-2026-02-04-001
...
- **Outcome**: Deployment successful

### Correction (2026-02-04 18:00)
Deployment initially reported successful, but post-deploy health check revealed issue. Rolled back. See INCIDENT-2026-02-04-001 for details.
```

---

## Summary

These four record types form the complete session memory system for AMAMA:

| Record Type | File | Purpose | Update Trigger |
|-------------|------|---------|----------------|
| Project Registry | `project-registry.md` | Track projects and orchestrators | Project creation, status change |
| Approval Log | `approval-log.md` | Audit trail of decisions | Every approval request |
| Active Orchestrator Sessions | `active-orchestrator-sessions.md` | Monitor running instances | Orchestrator launch, health check, shutdown |
| User Interactions | `user-interactions.md` | Conversation continuity | Every user message |

**All four files are mandatory for AMAMA to function correctly across sessions.**
