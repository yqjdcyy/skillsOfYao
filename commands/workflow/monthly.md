# Monthly Report

Apply the **report-workflow** skill to generate last month's work report.

## Steps

1. **Read** `{year}-luckin.md`：提取**目标月**（上月）`## 日报`、**前月**`## 月报`（用于 OKR 进度基线）。文件根路径优先使用 `config/system.json` -> `paths.recordRepoRoot`。
2. **Progress**：若无前月月报，提示用户手动提供进度/OKR；否则基于前月月报 OKR + 目标月日报，计算进度变化并更新 OKR 表与备注。
3. **OKR**：若目标月为 1/4/7/10，提示用户提供本季度 OKR（Markdown），等待用户在对话中补充后再继续。
4. **Lucp 发版**（必执行）：
   - `lucp_search_user` keyword=`config/system.json` -> `reportWorkflow.lucpCreatorKeyword` → creatorId
   - `lucp_search_launch` creatorIds、上月 createStartTime/createEndTime → 由我创建的上线单列表
   - `lucp_get_business_detail` 每条 Launch → 变更详情（changeReason、detail、testInfo）
   - 合并本地方案：从 `{year}-luckin.md` 中目标月相关记录提取版本号；若无则提示用户手动提供 tag 版本（lucp 不返回版本）
   - 产出发版表：**项目 | tag 版本 | 变更内容 | lucp 上线单**
5. **Generate** 月报：按 **月报** 模板；subtitle 使用 `reportWorkflow.authorName` 与 `reportWorkflow.reviewGroup`；若配置缺失先提示用户提供。OKR 表同 O 多 KR 时 O 列后续行留空；上线表同服务多版本时服务名列后续行留空；线上变更用 [Launch-xxx](url)。
6. **Append** 到 `{year}-luckin.md` 的 `## 月报` 下。
