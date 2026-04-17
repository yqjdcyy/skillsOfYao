---
name: report-workflow
description: Generates daily/weekly/monthly work reports from plan.md and record files. Use when /daily, /weekly, /monthly, or /shoot-weekly commands are invoked to append formatted reports to {year}-luckin.md.
---

# Report Workflow

Work report generation for Luckin work records. Supports four report types: daily, weekly, monthly, shoot-weekly.

## Config

Read defaults from `config/system.json`.

Required keys:

- `paths.recordRepoRoot`
- `paths.reportTemplatePath`
- `reportWorkflow.authorName`
- `reportWorkflow.reviewGroup`
- `reportWorkflow.lucpCreatorKeyword`

If these keys are missing, ask the user to provide them first.

## Paths

| Item | Path |
|------|------|
| Plan | `{paths.recordRepoRoot}/plan.md` |
| Record | `{paths.recordRepoRoot}/{year}-luckin.md` e.g. 2026-luckin.md |
| Templates | `paths.reportTemplatePath` or local [templates.md](templates.md) |

## /daily

1. **Input sources**: User input + git diff of `{paths.recordRepoRoot}/plan.md` vs last commit (changes made today)
2. **Get today's changes**: Run `git diff plan.md` in the repo configured by `paths.recordRepoRoot` to get uncommitted changes. If no prior commit, use full `# TODAY` section content.
3. **plan.md 分析规则**:
   - **完成细项来源**：**仅限** diff 中 `+` 且被 `<!-- -->` 包围的内容——即新增项中，被注释掉（已完成）的才算今日完成。例如 `+<!-- - 回归测试/ 1 - 2h -->` 表示今日完成「回归测试」。
   - **不算完成**：`+` 行中未被 `<!-- -->` 包围的项（如 `+- 功能上线`、`+- 联调测试 - 2h`）为待做/进行中，**禁止**当作完成细项写入日报。
   - **禁止**将 `-`（删除项）当作「今日完成」——删除项多为已完成后从 plan 移除，不再作为完成细项来源。
   - **今日无新增工作的判定**：该需求下 diff 的 `+` 行中无 `<!-- ... -->` 包围的完成项。
   - **用户补充优先**：用户若说明某需求今日有跟进/完成，以用户为准，列入日报并填写完成细项（可概括写，如「双周会跟进」）。
   - **其它/会议类**：若 diff 中「其它」块有变更（如 双周会准备→双周会、需求收集等），且可能涉及当日跟进，可列入日报，完成细项用概括描述（如「双周会跟进」），避免漏报。
   - **大项后 / 数字**：如 `/ 3` 仅为当日完成优先级，可忽略
   - **工时标识**：大项后 `3h`、`1d` 等格式用于指定该需求工时
   - **场景标签**：涉及 skywalking、SwAgent、国际化 的标为「国际化」，其它默认「国内」
   - **链接透出**：plan.md 中完成项或相关描述若包含 URL（如 `https://lexiangla.com/...`、`Launch-87610`、`http://wiki...` 等），须在日报完成细项中原样保留或转为 Markdown 链接 `[描述](url)` / `描述（[链接](url)）`， lucp 上线单用 `[Launch-xxx](https://lucp.lkcoffee.com/launch/Launch-xxx)`。
   - **多层次展现**：完成细项按 plan.md 原有层级输出，用缩进体现父子关系。顶层环节（如 功能上线、回归测试）为一级；其子项缩进一层；子项下再有细项则继续缩进。
4. **Output**: Generate daily report per [templates.md](templates.md) daily format; 工时 default: 8h total per day, evenly split across demands unless specified
5. **Append** to `{paths.recordRepoRoot}/{year}-luckin.md` under `## 日报` section; if file/section missing, create them
6. **Post-action**: Run `git add plan.md {year}-luckin.md && git commit -m "daily: {date}"` to establish diff baseline for next day

## /weekly

1. **Input sources**: `## 日报` entries in record + last `## 周报` entry (for progress comparison)
2. **Time range**: Default last 7 days, or 上周四～本周四 when specified
3. **Output**: Per [templates.md](templates.md) weekly format: title `{reportWorkflow.authorName} YYYY.MM.DD-YYYY.MM.DD 工作周报`; table columns **工作项 | 进度 | 备注**; aggregate by 工作项 (可合并如 排障订阅能力增强→故障订阅能力建设); 进度 as percentage or x%→y%; 备注 as bullet points (<br>, &nbsp;&nbsp;•); content complete, no 见日报
4. **Append** to `{paths.recordRepoRoot}/{year}-luckin.md` under `## 周报` section

## /monthly

1. **Input sources**:
   - Progress: 本地 `{year}-luckin.md` 中**前一个月**的 `## 月报` OKR 表 + **目标月**的日报；若无前月月报则提示用户手动提供进度/OKR
   - 发版：**lucp MCP** 获取由 `reportWorkflow.lucpCreatorKeyword` 对应创建人的上线单（见下方 lucp 流程）
2. **Time range**: 目标月份 = 上月（1 号～最后一天）
3. **OKR**: 若目标月为 1/4/7/10，需提示用户提供本季度 OKR（Markdown）；用户于对话中补充
4. **Progress update**: 基于前月月报 OKR 进度与目标月日报，计算进度变化（x%→y%），填充 OKR 表与备注
5. **Lucp 发版流程**（必执行）:
   - 调用 `lucp_search_user` keyword=`{reportWorkflow.lucpCreatorKeyword}` 获取 creatorId
   - 调用 `lucp_search_launch`：creatorIds=[creatorId]，createStartTime=目标月 1 日 00:00，createEndTime=目标月最后一日 23:59，pageSize=100
   - 对每条 launch 调用 `lucp_get_business_detail` businessType=LAUNCH, businessNo=Launch-xxx 获取变更详情
   - **tag 版本**：lucp 接口不返回版本号；优先从本地 `{paths.recordRepoRoot}/{year}-luckin.md` 中目标月相关记录（日报/周报/月报草稿）的「三、本月上线」提取，或提示用户手动补充
   - 输出发版表：**项目 | tag 版本 | 变更内容 | lucp 上线单**；项目取自 detail「涉及的应用服务名」映射（home→luckyzeushome，analyzer→luckyzeusanalyzer）；变更内容取自 changeReason、detail、testInfo
6. **Output**: 按 [templates.md](templates.md) 月报格式生成；subtitle 使用 `{reportWorkflow.authorName}-YYYY.MM 工作复盘 ({reportWorkflow.reviewGroup})`；OKR 表同 O 多 KR 时 O 列后续行留空；上线表同服务多版本时服务名列后续行留空；线上变更用 [Launch-xxx](url)；内容完整，无占位符
7. **Append** 到 `{paths.recordRepoRoot}/{year}-luckin.md` 的 `## 月报` 下

## /shoot-weekly

1. **Input sources**: `## 日报` entries in record
2. **Time range**: Default last 7 days
3. **Output**: Iteration summary for troubleshooting domain per shoot-weekly format in [templates.md](templates.md)
4. **Format**: Group by iteration direction (触发能力、分析能力、生命周期管理、其它)

## Record File Structure

```md
## 日报
### 日报｜2026-02-18
...

## 周报
### 周报｜2026-02-18～2026-02-25
...

## 月报
### 月报｜2026-02
...
```

Append new entries under the correct section header. Maintain section order: 日报 → 周报 → 月报.
