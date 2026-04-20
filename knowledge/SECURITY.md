# Security

> Security guidelines, threat model, and compliance requirements for skillsOfYao.

## Threat Model

- Protect repository source rules, workflow logic, and configuration from accidental drift or unsafe agent edits.
- Main risks are:
  - hard-coded local paths
  - accidental leakage of external roots or private workflow details
  - agents silently changing workflow behavior without updating design intent

## Authentication & Authorization

- External system access should flow through configured MCP integrations rather than copied credentials in repo files.
- Commands and skills should reference config keys, not embed secrets or tokens.

## Data Protection

- Do not store secrets in skill source, command docs, or design docs.
- External roots and identifiers may exist in config, but sensitive values should stay empty until the user deliberately fills them.

## Dependencies

- Harness-generated helper scripts and external skills should be introduced in a way that does not override protected repo rules.
- Before adopting new integrations, confirm whether they add files that conflict with protected filenames or existing conventions.

## Incident Response

- If a generated tool attempts to write protected files, stop and adapt the workflow rather than forcing the write.
- If a command output includes sensitive values, do not echo those values back into repo docs or chat summaries.
