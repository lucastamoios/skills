# skills

Markdown prompts that encode my software lifecycle, from idea to merged PR.
Each one is a [Claude Code skill](https://docs.claude.com/en/docs/claude-code/skills).

→ **Talk:** [laguiar.dev/workflow](https://laguiar.dev/workflow)

## The loop

```
requirements  →  design-spec  →  plan  →  create-issues  →  next-issue
              →  code-tdd  →  code-review  →  architecture-review
              →  qa  →  create-pr  →  implement-review  →  autopilot
```

Same shape as **GMP validation** in pharma manufacturing — URS, design specs,
validation plans, traceability — encoded as prompts an agent runs.

## Install

System-wide:

```bash
git clone git@github.com:lucastamoios/skills.git ~/.claude/skills
```

Or per-project, inside any repository:

```bash
git clone git@github.com:lucastamoios/skills.git .claude/skills
```

## Inventory

**Lifecycle.**
`requirements` · `design-spec` · `plan` · `create-issues` · `next-issue`
· `code-tdd` · `code-review` · `architecture-review` · `implement-review`
· `qa` · `create-pr` · `autopilot`

**Knowledge & docs.**
`docs-update` · `docs-prune` · `docs-audit` · `session-log` · `session-distill`
· `meeting-distill` · `business-rules`

**Quality.**
`concept-review` · `concept-review-docs` · `tech-debt` · `audit` · `shield`

**Thinking.**
`brainstorm` · `think-through` · `fix`

## License

MIT — see [LICENSE](./LICENSE).
