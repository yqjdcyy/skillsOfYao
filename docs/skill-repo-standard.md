# 技能仓库规范

适用范围：

- 新建 skill
- 现有 skill 迁移入仓
- 新增或迁移 command
- 为 skill 配套编写的脚本、模板、参考文件

本规范对 `skillsOfYao` 仓库内所有 skill 与 command 生效。

## 1. 仓库定位

`skillsOfYao` 是个人 skill 与共享 command 的唯一源码仓库。

禁止做法：

- 直接把新 skill 创建到全局目录
- 在全局目录中手工维护源码副本
- 把绝对路径、人员信息、仓库名、敏感配置写死在 skill 或 command 中

正确做法：

- 源码统一落在本仓库
- 通过安装脚本暴露到全局入口
- 所有默认值优先走 `config/system.json`

## 2. 目录规范

### 2.1 Skill 场景目录

- `learning/<skill-name>/`
- `work/<skill-name>/`
- `work/document-output/<skill-name>/`
- `work/workflow/<skill-name>/`
- `life/<skill-name>/`

### 2.2 Command 目录

- `commands/workflow/<command>.md`
- 后续若新增独立类别，可增设 `commands/<scene>/`

### 2.3 脚本目录

- `scripts/install.sh`
- `scripts/uninstall.sh`
- `scripts/git_report.sh`
- `scripts/config.sh`

### 2.4 文档与规则

- 详细规范：`docs/skill-repo-standard.md`
- 持久规则：`.cursor/rules/skills-repo-standard.mdc`

## 3. Skill 文件结构规范

每个 skill 目录必须至少包含：

- `SKILL.md`

按需包含：

- `reference.md`
- `templates.md`
- `RULES.md`
- `config/`
- `scripts/`
- `run.sh`

禁止迁入或默认保留的内容：

- 历史产物目录，如 `output/`
- 临时调试文件
- 与运行无关的缓存

## 4. 配置规范

### 4.1 配置源

统一配置文件：

- `config/system.json`

所有默认路径、人员信息、仓库名、流程关键参数都应优先从该文件读取。

### 4.2 配置分层

#### `shared`

用于仓库级公共配置，例如：

- `shared.repoRoot`
- `shared.cursorRoot`
- `localExposure.projectSkillRoots`

#### `paths`

用于路径类配置，例如：

- `paths.recordRepoRoot`
- `paths.monitorDetailsRoot`
- `paths.monitorDoneRoot`
- `paths.reportTemplatePath`

#### 业务配置块

按 skill 域拆分，例如：

- `reportWorkflow.authorName`
- `reportWorkflow.reviewGroup`
- `reportWorkflow.lucpCreatorKeyword`
- `requirementWorkflow.defaultRepos`
- `techExplorer.feishuWebhook`

### 4.3 配置使用原则

1. 有配置：直接读取并使用
2. 无配置但能安全降级：使用本仓库内相对资源
3. 无配置且无法安全推断：提示用户优先提供配置

禁止继续使用写死默认值的场景：

- 绝对路径
- 人名
- creator keyword
- 默认仓库列表
- 全局入口目录

## 5. 文案与使用方式规范

### 5.1 Skill 文档

每个 skill 的 `SKILL.md` 推荐包含：

- `## Config`
- `## 何时使用` / `## 执行步骤`
- 对必需配置的说明
- 配置缺失时的处理方式

若 skill 依赖系统配置，应显式写出配置键名，而不是路径常量。

### 5.2 Command 文档

每个 command 需要说明：

- 依赖哪个 skill
- 依赖哪些配置键
- 配置缺失时应先提示用户补充

### 5.3 脚本

脚本必须：

- 优先通过 `scripts/config.sh` 读取系统配置
- 对关键缺失配置直接报错退出
- 不偷偷回退到写死值

## 6. 迁移规范

现有 skill 迁移入仓时，必须完成以下检查：

1. 将源码迁入正确场景目录
2. 补齐运行依赖文件
3. 去掉历史产物目录
4. 搜索并替换所有写死地址、写死人名、写死仓库名、写死全局路径
5. 把默认值沉淀到 `config/system.json`
6. 若暂时无法配置化，至少改为显式提示用户提供
7. 更新 README 或相关文档说明

若存在项目内 `.cursor/skills` 旧入口，优先通过 `localExposure.projectSkillRoots` 统一纳入安装脚本维护，不再人工逐个重链。

## 7. 新建规范

新建 skill 时必须：

1. 使用统一入口 `commands/workflow/new-skill.md`
2. 先确定场景目录
3. 先创建到本仓库，不直接写到全局目录
4. 创建后展示文件清单
5. 用户确认后才允许执行本地 Git 提交

## 8. 验收清单

以下任一项不满足，都不算合规：

- skill 或 command 中仍存在写死绝对路径
- 仍存在写死人名或 creator keyword
- 全局目录位置仍被写死
- 配置缺失时没有提示用户补充
- 新建 skill 没有走统一入口
- 迁移 skill 没有补充运行依赖说明
