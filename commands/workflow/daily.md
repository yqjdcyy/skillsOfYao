# Daily Report

Apply the **report-workflow** skill to generate today's work report.

## Steps

1. Read `plan.md`（及 `today.md` / `daily.md` 若存在）；可用 `git diff plan.md` 辅助看新增与 `<!-- ... -->` 线索。细则见 skill **「plan.md 对齐」**、**「plan 结构识别」**。
2. Combine with any user input (additional work items or corrections).
3. Generate the daily report using the **日报** format from report-workflow（**「日报格式控制」**）。
4. **链接透出**：plan.md 中完成项或相关描述若包含 URL，须在日报 `完成细项` 或 `- 文档` 中原样保留或转为 Markdown 链接。
5. **多层次展现**：完成细项按 plan.md 原有层级输出，用缩进体现父子关系。
6. Show draft；用 **`AskQuestion`** 走 **Confirmation Gate**（见 skill）。
7. 用户确认后：将新段落写入 `reports/{year}/daily/{year}-{month}.md`。
8. **`git add`**：`reports/{year}/daily/{year}-{month}.md`、`plan.md`、`today.md`；若存在与 `today.md` 同角色的 `daily.md`，一并加入。随后 `git commit -m "report(daily): YYYY-MM-DD"`、`git push`。
