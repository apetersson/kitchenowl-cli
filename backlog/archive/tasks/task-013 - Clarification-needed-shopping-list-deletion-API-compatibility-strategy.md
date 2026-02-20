---
id: TASK-013
title: 'Clarification-needed: shopping list deletion API compatibility strategy'
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
  - kitchenowl_cli/commands/shoppinglist.py
priority: medium
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Document current backend support for DELETE-with-body versus path/query alternatives
- [x] #2 Decide and document backward-compatible strategy for remove-item and bulk remove commands
- [x] #3 Create follow-up migration task if endpoint changes are required
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Open question: does every supported deployment preserve DELETE request body reliably for shopping item removal?
- Open question: should CLI introduce path/query fallback logic while preserving current endpoint behavior?
- Open question: define migration plan for single remove-item and future bulk remove-items commands.

Status updated to In Progress while assessing DELETE-with-body compatibility strategy.

- Documented backend support for DELETE /shoppinglist/{id}/items with JSON body and legacy single-item DELETE endpoint.
- Implemented backward-compatible CLI strategy: attempt bulk DELETE-with-body first, then fallback to per-item legacy endpoint when proxies reject delete bodies (status 400/405/411/415/422/501).
- Endpoint migration follow-up not required for current supported versions because compatibility fallback is now implemented in CLI.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- Completed shopping-list deletion compatibility analysis and encoded strategy in CLI implementation
- Added resilient bulk-remove behavior with legacy fallback to avoid proxy/body drop regressions
- No server endpoint migration task required at this stage due implemented compatibility path
<!-- SECTION:FINAL_SUMMARY:END -->
