---
name: drawio-orchestrator
description: 统一承接技术 drawio 绘图请求，先确认图类型，再做结构化转换、结构预览和二次确认，确认后才允许进入渲染。用于需要架构图、流程图、泳道图等技术绘图编排，但暂不直接定义具体图类型渲染细则的场景。
---

# drawio-orchestrator

## Config

- 当前版本无必填系统配置
- 若后续接入默认样式、模板目录或渲染脚本，再从 `config/system.json` 增加配置键

## 何时使用

- 用户要生成或梳理技术类 `drawio` 图
- 用户尚未明确图类型，需要先确认是架构图、流程图还是泳道图
- 需要先把原始材料转成结构化数据，再决定是否渲染

## 执行步骤

1. 判断请求是否属于技术绘图编排场景
2. 若图类型不明确，先使用 `AskQuestion` 确认图类型；若不可用，则用文本给出互斥选项，并允许用户手动补充
3. 将用户输入转成结构化中间数据；确认后产出顶层必填字段 `diagramType`
4. 同时展示结构化数据与文本化预览，`diagramType` 允许值统一为 `architecture`、`flowchart`、`swimlane`
5. 请求用户进行二次确认和调整
6. 只有确认完成后，才允许交给具体图类型或后续渲染阶段

## 不负责

- 不直接定义具体图类型布局细节
- 不直接定义具体图类型样式
- 不直接生成最终 drawio 坐标和元素布局

## Additional Resources

- 详细编排流见 [reference.md](reference.md)
- 确认模板见 [templates.md](templates.md)
