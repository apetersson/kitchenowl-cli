---
id: TASK-006
title: Fix recipe edit payload semantics and visibility validation
status: Done
assignee:
  - '@codex'
created_date: '2026-02-20 12:33'
updated_date: '2026-02-20 12:40'
labels:
  - blocker
  - v0.2
dependencies:
  - TASK-001
references:
  - kitchenowl_cli/commands/recipe.py
  - tests/test_recipe_helpers.py
priority: high
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Recipe edit no longer allows stale ingredients/items duplication to override user edits
- [x] #2 Recipe display/edit paths avoid duplicate ingredient/item representation
- [x] #3 Visibility accepts only 0, 1, or 2 with clear CLI validation errors
- [x] #4 Tests cover normalization, edit, and visibility validation
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Remove stale ingredients/items merge behavior that can overwrite edits
2. Ensure printable/editable recipe representation avoids duplicated fallback sections
3. Validate visibility through click choices or explicit guard
4. Extend recipe helper tests for merge + visibility cases
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Starting recipe payload and validation fixes.

Adjusted recipe normalization to avoid stale ingredients overriding items and tightened visibility validation.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- Stopped duplicating fallback ingredients from items in editable recipe templates
- Updated payload normalization so explicit items are not overridden by stale ingredients in update flows
- Enforced visibility to 0/1/2 at CLI option parsing level
- Added tests for payload behavior, editable recipe duplication guard, and visibility validation
<!-- SECTION:FINAL_SUMMARY:END -->
