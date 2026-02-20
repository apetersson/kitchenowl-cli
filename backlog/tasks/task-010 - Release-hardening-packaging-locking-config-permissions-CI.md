---
id: TASK-010
title: 'Release hardening: packaging, locking, config permissions, CI'
status: To Do
assignee: []
created_date: '2026-02-20 12:34'
updated_date: '2026-02-20 12:56'
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
- [ ] #1 pytest is moved out of runtime dependencies into a dev/optional dependency set
- [ ] #2 Config write path applies secure permissions where supported
- [ ] #3 Token refresh/write path is protected against concurrent process race conditions
- [ ] #4 CI/test docs are updated for new behavior and workflows
<!-- AC:END -->
