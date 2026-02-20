---
id: TASK-016
title: Add category and tag discovery commands
status: Done
assignee:
  - '@codex'
created_date: '2026-02-20 12:35'
updated_date: '2026-02-20 13:08'
labels:
  - feature
  - v0.2.x
dependencies: []
references:
  - ../feedback-zai.txt
priority: medium
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add commands to list categories relevant to shopping/recipe flows
- [x] #2 Add commands to list tags for recipe workflows
- [x] #3 Ensure --json and readable output parity with existing command groups
- [x] #4 Tests cover endpoint invocation and output paths
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add category command group with list output
2. Add tag command group with list output
3. Register groups in main.py and add tests for endpoint mapping/output modes
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Starting category/tag discovery implementation.

- Added new category command group with household-scoped list command.
- Added new tag command group with household-scoped list command.
- Registered both groups in main CLI and added endpoint mapping tests for each list command.
- Both commands support --json and human-readable table output.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- Implemented category and tag discovery command groups with list support
- Added consistent --json/table output behavior and default household resolution
- Added tests covering endpoint invocation paths for category and tag listing
<!-- SECTION:FINAL_SUMMARY:END -->
