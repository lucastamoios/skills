---
name: docs-prune
description: Reduce a project's documentation to the minimum tokens needed for future agents to do their work. Finds duplicated content across files, obsolete files, dead cross-references, and verbose prose; proposes a numbered change plan (delete / merge / move / trim per file); applies it after the user approves. Operates on every file under docs/ including docs/map/. Trigger on explicit pruning intent ("simplify the docs", "shrink the docs", "dedupe the docs", "the docs are bloated"); do not trigger on lookups or on the existing docs-audit skill which only inspects.
user_invocable: true
allowed-tools: Bash(git *), Bash(ls *), Bash(find *), Bash(wc *), Bash(rm *), Bash(mv *), Bash(mkdir *), Read, Grep, Glob, Edit, Write, AskUserQuestion
argument-hint: "<project path> (omit to use current directory)"
---

# Docs Prune

Take a project's `docs/` tree and make it strictly smaller without losing knowledge an agent needs. Three modes of reduction:

1. **Cross-file dedup**: same fact stated in two places -> keep one canonical home, replace the other with a one-line pointer.
2. **File-level removal**: superseded, obsolete, or never-referenced files get deleted.
3. **In-file trimming**: narrative prose, onboarding asides, and "we will / we plan to" forecasting get cut to fragments. Tables and bullet lists are kept; paragraphs that restate them are removed.

The output is a smaller `docs/` tree where every remaining sentence earns its tokens.

Argument: `$ARGUMENTS`

## When to use

Trigger only when the user clearly wants reduction, not a lookup or an audit. Examples:

- "simplify the docs", "shrink the docs", "dedupe the docs"
- "the docs are bloated - cut them down"
- "tighten the docs to save tokens"

Do **not** trigger on:

- "check the docs", "read the docs", "what do the docs say" (lookup)
- "audit the docs", "find contradictions" (use `docs-audit`)
- "update the docs" (use `session-distill`)

If unsure, ask once before invoking.

## What this skill does NOT do

- Does not edit requirements, design specs, plans, or runbooks **content** when those files map 1:1 to a Linear issue or feature spec - those are contracts. It only removes superseded ones, fixes broken cross-references inside them, and proposes terser wording for clearly redundant prose. Spec semantics stay verbatim unless the user explicitly says "rewrite for brevity".
- Does not consolidate `docs/map/` leaves into different concepts. The map's structure is owned by the `project-map` skill. This skill only trims wording inside leaves and removes dead cross-references.
- Does not invent new structure. If the docs need restructuring beyond what falls out of dedup, surface the suggestion in the report and let the user decide.

## Step 1: Resolve the project root

1. If `$ARGUMENTS` names a directory, `cd` there. Otherwise use cwd. Announce the choice in one line.
2. Confirm `<project>/docs/` exists. If not, abort with a clear error.
3. Run `git status` against the project. If there are unstaged or merge-conflict changes, ask the user once whether to continue. The skill will create real diffs; the user wants a clean baseline.

## Step 2: Inventory the docs tree

Walk `docs/` recursively. For every `.md` and `.feature` file, record:

- Path
- Token estimate (`wc -w` divided by ~0.75; rough is fine - this skill optimizes the relative ranking, not absolute counts)
- First-line title
- Section headings
- Outbound links (relative paths and Linear identifiers like `<TEAM>-####`)
- Inbound link count (how many other docs reference this file by path)
- Last-modified date from `git log -1 --format=%ci -- <path>` (use to spot stale files)

Group files into:

- **Index files**: `docs/index.md`, `docs/map/index.md`, any `*/index.md`.
- **Map leaves**: anything under `docs/map/` other than `index.md`.
- **Specs**: under `docs/requirements/`, `docs/design/`, `docs/plans/`, `docs/plan/`, `docs/runbooks/`.
- **Loose docs**: every other `.md` directly in `docs/` or in subdirectories not above (architecture.md, gotchas.md, decisions.md, etc.).

Print a table to the user: file count and total estimated tokens per group. This is the baseline.

## Step 3: Find duplications

For each pair of docs that share concepts, look for:

- **Verbatim repetition**: same paragraph or table appears in 2+ files. Use `grep` over distinctive phrases (e.g. unique sentence fragments from one file appearing elsewhere).
- **Paraphrased repetition**: same fact, different wording. Detect by overlapping subject + verb + object across summaries (e.g. "soft deletes only" stated in three places). LLM judgment, not regex.
- **Index-to-leaf overlap**: index files that re-summarize what their leaves already say. Index entries should be one-liners, not mini-summaries.
- **Cross-cutting conventions repeated per leaf**: convention belongs in the index's "cross-cutting" section, not in every leaf that brushes against it.

For every duplication, choose a canonical home using these rules:

1. Map index < loose docs < spec docs (the index is the cheapest place to keep universals).
2. Concept-specific facts go in the relevant map leaf, not in `gotchas.md` or `architecture.md`.
3. If two specs say the same thing, the newer one wins; older one gets a pointer and a "superseded by" header line.

Output: a "Dedup proposals" section in the change plan, one row per finding, naming canonical home and follow-up text for the other side.

## Step 4: Find removable files

Mark a file for deletion if **any** of these hold:

- Inbound link count is 0 AND no other doc, code file, or `CLAUDE.md` references it (search with `grep -r` outside `docs/`).
- File is fully superseded by another (e.g. old `key-files.md` after `docs/map/` exists - this is a real case in this repo).
- File contains only "TODO" / "WIP" / "this section is empty" content.
- File is a session note that has been distilled into permanent docs already.
- File is an obsolete plan (status closed, Linear issue done) AND the design/requirements that replace it exist.

Mark for **archive** rather than delete when the file is a historical record the user might want (decisions.md is usually like this; superseded but valuable). Archive target: `docs/archive/<original-path>`.

Never delete:

- Files explicitly referenced by a slash command, agent YAML (`agents/*.yml`), or hook configuration.
- Files referenced by `CLAUDE.md` (root, or any nested `CLAUDE.md`).
- The most recent runbook for any operational concern.

## Step 5: Find trimmable prose

For every doc, scan for:

- **Onboarding asides**: "you might wonder...", "the reason we did this is...", "this is great because..." -> cut.
- **Restating tables in prose**: a paragraph that re-narrates a bullet list or table immediately above or below -> cut the prose.
- **Forecasting**: "we plan to...", "future work will...", "eventually we will..." unless tied to a Linear issue or `## Open questions` block -> cut.
- **Step-by-step prose where a fragment list works**: convert paragraphs to bullet fragments where possible.
- **Em-dashes** (project rule: hyphens only). Project rule: use `-` not `—`.
- **Conventional Commits / git rules / no em-dash rules** repeated in every doc -> centralize in `CLAUDE.md` and remove from `docs/`.

Output: per-file "Trim proposals" with before/after snippets for the chunks that would change.

## Step 6: Find dead cross-references

For every link in every doc:

- If target file is missing -> mark for fix or removal.
- If target heading is missing (`other.md#section`) -> mark for fix.
- If link text differs sharply from target's actual title -> propose link-text update.
- If the link is to an external service (Linear / GitHub PR / Slack) -> leave it alone (cannot resolve here).

## Step 7: Build the change plan

Assemble a single markdown report with these sections, each numbered for easy reference:

```
## Baseline
| Group | Files | Tokens (est) |
| --- | --- | --- |
| Map index | 1 | ... |
| Map leaves | 20 | ... |
| Specs | N | ... |
| Loose docs | N | ... |
| **Total** | | |

## Removals (D-1 ... D-n)
For each: target path, reason, archive-or-delete, expected token reduction.

## Dedup moves (M-1 ... M-n)
For each: source path, target path, what content moves, what stays as a pointer line.

## Trims (T-1 ... T-n)
For each: file, section, before snippet, after snippet, expected token reduction.

## Cross-reference fixes (X-1 ... X-n)
For each: file, broken link, suggested fix or removal.

## Estimated impact
| Metric | Before | After | Delta |
| --- | --- | --- | --- |
| Total tokens | ... | ... | ... |
| File count | ... | ... | ... |
```

The report is the deliverable for this step. Do not edit anything yet. Print it to the user.

## Step 8: Approval gate

Use `AskUserQuestion`. Offer:

- **Apply all** - execute every D/M/T/X.
- **Apply selected** - user names IDs (e.g. "D-1, D-3, M-2, all T-*"); skill executes only those.
- **Apply removals only** - just the D items; skip rewrites.
- **Cancel** - do nothing, leave report as-is.

If the user picks "Apply selected", parse the ID list. Accept ranges (`T-1..T-5`) and wildcards (`all D-*`).

## Step 9: Execute

For each approved change, in this order (least destructive first):

1. **Cross-reference fixes (X)**: targeted Edit calls.
2. **Trims (T)**: Edit per file. Re-read the file before each edit; do not rely on snippets from the report verbatim if the file has been edited in this run.
3. **Dedup moves (M)**: Edit the source (replace duplicated block with a pointer line) and Edit the target (insert canonical content if it is not already there). Pointer format: `> See [<title>](<rel-path>#<section>) for details.`
4. **Removals (D)**:
   - Archive: `mkdir -p docs/archive/<dir>` then `mv` the file.
   - Delete: `rm` the file. Run `grep -r '<filename>' .` once more before deletion - abort that single removal if anything still references it.

After every change, run `git diff --stat` to confirm the diff is bounded to the planned files. If anything outside the planned set was touched, stop and report.

## Step 10: Verify

After execution:

1. Run a final inventory pass (same as Step 2). Print before/after totals next to the predicted ones.
2. Walk all docs again and re-check cross-references. If any new dead link appeared (because the target was deleted in this run), fix or remove it.
3. Suggest one commit per category (D, M, T, X) so the user can review them separately. Do **not** commit yourself - the user reviews and commits.

## Step 11: Post-run summary

Print:

- Files removed / archived / edited
- Tokens saved (predicted vs measured)
- Anything skipped because the user did not approve it
- Anything skipped because of a safety rule (e.g. file was referenced from `CLAUDE.md`)

That's it. Do not write a longer report; the diff itself is the artifact.

## Failure mode reference

| Situation | Behavior |
| --- | --- |
| Not in a git repo | Abort with clear error |
| Dirty working tree | Ask user once before continuing |
| `<project>/docs/` missing | Abort |
| Spec doc proposed for trim that maps 1:1 to Linear | Skip it; only propose `delete-if-superseded`, never `rewrite content` |
| File proposed for delete is referenced from `CLAUDE.md` or `agents/*.yml` | Drop the proposal automatically and note it in the summary |
| Dedup target file does not exist yet | Either create it (only if the user opts in via the change plan) or downgrade to "trim duplicates without consolidation" |
| User declines all proposals | Exit cleanly; report still serves as a checklist for manual work |
| Edit fails because the file changed mid-run | Re-read and retry once; if still failing, mark the change skipped and continue |

## Style anti-patterns to avoid in the change plan

- Do not propose stylistic rewrites that preserve length. Every T item must have a measurable token delta.
- Do not propose moves that just shuffle text without consolidating duplication.
- Do not bundle unrelated changes into one ID - one logical change per ID.
- Do not suggest deletions for files you have not actually inspected for inbound references.

## Suggested next step after this skill runs

The pruned tree is the cacheable surface that agents read. After the first prune:

- Verify the project's CLAUDE.md still points to surviving files.
- Run a single conceiving task end-to-end (requirements / design-spec) and inspect the trace - confirm the agents are loading fewer tokens than before and have not lost the context they need.
- If a leaf or doc came back from the dead during the conceive run (the agent grepped for something that used to be in the deleted file), restore it from `docs/archive/` and update the rule that deleted it.
