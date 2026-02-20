---
id: TASK-012
title: 'Clarification-needed: expense endpoint payload and category semantics'
status: Done
assignee:
  - '@codex'
created_date: '2026-02-20 12:34'
updated_date: '2026-02-20 13:08'
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
- [x] #1 Document required expense create/update payload shape including paid_by and paid_for semantics
- [x] #2 Document expense category endpoint behavior and required fields
- [x] #3 Capture unresolved edge cases in backlog notes for v0.2.x implementation
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Open question: final required payload for paid_for split entries in expense create/update across server versions.
- Open question: confirm minimal fields required for expense categories (name/color/order).
- Open question: decide pagination defaults for expense list and overview commands.

Status updated to In Progress while collecting expense payload and category contract details.

- Documented expense payload schema for create/update: name, amount, paid_by{id}, paid_for[{id,factor}], optional description/date/category/exclude_from_statistics.
- Documented category endpoints and fields: /expense/categories list/create with name/color/budget.
- Captured edge decisions for v0.2.x implementation: integer factors for paid_for, YYYY-MM-DD -> epoch conversion, and overview query params (view/frame/steps/page).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- Produced concrete expense/category contract mapping and implemented CLI payload handling accordingly
- Clarified required fields and optional semantics for expense create/update and category create/list
- Captured remaining edge constraints in task notes while unblocking and completing TASK-014
<!-- SECTION:FINAL_SUMMARY:END -->
