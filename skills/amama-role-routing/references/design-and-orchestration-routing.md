# Design Document & Module Orchestration Routing

<!-- TOC -->
- [Design Document Routing](#design-document-routing)
- [Module Orchestration Routing](#module-orchestration-routing)
<!-- /TOC -->

## Design Document Routing

### Handle Locally (AMAMA):

| Operation | Tool | Details |
|-----------|------|---------|
| Search designs by UUID | `amama_design_search.py --uuid` | Returns matching design docs |
| Search designs by keyword | `amama_design_search.py --keyword` | Full-text search in design/* |
| Search designs by status | `amama_design_search.py --status` | Filter by draft/approved/deprecated |
| List all designs | `amama_design_search.py --list` | Catalog of all design documents |

### Route to AMAA (Architect agent) for:

| Operation | User Intent Pattern | Handoff Content |
|-----------|---------------------|-----------------|
| Create new design | "design", "create spec", "architect solution" | Requirements, constraints |
| Update design | "modify design", "update spec", "revise architecture" | Design UUID, changes |
| Review design | "review design", "validate architecture" | Design UUID, review criteria |

### Search Before Route Decision Tree

```
User mentions design/spec/architecture
          |
          v
    +-------------------+
    | Does user give    |
    | UUID or path?     |
    +--------+----------+
             |
     +-------+-------+
     | YES           | NO
     v               v
+------------+  +-----------------+
| Search by  |  | Search by       |
| UUID/path  |  | keyword/context |
+-----+------+  +--------+-------+
      |                   |
      v                   v
+-------------------------------------+
|   Design found?                     |
+------------------+------------------+
         +---------+---------+
         | YES               | NO
         v                   v
+----------------+  +-----------------+
| Include design |  | Route to AMAA   |
| context in     |  | to create new   |
| routing        |  | design          |
+----------------+  +-----------------+
```

## Module Orchestration Routing

### Route to AMOA (Orchestrator agent) for:

| Operation | User Intent Pattern | Handoff Content |
|-----------|---------------------|-----------------|
| Start module implementation | "implement module", "build component" | Module UUID from design |
| Coordinate parallel work | "parallelize", "split tasks" | Task breakdown, dependencies |
| Resume orchestration | "continue building", "resume work" | Orchestration state, progress |
| Replan modules | "reorganize tasks", "reprioritize" | Current state, new priorities |

### Orchestration Handoff Checklist

When routing to AMOA, handoff MUST include:

1. **Design Reference**: UUID of approved design
2. **Module List**: Modules to implement (from design)
3. **Priority Order**: Which modules first
4. **Dependencies**: Inter-module dependencies
5. **Constraints**: Time, resources, technical limits
6. **Success Criteria**: What defines "done"
