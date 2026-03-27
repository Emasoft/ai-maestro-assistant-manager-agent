# Handoff Protocol

## Table of Contents
- [Steps](#steps)
- [Design Document Scripts](#design-document-scripts)
- [See Also](#see-also)

Procedure for routing work between AMAMA, AMCOS, and specialist agents.

---

## Steps

1. Create handoff .md file with UUID
2. Include all relevant context
3. Send via AI Maestro message to AMCOS (preferred) or directly to specialist if urgent
4. AMCOS routes to appropriate specialist (when routing via AMCOS)
5. Track handoff status
6. Report completion to user

## Design Document Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `amama_design_search.py` | Search design documents for user queries | `python scripts/amama_design_search.py --type <TYPE> --status <STATUS>` |

Use `amama_design_search.py` when:
- A user asks about project status or design progress
- Looking up design specifications to reference in responses
- Finding related designs to provide context in user communication

### Script Location

The script is located at `../../scripts/amama_design_search.py` relative to the skill directory.

---

## See Also

- [communication-patterns.md](communication-patterns.md) - Core communication templates
- [amcos-monitoring.md](amcos-monitoring.md) - AMCOS health monitoring
