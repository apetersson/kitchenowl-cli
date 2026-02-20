---
id: TASK-015
title: Implement shopping list bulk operations (v0.2.x)
status: Done
assignee:
  - '@codex'
created_date: '2026-02-20 12:34'
updated_date: '2026-02-20 13:08'
labels:
  - feature
  - v0.2.x
dependencies: []
references:
  - kitchenowl_cli/commands/shoppinglist.py
priority: medium
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add shoppinglist clear command
- [x] #2 Add shoppinglist remove-items command accepting multiple item ids
- [x] #3 Add optional add-items-from-file workflow if endpoint support is stable
- [x] #4 Tests cover endpoint invocation and argument parsing for bulk operations
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add remove-items command hitting /shoppinglist/{id}/items with multi-id payload
2. Add clear command that fetches current items and removes them in bulk
3. Add compatibility fallback to per-item remove when bulk DELETE-body is rejected
4. Add optional add-items-from-file workflow and tests
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Starting shopping list bulk operations implementation.

- Added shoppinglist remove-items command with multi-id support via /shoppinglist/{id}/items.
- Added clear command that fetches current list items and bulk-removes them.
- Added compatibility fallback to legacy single-item delete when DELETE-body is rejected by intermediaries.
- Added add-items-from-file command supporting JSON/YAML/text inputs and tests for bulk flows.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- Implemented shopping list bulk operations: remove-items, clear, and add-items-from-file
- Added robust compatibility fallback for environments that drop DELETE request bodies
- Added coverage for endpoint invocation, fallback behavior, clear flow, and file-based bulk add parsing
<!-- SECTION:FINAL_SUMMARY:END -->
