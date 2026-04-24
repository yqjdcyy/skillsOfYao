# Architecture

> Domain map for skillsOfYao.

## Domains

| Domain | Path | Owner | Description |
|--------|------|-------|-------------|
| report-workflow | `work/report-workflow/` | repo owner | Workflow report generation skill and templates |
| workflow-commands | `commands/workflow/` | repo owner | User-facing command entrypoints that dispatch workflow skills |
| learning-skills | `learning/` | repo owner | Exploration, research, and documentation-oriented skills |
| shared-config | `config/system.json` | repo owner | Cross-skill defaults for paths, authors, repos, and external integrations |

## Key Boundaries

- `commands/workflow/` should stay thin and defer business rules to `work/` or `learning/` skills.
- `config/system.json` is the only shared default source for repo-wide paths and external roots.
- `docs/design/` holds accepted design intent; `work/` holds executable skill behavior.
- `learning/` content may inform `work/` skills, but should not silently become production behavior without an explicit design change.

## Data Flow

1. User invokes a command under `commands/workflow/`.
2. The command applies the target skill under `work/` or `learning/`.
3. The skill reads defaults from `config/system.json`.
4. The skill consumes local inputs such as `plan.md`, design docs, or generated research output.
5. The skill produces local artifacts, prompts, or synced outputs depending on the workflow.

## Infrastructure

- GitHub repository: source of truth for skill and command code
- Cursor / local agent runtime: primary execution environment
- Optional external services: lucp MCP, Lexiang MCP, Context7 documentation MCP
- No dedicated CI is configured yet; validation currently depends on local checks and repository conventions
