"""
thresholds.py - Shared constants for Assistant Manager Agent.

These thresholds configure behavior for user communication,
status reporting, and approval workflows.
"""

# Session memory configuration
MAX_MEMORY_ENTRIES = 100
MEMORY_TTL_DAYS = 30

# Status reporting thresholds
STATUS_POLL_INTERVAL_SECONDS = 60
MAX_STATUS_RETRIES = 3

# Approval workflow timeouts
APPROVAL_TIMEOUT_SECONDS = 300
APPROVAL_REMINDER_INTERVAL_SECONDS = 60

# Communication thresholds
MAX_MESSAGE_LENGTH = 4000
MAX_HANDOFF_SIZE_KB = 100

# Governance roles (AI Maestro defines exactly 3)
VALID_GOVERNANCE_ROLES = frozenset(["manager", "chief-of-staff", "member"])

# Agent specializations (expressed via skills/tags, NOT via governance title)
VALID_SPECIALIZATIONS = frozenset(["architect", "orchestrator", "integrator"])
