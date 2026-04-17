---
name: init-cursor-plan
description: Structures prompts for Cursor plan with requirement description, feature breakdown, implementation details, and constraints. Use when preparing a plan prompt, scoping a change for Cursor plan, or when the user wants plan execution to be accurate and minimal in scope.
---

# Cursor Plan 提示词梳理

帮助把提供给 Cursor Plan 的 prompt 梳理成：需求描述清晰、功能可拆分、实现细节与注意事项明确，在最小化改动范围下便于 Plan 确定与执行。

## 原则

- **边界清晰**：只描述本次要做的范围，不混入无关需求。
- **可执行**：每条变更项对应具体文件/模块/接口，避免模糊表述。
- **可验证**：结果有明确验收标准（接口、行为、配置等）。

## 需求描述

一句说清本次要做的事，例如：「实现根因 TopN 与处置入口的关联」。

## 功能拆分

按**阶段**组织，每阶段包含：

| 项 | 说明 |
|----|------|
| **项目** | 如 zeus-nebula、zeus-home、zeus-react |
| **影响范围** | 类、方法、文件或路径，如 `com.ucarinc.monitor.zeus.home.service.fault.FaultService`、`/dashboard/rca/clue-config` |
| **功能点** | 具体改动点，逐条列出 |

多端/多模块时用多阶段；同一阶段内功能点对应到「动哪里」时尽量精确到方法或接口。

## 最小化改动范围

- 用「仅」「只」「不修改」等限定词明确边界。
- 列出**不改动**的模块/接口/配置，避免 Plan 扩大范围。
- 复用现有逻辑时，写清「沿用 X，仅调整 Y」。
- 新加代码优先放在新类/新方法，避免大段改老逻辑。

## 注意事项（在 prompt 中显式写出）

- 优化上下文经济效益，精简输出，避免无价值输出，提升输出质量的决策性。
- 遵循个人代码规范：`/Users/luckincoffee/Documents/code/Luckin/zeus-nebula/.cursor/rules/personal/qingju.yao01-personal-rule.mdc`
- 视需要补充：兼容性、配置/环境、依赖与顺序、风险点。

## 输出模板（供用户或 Agent 填）

```markdown
## 需求描述

- 「需求描述，如 实现根因 TopN 与处置入口的关联」

## 功能拆分

### 阶段一：「阶段需求描述」
- 项目
    - 「项目名称，如 zeus-nebula、zeus-home」
- 影响范围
    - 「类、方法、文件或路径，如 com.ucarinc.monitor.zeus.home.service.fault.FaultService、/dashboard/rca/clue-config」
- 功能点
    - 「改动点一」
    - 「改动点二」

### 阶段二：「阶段需求描述」
…

## 注意事项

- 优化上下文经济效益，精简输出，避免无价值输出，提升输出质量的决策性
- 遵循个人代码规范 /Users/luckincoffee/Documents/code/Luckin/zeus-nebula/.cursor/rules/personal/qingju.yao01-personal-rule.mdc
```

完整填写示例见 [reference.md](reference.md)。

## 自检清单（提交给 Plan 前）

- [ ] 需求描述是否一句话能说清
- [ ] 每阶段是否写明项目、影响范围、功能点
- [ ] 影响范围是否具体到类/方法/路径
- [ ] 注意事项是否包含上下文精简与个人规范
