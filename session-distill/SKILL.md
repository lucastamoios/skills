---
name: session-distill
description: Extract project knowledge from the current session into docs/. Keeps docs current, atomic, and indexed.
user_invocable: true
---

# Session Distill

Extract project-relevant knowledge from the current conversation and persist it into the `docs/` folder. Keeps documentation current, atomic, and organized behind `docs/index.md`.

## Step 1: Relevance check

Before doing any work, check if this session produced knowledge worth distilling. Look for:

- Files created or modified in the project
- Architecture or design decisions discussed
- Rationale given for choices (why X over Y)
- New components, patterns, or gotchas discovered
- Infrastructure or deployment configured
- Existing docs now outdated due to session work

If none apply (quick config tweak, question-only session, non-project work), skip silently. Do not announce that you're skipping.

## Step 2: Extract knowledge atoms

Scan the conversation and produce a mental list of **knowledge atoms** - self-contained facts worth persisting. For each atom, note:

- **Topic** (e.g., "webhook routing", "dev environment setup")
- **Type**: architecture, decision, gotcha, infrastructure, or component
- **Action needed**: create new doc, update existing doc, or remove outdated content

### What to extract

| Type | What to look for |
|------|-----------------|
| architecture | How components connect, data flow, system boundaries, protocols |
| decision | Choices made and WHY (e.g., "Django over FastAPI - company tech stack") |
| gotcha | Non-obvious behavior, workarounds, things that caused trouble |
| infrastructure | Deployment, tunnels, docker, secrets management, dev environment |
| component | New modules - purpose, interface, how to use them |

### What to ignore

- Code already in the codebase (code documents itself)
- Debugging steps that led nowhere
- Transient state (PIDs, temp files, session-specific URLs, port numbers that might change)
- Things already in CLAUDE.md or Claude memory files
- Conversation mechanics ("let me check that", "running tests")
- Implementation details that are obvious from reading the code

## Step 3: Check for skill impacts

Before touching docs, scan the session for changes that might affect existing skills in `.claude/skills/`. Look for:

- **Changed conventions** - naming patterns, commit rules, separator formats, file structures that a skill might reference or assume
- **New tools or workflows** - if the session introduced a new library, framework, or workflow pattern that a skill should use or know about
- **Changed processes** - if an implementation flow, review process, or deployment pipeline changed in a way that contradicts what a skill currently describes
- **New capabilities** - if something was built that could enhance an existing skill (e.g., a new helper that a coding skill should use)

For each potential skill impact, **ask the user** before making any changes:

> "This session changed [X]. The skill [skill-name] currently assumes [Y]. Should I update it?"

Do NOT update skills without explicit approval. Skills are shared across all projects and sessions - silent changes can have unintended effects.

If no skill impacts are found, move on silently.

## Step 4: Reconcile with existing docs

Read `docs/index.md` (if it exists) to understand what documentation already exists.

For each knowledge atom:

1. **Find the right file** - check if an existing doc covers the topic
2. **If a doc exists** - read it, update the relevant section. If the file now covers clearly separate topics, split it into focused files.
3. **If no doc exists** - create a new file. One focused topic per file.
4. **If content is outdated** - remove it. Delete the file if entirely obsolete.
5. **Flag stale planning docs** - if the session completed the last task of a plan, note that the plan/design/requirements files should be graduated (the `/code-tdd` skill's Step 8 handles the actual graduation). If `/code-tdd` was not used, flag the stale docs to the user and ask if they want you to graduate them now.

### Doc conventions

- **Atomic files** - one focused topic per file. Prefer small and focused over large and mixed.
- **Mermaid.js** for ALL diagrams - never ASCII art. Use ```mermaid fenced blocks.
- **Hyphens** (-) instead of em-dashes in all text.
- **Subdirectories** are fine when a topic has multiple related files (e.g., `docs/github/`).
- **No fluff** - write for an AI that needs facts, not prose. Lead with the what, then the why. Skip introductions and summaries.

## Step 5: Rebuild docs/index.md

After all changes, rebuild `docs/index.md` as a structured list of every doc file, grouped by category:

```markdown
# Documentation Index

## Architecture
- [System Overview](architecture.md) - Components, data flow, Temporal workflows

## Development
- [Dev Environment](dev-environment.md) - 1Password setup, SSH tunnel, justfile

## Reference
- [Key Files](key-files.md) - Task-to-file navigation
- [Gotchas](gotchas.md) - Non-obvious patterns and pitfalls
```

Categories emerge from the content - don't force a fixed structure. Each entry has the file link and a one-line description (under 80 chars).

The index must include ALL .md files in docs/ (recursively), excluding any working artifacts (plans/specs) that are still pending.

## Step 6: Verify

After writing, do a quick check:
- Every file listed in `docs/index.md` actually exists
- No orphan docs (files in docs/ not listed in the index)
- No broken Mermaid diagrams (valid syntax)
- No em-dashes anywhere
- CLAUDE.md has the instruction to read `docs/index.md` when context is needed

## Important notes

- Be efficient with token usage - don't read files you don't need to update.
- Don't announce what you're doing step by step. Just do the work and report what changed at the end.
- Report format: a short list of files created, updated, or removed. Nothing more.
