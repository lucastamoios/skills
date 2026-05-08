---
name: tech-debt
description: Scan a codebase for technical debt - outdated deps, test gaps, code churn hotspots, TODO/HACK markers, recurring Sentry errors, and missing Linear tickets. Produces a prioritized report and optionally creates issues.
user_invocable: true
allowed-tools: Bash(*), Read, Grep, Glob, Agent, AskUserQuestion, Edit, Write, mcp__sentry__search_issues, mcp__sentry__get_sentry_resource, mcp__linear-server__list_issues, mcp__linear-server__save_issue, mcp__linear-server__get_issue
argument-hint: "[path to project, e.g., the repo root or a sub-project directory]"
---

# Tech Debt

Scan a codebase for technical debt, prioritize findings, and produce actionable output.

Argument: `$ARGUMENTS`

## Step 1: Determine scope

- If `$ARGUMENTS` contains a path, use it as the project root.
- If empty, use the current working directory.
- Read the project's `CLAUDE.md` and `docs/index.md` (if they exist) for context on stack, conventions, and known issues.
- Detect the language/framework (check for `pyproject.toml`, `package.json`, `go.mod`, `Gemfile`, etc.) to determine which scans apply.

## Step 2: Run scans

Run all applicable scans. Parallelize where possible (independent scans in the same message).

### 2a. Dependency health

- **Outdated packages**: run the appropriate outdated check for the package manager (`pip list --outdated`, `npm outdated`, `go list -m -u all`, etc.)
- **Known vulnerabilities**: run vulnerability audit if available (`pip-audit`, `npm audit`, `govulncheck`, etc.)
- Classify each finding: MAJOR behind, MINOR behind, or has known CVE.

### 2b. Code churn hotspots

Find files that change most frequently - high churn correlates with debt:

```bash
git log --since="3 months ago" --name-only --pretty=format: | sort | uniq -c | sort -rn | head -20
```

Cross-reference with file size. Large files with high churn are the strongest debt signals.

### 2c. TODO/FIXME/HACK markers

Search for debt markers left by developers:

```
TODO, FIXME, HACK, XXX, WORKAROUND, TEMP, KLUDGE
```

Group by file and count. Exclude vendor/node_modules/migrations directories. Note any that reference ticket numbers (they may already be tracked).

### 2d. Test coverage gaps

Identify source modules that lack corresponding test files:

- List all source files in the project
- List all test files
- Find source modules with no matching test file
- Prioritize gaps on high-churn files (from 2b) - these are the riskiest untested areas

### 2e. Recurring Sentry errors (if Sentry MCP is connected)

Search for unresolved errors in the project's Sentry:

- Look for issues with high frequency or long duration (first seen > 30 days ago, still unresolved)
- These indicate systemic bugs that nobody has fixed - a form of operational debt
- Note the affected files for cross-reference with other scans

### 2f. Dead code signals

Look for:

- Unused imports (if a linter is configured, run it)
- Files not imported anywhere (orphan modules)
- Feature flags that appear permanently on or off

This scan is best-effort - false positives are common. Flag findings as "potential" rather than definitive.

## Step 3: Cross-reference with Linear

Check if existing Linear issues already cover the findings:

- Search Linear for issues with labels like "tech-debt", "refactor", "maintenance", or "bug"
- Match findings against existing issues by file path or keyword
- Mark findings as "already tracked" if a Linear issue exists

This avoids creating duplicate tickets.

## Step 4: Prioritize

Classify each finding using this matrix:

| Priority | Criteria | Examples |
|----------|----------|----------|
| **P0 - Fix now** | Security risk, data loss potential, blocks development | CVE in dependency, broken test suite, secrets in code |
| **P1 - This sprint** | Causes recurring bugs, significant developer friction | High-churn file with no tests, recurring Sentry errors, major version behind on framework |
| **P2 - Next quarter** | Slows feature work, increasing maintenance cost | Outdated deps (minor), large files needing split, scattered TODOs |
| **P3 - Backlog** | Nice to have, cosmetic, low-traffic paths | Minor outdated deps, style inconsistencies, dead code |

**Prioritization signals** (higher priority when multiple apply):
- File appears in multiple scans (high churn + no tests + TODOs = P1)
- File is in a critical path (auth, payments, data pipeline)
- Finding has been open for a long time (Sentry error from months ago)
- Finding blocks or complicates upcoming planned work

## Step 5: Report

Present findings grouped by priority, then by category:

```
# Tech Debt Report
Project: [name] | Date: [today] | Scope: [what was scanned]

## Summary
| Priority | Count |
|----------|-------|
| P0       | X     |
| P1       | Y     |
| P2       | Z     |
| P3       | W     |

Already tracked in Linear: N items

## P0 - Fix Now
### [Category] Finding title
- **Location**: file:line
- **Detail**: what and why this is debt
- **Impact**: what breaks or degrades
- **Effort**: S/M/L
- **Linear**: <TEAM>-XXX (if already tracked) or "not tracked"

## P1 - This Sprint
...

## Churn Hotspots (top 10)
| File | Changes (3mo) | Lines | Has tests? | TODOs |
|------|--------------|-------|------------|-------|
| ... | ... | ... | ... | ... |

## Dependency Health
| Package | Current | Latest | Behind | CVE? |
|---------|---------|--------|--------|------|
| ... | ... | ... | ... | ... |
```

## Step 6: Ask what to do next

After presenting the report, offer:

1. **Create Linear issues** - one per P0/P1 finding, with full context in the body
2. **Deep dive** - investigate a specific finding in detail (read the code, propose a fix approach)
3. **Export** - save the report to `docs/tech-debt-report-YYYY-MM-DD.md`
4. **Done** - report only, no further action

## Key principles

- **Scan first, judge second.** Collect data before prioritizing. Do not skip scans because "the codebase looks fine."
- **Cross-reference everything.** A finding that appears in multiple scans is more important than one that appears in only one.
- **Respect existing tracking.** If a Linear issue already exists, do not create a duplicate. Link to it instead.
- **Be honest about effort.** S = hours, M = days, L = week+. Do not underestimate.
- **Do not fix anything.** This skill is for discovery and prioritization. Use `/fix` or `/code-tdd` for the actual work.
- **Do not use em-dashes.** Use hyphens, commas, or parentheses instead.
