# Shoot-Weekly (Troubleshooting Iteration Report)

Apply the **report-workflow** skill to generate a troubleshooting domain iteration summary for the last week.

## Steps

1. Read the target cycle's daily reports from `reports/{year}/daily/`.
2. Summarize troubleshooting iteration progress by direction: 触发能力、分析能力、生命周期管理、其它.
3. Output using the shoot-weekly template from report-workflow templates.
4. Default behavior: output in chat only.
5. 若用户明确要求**落盘**：展示草稿后以 **`AskQuestion`** 确认路径与内容（见 report-workflow **Confirmation Gate**），再写入。
