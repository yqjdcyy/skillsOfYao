# Plans Index

Plans for skillsOfYao. Every plan is a single `.md` file that moves through the pipeline.

## How It Works

- **Plan file**: `plans/<slug>-YYYY-MM-DD.md` — the card that moves through the pipeline
- **Plan details**: `plan-details/<slug>/` — supporting docs (shaping, breadboards, spikes) + `scratchpad.md` for working notes. Permanent, never moves. Plan file links to it.

## Pipeline

```
plans/              → plans/in-progress/     → plans/complete/
(draft)               (executing)              (done)
```

Only the plan file moves. Details stay in `plan-details/`.

## Draft Plans

| Plan | Created | Has Details | Summary |
|------|---------|-------------|---------|
| — | — | — | No draft plans |

## In-Progress Plans

See [plans/in-progress/](plans/in-progress/) for plans currently being executed.

## Completed Plans

| Plan | Completed | Summary |
|------|-----------|---------|
| [report-workflow-harness-trial-2026-04-17](plans/complete/report-workflow-harness-trial-2026-04-17.md) | 2026-04-17 | Trial Harness on `skillsOfYao` while upgrading `report-workflow` |
