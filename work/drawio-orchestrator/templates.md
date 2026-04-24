# drawio-orchestrator templates

## 图类型确认

推荐选项：

- 架构图
- 流程图
- 泳道图

## 结构化预览模板

### 结构化数据

- `edges[].id`：语义不变时保持稳定，不因顺序变化重生

- diagramType:
- groups:
    - id:
      label:
      kind:
- nodes:
    - id:
      label:
      kind:
      groupId:
- edges:
    - id:
      source:
      target:
      label:
      relation:
- annotations:
    - target:
      text:
- legend:
    - label:
      meaning:
- layoutHints:
    direction:
    grouping:
    alignment:

### 文本化预览

- 图的主层次：
- 主链：
- 辅助关系：
- 备注：
- 暂不进入主图的内容：

## 二次确认提问模板

- 是否需要增删节点？
- 是否需要调整层次或分组？
- 是否需要调整主链或辅助关系？
- 是否允许进入渲染阶段？

## 确认通过模板

- 最终图类型：
- 审批结论：通过
- 是否允许进入渲染阶段：允许

### 下游传递结构化数据

- `edges[].id`：语义不变时保持稳定，不因顺序变化重生

- diagramType:
- groups:
    - id:
      label:
      kind:
- nodes:
    - id:
      label:
      kind:
      groupId:
- edges:
    - id:
      source:
      target:
      label:
      relation:
- annotations:
    - target:
      text:
- legend:
    - label:
      meaning:
- layoutHints:
    direction:
    grouping:
    alignment:
