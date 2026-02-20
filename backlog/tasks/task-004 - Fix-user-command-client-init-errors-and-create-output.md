---
id: TASK-004
title: Fix user command client init errors and create output
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
  - kitchenowl_cli/commands/user.py
priority: high
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 user._client_and_config wraps ApiClient initialization failures as click.ClickException
- [x] #2 create user success output does not print None fields when API omits id/username
- [x] #3 Tests cover unauthenticated user command invocation and create output behavior
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Wrap user _client_and_config initialization errors as ClickException
2. Fix create output to avoid None placeholders
3. Add tests for init and output behavior
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Starting user command bug fixes.

Updated user command helper error wrapping and create-user success messaging.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- user._client_and_config now wraps ApiClient init errors as click.ClickException
- create-user success output now avoids reporting None placeholders when API omits id/username
- Added tests for helper error wrapping and create-user message fallback
<!-- SECTION:FINAL_SUMMARY:END -->
