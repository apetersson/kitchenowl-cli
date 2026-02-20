---
id: TASK-013
title: 'Clarification-needed: shopping list deletion API compatibility strategy'
status: In Progress
assignee:
  - '@codex'
created_date: '2026-02-20 12:34'
updated_date: '2026-02-20 12:48'
labels:
  - clarification-needed
  - api-contract
dependencies:
  - TASK-010
references:
  - kitchenowl_cli/commands/shoppinglist.py
priority: medium
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document current backend support for DELETE-with-body versus path/query alternatives
- [ ] #2 Decide and document backward-compatible strategy for remove-item and bulk remove commands
- [ ] #3 Create follow-up migration task if endpoint changes are required
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Open question: does every supported deployment preserve DELETE request body reliably for shopping item removal?
- Open question: should CLI introduce path/query fallback logic while preserving current endpoint behavior?
- Open question: define migration plan for single remove-item and future bulk remove-items commands.

Status updated to In Progress while assessing DELETE-with-body compatibility strategy.
<!-- SECTION:NOTES:END -->
