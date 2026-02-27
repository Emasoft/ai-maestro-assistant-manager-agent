# Success Criteria for Assistant Manager Operations


## Contents

- [Success: User Request Understood](#success-user-request-understood)
- [Success: Project and Team Creation Complete](#success-project-and-team-creation-complete)
- [Success: AMCOS Agent Created and Ready](#success-amcos-agent-created-and-ready)
- [Success: Approval Processed](#success-approval-processed)
- [Success: Status Reported](#success-status-reported)
- [General Success Verification Principles](#general-success-verification-principles)
  - [Before Reporting Completion](#before-reporting-completion)
  - [When Self-Checks Fail](#when-self-checks-fail)
  - [Evidence Standards](#evidence-standards)
  - [Completion vs. Progress](#completion-vs-progress)

Each operation has clear success criteria. Verify these before reporting completion to the user.

---

## Success: User Request Understood

**Completion Checklist:**

- [ ] User request parsed into structured intent (action, target, constraints)
- [ ] Ambiguities identified and clarified with user
- [ ] Routing decision made (handle directly vs. delegate to AMCOS)
- [ ] If delegation: AMCOS session name identified or created
- [ ] User acknowledged receipt of routing decision

**Verification Evidence:**

```
User request: "Build a REST API for the inventory system"
Parsed intent: {action: "build", target: "REST API", project: "inventory-system"}
Routing: ORCHESTRATOR (via AMCOS)
User notified: "Routing your request to AMCOS, who will coordinate with AMOA to implement the REST API..."
```

**Self-Check Questions:**
- Did I identify all ambiguities in the user's request?
- Did I clarify unclear aspects before proceeding?
- Can I articulate the structured intent in a clear format?
- Did the user acknowledge understanding of the routing?

---

## Success: Project and Team Creation Complete

**Completion Checklist:**

- [ ] Project directory created at specified/clarified location
- [ ] Git repository initialized
- [ ] Initial project structure created (README.md, .gitignore)
- [ ] AI Maestro team created for this project
- [ ] AMCOS agent created for this project with correct working directory
- [ ] COS role assigned to AMCOS agent via team governance
- [ ] AMCOS responding to health check ping
- [ ] Project registered in `docs_dev/projects/project-registry.md`
- [ ] User notified of project creation and AMCOS readiness

**Verification Evidence:**

```bash
ls -la /path/to/new-project  # Directory exists
cd /path/to/new-project && git status  # Git initialized
```

Verify AMCOS is alive by sending a health check ping using the `agent-messaging` skill and confirming a `pong` response.

**Self-Check Questions:**
- Does the project directory exist at the agreed location?
- Is git initialized with correct user config?
- Does the initial structure include all required files?
- Did AMCOS respond to the health check ping?
- Is the project registered in the registry file?
- Did I notify the user with all relevant details?

---

## Success: AMCOS Agent Created and Ready

**Completion Checklist:**

- [ ] Agent creation command succeeded (exit code 0) via the `ai-maestro-agents-management` skill
- [ ] COS role assigned via `PATCH /api/teams/{id}/chief-of-staff`
- [ ] AMCOS session registered in AI Maestro (visible in agent list)
- [ ] AMCOS main agent loaded with correct role constraints
- [ ] AMCOS plugins loaded (verify via plugin list if possible)
- [ ] AMCOS working directory set correctly
- [ ] AMCOS health check ping successful
- [ ] AMCOS added to active sessions log in `docs_dev/sessions/active-amcos-sessions.md`

**Verification Evidence:**

Verify session exists using the `ai-maestro-agents-management` skill's agent listing feature.
Verify AMCOS responds by sending a health check ping using the `agent-messaging` skill.

**Self-Check Questions:**
- Did the agent creation succeed (exit code 0)?
- Is the AMCOS session visible in the agent list via the `ai-maestro-agents-management` skill?
- Are all required plugins loaded?
- Is the working directory correctly set?
- Did AMCOS respond to the health check ping within 30 seconds?
- Is the session logged in the active sessions file?

---

## Success: Approval Processed

**Completion Checklist:**

- [ ] AMCOS approval request read and parsed
- [ ] Risk assessment completed (destructive? irreversible? in-scope?)
- [ ] Decision made (approve, deny, escalate to user)
- [ ] If escalated: User decision received
- [ ] Response sent to AMCOS via AI Maestro
- [ ] Approval logged in `docs_dev/approvals/approval-log.md`
- [ ] AMCOS acknowledgment received (if expected)

**Verification Evidence:**

```bash
# Check approval log contains this approval
grep "AMCOS-REQUEST-12345" docs_dev/approvals/approval-log.md
```

Verify the response was sent by checking sent messages using the `agent-messaging` skill, filtering for subjects containing the request ID.

**Self-Check Questions:**
- Did I correctly assess the risk level of the operation?
- Did I apply the approval decision tree correctly?
- If escalated, did I present sufficient context to the user?
- Was the response sent successfully to AMCOS?
- Is the approval logged with all required details?
- Did AMCOS acknowledge the approval decision?

---

## Success: Status Reported

**Completion Checklist:**

- [ ] Status request from user parsed
- [ ] Relevant agents identified (which AMCOS? which specialists?)
- [ ] Status query sent via AI Maestro
- [ ] Responses collected (with timeout if no response)
- [ ] Status aggregated into human-readable summary
- [ ] Summary presented to user
- [ ] User acknowledged (no follow-up questions)

**Verification Evidence:**

```
User: "What's the status of the API implementation?"
Status query sent to: amcos-inventory-system
Response: "AMOA reports 8/12 tasks complete, AMIA completed code review, tests passing"
User notified: "API implementation is 67% complete. 8 of 12 tasks done. Code review passed. All tests passing."
```

**Self-Check Questions:**
- Did I identify all relevant agents to query for status?
- Were status queries sent to all identified agents?
- Did I handle timeout cases appropriately?
- Is the aggregated summary clear and actionable?
- Did the user acknowledge understanding without confusion?
- Were there any follow-up questions indicating incomplete information?

---

## General Success Verification Principles

### Before Reporting Completion

Always verify:
1. **All checklist items completed** - No skipped steps
2. **Evidence collected** - Concrete proof of completion
3. **User acknowledged** - User understands what was done
4. **Records updated** - All logs and registries current
5. **No errors logged** - Clean execution path

### When Self-Checks Fail

If ANY self-check question reveals a gap:
- **STOP** - Do not report completion
- **Fix the gap** - Complete the missing verification
- **Re-verify** - Run through checklist again
- **Only then report** - When all criteria met

### Evidence Standards

Evidence MUST be:
- **Concrete** - Not assumptions or hopes
- **Verifiable** - Can be checked by running commands
- **Timestamped** - Know when the evidence was collected
- **Logged** - Recorded in appropriate files for audit trail

### Completion vs. Progress

**Completion** means:
- All checklist items checked off
- All verification commands run successfully
- All records updated
- User acknowledged

**Progress** means:
- Some checklist items done, others pending
- Report progress, NOT completion
- Set expectations for remaining work
