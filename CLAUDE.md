# Claude Code — Repo Instructions

## Primary Knowledge Base

**Read @knowledge/index.md before any task.** It is the local table of contents for project knowledge in this repo.

## Enforced Behaviors

1. **Read @knowledge/index.md first.** Before coding, planning, or reviewing — read the knowledge index and follow its pointers.
2. **Update knowledge/ when code changes.** If behavior changes, docs must change in the same PR.
3. **Create plans before multi-step work.** Plans are always single files: `knowledge/plans/<slug>-YYYY-MM-DD.md`. For deep work, the plan links to a details directory at `knowledge/plan-details/<slug>/`.
4. **Plan lifecycle.** Draft → `in-progress/` when executing → `complete/` when done. Move plans through the pipeline.
5. **No tribal knowledge.** If it was discussed in Slack, a meeting, or a conversation — encode it into `knowledge/`. The repo is the single source of truth.
6. **Quality score must not regress.** Check `knowledge/quality-score.md` after changes.
7. **Track tech debt.** New debt gets logged in `knowledge/tech-debt-tracker.md`.
8. **Conventional Commits.** Use `feat|fix|refactor|build|ci|chore|docs|style|perf|test` prefixes.
9. **Files < 500 LOC.** Split large files proactively.
