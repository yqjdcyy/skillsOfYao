# Monthly Report

Apply the **report-workflow** skill to generate last month's work report.

## Steps

1. Use the target month `上月` by default.
2. Resolve the previous monthly report as the baseline:
   - copy its OKR section by default
   - use its work-item progress as the baseline progress
3. Compare target-month `plan.md` content and extract newly added work content.
4. New work items start at `0%`; update progress with `设计 20% / 开发 50% / 测试 80% / 上线 100%`.
5. Update monthly OKR using the target month's daily reports.
6. If the target month is `1 / 4 / 7 / 10`, or if no OKR exists, ask the user to provide OKR content or links before continuing.
7. Run the lucp release flow:
   - `lucp_search_user`
   - `lucp_search_launch`
   - `lucp_get_business_detail`
   - ask the user for tag versions if lucp cannot provide them
8. Generate the monthly draft using the updated monthly template.
9. 展示草稿；用 **`AskQuestion`** 走 report-workflow **Confirmation Gate**（见 skill）；无该工具时降级为文字三选一。
10. 用户确认后：写入 `reports/{year}/monthly/{year}-{month}.md`，再 `git add` / `commit` / `push`（与本月报相关的 `plan.md` 等若有修改一并纳入）。
11. If Lexiang monthly sync is configured, sync to `03.工作复盘/{年份}工作复盘（监控组）/{authorName} -{周期} 工作复盘 ({reviewGroup})`. Create missing folders when needed.
