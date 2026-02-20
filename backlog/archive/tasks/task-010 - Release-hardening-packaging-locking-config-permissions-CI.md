---
id: TASK-010
title: 'Release hardening: packaging, locking, config permissions, CI'
status: Done
assignee:
  - '@codex'
created_date: '2026-02-20 12:34'
updated_date: '2026-02-20 13:08'
labels:
  - hardening
  - v0.2
dependencies: []
references:
  - pyproject.toml
  - kitchenowl_cli/config.py
priority: medium
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 pytest is moved out of runtime dependencies into a dev/optional dependency set
- [x] #2 Config write path applies secure permissions where supported
- [x] #3 Token refresh/write path is protected against concurrent process race conditions
- [x] #4 CI/test docs are updated for new behavior and workflows
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Move pytest to optional dev dependency set in pyproject
2. Add secure config write permissions and lock primitive
3. Protect refresh token rotation/write path with file lock
4. Update README/docs for test workflows and hardening behavior
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Starting release hardening implementation.

- Moved pytest from runtime dependencies to [project.optional-dependencies].dev in pyproject.toml.
- Added secure config write permissions (0600 on supported platforms) and config file lock helper.
- Updated ApiClient.refresh_tokens to acquire config lock, reload latest refresh token, and persist updated tokens atomically under lock.
- Updated README development/test guidance and troubleshooting docs to reflect new workflows and failure handling.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- Release hardening complete: dependency hygiene, secure config writes, and token refresh concurrency protections implemented
- Added file-lock based token refresh/write coordination and config permission hardening
- Documented updated testing workflow and troubleshooting guidance in README
<!-- SECTION:FINAL_SUMMARY:END -->
