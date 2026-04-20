# Reliability

> Reliability requirements, SLOs, and operational guidelines for skillsOfYao.

## SLOs

- Generated skills and commands should remain readable and internally consistent after each workflow change.
- Repo-level reliability is measured more by maintenance safety than by uptime because this is a source repository, not a hosted service.

## Error Budget

- Draft-level documentation gaps are acceptable during exploration.
- Mismatches between command docs, skill rules, templates, and config are not acceptable in merged changes.

## Incident Response

- If a skill change introduces inconsistent behavior, stop further rollout and reconcile the design doc, skill file, templates, and command entrypoints first.
- If an external integration path or MCP root is missing, fail closed and ask the user for configuration instead of guessing.

## Monitoring

- Current monitoring is manual:
  - repo diffs
  - design/skill/template consistency checks
  - local lint or script-based verification
- As the Harness trial matures, `scripts/harness/knowledge-check.sh` becomes the minimum repo-structure monitor.
