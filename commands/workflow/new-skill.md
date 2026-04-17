# New Skill

Create a new personal skill in the repo configured by `config/system.json`, confirm the generated files, then optionally run the local Git flow.

Before creating or migrating any skill, follow:

- `docs/skill-repo-standard.md`
- `.cursor/rules/skills-repo-standard.mdc`

## Rules

1. **Never** create the new skill directly under the global skill directory.
2. Always create the skill under `config/system.json` -> `shared.repoRoot`.
3. Collect the minimum required inputs before creating files:
   - `skill-name`
   - `scene`: `learning` / `work` / `work-document-output` / `work-workflow` / `life`
   - `description`
   - whether extra files are needed:
     - `reference.md`
     - `templates.md`
     - `RULES.md`
     - `config/`
     - `scripts/`
     - `run.sh`
   - whether a command entry is also needed
4. Use these path mappings:
   - `learning` -> `learning/<skill-name>/`
   - `work` -> `work/<skill-name>/`
   - `work-document-output` -> `work/document-output/<skill-name>/`
   - `work-workflow` -> `work/workflow/<skill-name>/`
   - `life` -> `life/<skill-name>/`
5. Create the skill files in the personal repo first.
6. Show the full list of new or modified files.
7. Ask for confirmation before any Git action.
8. If the user confirms Git, run:

```bash
bash scripts/git_report.sh --paths "<space-separated-paths>" --message "<commit message>"
```

9. Only do local Git actions:
   - `git status`
   - `git add`
   - `git commit`
10. Do **not** push automatically.

## Minimum SKILL.md template

```md
---
name: <skill-name>
description: <description>
---

# <skill-name>

## 何时使用

## 执行要点
```
