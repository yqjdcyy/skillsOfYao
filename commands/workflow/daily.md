# Daily Report

Apply the **report-workflow** skill to generate today's work report.

## Steps

1. Get today's changes from `plan.md`: run `git diff plan.md` (or `git diff -- plan.md`) in this project. Focus on **additions** (`+` lines); deletions (completed items) can be ignored. If plan.md has no prior commit, read the full `# TODAY` section.
2. Combine with any user input (additional work items or corrections).
3. Generate the daily report using the **日报** template from report-workflow's templates.
4. **链接透出**：plan.md 中完成项或相关描述若包含 URL（如 `https://lexiangla.com/...`、`Launch-87610`、`http://wiki...` 等），须在日报完成细项中原样保留或转为 Markdown 链接，如 `[描述](url)` 或 `描述（[链接](url)）`。
5. **多层次展现**：完成细项需按 plan.md 原有层级输出，用缩进体现父子关系。例如：`- 功能上线` 下有 `上线合并`、`PRE 回归校验` 等子项时，子项缩进一层；子项下再有细项则继续缩进。
6. Append to `{year}-luckin.md` (e.g. 2026-luckin.md) under the `## 日报` section. Create the file and section if they do not exist.
7. Run `git add plan.md {year}-luckin.md && git commit -m "daily: $(date +%Y-%m-%d)"` to establish the diff baseline for the next day.
