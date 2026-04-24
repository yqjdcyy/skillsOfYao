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

If any required key is missing, ask the user to provide it first. If a Lexiang sync is needed but any Lexiang key is missing：**仍可对报告文件落盘并 git push**，仅跳过乐享同步并在回复中说明须补配置；或在 **AskQuestion** 确认前先行提示缺项（由执行方二选一，不得静默失败）。

## Paths

| Item | Path |
|------|------|
| Plan | `{paths.recordRepoRoot}/plan.md` |
| 日粒度细节补充（可选） | `{paths.recordRepoRoot}/today.md`；若仓库另有 `daily.md` 则与 `today.md` **二选一同源角色**，见 **「日粒度细节补充文件」** |
| Daily reports | `{paths.recordRepoRoot}/reports/{year}/daily/{year}-{month}.md` |
| Weekly reports | `{paths.recordRepoRoot}/reports/{year}/weekly/{year}-W{week}.md` |
| Monthly reports | `{paths.recordRepoRoot}/reports/{year}/monthly/{year}-{month}.md` |
| Templates | `paths.reportTemplatePath` or local [templates.md](templates.md) |

## Shared Rules

### Confirmation Gate

All four report types must follow this gate:

1. Collect inputs
2. Generate draft
3. Show the draft；**与用户确认**：在 **Cursor Agent** 中 **必须**调用 **`AskQuestion`**（内置工具）呈现选项，**不得**仅依赖聊天内「回复 1/2/3」作为唯一确认方式。
4. **`AskQuestion` 标准三选项**（一条 question、三个 option id；`label` 用简短中文）：
   - `confirm`：确认并执行落盘；`git add` / `git commit` / `git push` 时**须**将 **日报成稿** 与 **`plan.md`、`today.md`**（及与 `today.md` 同角色的 **`daily.md`**，若存在）**一并纳入同一提交**（见 **「/daily Post-confirm Actions」**）；并按类型执行乐享同步（若配置完整）
   - `cancel`：取消，不改仓库
   - `revise`：用文字补充要求后重新出稿（用户下一条消息给出补充后从步骤 2 重跑，再 **再次** `AskQuestion`）
5. **仅当用户选择 `confirm`**：**直接**写入目标文件并完成 git 与乐享（若可）。**不**再插入「请自行改稿后再保存」；成稿以当前草稿为准，除非用户选了 `revise` 并触发了重新生成。
6. 若乐享相关配置不全：用户 **`confirm`** 后**仍**执行报告落盘与 `git push`，仅**跳过**乐享同步并在回复中说明原因。
7. **降级**：仅当运行环境 **不具备** `AskQuestion` 时，可用文字列举等价三选一（原「数字菜单」语义）。

#### Cursor `AskQuestion` 调用约定

- **何时调用**：每次展示周报/月报/日报/ shoot-weekly 需保存的草稿之后、**第一次**执行写文件与 git 之前；`revise` 循环中每次新草稿后 **再调用一次**。
- **与草稿的关系**：同一条回复中可先简述草稿要点，再 **紧接着** 调用 `AskQuestion`；选项 id 与上表一致，便于会话追溯。
- **工时超额均分**（日报「1.5d 上限」）：同一套闸门，但该步的 `AskQuestion` 三选项为：`apply_split`（按均分落盘）、`keep_hours`（保留原始各条工时）、`revise`（补充说明后重新出稿）。

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
- **`- 文档`（跟进用）**：用户要求或事项含调研/方案/对照时，宜写全 **https URL** 与需跟进的 **本地文件绝对路径**（如 `monitor/details/.../*.md`）。**禁止**将 `plan.md` 里独立的 **`## 相关文档` / 通用「操作文档 / 答疑文档」块** 无差别复制到**每一个** `###` 事项下。某事项的 `- 文档` 仅允许来自：**(a)** 该事项在 `plan`/`today` 的**对应块、子 bullet 或 `<!-- ... -->` 中明确出现的**链接或路径；**(b)** 用户当轮在会话中**为该项单独指定**的链接（含补链、更正）。
- **工时行书写**：`- 工时： 3h` —— **冒号后空一格**再写数值与单位（`h` / `d` / `天` 等，解析脚本与 `1d=8h` 换算一致）。
- **非工时标记**：`plan` 中标题行常见的 **` / 1`、`/ 2`** 等为**优先级/分组/排序**自用小记，**不是**日报 `- 工时` 的数字来源。日报 `- 工时` 只来自**用户当轮口头指定**、或 **`<!-- ... - Nh -->` / 注释里与该项可对读的 `Nh`**；二者皆无时**可省略** `- 工时` 行，**不得**用「`/ 1` = 1h」等方式推断填数。
- **换算与 1.5d 上限**：统计时 **`1d` = 8h**；只累加**能解析出正数工时**的条目。若当日 **合计 > 12h（1.5d）**，视为不合理堆积，**将 12h 在 n 个有工时条目间均分**（`n` 为上述条目数），再写回各条 `- 工时`。交互生成日报时：草稿中写明**原合计**与**均分结果**，并请用户用 **`AskQuestion`** 在 `apply_split` / `keep_hours` / `revise` 中择一（语义见 **「Cursor `AskQuestion` 调用约定」** 之工时超额均分条）；无 `AskQuestion` 时降级为文字三选一。
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

### 日粒度细节补充文件（`today.md`）

- **定位**：仅作 **细节补充**（措辞、`完成细项` 颗粒度、对照与链接线索），**不**单独决定「当日有哪些事项要写进日报」。
- **不得**仅凭该文件块标题，把未在 `plan.md` + 下文 **plan 对齐规则** 中出现的主题升格为独立 `###` 主线（除非用户确认）。
- 与 `plan` **共用范围**：只合并 **已纳入本日日报候选** 的对应段落/列表；与当日主线无关的探索块不强行写入。
- 仓库实现：以 `{paths.recordRepoRoot}/today.md` 为主；若存在 `daily.md` 且团队约定使用，则与其 **二选一**，语义与本节相同。凡写入「完成」类内容，**与 `plan.md` 共用下条「完成认定」**；不得仅因正文出现在 `today.md` 就等同已闭环。

### 完成认定（`plan.md` + `today.md`）

对**今日写入日报**时记为**已完成**（`完成细项` 下、作为落地事实的条目）的事项，**须同时满足**：

1. 在 **相对 `HEAD`（或用户指定 ref）的 `git diff plan.md` / `git diff today.md` 中** 呈现为 **`+` 新增行**（仅删、仅改、无新增行**不**单独作为「本日新完成」依据）。
2. 与 **`<!-- ... -->` 内标识**可对读：注释内可含简称、`- Nh`、完成戳、URL 或与正文新增强调的对应关系；**用于把「+ 新增」锚定为已验收的完成项**。

**不满足 (1)(2) 的条目**不得写入日报的 **已完成** 表述；**例外**：用户在当轮通过 **`AskQuestion` 明确选项** 或**口述**对某条**单独追认**并同意写入。Agent 在出 `/daily` 草稿前**必须**对 `plan.md` 与 `today.md` 各跑 **`git diff`（对同一 ref）**，并在内部按上表筛「完成」。

### plan.md 对齐：`git diff` 与 `<!-- ... -->`（与「完成认定」联读）

- **新增与注释**：`<!-- ... -->` 内承载**线索、工时、待办、URL、完成与正文列表的对应**；**未**以「`+` 新增行 + 可对读 `<!-- ... -->`」双夹的改动，不自动进入「今日已完成」。
- **与「完成认定」的例外条一致**：有 **用户当轮追认** 的，可写入，但须在会话中留下追认，避免与硬规则误读为冲突。

### plan 结构识别（避免错归事项）

根目录 `plan.md` 中 **同级 `##` 区块相互独立**，生成日报时 **不得**合并错位：

| plan 区块 | 日报侧要点 |
|-----------|------------|
| `## 双周会跟进` 或同类 | 会议/推进/对齐类：**独立** `### 双周会跟进`（或 `plan` 中实际标题），**不得**因「像杂项」就并入 `### 其它` 或**漏写**；块内子项与 `today` 注释对读补全 `完成细项`。|
| `## 答疑` | 支持类工作：**单独** `### 答疑`（或既有等价标题），**不**并入 `### AI 排障专家…`。|
| `## 学习` 或内含「AI 领域名词」「名词解释」等 | **学习/词汇/方法论**：事项名落在 **学习线**（如 `### 学习`、`### AI 领域名词解析`），**不**标成排障主线。|
| `## AI 排障专家` | 仅该块下条目（含块内 HTML 注释线索）归入 **排障专家** 类 `###`，**不**把别块的 AI 探索塞入此项。|
| `## 智能化场景尝试` 等 | 按块内真实列表与注释归属；与「名词解析」同在整块时，按子 bullet/`<!-- -->` 归属拆到对应 `###`，避免一句「AI」全装进排障。|

用户粘贴全文 `plan` 时，以上规则仍适用（结构以粘贴稿为准）。

### Inputs

- user-provided full `plan.md` content, if supplied; otherwise `{paths.recordRepoRoot}/plan.md`（**整体计划**）
- optional: **日粒度细节补充文件**（`today.md`，或仓库约定的 `daily.md`）
- user clarifications override inferred scope

### Processing

1. Read `plan.md`；对 **`plan.md` 与 `today.md`（及存在时的 `daily.md`）** 各运行 **`git diff`**（默认相对 `HEAD`；无 git 或用户指定 paste-only 时跳过，并提示「未对 diff 或完成认定」）。用户粘贴全文 `plan` 时以粘贴为准，但若声称「依完成认定落稿」仍**建议**补跑本地 `git diff` 后对齐。
2. **候选与「完成」分离**：`+` 新增与 `<!-- ... -->` 为 **候选项与追溯线索**；**已完成的日报条目** 须符合 **「完成认定（plan.md + today.md）」**；**禁止**把未满足 (1)(2) 的 diff 新增 **或** 仅口头产出 **直接**写入 **已完成**（除用户追认外）。
3. **当日写入范围**：`###` 事项以 **用户确认的当日主线** 为准；与 **「plan 结构识别」** 表一致，答疑 / 学习名词 / AI 排障专家 **分线命名**，不得因同属「智能/AI」主题而合错栏。
4. **日粒度细节补充文件**：仅用于充实 **`完成细项`**、链接与对照说法；**不**反向覆盖第 2、3 步的范围判定。
5. **工时**：优先**用户当轮口述**；其次 `plan` / 日粒度补充文件内**与该事项可对读的** **`<!-- ... - Nh -->`** 或等价（多事项分项须与用户对齐）。**不得**用 `## 某事项/ 1` 标题里的 ` / 1` 等推断为 1h（见 **「日报格式控制」** 之**非工时标记**）。
6. User 补充优先：用户要求增删事项或文档，照办（含**更正**某条工时、**仅为某事项**补文档链）。
7. **链接与文档**：按 **「日报格式控制」** 的 `- 文档` 条：只挂到**对应事项**；调研/方案类有明确锚点时再写全 URL/路径。禁止把 `## 相关文档` 整段**广播**到所有事项。
8. Summarize by work item，严格遵循 **「日报格式控制」**（事项名标题、字段、工时行、无进度/说明）。
9. 涉及 **工时合计 > 1.5d** 时：按该节 **换算、均分与 `AskQuestion`** 执行（见 **「Cursor `AskQuestion` 调用约定」**）；脚本批处理时的开关与行为亦以 **「日报格式控制」** 该节为准。

### Output

- write to `{paths.recordRepoRoot}/reports/{year}/daily/{year}-{month}.md`
- append the new day entry into the month file

### Post-confirm Actions

- **`git add` 范围（日报）**：除当月 `reports/{year}/daily/{year}-{month}.md` 外，**必须**显式包含 `{recordRepoRoot}/plan.md`、`{recordRepoRoot}/today.md`；若仓库使用 **`daily.md`** 作为日粒度补充文件且存在该路径，**一并** `git add`。目的：与日报同批归档当日计划与补充笔记；若某文件相对 `HEAD` 无变更，`add` 后不会产生额外 diff，仍保持命令一致。
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
