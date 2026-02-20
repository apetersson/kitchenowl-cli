---
id: TASK-019
title: Add file/photo upload workflow for recipes and expenses
status: To Do
assignee: []
created_date: '2026-02-20 13:21'
labels:
  - feature
  - v0.3
dependencies: []
references:
  - ../missing2.txt
priority: medium
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add CLI command(s) to upload local files via /api/upload and return reusable file identifiers
- [ ] #2 Wire uploaded file identifiers into recipe and expense commands via --photo or dedicated attach subcommands
- [ ] #3 Support --json and human-readable output for upload operations
- [ ] #4 Add tests for upload endpoint invocation and command payload integration
<!-- AC:END -->
