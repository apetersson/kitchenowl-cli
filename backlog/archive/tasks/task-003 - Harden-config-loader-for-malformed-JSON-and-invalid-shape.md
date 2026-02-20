---
id: TASK-003
title: Harden config loader for malformed JSON and invalid shape
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
  - kitchenowl_cli/config.py
priority: high
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 load_config handles malformed/truncated JSON without crashing the CLI
- [x] #2 Config values are type-validated for critical fields and invalid values are sanitized or ignored safely
- [x] #3 Tests cover malformed JSON and wrong-type fields
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Harden load_config against malformed JSON and IO failures
2. Add config shape sanitizer for critical fields
3. Add tests for malformed and wrong-type configs
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Starting config hardening implementation.

Implemented defensive config parsing and critical field normalization in load_config.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- Hardened load_config against malformed JSON and read errors
- Added config normalization for critical fields (server/tokens/user/default_household)
- Added tests for malformed JSON, non-object JSON, and wrong-type field sanitization
<!-- SECTION:FINAL_SUMMARY:END -->
