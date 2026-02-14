# Success Criteria for Assistant Manager Operations


## Contents

- [Success: User Request Understood](#success-user-request-understood)
- [Success: Project Creation Complete](#success-project-creation-complete)
- [Success: ECOS Spawned and Ready](#success-ecos-spawned-and-ready)
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
- [ ] Routing decision made (handle directly vs. delegate to ECOS)
- [ ] If delegation: ECOS session name identified or created
- [ ] User acknowledged receipt of routing decision

**Verification Evidence:**

```
User request: "Build a REST API for the inventory system"
Parsed intent: {action: "build", target: "REST API", project: "inventory-system"}
Routing: ORCHESTRATOR (via ECOS)
User notified: "Routing your request to ECOS, who will coordinate with EOA to implement the REST API..."
```

**Self-Check Questions:**
- Did I identify all ambiguities in the user's request?
- Did I clarify unclear aspects before proceeding?
- Can I articulate the structured intent in a clear format?
- Did the user acknowledge understanding of the routing?

---

## Success: Project Creation Complete

**Completion Checklist:**

- [ ] Project directory created at specified/clarified location
- [ ] Git repository initialized
- [ ] Initial project structure created (README.md, .gitignore)
- [ ] ECOS spawned for this project with correct working directory
- [ ] ECOS responding to health check ping
- [ ] Project registered in `docs_dev/projects/project-registry.md`
- [ ] User notified of project creation and ECOS readiness

**Verification Evidence:**

```bash
ls -la /path/to/new-project  # Directory exists
cd /path/to/new-project && git status  # Git initialized
```

Verify ECOS is alive by sending a health check ping using the `agent-messaging` skill and confirming a `pong` response.

**Self-Check Questions:**
- Does the project directory exist at the agreed location?
- Is git initialized with correct user config?
- Does the initial structure include all required files?
- Did ECOS respond to the health check ping?
- Is the project registered in the registry file?
- Did I notify the user with all relevant details?

---

## Success: ECOS Spawned and Ready

**Completion Checklist:**

- [ ] Agent creation command succeeded (exit code 0) via the `ai-maestro-agents-management` skill
- [ ] ECOS session registered in AI Maestro (visible in agent list)
- [ ] ECOS main agent loaded with correct role constraints
- [ ] ECOS plugins loaded (verify via plugin list if possible)
- [ ] ECOS working directory set correctly
- [ ] ECOS health check ping successful
- [ ] ECOS added to active sessions log in `docs_dev/sessions/active-ecos-sessions.md`

**Verification Evidence:**

Verify session exists using the `ai-maestro-agents-management` skill's agent listing feature.
Verify ECOS responds by sending a health check ping using the `agent-messaging` skill.

**Self-Check Questions:**
- Did the agent creation succeed (exit code 0)?
- Is the ECOS session visible in the agent list via the `ai-maestro-agents-management` skill?
- Are all required plugins loaded?
- Is the working directory correctly set?
- Did ECOS respond to the health check ping within 30 seconds?
- Is the session logged in the active sessions file?

---

## Success: Approval Processed

**Completion Checklist:**

- [ ] ECOS approval request read and parsed
- [ ] Risk assessment completed (destructive? irreversible? in-scope?)
- [ ] Decision made (approve, deny, escalate to user)
- [ ] If escalated: User decision received
- [ ] Response sent to ECOS via AI Maestro
- [ ] Approval logged in `docs_dev/approvals/approval-log.md`
- [ ] ECOS acknowledgment received (if expected)

**Verification Evidence:**

```bash
# Check approval log contains this approval
grep "ECOS-REQUEST-12345" docs_dev/approvals/approval-log.md
```

Verify the response was sent by checking sent messages using the `agent-messaging` skill, filtering for subjects containing the request ID.

**Self-Check Questions:**
- Did I correctly assess the risk level of the operation?
- Did I apply the approval decision tree correctly?
- If escalated, did I present sufficient context to the user?
- Was the response sent successfully to ECOS?
- Is the approval logged with all required details?
- Did ECOS acknowledge the approval decision?

---

## Success: Status Reported

**Completion Checklist:**

- [ ] Status request from user parsed
- [ ] Relevant agents identified (which ECOS? which specialists?)
- [ ] Status query sent via AI Maestro
- [ ] Responses collected (with timeout if no response)
- [ ] Status aggregated into human-readable summary
- [ ] Summary presented to user
- [ ] User acknowledged (no follow-up questions)

**Verification Evidence:**

```
User: "What's the status of the API implementation?"
Status query sent to: ecos-inventory-system
Response: "EOA reports 8/12 tasks complete, EIA completed code review, tests passing"
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
