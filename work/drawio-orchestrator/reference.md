# drawio-orchestrator reference

## 编排目标

总入口只负责确认和收口，不直接承担具体图类型渲染。

## 标准流程

1. 接收用户原始输入
2. 确认图类型
3. 生成结构化中间数据
4. 输出结构化数据 + 文本化预览
5. 等待二次确认
6. 确认通过后，允许进入具体图类型或渲染阶段

## 公共中间数据

- `diagramType`
- `groups`
- `nodes`
- `edges`
- `annotations`
- `legend`
- `layoutHints`

### 消费约定

- `diagramType` 为顶层字段，在确认通过后必填，允许值仅 `architecture`、`flowchart`、`swimlane`
- `groups`、`nodes`、`edges` 为主数据；其余字段可选
- `groups[].id`、`nodes[].id` 必填，且在同一次结果中唯一
- `nodes[].groupId` 若存在，必须引用已声明的 `groups[].id`
- `edges[].id`、`edges[].source`、`edges[].target` 必填，且 `source`、`target` 必须引用已声明的 `nodes[].id`
- 同一语义边在二次确认或迭代调整中，如关系含义未变，`edges[].id` 必须保持稳定，不能因顺序变化而重生
- `edges` 方向语义统一为 `source -> target`，表示主链或依赖流向
- `groups` 用于层级、分组或泳道容器；`nodes` 用于实际图元；`edges` 用于节点间关系
- `annotations` 用于备注、限制、解释；`legend` 用于图例说明
- `layoutHints` 只允许表达全局或分组级布局提示，如方向、分层、对齐，不承载具体坐标

### 最小对象结构

- `groups[]` 至少包含 `id`、`label`，建议补充 `kind`
- `nodes[]` 至少包含 `id`、`label`，建议补充 `kind`；若属于某分组，则补 `groupId`
- `edges[]` 至少包含 `id`、`source`、`target`，建议补充 `label` 或 `relation`
- `annotations[]` 至少包含 `target`、`text`，`target` 可引用 `group.id`、`node.id` 或 `edge.id`
- `legend[]` 至少包含 `label`、`meaning`，用于说明颜色、线型或类别含义
- `layoutHints` 至少包含 `direction`，可选 `grouping`、`alignment`，仅表达布局提示
- `label` 用于展示名称；`kind` 用于下游图类型判断节点或分组类别
- `relation` 用于表达关系类型，如调用、依赖、流转、包含
- `annotations`、`legend`、`layoutHints` 不承载坐标、尺寸或 drawio 私有渲染参数

## 渲染门禁

未完成以下任一项时，不允许进入渲染：

- 图类型确认
- 结构化数据生成
- 用户二次确认

## 与后续图类型 skill 的边界

- 本 skill 负责“先确认、再放行”
- 具体图类型 skill 负责布局和样式细则
- 后续若扩展 `drawio-flowchart`、`drawio-architecture`、`drawio-swimlane`，由它们消费这里产出的结构化结果
