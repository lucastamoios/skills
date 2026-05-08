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

## Catalog

### Lifecycle

| Skill | What it does |
|---|---|
| `requirements` | Capture numbered, technology-free user requirements; outputs `.md` and BDD `.feature` files. |
| `design-spec` | Capture technical design decisions, each traced back to a requirement. |
| `plan` | Break work into ordered steps with test cases tied to requirements. |
| `create-issues` | Slice the plan into self-contained ~250-LOC Linear issues with the spec embedded. |
| `next-issue` | Pick the next unblocked issue, create a branch and worktree, install deps. |
| `code-tdd` | Implement outside-in: red → green → refactor, every cycle traceable to a requirement. |
| `code-review` | Review a diff for bugs, logic errors, security, edge cases, requirements alignment. |
| `architecture-review` | Review for SOLID, layer boundaries, dependency direction, error flow. |
| `qa` | Run tests, exercise endpoints with curl, drive the UI with Playwright. |
| `create-pr` | Rebase the chain, push with `--force-with-lease`, write a smart PR title and body. |
| `implement-review` | Triage PR review comments, judge validity, implement the valid ones test-first. |
| `autopilot` | Run the entire loop above, hands-off, across a queue of issues. |

### Knowledge & docs

| Skill | What it does |
|---|---|
| `docs-update` | Refresh `docs/map/` plus the requirements and design indexes, keyed on per-folder SHAs. |
| `docs-prune` | Find duplication, dead refs, and verbose prose; propose a token-saving change plan. |
| `docs-audit` | Cross-check requirements, design, and code consistency; surface contradictions. |
| `session-log` | Capture session activity into a daily file under `logs/`. |
| `session-distill` | Extract durable knowledge from the current session into `docs/`. |
| `meeting-distill` | Extract durable knowledge from a meeting transcript. |

### Quality

| Skill | What it does |
|---|---|
| `concept-review` | Ontological review of code abstractions; finds misnamed, misplaced, or confused concepts. |
| `concept-review-docs` | The same lens applied to requirements and design specs. |
| `tech-debt` | Scan for outdated deps, churn hotspots, TODO/FIXME markers, test gaps, and recurring Sentry errors; prioritize P0–P3. |

### Thinking

| Skill | What it does |
|---|---|
| `brainstorm` | Open-ended thinking partner; challenges assumptions, never concludes on its own. |
| `think-through` | Structured reasoning frameworks (pre-mortem, inversion, three-property test). |
| `fix` | Diagnose a bug end-to-end, write a regression test, fix it red-green-refactor. |

## License

MIT — see [LICENSE](./LICENSE).
