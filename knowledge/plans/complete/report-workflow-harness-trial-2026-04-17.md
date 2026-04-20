# report-workflow Harness trial - 2026-04-17

## Goal

Use `report-workflow` as the first concrete upgrade target while trialing whether Harness Engineering improves planning, repo legibility, and verification flow in `skillsOfYao`.

## Scope

- initialize Harness artifacts under `knowledge/`
- adapt Harness entry assumptions to this repo's constraints
- upgrade `report-workflow` skill, templates, commands, and config
- run a minimum verification loop

## Success Criteria

- `knowledge/` becomes a usable secondary knowledge base without polluting `docs/`
- `report-workflow` aligns with `docs/design/report-workflow.md`
- `scripts/harness/knowledge-check.sh` passes after repo-specific adaptation
- the trial produces enough signal to decide whether Harness is worth keeping
