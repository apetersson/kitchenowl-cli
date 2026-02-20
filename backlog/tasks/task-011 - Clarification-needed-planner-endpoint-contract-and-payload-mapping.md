---
id: TASK-011
title: 'Clarification-needed: planner endpoint contract and payload mapping'
status: In Progress
assignee:
  - '@codex'
created_date: '2026-02-20 12:34'
updated_date: '2026-02-20 12:56'
labels:
  - clarification-needed
  - api-contract
dependencies: []
references:
  - ../feedback-zai.txt
priority: medium
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document exact planner endpoint paths/methods and required payload fields for all planned CLI commands
- [ ] #2 Capture any server-version differences and fallback behavior in notes/docs
- [ ] #3 If ambiguities remain, record them as follow-up tasks without blocking stable commands
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Open question: should CLI expose /api/household/{hid}/planner/recipes in addition to planner list endpoint?
- Open question: should we support legacy --day flags or only --cooking-date for planner operations?
- Open question: confirm whether refresh-suggested-recipes endpoint is stable across supported server versions.

- Implemented planner baseline using /api/household/{hid}/planner, /planner/recipe, /planner/recipe/{id}, /planner/recent-recipes[/page], /planner/suggested-recipes[/page], and /planner/refresh-suggested-recipes.
- Deferred /planner/recipes endpoint exposure; created baseline without it to keep command surface minimal.
- Deferred legacy day-based flags; baseline currently supports --date (YYYY-MM-DD) only.

Status updated to In Progress after initial endpoint mapping and ambiguity capture.
<!-- SECTION:NOTES:END -->
