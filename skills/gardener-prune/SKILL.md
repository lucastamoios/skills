---
name: gardener-prune
description: Reduce a documentation folder to the minimum tokens a future agent needs, without losing knowledge, and leave it better connected and convention-clean. Finds duplicated content across files, obsolete files, dead cross-references, oversized notes, verbose prose, weak interlinking, and non-conforming frontmatter; proposes a numbered change plan (delete-or-archive / merge / split / trim / fix / link / normalize per file); applies it after approval. Every prune also enriches the link graph and normalizes frontmatter to the folder's conventions, making an audit's findings fully actionable. Detects the folder's conventions - a brain-vault subtree (wikilinks, status:Archived blockquote, index.md, sensitivity markers) or a code-repo docs/ tree - and prunes to match. Trigger on explicit reduction intent ("prune the docs", "the project docs are bloated", "shrink/dedupe/tighten <folder>"); do not trigger on lookups, or on gardener-audit which only inspects.
argument-hint: "<folder> (a vault subtree like project, or a repo path; omit to ask)"
allowed-tools: Bash(git *), Bash(ls *), Bash(find *), Bash(wc *), Bash(rm *), Bash(mv *), Bash(mkdir *), Read, Grep, Glob, Edit, Write, AskUserQuestion
---

# Gardener: Prune

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Take a documentation folder and make it leaner and better connected: strictly
smaller without losing knowledge an agent needs, and more densely cross-linked so
both agents and the user can navigate it. This is the pruning arm of the gardener
family (see [[gardener]] for the orchestrator, [[gardener-inbox]] for capture
filing, [[gardener-audit]] for the read-only consistency sweep).

Five modes of reduction, plus two conformance modes (enrichment and frontmatter):

1. **Cross-file dedup**: same fact stated in two places -> keep one canonical home, replace the other with a one-line pointer.
2. **File-level removal**: superseded, obsolete, or never-referenced files get archived (preferred) or deleted.
3. **Split oversize**: a note past roughly 200 lines or holding unrelated sections gets split into subnotes under a folder, with the original turned into a hub that links them.
4. **In-file trimming**: narrative prose, onboarding asides, and "we will / we plan to" forecasting get cut to fragments. Tables and bullet lists are kept; paragraphs that restate them are removed.
5. **Dead-reference repair**: fix or drop links whose target file or heading no longer exists.
6. **Link enrichment**: add cross-links between genuinely related notes that are not yet connected, so the graph reflects the relationships that already exist in the content. This is the one additive mode; it costs a few tokens to save navigation time. It never invents a relationship or forces a link where there is no natural anchor.
7. **Frontmatter normalization**: bring each note's YAML frontmatter into line with the folder's conventions and fix redundant, missing, or malformed fields. In vault mode the conventions are `vault/AGENTS.md`'s: `type` present (Note/Project/Reference), `related_to` as `[[wikilinks]]`, `tags` mirroring the folder path, `status` only when not active, `sensitivity` only when personal. This is the mode that makes an audit's frontmatter findings applicable; without it they have nowhere to land.

Argument: `$ARGUMENTS`

## When to use

Trigger only when the user clearly wants reduction, not a lookup or an audit:

- "prune the docs", "shrink/dedupe/tighten `<folder>`"
- "the project docs are bloated - cut them down", "summarize the old stuff and archive it"

Do **not** trigger on: "check/read the docs" (lookup), "audit the docs / find contradictions" (use [[gardener-audit]]), or "file this capture" (use [[gardener-inbox]]).

## Step 1: Resolve the folder and detect the mode

1. If `$ARGUMENTS` names a folder, use it. A bare name like `project` resolves to `profile.paths.vault/project`. An absolute path or `.` is used as-is. If nothing is given, ask once. Announce the choice in one line.
2. **Detect the mode** - this drives every convention below. Announce it too.
   - **Vault mode**: the folder is at or under `profile.paths.vault` (there is a `vault/AGENTS.md` at or above it). The vault is the source of truth; there is no Linear or code to cross-check against. Conventions come from `vault/AGENTS.md` and `vault/index.md`.
   - **Repo mode**: anything else. Expect a `docs/` tree in a code project. The code and Linear are the source of truth; conventions come from the repo's `CLAUDE.md` and `docs/index.md`. If neither a vault nor a recognizable `docs/` tree is present, abort with a clear error.
3. Run `git status` on the enclosing repo. If the working tree is dirty or mid-merge, ask once whether to continue - this skill creates real diffs and wants a clean baseline.

## Step 2: Inventory the folder

Walk the folder recursively. For every `.md` (and `.feature` in repo mode) record: path; token estimate (`wc -w` / 0.75, rough is fine); first-H1 title; section headings; line count; outbound links (`[[wikilinks]]` and relative paths in vault mode; relative paths and `<TEAM>-####` identifiers in repo mode); inbound link count; last-modified date from `git log -1 --format=%ci -- <path>`.

Group and print a baseline table (file count + estimated tokens per group):
- **Vault mode**: hubs (a note whose job is to link subnotes, e.g. `engineering.md`), subnotes (files under a hub's folder), the folder's own `index`-style entries, loose notes, and already-`Archived` notes.
- **Repo mode**: index files (`*/index.md`), map leaves (`docs/map/*`), specs (`requirements/`, `design/`, `plans/`, `runbooks/`), loose docs.

## Step 3: Find duplications

For each pair of docs sharing concepts, look for verbatim repetition (grep distinctive phrases), paraphrased repetition (same subject+verb+object, different words - LLM judgment), hub/index-to-leaf overlap (a hub or index that re-summarizes what its subnotes already say; those entries should be one-liners), and cross-cutting conventions repeated in every note that brushes them (belongs once in the hub/index).

Choose a canonical home:
- Cheapest home wins for universals: index/hub < loose note < detailed subnote/spec.
- Concept-specific facts live in the relevant subnote, not in a general "overview" or "gotchas" note.
- If two docs say the same thing, the newer wins; the older gets a pointer.
- **Vault mode pointer**: `See [[canonical-note]] for details.` **Repo mode pointer**: `> See [<title>](<rel-path>#<section>) for details.`

## Step 4: Find removable files

Mark for removal if **any** hold: inbound link count is 0 and nothing outside the folder references it (grep the wider repo, and `CLAUDE.md`/`AGENTS.md`); fully superseded by another note; contains only TODO/WIP/empty content; a session note already distilled into permanent docs; an obsolete plan whose Linear issue is Done and whose replacement exists (repo mode).

Prefer **archive over delete** whenever the file is a historical record that might be wanted later (superseded but valuable). This is the core "summarize into the main doc and move the detail to an archive" behavior the user wants:

- **Vault mode**: first make sure the durable kernel of the note lives in its live hub or the folder's main note (move it there as part of a dedup step if it does not). Then move the file to the archive - `profile.paths.vault/archive/` in general, or `profile.work.knowledge_root/archive/` for anything under `project/`. Give the archived note `status: Archived` in frontmatter and a one-line blockquote directly under its H1: when it was archived, why, and a `[[wikilink]]` to the live note that supersedes or distills it. Add a backlink from the live note where the history is relevant. Update the Archive section of `vault/index.md`.
- **Repo mode**: `mkdir -p docs/archive/<dir>` and `mv` the file there.

**Never remove**: files referenced by a slash command, agent YAML, or hook config; files referenced from any `CLAUDE.md` or `vault/AGENTS.md`; the most recent runbook for an operational concern; in vault mode, anything under `personal/journal/` (sensitive; do not even read it unless the user is explicitly working on journal content).

## Step 5: Find splittable notes (vault mode emphasis)

Flag any note past ~200 lines or collecting unrelated sections. Propose splitting it into subnotes under a folder named for the note, turning the original into a hub that links them with `[[wikilinks]]` (the pattern `<project>/engineering.md` and `<project>/automation.md` already use). One topic per note. In repo mode, do not restructure `docs/map/` leaves - that structure is owned elsewhere; only trim wording and fix links inside them.

## Step 6: Find trimmable prose

Per doc, scan for: onboarding asides ("you might wonder", "the reason we did this"); prose that re-narrates a table or list right next to it; forecasting ("we plan to", "future work will") unless tied to a Linear issue or an Open-questions block; step-by-step prose that works better as bullet fragments; **connector dashes** (none allowed - use commas, colons, periods, parentheses; em-dash and spaced-hyphen-as-connector both out); and git/commit/convention boilerplate repeated per file (centralize in `CLAUDE.md`/`AGENTS.md`, remove from the docs). Every trim must have a measurable token delta - no equal-length rewrites.

## Step 7: Find cross-reference and frontmatter problems

**Dead references.** For every link: missing target file -> fix or drop; missing target heading -> fix; link text sharply different from the target's real title -> update; external links (Linear/GitHub/Slack) -> leave alone. In vault mode this includes `[[wikilinks]]` whose basename resolves to no file under `vault/**`.

**Missing links (enrichment - runs every prune).** Build the folder's current link graph, then look for edges the content implies but the graph is missing. Propose an addition only when there is both a genuine topical relationship and a natural anchor:

- **Unlinked mention**: a note names a concept, tool, person, or project that has its own note, in prose, without linking it. Add a `[[wikilink]]` (vault) or relative-path link (repo) at that existing phrase - never insert a new sentence just to hold a link.
- **Sibling cluster**: notes that are peers of one kind (e.g. the observability access notes for temporal/langfuse/learnings, or the subnotes under one hub) should point to each other, not only up to the hub.
- **Reciprocity**: when note A links B and the relationship is mutual, add the B->A edge (inline where an anchor exists, else `related_to` frontmatter in vault mode).
- **Thin/orphan notes**: a note with zero or one outbound link is a navigation dead end. Find the two or three notes it is most related to and connect it.
- **Anchor choice**: prefer an inline link at a phrase already in the text. Only when there is no natural inline anchor, add a `related_to` frontmatter edge (vault) - do not manufacture prose. In repo mode use relative-path links and requirement/design cross-references, not wikilinks.

Reasonableness bar: err toward the link when a reader of one note would plausibly want the other. Do not chain-link every co-occurring term, do not add a link a reader would never follow, and do not duplicate a link that already exists in the same note. Over-linking is noise; the goal is the few edges that actually aid navigation.

**Frontmatter conformance (runs every prune).** Read each note's YAML block and compare it to the folder's conventions (vault mode: `vault/AGENTS.md`). Propose a fix for:

- **Redundant fields**: `status: Active` (the default; omit it), or any field set to its default value.
- **Missing fields**: no `type`; no `tags`, or `tags` that do not mirror the note's folder path; a personal note without `sensitivity`.
- **Malformed fields**: `related_to` values that are not `[[wikilinks]]`, a single relationship written as a list of one (or vice versa against the convention), `title:` present (the H1 is the title), unquoted wikilink scalars.
- **Stale links in frontmatter**: a `related_to` wikilink whose target no longer exists (fix or drop, same as a body dead link).

Only normalize when the correct value is unambiguous from the conventions or the note's own content. If `type`, the right `related_to` target, or a `sensitivity` marker is genuinely unclear, flag it in the plan for the user rather than guessing. Never touch domain-specific frontmatter that a note legitimately carries (e.g. the pacto sheets' `semana_inicio`/`pontos_total`, or meeting notes' `date`/`attendees`); those are not normalized away.

## Step 8: Build the change plan

Assemble one numbered markdown report and print it. **Edit nothing yet.**

```
## Baseline
| Group | Files | Tokens (est) |
| --- | --- | --- |
...

## Removals (D-1 ... D-n)        target, reason, archive|delete, kernel-already-in (vault), token delta
## Dedup moves (M-1 ... M-n)     source, target, what moves, pointer left behind
## Splits (S-1 ... S-n)          note, proposed subnotes, hub shape
## Trims (T-1 ... T-n)           file, section, before/after snippet, token delta
## Cross-reference fixes (X-1 ... X-n)  file, broken link, fix or removal
## Link additions (L-1 ... L-n)  file, anchor phrase (or "frontmatter related_to"), target note, why the relationship is real
## Frontmatter fixes (F-1 ... F-n)  file, field, current -> corrected (or "flag: unclear"), which convention

## Estimated impact
| Metric | Before | After | Delta |
```

`L` items are additive, so the impact table nets them against the reductions rather than hiding them (report new-edges count alongside tokens saved). If a prune finds nothing to reduce, an `L`-only plan is still a valid, useful run.

## Step 9: Approval gate

Use `AskUserQuestion`. Offer: **Apply all**; **Apply selected** (the user names IDs; accept ranges `T-1..T-5` and wildcards `all D-*`, `all L-*`, `all F-*`); **Reductions only** (skip the `L` link additions and `F` frontmatter fixes); **Cancel**.

## Step 10: Execute (least destructive first)

1. **X** cross-reference fixes.
2. **L** link additions - add each `[[wikilink]]`/relative-path link at the planned anchor phrase, or the `related_to` frontmatter edge.
3. **F** frontmatter fixes - edit the YAML block in place to the corrected value; skip any item flagged unclear. Do these non-destructive edits (X, L, F) before any content moves so later steps see the new links and clean frontmatter.
4. **T** trims - re-read each file before editing; do not trust report snippets verbatim if the file changed this run.
5. **M** dedup moves - insert canonical content in the target if absent, replace the duplicate with the mode-appropriate pointer.
6. **S** splits - create the subnotes with proper frontmatter and H1, rewrite the original as a hub of `[[wikilinks]]`, update `index.md`.
7. **D** removals - for archive, ensure the kernel is in the live note, `mv` to the right archive dir, add the `status: Archived` frontmatter + under-H1 blockquote + live-note backlink + `index.md` Archive entry (vault) or `mkdir -p docs/archive` + `mv` (repo). For delete, `grep -r` the wider repo once more and abort that single removal if anything still references it.

After each change run `git diff --stat`; if anything outside the planned files was touched, stop and report.

## Step 11: Verify, then commit

1. Re-run the Step 2 inventory. Print before/after totals next to the predictions.
2. Re-walk all links; fix any new dead reference created by a removal this run (a `[[wikilink]]` or path pointing at something just archived should point at the archived location or the live note).
3. **Vault mode**: commit the run so it is reversible - `git -C profile.paths.brain commit -S` with the 30 second signing timeout from AGENTS.md, unsigned only if signing fails or times out, no Co-Authored-By line, no connector dashes, summarizing what was pruned. **Repo mode**: do not commit; suggest one commit per category (D/M/S/T/X) and let the user review.

## Step 12: Post-run summary

Print: files removed/archived/split/edited; tokens saved (predicted vs measured); links added (count and the notes now connected); frontmatter fields normalized (and any flagged unclear); anything skipped because the user did not approve it; anything skipped by a safety rule (referenced from `CLAUDE.md`/`AGENTS.md`, journal content, etc.). The diff is the artifact - keep the summary short.

## Failure mode reference

| Situation | Behavior |
| --- | --- |
| Not in a git repo | Abort with clear error |
| Dirty working tree | Ask once before continuing |
| Neither a vault subtree nor a `docs/` tree | Abort |
| Spec doc that maps 1:1 to a Linear issue (repo mode) | Never rewrite content; only propose delete-if-superseded and link fixes |
| Removal target referenced from `CLAUDE.md` / `AGENTS.md` / agent YAML | Drop the proposal, note it in the summary |
| `personal/journal/` content (vault mode) | Never read, trim, move, or delete it |
| Dedup target note does not exist yet | Create it only if the user opts in via the plan, else downgrade to "trim duplicates in place" |
| Edit fails because the file changed mid-run | Re-read and retry once, else mark skipped and continue |

## Anti-patterns in the change plan

- No stylistic rewrites that preserve length - every T needs a token delta.
- No moves that shuffle text without consolidating duplication.
- One logical change per ID; do not bundle unrelated changes.
- No deletion proposals for files whose inbound references you did not actually check.
- No link spam: every `L` needs a real topical relationship and a natural anchor already in the text. Never add a sentence solely to host a link, never link every co-occurring term, and never re-add a link the note already has.
- No frontmatter guesses: normalize an `F` item only when the correct value is unambiguous from the conventions or the note's content. If `type`, `related_to`, or `sensitivity` is genuinely unclear, flag it for the user; do not fabricate a value or strip a domain-specific field you do not recognize.
