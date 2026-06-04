# design/proposals/ — TRDDs awaiting approval

This folder holds TRDDs with `status: proposal` — tasks that have been
**authored** but **not yet authorized to execute**. They are requests,
not commitments.

A proposal is promoted by the authority its **approval tier** requires
(USER / MANAGER / CHIEF-OF-STAFF — see
`~/.claude/rules/trdd-approval-tiers.md` Part B). On approval the
approver sets `status: planned`, records the decision in the TRDD's
`## Approval log`, and **`git mv`s the file into `design/tasks/`**.

Agents do **not** stage Tier-0 work here. DERIVED TASKS (NPT/EHT) and
other tasks inside an agent's own independent authority are authored
**directly** in `design/tasks/` as `status: planned` — see Part A of the
rule.

Keep this folder an accurate index of "pending approval": once a
proposal is approved, it leaves; once rejected, it is marked
`status: rejected` in its body and may stay here as an audit record or
be removed per project convention.
