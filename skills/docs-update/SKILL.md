---
name: docs-update
description: Refresh the project's docs in three places, all keyed on per-folder SHAs that record what was last reconciled. (1) `docs/map/` - concept-first codebase digest the conceiving agents (requirements, design-spec, plan, issue-creation) read instead of grepping source. (2) `docs/requirements/index.md` - registry of requirement docs in `docs/requirements/`. (3) `docs/design/index.md` - registry of design docs in `docs/design/`. On refresh, each folder is diffed against its stored SHA; map leaves whose source files changed are regenerated, and requirements/design index entries are added/updated/removed for files added/modified/deleted in the diff. Run from the project root. First run bootstraps; subsequent runs diff-refresh.
user_invocable: true
allowed-tools: Bash(git *), Read, Glob, Grep, Write, Edit, AskUserQuestion
argument-hint: "[optional: 'rebuild' to force re-bootstrap of docs/map/; otherwise auto-detect mode]"
---

# Docs Update

Refresh three doc surfaces in one pass, each tracked by its own SHA:

| Surface | Folder | SHA stored in | Purpose |
|---------|--------|---------------|---------|
| Codebase map | `docs/map/` | `docs/map/index.md` frontmatter | Concept-first digest the conceiving agents inject into their cached system prompt |
| Requirements registry | `docs/requirements/` | `docs/requirements/index.md` frontmatter | One-line summary per requirement doc; tells humans and agents what exists |
| Design registry | `docs/design/` | `docs/design/index.md` frontmatter | One-line summary per design doc; same role as requirements registry |

The map regenerates leaves whose source files changed. The requirements and design registries add/update/remove their entries based on which `.md` files in their folder were added/modified/deleted in the diff. The `.md` files themselves are never touched - they are at HEAD and are the source of truth.

Argument: `$ARGUMENTS`

## Style rules (apply to every file you write)

These rules are non-negotiable. Re-read them before writing each file.

- **Agent-shape, not human-shape.** Dense bullets. No narrative. No onboarding examples. No "this is great because...".
- **Minimum words.** If a sentence can be a fragment, make it a fragment. If a fragment can be cut, cut it.
- **Synthesize, do not enumerate.** "All webhook handlers verify HMAC and dedupe before dispatching" beats listing five handlers each doing the same thing.
- **Concept-first (map leaves).** A leaf describes WHAT a concept is and WHERE it lives. Never list a file and describe its contents - that inversion goes stale.
- **Cite files by path.** Optionally add line numbers or function names if pinpointing matters. Never paste code.
- **One-line summaries (registries).** Each entry in `docs/requirements/index.md` and `docs/design/index.md` is exactly one sentence. Lead with the noun (the user-observable behavior or the design concept), not the filename.

## Step 1: Mode detection

Run from the project root (the directory containing the project's source tree). The skill operates on the current working directory.

Per-surface mode detection:

```
map_mode  = "bootstrap" if not (cwd / "docs/map/index.md").exists() else "refresh"
reqs_mode = "bootstrap" if not (cwd / "docs/requirements/index.md").exists() else "refresh"
des_mode  = "bootstrap" if not (cwd / "docs/design/index.md").exists() else "refresh"

if $ARGUMENTS == "rebuild":
    map_mode = "bootstrap"  # only the map honors `rebuild`; registries are cheap to refresh, no full re-bootstrap needed
```

If `docs/requirements/` or `docs/design/` does not exist as a directory, skip that surface entirely (announce in the summary). Some projects have only one or neither.

Announce per-surface modes in one line, then proceed.

## Step 2: Pre-flight checks (all surfaces)

Before doing anything destructive:

| Condition | Behavior |
|-----------|----------|
| `git status` shows merge conflict markers | Ask user to confirm running anyway. Abort if no. |
| `git status` shows uncommitted changes | Ask user to confirm. Abort if no. Note: refresh will diff against HEAD, so uncommitted work is invisible. |
| Not in a git repo | Abort with a clear error. |

Use `AskUserQuestion` for the prompts. Do not use multiple-choice when a yes/no is enough.

# Surface 1: docs/map/

The map is the largest and most opinionated of the three. Bootstrap requires user-confirmed concept discovery; refresh is mechanical.

## Map / Step 3 (bootstrap mode): discover concepts

The goal is to produce a list of 10-25 domain concepts. Each concept becomes one leaf.

What "concept" means: a coherent piece of behavior or knowledge that can be discussed independently. Examples from a Django app: "request authentication", "ORM model conventions", "background task dispatch", "billing reconciliation". Examples from a workflow-orchestration service: "job lifecycle", "webhook routing", "retry patterns", "state storage and retrieval".

### How to discover

In this order:

1. **Read existing high-level docs.** `README.md`, `CLAUDE.md`, `docs/index.md`, `docs/architecture.md`, `docs/decisions.md`, `docs/gotchas.md`, `docs/key-files.md` if present. These often already name the concepts; harvest them.
2. **Read top-level structure.** `ls src/` (or equivalent). Each top-level package is usually one concept or contains a few.
3. **Read recent commits.** `git log --oneline -50`. Recurring themes signal active concepts.
4. **Sample for vocabulary.** Read 5-10 source files that look central (entry points, service classes, main models). Note the named concepts they reference.
5. **Combine into a candidate list.** Aim for 10-25 concepts. Each name is a noun phrase (1-4 words).

### Propose to user

Present the candidate list as a bulleted list with a one-line "what it covers" gloss for each. Use `AskUserQuestion` to ask:

> "Concept list - want to add, remove, rename, or accept as-is? You can edit freely; nothing is written until you confirm."

Iterate until the user approves. Then proceed.

## Map / Step 4 (bootstrap mode): generate the index

Write `docs/map/index.md` using this template:

```markdown
---
generated_at_sha: <full SHA from `git rev-parse HEAD`>
commits_since: 0
---

# <Project Name> Map

<2-4 sentences: what this project is, primary tech stack, deployment target. Synthesize - do not enumerate.>

## Concepts

| Concept | Leaf | When to load |
|---------|------|--------------|
| <Concept Name> | [<concept-slug>.md](<concept-slug>.md) | <one-line trigger phrase: when an agent should read this leaf> |
...

## Cross-cutting conventions

- <bullet: convention that applies project-wide, e.g. "Soft deletes only - never DELETE; filter `WHERE deleted_at IS NULL`">
- <bullet>
- <bullet>
(5-12 bullets total. These belong here only because they cut across leaves; concept-specific patterns go in the leaf.)
```

The "When to load" column is the most important field in the entire map. It determines whether agents pull the right leaf at the right moment. Make each entry trigger-phrase-shaped: think "if the user is talking about X, load this leaf".

## Map / Step 5 (bootstrap mode): generate each leaf

For each concept, write `docs/map/<concept-slug>.md` using this template:

```markdown
---
generated_at_sha: <same SHA as index>
commits_since: 0
concept: <Concept Name>
---

# <Concept Name>

<1-2 sentences: what this concept is and why it exists. Synthesize.>

## Files

- `<path>`: <what role>
- `<path>`: <what role>
(Path is enough when the file is small or single-purpose. Add `:line-range` or `:function_name` when the concept lives in part of a larger file.)

## Key types and functions

- `<TypeName>` (`<path>`): <one-line role>
- `<function_name>` (`<path>:<line>`): <one-line role>
(Include only the 3-8 names an agent will need. Skip if the file list above already makes the concept obvious.)

## Patterns and invariants

- <bullet: behavior that must hold, conventions, gotchas specific to this concept>
- <bullet>
(Skip the section if there are none. Do not pad.)

## Related

- See [other-leaf.md](other-leaf.md) when <when>.
(0-3 cross-references. Skip if none.)
```

Discover the file paths by reading code. Use `Glob` and `Grep` to locate where the concept actually lives. Do not guess paths - verify they exist before writing them in.

Keep each leaf under ~1500 tokens. If a leaf is heading past that, that is a signal the concept is too coarse - propose splitting it before writing (see Map / Step 6).

## Map / Step 6 (bootstrap mode): split-on-write check

Before finalizing each leaf, look at its draft size. If above ~1500 tokens or referencing more than ~12 files, ask the user:

> "Concept '<X>' has grown to <N> tokens / <M> file refs. Split into sub-concepts? Suggested split: <auto-suggestion based on the file groupings>."

If yes, propose two or more sub-concept names, get user confirmation, write each sub-leaf, and update the index accordingly.

## Map / Step 7 (bootstrap mode): handle existing key-files.md

If `docs/key-files.md` exists, the map supersedes it. Do not delete it automatically. Tell the user:

> "`docs/key-files.md` is now superseded by `docs/map/`. Delete it after reviewing the new map."

## Map / Step 8 (refresh mode): diff against stored SHA

Read the SHA from `docs/map/index.md`'s frontmatter. Run:

```bash
git diff --name-only <stored-sha>..HEAD
git rev-list --count <stored-sha>..HEAD   # for the new commits_since value
```

If the stored SHA is missing from history (rebased / squashed), ask the user:

> "Stored SHA <abc1234> for docs/map/ is no longer in history. Choose: (1) full re-bootstrap, (2) bootstrap from merge-base with main, (3) skip and exit."

For options (1) and (2), proceed accordingly. For (3), exit cleanly.

## Map / Step 9 (refresh mode): match changed files to concepts

Read every existing leaf's frontmatter and "Files" section. For each changed file from the diff:

1. **Find the closest existing leaf** by comparing the file's path and inferred role to the leaves' concept names and file lists. This is LLM judgment, not a string match.
2. **If a leaf clearly fits**, mark that leaf for regeneration.
3. **If no leaf fits well** (low confidence on the closest match), propose a new leaf. Suggest a name from the file's path and content. Ask user to accept or rename.
4. **If multiple leaves are touched by the same file**, regenerate all of them.

Do not ask the user about every match. Only ask when (a) creating a new leaf or (b) confidence is genuinely low.

Also check for **deleted leaves** referenced by the index but missing on disk. Ask:

> "Leaf `<concept>.md` is in the index but not on disk. Choose: (1) regenerate, (2) drop from index, (3) skip."

## Map / Step 10 (refresh mode): regenerate marked leaves

For each leaf marked for regeneration, rewrite it end-to-end using the leaf template. Do not patch in place. Update its `generated_at_sha` and `commits_since` headers.

For each new leaf, write it from scratch and add a row to the index.

## Map / Step 11 (refresh mode): split-on-refresh check

After regeneration, re-check size for every regenerated leaf. If past the soft threshold (~1500 tokens or ~12 file refs), propose a split exactly as in Map / Step 6.

## Map / Step 12: update the map index frontmatter

Update `docs/map/index.md`:

- Set `generated_at_sha` to current `HEAD`.
- Set `commits_since` to 0.
- Refresh the concept table to reflect any added, removed, or renamed leaves.
- Re-check the cross-cutting conventions section: anything new from the diff that applies project-wide?

Leaves that were not regenerated keep their own `generated_at_sha` and `commits_since` from the last time they were written. Do not touch their headers. To check current staleness of a specific leaf, a reader runs `git rev-list --count <leaf_sha>..HEAD`.

This per-leaf SHA model means the index's SHA tells you when the concept *list* was last reconciled, while each leaf's SHA tells you when its *content* was last verified. They can legitimately diverge.

# Surface 2: docs/requirements/

A flat folder of `.md` files, one per requirement (e.g. `docs/requirements/cd-pipeline.md`). The skill maintains `docs/requirements/index.md`: a registry with frontmatter SHA + a table of one-line summaries per file. Bootstrap and refresh share most of the work; the only difference is whether you start from an existing index.

## Reqs / Step 1 (bootstrap mode): build the registry from scratch

Skip if `docs/requirements/` does not exist. Otherwise:

1. List every `.md` file directly under `docs/requirements/` (one level, no subdirs unless the project actually uses them).
2. For each file, read it. Generate a one-sentence summary that names the user-observable behavior or feature. Lead with the noun, not the filename. Examples:
   - **Good**: "GitHub Actions deploys the API to staging on every push to main."
   - **Bad**: "cd-pipeline.md describes the deploy pipeline."
3. Write `docs/requirements/index.md`:

```markdown
---
generated_at_sha: <full SHA from `git rev-parse HEAD`>
commits_since: 0
---

# Requirements Registry

| File | Summary |
|------|---------|
| [cd-pipeline.md](cd-pipeline.md) | <one-line summary> |
| [staging-environment.md](staging-environment.md) | <one-line summary> |
...
```

Sort rows alphabetically by filename so the diff between runs is small. Keep it as a flat table; do not group by topic - that is the map's job.

## Reqs / Step 2 (refresh mode): diff against stored SHA

Read the SHA from `docs/requirements/index.md`'s frontmatter. Run:

```bash
git diff --name-status <stored-sha>..HEAD -- docs/requirements/
git rev-list --count <stored-sha>..HEAD -- docs/requirements/
```

The first command yields lines like `A path`, `M path`, `D path`, `R### old new` (rename). Parse them.

If the stored SHA is missing from history, ask the user:

> "Stored SHA <abc1234> for docs/requirements/ is no longer in history. Choose: (1) bootstrap registry from scratch, (2) skip this surface."

## Reqs / Step 3 (refresh mode): apply add/update/remove

For each diff entry:

| Status | Action |
|--------|--------|
| `A path` | Read the file. Generate one-line summary. Add a new row to the registry, sorted alphabetically. |
| `M path` | Re-read the file. Regenerate the summary. Replace the existing row. (Skip if the file's content semantically did not change - judgment call.) |
| `D path` | Remove the row from the registry. |
| `R### old new` | Remove the `old` row, add a `new` row with regenerated summary. |
| Anything else | Log and skip. |

Update `generated_at_sha` to current `HEAD` and `commits_since` to 0.

If the diff is large (>20 changes), ask the user before applying:

> "<N> requirement files changed since the last registry update. Apply add/update/remove to the registry? (1) Yes, (2) Show me the list first, (3) Skip."

## Reqs / Step 4: cross-check with map references

If any map leaf cites a requirement file in its "Related" section, those references survive automatically (we are not touching leaves here). But if a requirement was DELETED, scan map leaves for stale links to it and flag them in the post-run summary - do not auto-edit map leaves from this step.

# Surface 3: docs/design/

Identical structure and rules to Surface 2. Substitute `docs/design/` for `docs/requirements/` and "Design Registry" for "Requirements Registry" throughout. The summary should describe the design decision or system, not the requirement.

# Step 13: post-run summary

Print a one-screen summary covering all three surfaces:

- **Map**: mode (bootstrap or refresh), leaves written, splits performed, new leaves added, files skipped (untouched leaves)
- **Requirements**: mode, files added/updated/removed in the registry, total entries
- **Design**: same shape as Requirements
- **Cross-surface notes**: stale map references to deleted requirements/designs (if any), `docs/key-files.md` still present (if any)

That's it. Do not write a longer report; the diff itself is the artifact.

## Failure mode reference

| Situation | Behavior |
|-----------|----------|
| No git repo | Abort with clear error |
| Merge conflict in progress | Ask user to confirm before running |
| Dirty working tree | Ask user to confirm before running |
| Stored SHA gone from history (any surface) | Ask: bootstrap that surface, or skip |
| Map leaf in index but not on disk | Ask: regenerate, drop from index, or skip |
| Map leaf grew past size threshold | Ask: split into sub-concepts (offer auto-suggestion) |
| Map diff touches a file no leaf covers | Propose new leaf; ask user to accept or rename |
| Requirements/design folder missing | Skip that surface, note in summary |
| Requirements/design diff is large (>20 changes) | Ask before applying; offer to show the list |
| `docs/key-files.md` exists at bootstrap | Notify user it is superseded by the map; do not delete |

All prompts use `AskUserQuestion`.

## What this skill does NOT do (deferred)

- Does not validate that paths cited in map leaves still exist (drift check beyond SHA + commit count).
- Does not check whether high-churn files lack any map leaf coverage.
- Does not edit the actual `docs/requirements/*.md` or `docs/design/*.md` files - the registries point at them, the files themselves are at HEAD and authoritative.
- Does not auto-edit map leaves when a requirement/design they reference is deleted - it flags the stale reference in the summary.
- Does not sync against external sources (Linear, other branches). The diff is always local-git from the stored SHA to HEAD.
- Does not run non-interactively. CI mode is future work; when added, every interactive prompt becomes a hard failure that the PR author resolves locally.

## Style anti-patterns to avoid

After writing a file, re-read it and check:

- Did you write a paragraph where a bullet list would do? Cut it.
- Did you describe a file ("`foo.py` contains the FooService class which handles...")? Re-shape: lead with the concept, mention the file as evidence.
- Did you include onboarding-style "you might wonder why..." prose? Cut it.
- Did you list the same convention three times across leaves? Move it to the index's cross-cutting section.
- Did you write a registry summary that names the filename instead of the behavior? Re-write it leading with the noun.
- Did you exceed the soft size targets without proposing a split? Propose now.

## Suggested next step after this skill runs

The map is consumed by the conceiving agents (requirements, design-spec, plan, issue-creation) via `AgentContext.project_map`. After the first map is written or a major refresh, verify the agent harness loads `docs/map/index.md` from the worktree and injects it into the cached system prompt. Run a single conceiving task end-to-end and inspect the trace to confirm the map shows up in the prompt and the agent uses it (i.e., loads leaves via `read_file` instead of grepping source).

The requirements and design registries do not feed the agents directly today - they exist for humans (and for future skills that want a quick one-line view of all requirements / designs without opening every file).
