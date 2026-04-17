# skillsOfYao

个人 skill 与 command 的唯一源码仓库。

## 系统配置

仓库级系统配置文件：`config/system.json`

优先通过该文件维护当前机器上的路径与默认参数，例如：

- `shared.repoRoot`
- `shared.cursorRoot`
- `localExposure.projectSkillRoots`
- `paths.recordRepoRoot`
- `paths.monitorDetailsRoot`
- `paths.monitorDoneRoot`
- `paths.reportTemplatePath`
- `reportWorkflow.authorName`
- `reportWorkflow.reviewGroup`
- `reportWorkflow.lucpCreatorKeyword`
- `requirementWorkflow.defaultRepos`
- `techExplorer.feishuWebhook`

若配置不存在或缺少关键项，相关 skill、command、脚本应优先提示用户提供配置，而不是继续依赖写死地址。

其中 `localExposure.projectSkillRoots` 用于维护项目内 `.cursor/skills` 入口。`install.sh` 会对这些目录中已存在的同名 skill 做备份并重链到 `skillsOfYao`；`uninstall.sh` 会移除指向本仓库的本地软链。

## 仓库规范

详细规范见：

- `docs/skill-repo-standard.md`

持久规则见：

- `.cursor/rules/skills-repo-standard.mdc`

后续新建 skill 或迁移现有 skill 时，都必须遵守这两份规范。

## 目录

- `learning/`: 学习类 skill
- `work/`: 工作主场景 skill
- `work/document-output/`: 文档输出类 skill
- `work/workflow/`: 工作流类 skill
- `life/`: 生活类 skill
- `commands/`: 共享命令入口
- `scripts/`: 安装、卸载、Git 辅助脚本

## 运行依赖

运行依赖指 `SKILL.md` 明确引用或脚本直接读取的文件，例如：

- `RULES.md`
- `templates.md`
- `reference.md`
- `config/`
- `scripts/`
- `run.sh`

历史产物不作为运行依赖迁入，例如：

- `learning/tech-explorer/output/reports/`

## 安装

```bash
bash scripts/install.sh
```

## 卸载

```bash
bash scripts/uninstall.sh
```

## 新增 Skill

通过 `commands/workflow/new-skill.md` 作为统一入口。

默认规则：

- 新 skill 统一创建到本仓库
- 创建后先确认
- 确认后只执行本地 Git 提交，不自动 push

## 冲突处理

若 `config/system.json` 中的 `shared.cursorRoot` 对应目录下存在同名且不指向本仓库的入口，先人工处理冲突，再执行安装脚本。
