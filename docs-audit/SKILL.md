---
name: docs-audit
description: Audit a project's documentation (requirements, design specs, plans, index, glossary) for inconsistencies and produce a report with suggested fixes. For each finding, cross-checks Linear (source of truth), then the code (how the behavior is actually handled), then sibling docs that touch the same concept, to surface tensions you would otherwise only find at integration time. Never edits docs except `docs/glossary.md` when terminology is resolved. Trigger on explicit audit intent only ("audit the docs", "find contradictions", "are the docs consistent"); do **not** trigger on generic verbs like "check the docs" or "read the docs", which usually mean a lookup, not a consistency sweep.
user_invocable: true
allowed-tools: Bash(git *), Bash(ls *), Bash(find *), Read, Grep, Glob, Agent, AskUserQuestion, Write, mcp__linear-server__*, LSP
argument-hint: "<project path> (omit to ask)"
---

# Docs Audit

Run a sanity audit on the documentation under a project path. Produce a single report with findings and suggested fixes. Do not edit requirements, design, plan, runbook, code, or index files. The user reads the report and decides which fixes to apply.

Argument: `$ARGUMENTS`

## When to use
Trigger only when the user clearly wants a consistency sweep, not a lookup. Examples that should trigger:
- "audit the docs", "run a docs audit", "do a docs sanity check"
- "find contradictions in the docs", "are the docs consistent"
- "the docs drifted - find the gaps", "check the docs against Linear"

Examples that should **not** trigger (these are lookups, use normal Read/Grep):
- "check the docs to see how X works"
- "read the docs"
- "what do the docs say about Y"

If you are unsure, ask the user before invoking.

## Step 1: Determine scope

1. If `$ARGUMENTS` names a project path, use it. Otherwise ask the user once and default to the current directory only if they decline to specify.
2. Confirm the working subtree contains a `docs/` directory. If not, stop and say so.
3. Index everything under `<project>/docs/`:
   - Requirements: `docs/requirements/*.md` and the matching `*.feature` files.
   - Design: `docs/design/*.md`.
   - Plans: `docs/plans/*.md` and any sibling `docs/plan/*.md`.
   - Index: `docs/index.md`.
   - Glossary: `docs/glossary.md` (no underscore - it is a first-class doc).
   - Runbooks: `docs/runbooks/*.md`.
4. For every doc, record: numbered requirements (`^\d+\.` or `**REQ N.**`), design decisions (`### D<n>`), cross-references (`REQ N`, `D<n>`, file paths, `<TEAM>-XXXX`), the "Last updated" header, any linked Linear issue.

## Step 2: For each finding, follow the same path

This is the heart of the skill. **Do not shortcut.** The cross-system tensions only surface when all three perspectives are consulted in order.

1. **Linear first.** Linear is the source of truth. For each REQ or decision under suspicion, fetch the corresponding issue (via the `Linear issue:` line, a `<TEAM>-XXXX` mention, or a title search). Quote the authoritative text.
2. **Code second.** Use LSP (`findReferences`, `goToDefinition`, `workspaceSymbol`) to find how the behavior is actually implemented. Read the call site that decides the behavior, not just the symbol declaration. Fall back to grep with a flagged note if LSP is unavailable for the language.
3. **Sibling docs third.** Find every other doc that mentions the same entity, REQ, or decision. Compare what they say. The most valuable findings are not "the doc disagrees with Linear" but "doc A and doc B each match the code in isolation, but they describe the same operation at different layers without acknowledging each other, and a reader of either doc alone will get it wrong."

## Step 3: Run checks

Run these in order. Each produces zero or more findings.

### Numbering integrity
- Gaps, duplicates, out-of-order numbers in REQ lists.
- Gaps in `D<n>` numbering.
- Companion file missing (requirement without `.feature`, design without plan, etc.).
- Missing or stale "Last updated" header.

### In-repo cross-references
- REQ cited in design or plan but absent from the requirements file. Severity: critical.
- `D<n>` cited in plan but absent from the design file. Severity: critical.
- Index link points at a non-existent file. Severity: critical. Auto-fixable: drop the line.
- A plan in `plans/` whose Linear issue is `Done`. Severity: hint. Suggestion: graduate durable content into permanent docs (architecture / decisions / gotchas / key-files) per `session-distill`.

### Linear alignment
- For each REQ in the doc, fetch the Linear issue. If meaning differs, Linear wins; flag the doc as drifted.
- If a Linear issue lists REQ N but the doc has different text at REQ N, flag (this happens when docs are hand-edited and lose sync).
- If the Linear MCP is unreachable, skip this category and note "Linear unreachable" in the report header.

### Code alignment and cross-system tension (highest value)
For each REQ that names a domain entity (class, table, column, function, env var, agent slug, file path):
- Confirm the entity exists in code with that name.
- Read the path that decides its behavior. Compare the actual invariant to the REQ text.
- Look at every other doc mentioning the same entity. Flag when:
  - Code matches REQ A but contradicts REQ B.
  - Two REQs describe the same operation at different layers (capability vs decision logic) without acknowledging each other.
  - Two REQs describe the same data model with different shapes (e.g. INTEGER PK vs UUID PK).
  - The actual code invariant is stricter or looser than any single REQ states.
- Use LSP, not grep, when checking which other code paths reference the entity.

### Terminology drift
- Load `docs/glossary.md`. For each canonical term, scan all docs and report variants used.
- For terms not in the glossary, infer the canonical form from code (DB model name, class name, public symbol). If a doc uses a variant of a code-canonical term, flag and propose a glossary entry.
- If a term is genuinely ambiguous (no code canonical, multiple equally common variants in docs), do **not** guess. Add an entry to the **Open questions** section of the report and stop the run to ask the user. After the user answers, append the resolved term to `docs/glossary.md` and continue.

### Internal contradictions
- Within each doc and across each related pair (requirements ↔ design ↔ plan), look for two statements that cannot both hold (e.g. one REQ says "always store X on success", another says "store X only when Y").
- Modal-verb mixing inside one doc (must / shall / present indicative) is a hint, not a critical.

## Step 4: Glossary maintenance

When the user resolves an ambiguous term during the run, append to `docs/glossary.md`:

```
## <term>
- Canonical: `<canonical form>`
- Variants seen: `<variant>`, `<variant>`
- Source of truth: <code path | doc | Linear issue>
- Catalogued: YYYY-MM-DD
```

This and the audit report are the only files the skill writes. If `docs/glossary.md` does not exist yet, create it with a one-paragraph header explaining what it is for.

## Step 5: Write the report

Write to `<project>/docs/audits/YYYY-MM-DD-audit.md`. Create the `audits/` directory if needed.

The report has four sections, in order:

1. **Summary** - one line with counts by severity, plus "Linear unreachable" or "LSP unavailable" notes if relevant.
2. **Findings** - grouped by severity (critical, then warning, then hint).
3. **Open questions** - anything the skill needed to ask but could not resolve.
4. **Auto-fixable summary** - a flat list of titles + `file:line` for every finding marked `Auto-fixable: yes`, so the user can apply them in bulk.

Each finding is one block. Keep it under ~150 words.

```
## F<n> [<severity>] <title>
- **Where:** <file:line>(, more)
- **Truth:**
  - Linear: <quote / "not found" / "unreachable">
  - Code: <file:line - one-line summary / "no relevant code">
- **Conflict:** <other doc/code that disagrees, if any>
- **Suggested fix:** <imperative one-liner>
- **Auto-fixable:** yes | no
```

### Severity

- **critical** - silently broken: numbering scrambled, cross-reference points at a non-existent target, REQ text contradicts Linear or code, two docs disagree on a data shape.
- **warning** - reader will be confused: terminology drift, contradiction across two docs that the code resolves but the docs do not, missing "Last updated".
- **hint** - low-impact: modal verbs mixed, plan describing finished work, optional metadata missing.

## What this skill never does
- Edit requirements, design, plan, runbook, code, or index files.
- Renumber anything.
- Delete files.
- Touch Linear (no comments, no status changes).
- Open PRs.
- Mark anything `Auto-fixable: yes` that requires judgment (e.g. resolving a contradiction). Auto-fixable means a script could safely apply the change without human review.

## Re-running

The audit is idempotent. Running it twice on unchanged docs produces the same findings (modulo the date in the filename and any glossary entries that already exist). The skill is intended to be run repeatedly during a docs-cleanup pass.
