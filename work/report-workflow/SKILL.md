---
name: report-workflow
description: Generates daily, weekly, monthly, and troubleshooting summary reports from plan.md into record/reports/{year}/daily|weekly|monthly. Use when /daily, /weekly, /monthly, or /shoot-weekly commands are invoked and the user needs confirmation-first report generation plus git or Lexiang sync.
---

# Report Workflow

Work report generation for Luckin work records. Supports four report types: `daily`, `weekly`, `monthly`, `shoot-weekly`.

## Config

Read defaults from `config/system.json`.

Required keys:

- `paths.recordRepoRoot`
- `paths.reportTemplatePath`
- `reportWorkflow.authorName`
- `reportWorkflow.reviewGroup`
- `reportWorkflow.lucpCreatorKeyword`

Conditional keys:

- `reportWorkflow.lexiangWeeklyRoot`
- `reportWorkflow.lexiangMonthlyRoot`
- `reportWorkflow.lexiangMcpPersonalToken`（仓库内为占位 `<LEXIANG_MCP_PERSONAL_TOKEN>`；实值在 **gitignore** 的 `config/system.secrets.json` 或环境变量 `LEXIANG_MCP_PERSONAL_TOKEN`）
- `reportWorkflow.lexiangMcpServer`（`name`、`url`、`transportType`；与 Cursor 的 `mcp.json` 对齐）
- 在 Cursor 里 `call_mcp_tool` 的 **server** 参数：以工作区 `mcps/<id>/SERVER_METADATA.json` 的 `serverIdentifier` 为准（乐享常为 **`user-lexiang`**），与 `mcp.json` 里配置的 key 可能不一致。

**乐享 MCP 初始化（凭证）**

1. 安装后可选提示，或手动：`bash scripts/lexiang-mcp-setup.sh`（支持 `--token`、`LEXIANG_MCP_PERSONAL_TOKEN`、交互输入）。
2. **默认**：写入 `config/system.secrets.json`（勿提交）并 **合并** `shared.cursorRoot/mcp.json` 中同名服务，便于 Cursor 直接调 MCP。
3. **仅本机 secrets**：`--secrets-only`；**仅写 mcp**（凭证已在 secrets 或环境变量）：`--mcp-only`。
4. 脚本与 `scripts/config.sh` 的 `read_lexiang_mcp_personal_token`：**优先**环境变量 → `system.secrets.json` → `system.json`（跳过占位符）。

If any required key is missing, ask the user to provide it first. If a Lexiang sync is needed but any Lexiang key is missing：**仍可对报告文件落盘并 git push**，仅跳过乐享同步并在回复中说明须补配置；或在数字菜单确认前先行提示缺项（由执行方二选一，不得静默失败）。

## Paths

| Item | Path |
|------|------|
| Plan | `{paths.recordRepoRoot}/plan.md` |
| Daily reports | `{paths.recordRepoRoot}/reports/{year}/daily/{year}-{month}.md` |
| Weekly reports | `{paths.recordRepoRoot}/reports/{year}/weekly/{year}-W{week}.md` |
| Monthly reports | `{paths.recordRepoRoot}/reports/{year}/monthly/{year}-{month}.md` |
| Templates | `paths.reportTemplatePath` or local [templates.md](templates.md) |

## Shared Rules

### Confirmation Gate

All four report types must follow this gate:

1. Collect inputs
2. Generate draft
3. Show the draft; ask for **数字菜单**选择（至少：`1` = 确认并执行落盘与推送；`2` = 取消；可选 `3` = 用文字补充要求后重新出稿）。
4. **仅当用户选择确认项（如 `1`）后**：**直接**写入目标文件、`git add` / `git commit` / `git push`，并按类型执行乐享同步（若配置完整）。**不**再插入「请自行改稿后再保存」的步骤；成稿以当前草稿为准，除非用户在第 3 步选了补充并触发了重新生成。
5. 若乐享相关配置不全：用户数字菜单**确认**后**仍**执行报告落盘与 `git push`，仅**跳过**乐享同步并在回复中说明原因。

### Progress Mapping

Use these stage-based progress defaults when the source text only indicates stage, not percentage:

- `设计` -> `20%`
- `开发` -> `50%`
- `测试` -> `80%`
- `上线` -> `100%`

For weekly and monthly reports:

- baseline progress comes from the previous report
- newly discovered work items start at `0%`
- update progress using the latest stage found in the target cycle

### Report Grouping

**日报**成稿结构以 **「日报格式控制」** 为准（见下节）；母版片段见 [templates.md](templates.md) 日报节。

**周报**仍为分层 `### 具体事项名`，含 `进度`、`说明`、`完成细项` 等（见 templates 周报节）。

杂项可放在 `### 其它`。

### 日报格式控制

与周报区分：日报**不写** `- 进度`、`- 说明`；用 **具体事项名** 作三级标题。

- **标题**：每条任务 **`### 具体事项名`**（如 `### 答疑`、`### 故障处置-v2`），**禁止**用泛化标题 `### 工作事项` 顶替真实事项名。
- **字段顺序**：`- 标签：`；有则 `- 工时：`；`- 完成细项`；可选 `- 文档`。子项缩进与列表层级保持与仓库既有 `reports/{year}/daily` 一致。
- **工时行书写**：`- 工时： 3h` —— **冒号后空一格**再写数值与单位（`h` / `d` / `天` 等，解析脚本与 `1d=8h` 换算一致）。
- **换算与 1.5d 上限**：统计时 **`1d` = 8h**；只累加**能解析出正数工时**的条目。若当日 **合计 > 12h（1.5d）**，视为不合理堆积，**将 12h 在 n 个有工时条目间均分**（`n` 为上述条目数），再写回各条 `- 工时`。交互生成日报时：草稿中写明**原合计**与**均分结果**，并走 **Confirmation Gate 数字菜单**：`1` 按均分落盘；`2` 保留原始各条工时；`3` 用户补充说明后重新出稿。
- **批处理脚本**：`{recordRepoRoot}/scripts/regenerate_daily_reports.py` 用于从 **`2026-luckin.md`** 与 **`daily/*.md`** 重算月度日报；默认对超额日 **自动均分**；`--no-hour-split` 或环境变量 **`DAILY_NO_HOUR_SPLIT=1`** 关闭均分；对调整过的日期会向 **stderr** 输出 `[daily-hours]` 一行便于对账。
- **luckin 与 daily 合并**（脚本逻辑）：同一自然日以 **`2026-luckin.md`** 中 `## 日报｜日期` 段落为主，**`daily/YYYY-MM-DD.md`** 中**标题归一化后不重复**的条目追加在后；若某日期仅见于已落盘的 `reports/.../daily`（无 luckin/daily 源）则保留该段成稿。人工在 Cursor 写 `/daily` 时无此合并，按 plan 与格式控制直接写即可。

### Weekly Aggregation (完成细项)

When building `/weekly` from dailies, `plan.md`, or meeting notes:

- **Merge by function**, not by calendar day: each bullet under `完成细项` describes an outcome or thread (e.g. 上线、hotfix、方案对齐), not `MM-DD：` prefixed lines.
- De-duplicate: same thread spread across multiple days becomes one or a few bullets.
- **Prefer merged phrasing**: combine related bullets into thematic lines (e.g. 上线与版本、开发与验证); use **one level of hierarchy** (group title + sub-bullets) when many items would otherwise sit as messy siblings.
- **`### 其它`**: group 双周会、答疑、学习、`plan` 结构调整等 by topic; avoid day-by-day dumps unless the user explicitly asks for a diary layout.

### Weekly 进度与说明

- **`- 进度：`**：若上周末与本周末为**同一百分数**（如均为 100%），写**单一** `100%`，不写 `100%->100%`。有真实推进时保留 `A%->B%`。
- **`- 说明：`**：体现**最新**进度与关键路径；**上线/发版**尽量写清**版本号、Launch、tag**（可从日报或上线单补）。避免仅「本周围绕…推进」式空话。
- **进度格式**：`A%->B%` 中间**不留空格**（例如 `50%->100%`，不要 `50%-> 100%`）。

### Weekly 本地成稿版面（record）

写入 `{year}-W{week}.md` 的**成稿**只承载工作事实，不承载生成过程或日历流水账：

- **须有**：`## 周报｜{周期}`（与乐享该周页面标题/周期一致）；`### 乐享个人周报地址`（**本周**、**上周**、**库入口** 三条链接，`company_from` 等与 `reportWorkflow.lexiangWeeklyRoot` 一致）；各 `### 事项名` 下按需含 **`- 进度：`**、**`- 说明：`**、**`- 完成细项`**、**`- 文档`**（无则省略小节）。
- **不得写入成稿**：文首 blockquote 里 MCP/对账/流程说明；`### 对比上周`；**`- 对照：`**；`完成细项` / `说明` 里按 **MM-DD** 或「周几」拆条；「哪几天有/无日报」「摄入了哪几天」等元信息；`call_mcp_tool`、工具名等过程描述。
- **对账与 MCP**：生成前可用 **`user-lexiang`** 拉取乐享本周/上周页、`entry_describe_ai_parse_content` 对齐 **事项名、进度、备注**；上周 baseline 取自乐享优先、本地 `{year}-W{week-1}.md` 次之——仅用于**推导**成稿内容，**不**把对账步骤写进 md。
- **乐享表 ↔ 本地**：线稿表格无备注时，本地可在 `说明` 或 `完成细项` 合并日报/plan 补充，**不出现日期前缀**；同步乐享前若需与表格式一致，按乐享版面删减（见 **`### 其它` 双轨**）。

### Weekly 事项合并与乐享对账（经验）

从「仅日报聚合」到「与乐享定稿一致」时按下列规则收敛（**合并逻辑用于成稿内容，不额外输出 `- 对照` 小节**）：

- **同一产品迭代只保留一条 `###`**：若日报里「准确率 / 评分优化 / hotfix」等实为**同一迭代、同一上线窗口**，周报**不得**拆成两条平行事项（避免双 `100%`、同一迭代分裂成两节）。合并为**乐享所用事项名**（如「故障分析评分迭代」），`完成细项` 用 **Weekly Aggregation** 去重合并。
- **标题与阶段对齐乐享**：可用「`事项名.阶段`」（如 `AI 排障专家.方案设计`）。**阶段未到交付**时，不得仅因日报里「评审/开发很忙」就写成 `0%->100%`；**`- 进度：`** 须与**乐享上周 baseline + 本周真实阶段**一致（设计期可能为 `35%->50%` 等）。
- **定稿覆盖草稿**：用户粘贴或指定**乐享/实际周报片段**时，以其中的**事项名、进度、说明、完成细项、Launch/文档**为准**重写**该节；日报多出的细项并入同一节 `完成细项` 或 **`### 其它`**，用语义合并表述，**不加日期标签**；避免与乐享主文矛盾。
- **上线信息写全**：合并迭代事项的 `- 说明：` 写清**版本号**（含补丁线，如 v3.34.1 / v3.34.1.1）；`- 文档` 优先列 **LUCP Launch** 全 URL，可并列乐享设计/评审页。
- **`### 其它` 双轨**：乐享常为**简版**（如双周会、若干工具体验）；本地 `record` 可列更全的并行项，**同步乐享前**按线稿版面删减至一致。

## /daily

### Inputs

- user-provided full `plan.md` content, if supplied
- otherwise the current `{paths.recordRepoRoot}/plan.md`
- direct current changes are the default comparison source

### Processing

1. Prefer full `plan.md` pasted by the user; otherwise read the local `plan.md`.
2. Compare against the current baseline and extract today's newly completed content.
3. User补充优先。If the user says a work item should be included, include it.
4. Preserve links, Launch IDs, and document references.
5. Summarize by work item，严格遵循 **「日报格式控制」**（事项名标题、字段、工时行、无进度/说明）。
6. 涉及 **工时合计 > 1.5d** 时：按该节 **换算、均分与数字菜单** 执行；脚本批处理时的开关与行为亦以该节为准。

### Output

- write to `{paths.recordRepoRoot}/reports/{year}/daily/{year}-{month}.md`
- append the new day entry into the month file

### Post-confirm Actions

- `git add` the touched report file and related `plan.md` if changed
- `git commit -m "report(daily): {date}"`
- `git push`

## /weekly

### Time Range

- default cycle: `上周五 -> 本周四`

### Inputs

- cycle-scoped `plan.md` changes
- previous weekly report progress baseline
- previous weekly report should prefer the online Lexiang copy
- if online weekly report is unavailable, fall back to the last local weekly file

### Processing

1. Determine the target Friday-Thursday cycle (or the user-specified range; still use `{year}-W{week}` from the cycle end date for the filename).
2. Resolve the previous weekly report baseline:
   - Lexiang first
   - local file second
3. Compare the cycle's `plan.md` content and extract newly added work content.
4. Ingest daily files under `reports/{year}/daily/{year}-{month}.md` that fall in the cycle when present.
5. For each work item:
   - use the previous weekly report (Lexiang or local `{year}-W{week-1}.md`) as baseline progress
   - default new work items to `0%`
   - update progress by the latest detected stage
6. **Reconcile internally** (do not write into the markdown): Lexiang group page via MCP **`user-lexiang`** (`entry_list_children`, `entry_describe_ai_parse_content`) for 本周/上周 author row; merge with **Weekly 事项合并与乐享对账**; ingest dailies **only** through **Weekly Aggregation** (no day-indexed output).
7. **Build the local weekly file** per **Weekly 本地成稿版面（record）**:
   - `## 周报｜{周期}` then `### 乐享个人周报地址`（本周、上周、库入口）。
   - Each `### 事项名`: **`- 进度：`**（规则见 **Weekly 进度与说明**：有变化 `A%->B%`，无变化单一 `B%`，不写 `100%->100%`；上周无百分数时可用 `（上周无百分数）->B%`；新事项 `0%->B%`；「上周末」取 baseline 串中**最后一个**百分数）、**`- 说明：`**、**`- 完成细项`**、**`- 文档`**。
   - **禁止**出现在成稿：`### 对比上周`、`- 对照：`、blockquote 流程/MCP、MM-DD 拆条、日报摄入元信息。

### Output

- write to `{paths.recordRepoRoot}/reports/{year}/weekly/{year}-W{week}.md`

### Lexiang Sync

After confirmation and local write:

1. push git changes
2. sync to Lexiang using:
   - root: `reportWorkflow.lexiangWeeklyRoot`
   - hierarchy: `02.个人周报/{年份} - 监控组个人周报/{周期}【监控组个人周报】`（验证稿等可在标题追加 `【验证】`，**周期与本地 `## 周报｜` 标题一致**）
3. If the hierarchy does not exist, create it.
4. If copying the previous weekly document is supported, copy first and overwrite content.
5. If copying is not supported, create a new document with the target title.

## /monthly

### Time Range

- default target month: `上月`

### Inputs

- target month's `plan.md` changes
- previous monthly report progress baseline
- previous monthly OKR content
- target month's daily reports
- lucp release records for the target month

### Processing

1. Resolve the target month.
2. Read the previous monthly report:
   - use its work-item progress as the default baseline
   - copy its OKR section as the default OKR source
3. Compare the month's `plan.md` content and extract newly added work content.
4. Update work-item progress with the stage mapping rules.
5. Update monthly OKR progress using the target month's daily reports.
6. If the target month is `1 / 4 / 7 / 10`, or if no OKR exists, ask the user to provide OKR text or links first.
7. Run the lucp release flow:
   - `lucp_search_user` with `reportWorkflow.lucpCreatorKeyword`
   - `lucp_search_launch` for the target month
   - `lucp_get_business_detail` for each launch
   - if tag version is still missing, ask the user to provide it
8. Generate the monthly draft with complete content and no placeholders.

### Output

- write to `{paths.recordRepoRoot}/reports/{year}/monthly/{year}-{month}.md`

### Lexiang Sync

After confirmation and local write:

1. push git changes
2. sync to Lexiang using:
   - root: `reportWorkflow.lexiangMonthlyRoot`
   - hierarchy: `03.工作复盘/{年份}工作复盘（监控组）/{authorName} -{周期} 工作复盘 ({reviewGroup})`
3. If the hierarchy does not exist, create it.
4. Create or update the target monthly review document.

## /shoot-weekly

### Inputs

- target cycle's daily reports

### Processing

1. Read the daily reports in the target cycle.
2. Group the troubleshooting summary by:
   - `触发能力`
   - `分析能力`
   - `生命周期管理`
   - `其它`
3. Generate the summary using the shoot-weekly format from [templates.md](templates.md).

### Output

- default: return in chat
- if the user explicitly asks to save it, write to the requested location

## Notes

- Keep `shoot-weekly` behavior explicit. Do not silently write files unless the user asks.
- Do not claim git push or Lexiang sync succeeded unless you have actually run the command or MCP action and checked the result.
