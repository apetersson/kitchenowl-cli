---
id: TASK-011
title: 'Clarification-needed: planner endpoint contract and payload mapping'
status: Done
assignee:
  - '@codex'
created_date: '2026-02-20 12:34'
updated_date: '2026-02-20 13:08'
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
- [x] #1 Document exact planner endpoint paths/methods and required payload fields for all planned CLI commands
- [x] #2 Capture any server-version differences and fallback behavior in notes/docs
- [x] #3 If ambiguities remain, record them as follow-up tasks without blocking stable commands
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

- Documented planner command contract: /api/household/{hid}/planner, /planner/recipe, /planner/recipe/{id}, /planner/recent-recipes[/page], /planner/suggested-recipes[/page], /planner/refresh-suggested-recipes.
- Recorded compatibility decisions: keep --date (YYYY-MM-DD) baseline, defer legacy day-based flags, and defer /planner/recipes exposure to keep v0.2 CLI surface focused.
- No blocker remained for planner baseline delivery; deferred ambiguities are captured as explicit notes rather than release blockers.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
- Completed planner endpoint and payload contract mapping used by implemented planner commands
- Captured version-compatibility and scope decisions (date-first API, deferred legacy/day and extra listing endpoint)
- Clarification output fed directly into TASK-008 implementation with no unresolved release blocker
<!-- SECTION:FINAL_SUMMARY:END -->
