---
id: TASK-007
title: Fix run_cli_e2e admin lookup fallback and failure behavior
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
  - run_cli_e2e.sh
priority: high
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 run_cli_e2e.sh does not fallback to hardcoded admin id 1
- [x] #2 Script fails with explicit error when admin candidate cannot be resolved
- [x] #3 Script output documents required preconditions for admin assignment
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Remove admin id fallback from e2e script
2. Add explicit error handling when admin lookup is empty or invalid
3. Clarify precondition in script output
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Starting e2e admin lookup hardening.

Removed hardcoded admin fallback and added explicit failure messaging in e2e script.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- Removed unsafe fallback to admin id 1 in run_cli_e2e.sh
- Admin lookup now fails explicitly when no valid admin id is resolved
- Added clear precondition error message for admin availability/search permissions
<!-- SECTION:FINAL_SUMMARY:END -->
