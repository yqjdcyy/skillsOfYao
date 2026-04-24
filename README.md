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

其中 `localExposure.projectSkillRoots` 用于维护**各项目内** skill 入口（常见为 `<项目>/.cursor/skills`；若 OpenClaw 等仍使用项目根下 `skills/`，也可把该目录加进列表）。

`install.sh` 行为要点：

- 将本仓库内全部 skill 链到 `shared.cursorRoot/skills`，commands 链到 `.../commands`。
- 对 `projectSkillRoots` 中**每一个已配置目录**：按本仓库 skill **同名**建立或刷新软链；若该处已是同名真实目录则先备份到同级 `_backup_before_skillsOfYao_relink/` 再链；若尚不存在则**新建软链**（与旧版「仅当目录已存在才处理」不同，避免 `report-workflow` 等从未出现在 `.cursor/skills` 时漏装）。
- **唯一源码**：例如 `report-workflow` 以 `work/report-workflow/` 为准；`record/skills/report-workflow` 等历史副本应删除或改为指向本路径的软链，不要双轨维护。

`uninstall.sh` 会移除 `cursorRoot` 下及 `projectSkillRoots` 各目录中、解析后仍落在本仓库内的软链。

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

安装结束可交互配置 **乐享 MCP**：写入 `config/system.secrets.json`（已 `.gitignore`）并合并 `shared.cursorRoot/mcp.json`。亦可之后执行：

```bash
bash scripts/lexiang-mcp-setup.sh
# 或：LEXIANG_MCP_PERSONAL_TOKEN=lxmcp_xxx bash scripts/lexiang-mcp-setup.sh --mcp-only
```

模板见 `config/system.secrets.json.example`。

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
