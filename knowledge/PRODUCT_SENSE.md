# Product Sense

> User context, personas, and product intuition for skillsOfYao.

## Users

- Primary user: the repo owner, who maintains reusable skills and workflow commands for daily work
- Secondary user: future agents operating in this repo, who need enough structure to safely update skills without hidden context
- Goals:
  - create and iterate reusable skills quickly
  - keep command entrypoints and skill behavior aligned
  - reduce repeated prompt engineering by turning stable workflows into repo assets

## Key Workflows

- Design a new or upgraded skill in `docs/design/`
- Implement or update skill behavior in `work/` or `learning/`
- Expose the behavior through `commands/workflow/`
- Keep shared defaults in `config/system.json`
- Verify that repo knowledge remains legible enough for agents to keep iterating safely

## Product Principles

- Source-first: this repo is the source of truth for skills, not the global install location
- Small moving parts: commands stay thin, skills hold the rules
- Config over hardcode: path, identity, and integration defaults live in shared config
- Design before drift: meaningful workflow changes should be explained in a design doc before they spread across commands and skills
- Practical agent usability matters more than abstract framework purity
