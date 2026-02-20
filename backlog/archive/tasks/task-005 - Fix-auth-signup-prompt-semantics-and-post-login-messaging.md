---
id: TASK-005
title: Fix auth signup prompt semantics and post-login messaging
status: Done
assignee:
  - '@codex'
created_date: '2026-02-20 12:33'
updated_date: '2026-02-20 12:56'
labels:
  - blocker
  - v0.2
dependencies: []
references:
  - kitchenowl_cli/commands/auth.py
priority: high
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 signup prompt asks for username semantics that match backend constraints
- [x] #2 login/signup report partial setup failures clearly without implying full success
- [x] #3 Tests cover updated prompt/message flow behavior
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update signup prompt wording and input flow
2. Improve login/signup post-auth messaging when household fetch fails
3. Add tests for messaging behavior
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Starting auth UX fixes.

Added auth helper for default household setup warnings and updated signup prompt semantics.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- Signup prompt now asks for Username (email remains a separate optional field)
- Login/signup now surface a warning when post-auth default household setup fails
- Added tests for signup prompt text and warning message path in login
<!-- SECTION:FINAL_SUMMARY:END -->
