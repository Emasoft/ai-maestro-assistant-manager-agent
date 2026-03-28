# Detailed Routing Rules

<!-- TOC -->
- [Route to AMAA (Architect)](#route-to-amaa-architect-specialization-role-member)
- [Route to AMOA (Orchestrator)](#route-to-amoa-orchestrator-specialization-role-member)
- [Route to AMIA (Integrator)](#route-to-amia-integrator-specialization-role-member)
- [Route to AMCOS (Chief of Staff)](#route-to-amcos-chief-of-staff----governance-role-chief-of-staff)
- [Handle Directly (no routing)](#handle-directly-no-routing)
<!-- /TOC -->

**IMPORTANT**: All specialist routing goes through AMCOS (chief-of-staff). AMAMA never communicates directly with specialist agents. When a routing rule says "route to AMAA/AMOA/AMIA", it means: create a handoff, send it to AMCOS, and AMCOS delegates to the appropriate specialist.

## Route to AMAA (Architect specialization, governance title: `MEMBER`)

1. **New project/feature design needed**
   - User says: "Design a...", "Plan how to...", "Create architecture for..."
   - Action: Create handoff with requirements, send to AMCOS for AMAA delegation

2. **Requirements analysis required**
   - User says: "What do we need for...", "Analyze requirements for..."
   - Action: Create handoff with context, send to AMCOS for AMAA delegation

3. **Technical specification needed**
   - User says: "Spec out...", "Document how...", "Define the API for..."
   - Action: Create handoff, send to AMCOS for AMAA delegation

4. **Module planning required**
   - User says: "Break down...", "Modularize...", "Plan implementation of..."
   - Action: Create handoff, send to AMCOS for AMAA delegation

## Route to AMOA (Orchestrator, governance title: `ORCHESTRATOR`)

1. **Implementation ready to start**
   - Condition: Approved design/plan exists
   - Action: Create handoff with design docs, send to AMCOS for AMOA delegation

2. **Task coordination needed**
   - User says: "Build...", "Implement...", "Start development..."
   - Action: Create handoff with requirements, send to AMCOS for AMOA delegation

3. **Multi-agent work coordination**
   - Condition: Work requires multiple parallel agents
   - Action: Create handoff with task breakdown, send to AMCOS for AMOA delegation

4. **Progress monitoring required**
   - Condition: Orchestration in progress, need intervention
   - Action: Forward message to AMCOS for AMOA

## Route to AMIA (Integrator specialization, governance title: `MEMBER`)

1. **Work ready for integration**
   - Condition: Orchestrator agent signals completion
   - Action: Create handoff with completion report, send to AMCOS for AMIA delegation

2. **Code review requested**
   - User says: "Review...", "Check the PR...", "Evaluate changes..."
   - Action: Create handoff with PR details, send to AMCOS for AMIA delegation

3. **Quality gates needed**
   - User says: "Test...", "Validate...", "Run quality checks..."
   - Action: Create handoff, send to AMCOS for AMIA delegation

4. **Release preparation**
   - User says: "Prepare release...", "Merge...", "Deploy..."
   - Action: Create handoff, send to AMCOS for AMIA delegation

## Route to AMCOS (Chief of Staff -- governance title: `CHIEF-OF-STAFF`)

1. **Agent lifecycle operations needed**
   - User says: "Spawn a new agent", "Create agent for...", "Start new session"
   - Action: Create handoff with agent requirements, route to AMCOS
   - **IMPORTANT**: When AMCOS creates new agents, it MUST set the correct governance title: `ORCHESTRATOR` for orchestrator agents, `MEMBER` for all other specialist agents. Specialization is expressed via `skills` and `tags`, never via the `title` field (except ORCHESTRATOR which IS a governance title).

2. **Agent termination required**
   - User says: "Terminate agent", "Stop session", "Kill agent"
   - Action: Create handoff with agent ID, route to AMCOS

3. **Session management needed**
   - User says: "Restart agent", "Check agent health", "Agent status"
   - Action: Create handoff with session details, route to AMCOS

4. **Permission management required**
   - Condition: Sensitive operation requires elevated permissions
   - Action: Create handoff with permission request, route to AMCOS

5. **Failure recovery needed**
   - Condition: Agent failure detected, escalation required
   - Action: Create handoff with failure details, route to AMCOS

6. **Approval requests from AMCOS**
   - Condition: AMCOS requests user approval for agent operations
   - Action: Present approval request to user, forward decision to AMCOS

## Handle Directly (no routing)

1. **Status requests** - Query relevant agents, compile report, present to user
2. **Approval decisions** - Record decision, forward to requesting agent
3. **Clarification requests** - Answer directly or query relevant agent
4. **Configuration/settings** - Handle directly
