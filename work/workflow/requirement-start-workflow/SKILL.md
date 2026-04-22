---
name: requirement-start-workflow
description: Creates a new requirement workspace under monitor details directory. Creates a {month}-{summary} folder and an onboarding markdown following the Zeus monitor release template. Use when starting a new requirement, feature, or release in the Luckin monitor project.
---

# 需求开始流程

## Config

与本 skill 目录同级：读取 `requirement-start-workflow/config/system.json` 中的 `paths.monitorDetailsRoot`。

路径或键缺失时，先请用户补全。

## 月份（YYMM）

- **含义**：`YY` = 公历年份后两位，`MM` = 月份（01–12，两位补零）。例：`2603` = 2026 年 3 月。
- **取值**：
  1. 用户在本轮消息中明确给出的 YYMM（归属非当前自然月时，以用户为准）；
  2. 未给出时，用**当前公历年月**生成 YYMM：`YY` + `MM`（取执行时的权威当前日期：优先会话 user_info「Today's date」等已给出的日期；否则用运行环境当前日期）。
- **不得**：凭 `monitorDetailsRoot` 下其它文件夹名猜测 YYMM；不使用配置文件中的固定默认 YYMM。

## 执行步骤

1. **确认需求信息**：解析或确认 `月份`（YYMM）与 `需求概述`（简短描述，如 CursorSDD模式尝试），月份按上一节规则处理。

2. **创建需求目录**：在 `paths.monitorDetailsRoot` 下创建目录 `{月份}-{需求概述}`

3. **创建上线文档**：在上述目录下创建 `{需求概述}功能上线.md` 或 `{月份}-{需求概述}上线.md`，内容使用下方模板

## 目录与文件命名

| 项 | 格式 | 示例 |
|----|------|------|
| 月份 | YYMM（YY=年份后两位，MM=01–12） | 2603 |
| 需求概述 | 简短描述 | CursorSDD模式尝试 |
| 目录名 | {月份}-{需求概述} | 2603-CursorSDD模式尝试 |
| 文档名 | {需求概述}功能上线.md 或 {目录名}上线.md | 2603-CursorSDD模式尝试上线.md |

## 上线文档模板

```markdown
# 改动内容

# 开发进度

- home
- analyzer

# 配置变更

# 版本记录

- 开发分支
    - 
- 上线分支
    - 
- tag 记录
    - 
- 变更记录
\`\`\`md

\`\`\`

# 上线顺序

- 配置变更/ 前
- 工单审批
- 配置变更/ 中
- 服务发布
- 功能验证
- 日志观察
- 配置变更/ 后
- 工单完成
```

完整样本见 [reference.md](reference.md)

## 配置变更格式说明

如需在「配置变更」中填写，使用：

```markdown
- + 配置项路径
> 配置说明

\`\`\`json
{
    "key": "value"
}
\`\`\`
```

## 示例

**输入**：创建需求「2603-CursorSDD模式尝试」

**输出**：
- 目录：`{paths.monitorDetailsRoot}/2603-CursorSDD模式尝试/`
- 文件：`2603-CursorSDD模式尝试/2603-CursorSDD模式尝试上线.md`
