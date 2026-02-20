---
id: TASK-002
title: Fix API client transport errors and explicit auth mode handling
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
  - kitchenowl_cli/api.py
  - tests/test_api_helpers.py
priority: high
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 ApiClient.request/refresh/login/signup catch requests transport exceptions and raise ApiError with actionable message
- [x] #2 auth mode handling is explicit for access, refresh, and none, and invalid mode fails fast
- [x] #3 Unit tests cover timeout/connection failures and auth=none behavior
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add request exception wrapping around all network paths
2. Make auth mode branches explicit with validation
3. Add focused tests in test_api_helpers.py for transport errors and auth=none
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation started in api.py with tests.

Wrapped requests transport failures in ApiError across request/refresh/login/signup and made auth mode handling explicit.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- Wrapped all transport-level request failures as ApiError in api.py
- Added explicit auth mode handling for access/refresh/none and fail-fast for invalid values
- Added regression tests for request transport errors, auth=none, invalid auth mode, login transport failure, and signup transport failure
<!-- SECTION:FINAL_SUMMARY:END -->
