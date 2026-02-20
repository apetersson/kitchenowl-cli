---
id: TASK-001
title: 'Phase 0: Add blocker regression harness'
status: Done
assignee:
  - '@codex'
created_date: '2026-02-20 12:33'
updated_date: '2026-02-20 12:40'
labels:
  - stability
  - v0.2
dependencies: []
references:
  - ../v0.2-planning.md
priority: high
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Regression tests are added for each v0.2 blocker bug before fixes are merged
- [x] #2 Tests run with uv and fail before fixes, pass after fixes
- [x] #3 Test coverage includes malformed config and transport/network failures
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add regression tests that capture each blocker issue
2. Implement fixes in api/config/user/auth/recipe and run_cli_e2e.sh
3. Run uv test suite and iterate until green
4. Check acceptance criteria and document final summary
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Started blocker implementation batch with subagent analysis for concrete patch scope.

Completed blocker regression suite and implemented tasks 002-007 with green tests.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- Created and executed blocker-focused regression tests across API/auth/config/user/recipe paths
- Implemented all planned blocker fixes (tasks 002-007) including transport error wrapping, config hardening, auth/user UX fixes, recipe payload/visibility fixes, and e2e admin fallback removal
- Verified with uv run pytest (25 passed)
<!-- SECTION:FINAL_SUMMARY:END -->
