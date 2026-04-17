# Shoot-Weekly (Troubleshooting Iteration Report)

Apply the **report-workflow** skill to generate a troubleshooting domain iteration summary for the last week.

## Steps

1. Read `{year}-luckin.md`. Extract all `## 日报` entries from the last 7 days.
2. Summarize iteration progress in the troubleshooting domain. Group by direction: 触发能力、分析能力、生命周期管理、其它.
3. Output using the shoot-weekly format from report-workflow's templates:
   - `### 「迭代方向」` (e.g. 触发能力、分析能力、生命周期管理、其它)
   - Overall progress and key details
   - Sub-items by demand size
   - Relevant design docs, follow-up docs
4. Output to chat (or append to a dedicated section if specified). Default: output in chat.
