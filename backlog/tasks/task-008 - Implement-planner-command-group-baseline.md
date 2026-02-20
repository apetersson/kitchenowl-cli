---
id: TASK-008
title: Implement planner command group baseline
status: Done
assignee:
  - '@codex'
created_date: '2026-02-20 12:34'
updated_date: '2026-02-20 12:44'
labels:
  - feature
  - v0.2
dependencies:
  - TASK-002
  - TASK-003
references:
  - ../v0.2-planning.md
priority: high
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add planner commands for list, add-recipe, remove-recipe
- [x] #2 Add planner commands for recent-recipes, suggested-recipes, refresh-suggestions
- [x] #3 Support YYYY-MM-DD input conversion for planner date fields
- [x] #4 Commands provide --json output and human-readable output consistent with existing CLI style
- [x] #5 Tests cover planner payload building and endpoint invocation
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add planner command module with list/add/remove/recent/suggested/refresh commands
2. Add date parser helper for YYYY-MM-DD to epoch milliseconds
3. Register planner command group in main.py and add tests
4. Capture open API ambiguities in clarification-needed task notes
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Started planner command implementation.

Implemented planner command group with date conversion helper and endpoint mapping tests.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- Added new `planner` command group with list, add-recipe, remove-recipe, recent-recipes, suggested-recipes, and refresh-suggestions
- Implemented YYYY-MM-DD parsing to epoch milliseconds for planner payloads
- Registered planner group in CLI main entrypoint
- Added tests for date conversion, add payload construction, and recipe feed/refresh endpoints
<!-- SECTION:FINAL_SUMMARY:END -->
