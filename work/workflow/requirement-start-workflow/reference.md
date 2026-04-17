# 上线文档样本（最小化容灾功能）

## 完整结构参考

```markdown
# 改动内容

# 开发进度

- 模块
    - 功能项1
    - 功能项2

# 配置变更
> 系统配置、Gaea 配置、数据库变更语句等

- + tsdb.cluster.data.source.mapping
> 时序集群与数据源映射

\`\`\`json
{
    "APM": "zeus_apm_victoriametrics",
    "BASIC": "zeus_basic_victoriametrics",
    "COMMON": "zeus_common_victoriametrics"
}
\`\`\`


# 版本记录

开发分支：

上线分支：

tag 记录：

luckyzeushome-v3.33.3
功能项1
功能项2

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

## 开发进度模块说明

常见 Zeus 模块：core, home, ai, analyzer, alert, anomaly, metrics, notice。新建需求时根据实际涉及模块取消注释并填写。
