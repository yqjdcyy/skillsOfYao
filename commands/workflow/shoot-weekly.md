# Shoot-Weekly (Troubleshooting Iteration Report)

Apply the **report-workflow** skill to generate a troubleshooting domain iteration summary for the last week.

## Steps

1. Read the target cycle's daily reports from `reports/{year}/daily/`.
2. Summarize troubleshooting iteration progress by direction: 触发能力、分析能力、生命周期管理、其它.
3. Output using the shoot-weekly template from report-workflow templates.
4. Default behavior: output in chat only.
5. Only write a file if the user explicitly asks to save the summary.
