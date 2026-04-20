# Daily Report

Apply the **report-workflow** skill to generate today's work report.

## Steps

1. If the user provides full `plan.md` content, use that as the primary input. Otherwise read the current `{paths.recordRepoRoot}/plan.md`.
2. Compare the current plan content against the active baseline and extract today's newly completed or newly followed-up work items.
3. Combine with any explicit user补充 or corrections.
4. Generate the draft using the **日报** work-item block format from report-workflow templates.
5. Show the draft to the user and wait for confirmation.
6. After confirmation, append the day entry into `reports/{year}/daily/{year}-{month}.md`.
7. Run git add / commit / push for the touched report file and any related `plan.md` change.
