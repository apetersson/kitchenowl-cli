---
id: TASK-014
title: Implement expense command group baseline (v0.2.x)
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
  - ../v0.2-planning.md
priority: medium
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add expense commands for list, create, update, delete
- [x] #2 Add expense category commands for list and create
- [x] #3 Add overview and balance commands
- [x] #4 Support --json output and readable table output
- [x] #5 Tests cover payload building and endpoint invocation for expense commands
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add expense command group (list/create/update/delete)
2. Add category list/create plus overview and balance commands
3. Register command group and add tests for payload/endpoint mapping/output paths
4. Run full pytest and close task
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Starting expense command implementation.

- Implemented new expense command group with list/create/update/delete.
- Added expense category subcommands (list/create), overview command, and balance recalculation command.
- Added endpoint/payload tests for list/create/update/category/overview mappings with date and paid_for parsing.
- Registered expense command in main CLI and verified full test suite.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- Added full baseline expense CLI surface: CRUD, category list/create, overview, and balance recalc
- Implemented structured payload handling for paid_by/paid_for/date/category/statistics flags
- Added command-level tests for endpoint and payload mapping and validated with uv run pytest
<!-- SECTION:FINAL_SUMMARY:END -->
