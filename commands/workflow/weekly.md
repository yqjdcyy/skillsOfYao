# Weekly Report

Apply the **report-workflow** skill to generate this week's work report.

## Steps

1. Read `{year}-luckin.md`. Extract all `## 日报` entries in the target range (e.g. 上周四～本周四 or last 7 days) and the most recent `## 周报` entry.
2. Use the last `## 周报` to assess progress changes (进度用「x% → y%」或单百分比).
3. Generate the weekly report per templates: **表格列为「工作项 | 进度 | 备注」**；按工作项聚合日报（可合并相近需求，如 排障订阅能力增强→故障订阅能力建设）；进度列填百分比或「x%→y%」；备注列用要点（<br> 换行，子项用 &nbsp;&nbsp;•）；内容完整可展示，不得使用「见日报」等引用。
4. 标题使用 `config/system.json` -> `reportWorkflow.authorName`，格式为 ``{reportWorkflow.authorName} YYYY.MM.DD-YYYY.MM.DD 工作周报``；若配置缺失，先提示用户提供。表头对齐用 `:---`。
5. Append to `{year}-luckin.md` under the `## 周报` section.
