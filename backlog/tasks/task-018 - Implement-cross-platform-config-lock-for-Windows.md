---
id: TASK-018
title: Implement cross-platform config lock for Windows
status: To Do
assignee: []
created_date: '2026-02-20 13:21'
labels:
  - hardening
  - v0.3
dependencies: []
references:
  - ../missing2.txt
priority: medium
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Replace fcntl-only lock with cross-platform lock strategy that works on Windows and POSIX
- [ ] #2 Preserve current lock semantics for token refresh and config writes
- [ ] #3 Add tests for lock acquisition/release behavior through abstraction
- [ ] #4 Document Windows behavior and any fallback limitations
<!-- AC:END -->
