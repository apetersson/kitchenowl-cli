---
id: TASK-009
title: Implement recipe search command baseline
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
  - kitchenowl_cli/commands/recipe.py
priority: high
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add recipe search command with query input
- [x] #2 Add recipe search-by-tag command
- [x] #3 Output supports --json and readable table/list format
- [x] #4 Tests cover search command endpoint invocation and parameter handling
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add recipe search and search-by-tag commands in recipe.py
2. Reuse household resolution and json/table output patterns
3. Add tests for parameter handling and endpoint invocation
4. Run full pytest suite
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Started recipe search implementation.

Implemented search and search-by-tag commands with json/table output and endpoint tests.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- Added `recipe search` command (household scoped) with query/page/language/only-ids support
- Added `recipe search-by-tag` command (global public recipe search by tag)
- Reused recipe table rendering for human-readable output and preserved --json behavior
- Added tests verifying endpoint paths and query parameter mapping
<!-- SECTION:FINAL_SUMMARY:END -->
