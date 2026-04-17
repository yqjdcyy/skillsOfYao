# Cursor Plan 提示词示例

以下为按本 skill 梳理后的完整 prompt 示例，可直接改写使用。

---

## 示例：订阅关注推送开关

```markdown
## 需求描述

- 为「订阅关注」功能增加总开关，关闭时不再调用下游推送接口，便于故障演练时临时关闭告警推送。

## 功能拆分

### 阶段一：zeus-home 配置与推送逻辑
- 项目
    - zeus-home
- 影响范围
    - 配置读取处（现有 fault 配置类或调用推送的类）、SubscribeAttentionPostProcessor 或等价推送调用处
- 功能点
    - 新增 Gaea 配置项 `fault.subscribe.push.enabled`，默认 true
    - 推送前校验开关，为 false 时跳过推送、不报错

## 注意事项

- 优化上下文经济效益，精简输出，避免无价值输出，提升输出质量的决策性
- 遵循个人代码规范 /Users/luckincoffee/Documents/code/Luckin/zeus-nebula/.cursor/rules/personal/qingju.yao01-personal-rule.mdc
- 未配置时视为 true；仅加判断，不改变推送逻辑本身
```

---

使用方式：将上述内容复制到对话中，按需替换需求描述、阶段、项目、影响范围与功能点，即可作为 Cursor Plan 的输入。
