---
name: gardener-audit
description: Audit a documentation folder for inconsistencies and produce a report with suggested fixes - never edits the docs. Detects the folder's conventions and adapts. In a brain-vault subtree it checks wikilink integrity, index.md coverage, frontmatter, oversize notes, stale/duplicated facts, and cross-note contradictions (the vault is the source of truth). In a code-repo docs/ tree it cross-checks each claim against Linear, then the code, then sibling docs. Trigger on explicit audit intent ("audit the docs", "are the project docs consistent", "find contradictions in <folder>"); do not trigger on lookups, or on gardener-prune which edits.
argument-hint: "<folder> (a vault subtree like project, or a repo path; omit to ask)"
allowed-tools: Bash(git *), Bash(ls *), Bash(find *), Bash(wc *), Read, Grep, Glob, Agent, AskUserQuestion, Write, mcp__linear-server__*, LSP
---

# Gardener: Audit

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Run a read-only consistency sweep over a documentation folder and produce one
report of findings with suggested fixes. This is the audit arm of the gardener
family (see [[gardener]] for the orchestrator, [[gardener-inbox]] for capture
filing, [[gardener-prune]] for the arm that actually edits and archives).

This skill **edits nothing** except, in repo mode, a glossary entry when the user
resolves an ambiguous term during the run. the user reads the report and decides
what to fix - usually by running [[gardener-prune]] next.

Argument: `$ARGUMENTS`

## When to use

Trigger only for a consistency sweep, not a lookup: "audit the docs", "are the project docs consistent", "find contradictions", "the docs drifted - find the gaps". Do **not** trigger on "check/read the docs" or "what do the docs say" (lookups - use plain Read/Grep), or when the user wants reduction (use [[gardener-prune]]).

## Step 1: Resolve the folder and detect the mode

1. If `$ARGUMENTS` names a folder, use it (a bare name like `project` resolves to `profile.paths.vault/project`; an absolute path or `.` is used as-is). Otherwise ask once. Announce the choice.
2. **Detect the mode** and announce it:
   - **Vault mode**: at or under `profile.paths.vault` (a `vault/AGENTS.md` sits at or above the folder). The vault is the source of truth - there is nothing external to cross-check against, so the audit is about internal coherence, link integrity, and structure.
   - **Repo mode**: a code-repo `docs/` tree. Linear is the source of truth and the code is the second check.
   If neither is present, stop and say so.
3. Index every doc in the folder. Record H1 title, section headings, line count, outbound links, inbound link count, frontmatter fields, and last-modified date. In repo mode also record numbered requirements (`^\d+\.`, `**REQ N.**`), design decisions (`### D<n>`), and any `<TEAM>-XXXX` / `Linear issue:` references.

## Step 2 (repo mode only): for each finding, follow all three perspectives

Do not shortcut - the valuable tensions only surface when all three are consulted in order.

1. **Linear first** (source of truth). Fetch the issue behind each REQ/decision under suspicion; quote the authoritative text. If the Linear MCP is unreachable, skip this category and note it in the report header.
2. **Code second.** Use LSP (`findReferences`, `goToDefinition`, `workspaceSymbol`) to see how the behavior is actually implemented; read the deciding call site, not just the declaration. Fall back to grep with a flagged note if LSP is unavailable.
3. **Sibling docs third.** Find every other doc mentioning the same entity/REQ/decision and compare. The best findings are not "doc disagrees with Linear" but "doc A and doc B each match the code in isolation yet describe the same operation at different layers without acknowledging each other, so a reader of either alone gets it wrong."

## Step 3: Run the checks

### Structure and numbering
- **Vault mode**: notes past ~200 lines or mixing unrelated topics (candidate for a hub/subnote split - flag for [[gardener-prune]]). Kebab-case filenames. Exactly one H1. Frontmatter present and well-formed (`type`; `related_to` as `[[wikilinks]]`; `tags` mirroring the folder; `status` only when not active). A note with no inbound links and not listed in `index.md` (orphan).
- **Repo mode**: gaps/duplicates/out-of-order in REQ and `D<n>` numbering; a requirement with no companion `.feature`; missing or stale "Last updated" header.

### Cross-references and link integrity
- **Vault mode**: every `[[wikilink]]` whose basename resolves to no file under `vault/**` (dead link). Every relative link in a table pointing at a missing file. `index.md` entries pointing at moved/removed notes. Notes that exist but are absent from `index.md` (coverage gap).
- **Repo mode**: a REQ cited in design/plan but absent from requirements (critical); a `D<n>` cited in a plan but absent from design (critical); an index link to a non-existent file (critical, auto-fixable: drop the line); a plan whose Linear issue is Done (hint: graduate durable content into permanent docs).

### Alignment
- **Vault mode**: the vault is truth, so "alignment" means internal agreement - two notes stating the same fact differently (flag the duplication for [[gardener-prune]] to consolidate, name the better canonical home), and a hub/`index.md` summary that contradicts the subnote it points to.
- **Repo mode**: for each REQ, compare doc text to the Linear issue (Linear wins; flag drift). For each REQ naming a domain entity (class, table, column, function, env var, agent slug, path), confirm it exists in code with that name, read the deciding path, and flag when code matches REQ A but contradicts REQ B, two REQs describe the same operation at different layers, two REQs give the same data model different shapes, or the real code invariant is stricter/looser than any single REQ states. Use LSP, not grep, to find the other referencing paths.

### Terminology drift
- **Repo mode**: load `docs/glossary.md`; for each canonical term report variants across docs; for terms not in the glossary infer the canonical form from code and flag doc variants. If a term is genuinely ambiguous, do not guess - add it to Open questions, stop, and ask the user; after he answers, append the resolved term to `docs/glossary.md` and continue.
- **Vault mode**: there is no glossary or code canonical. Just report the same concept referred to by clearly different names across notes, as a warning, and suggest which name to standardize on.

### Contradictions
Within each doc and across each related pair, find two statements that cannot both hold (e.g. "always store X on success" vs "store X only when Y"). Mixed modal verbs inside one doc (must/shall/present indicative) is a hint, not a critical.

### Sensitivity (vault mode)
Never open, quote, or surface anything under `personal/journal/` (encrypted, `sensitivity: Personal`). If the audited folder includes it, skip those files and note that they were skipped.

## Step 4: Write the report

- **Vault mode**: **print the report inline to the user.** Do not create files in the vault - an `audits/` folder would pollute the knowledge graph.
- **Repo mode**: write to `<project>/docs/audits/YYYY-MM-DD-audit.md` (create `audits/` if needed).

Report structure, in order: **Summary** (one line, counts by severity, plus "Linear unreachable"/"LSP unavailable" notes when relevant); **Findings** (grouped critical -> warning -> hint); **Open questions** (anything you had to ask but could not resolve); **Suggested prune actions** (a flat list of findings that [[gardener-prune]] could apply - dedup consolidations, splits, archivals - so the user can hand them straight to that skill).

Each finding is one block under ~150 words:

```
## F<n> [<severity>] <title>
- **Where:** <file:line>(, more)
- **Truth:** (repo mode: Linear quote / code file:line; vault mode: which note is canonical)
- **Conflict:** <the other note/doc/code that disagrees, if any>
- **Suggested fix:** <imperative one-liner; name the gardener-prune action if applicable>
- **Auto-fixable:** yes | no
```

### Severity
- **critical** - silently broken: scrambled numbering, a link to a non-existent target, REQ text contradicting Linear or code (repo), a dead `[[wikilink]]`, two notes disagreeing on a fact of record.
- **warning** - reader will be confused: terminology drift, a cross-doc contradiction the code resolves but the docs do not, an oversize note, a coverage gap in `index.md`, a missing "Last updated".
- **hint** - low impact: mixed modal verbs, a plan describing finished work, optional metadata missing.

## What this skill never does
- Edit any note, requirement, design, plan, runbook, code, or `index.md` file (repo-mode glossary is the only exception, and only on the user's resolution).
- Renumber, delete, move, or archive anything - that is [[gardener-prune]].
- Touch Linear (no comments, no status changes) or open PRs.
- Read `personal/journal/` content.
- Mark a finding `Auto-fixable: yes` when applying it needs judgment (e.g. resolving a contradiction). Auto-fixable means a script could safely apply it without review.

## Re-running

The audit is idempotent: two runs on unchanged docs produce the same findings (modulo the date in the repo-mode filename and any glossary entries already present). It is meant to be run repeatedly during a tending pass, typically right before [[gardener-prune]].
