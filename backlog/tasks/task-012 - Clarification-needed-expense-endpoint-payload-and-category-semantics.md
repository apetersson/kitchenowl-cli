---
id: TASK-012
title: 'Clarification-needed: expense endpoint payload and category semantics'
status: In Progress
assignee:
  - '@codex'
created_date: '2026-02-20 12:34'
updated_date: '2026-02-20 12:48'
labels:
  - clarification-needed
  - api-contract
dependencies: []
references:
  - ../feedback-zai.txt
priority: medium
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document required expense create/update payload shape including paid_by and paid_for semantics
- [ ] #2 Document expense category endpoint behavior and required fields
- [ ] #3 Capture unresolved edge cases in backlog notes for v0.2.x implementation
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Open question: final required payload for paid_for split entries in expense create/update across server versions.
- Open question: confirm minimal fields required for expense categories (name/color/order).
- Open question: decide pagination defaults for expense list and overview commands.

Status updated to In Progress while collecting expense payload and category contract details.
<!-- SECTION:NOTES:END -->
