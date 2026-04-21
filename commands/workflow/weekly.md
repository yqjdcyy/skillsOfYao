# Weekly Report

Apply the **report-workflow** skill to generate this week's work report.

## Steps

1. Use the default weekly cycle `上周五 -> 本周四`.
2. Resolve the previous weekly report baseline:
   - prefer the online Lexiang weekly report
   - fall back to the last local weekly file if online data is unavailable
3. Compare cycle-scoped `plan.md` content and extract newly added work content.
4. Read in-cycle daily entries from `reports/{year}/daily/{year}-{month}.md` when available.
5. For each work item, use the previous weekly report as the baseline progress. New work items start at `0%`.
6. Update progress with the stage mapping `设计 20% / 开发 50% / 测试 80% / 上线 100%`.
7. Generate the draft using the weekly work-item block format: **`完成细项` 按功能合并**，不按日期逐条写；`其它` 按主题合并（双周会、答疑、学习等）。
8. **对比上周**：说明上周基线来自乐享上周周报或本地 `reports/{year}/weekly/{year}-W{前一周}.md`。**进度**：每个工作事项 `- 进度：` 写 `{上周末}%->{本周}%`（上周末取上周该标签进度串最后一个百分数；新事项 `0%->…`）。无上周稿时在文中写明。
9. 展示草稿；用 **`AskQuestion`** 走 report-workflow **Confirmation Gate**（见 skill）；无该工具时降级为文字三选一。
10. 用户确认后：写入 `reports/{year}/weekly/{year}-W{week}.md`，再 `git add` / `commit` / `push`（与本次周报相关的 `plan.md` 等若有修改一并纳入）。
11. If Lexiang weekly sync is configured, sync to `02.个人周报/{年份} - 监控组个人周报/{周期}【监控组个人周报}`. Create missing folders when needed. If copy is unsupported, create a new document instead.
