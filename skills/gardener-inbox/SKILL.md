---
name: gardener-inbox
description: Process the configured capture inbox into private notes, tasks and proposed follow-ups. Use for filing captured material into the user’s knowledge system.
---

# Gardener: Inbox

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Turn raw captures into filed, linked knowledge. The whole point: the user should
never have to decide where a thought goes at capture time - he dumps it in the
inbox, and you file it later.

This is one arm of the gardener family. It only drains the capture inbox. It does
not prune, trim, or archive existing docs - that is [[gardener-prune]]. It does
not audit docs for consistency - that is [[gardener-audit]]. It does not close
finished tasks on the board - that is [[gardener-board]]. The bare [[gardener]]
skill orchestrates the arms.

## Input

`profile.paths.brain/inbox.md` - append-only. Entries are delimited by `## <ISO-8601 timestamp>`
headers, each followed by the captured text.

## For each unprocessed entry: classify, then file

1. **Journal-bound** - feelings, reflections, personal narrative (e.g. "today I
   felt crushed"). Append to the current-year file in `vault/personal/journal/`
   under a dated heading, preserving the capture timestamp. (Encrypted at rest.)
2. **Task** - actionable (e.g. "create a panel for navigator"). File it into the
   Obsidian task folder, the canonical task store, via the local command:

   ```
   profile.paths.scripts/tasks.py add --title "<imperative title>" \
     --impact <1|2|4|8|16> --effort <minutes> \
     [--realm "<Realm Name>"] [--description "<detail>"]
   ```

   Use a succinct three-to-eight-word title that names the subject and concrete
   outcome. Store Linear and pull request identifiers through `--ticket` and
   `--pr`, or provide their URLs so the command can infer them. Set `--type` to
   Review, Implement, Investigate, Plan, Write, or Fix.

   Tasks land in the **To Do** lane by default. the user triages them there. Set the realm to the basename of the most
   relevant vault note so it becomes a wikilink. If the realm is unclear, omit
   `--realm` and say so in the description rather than guessing.

   **Always set `--impact` and `--effort`** - a best guess beats a blank, and
   the user corrects values at triage faster than he fills them in. If the capture
   is too vague to size at all, note that uncertainty in the description. Calibration:

   - Effort is **the user-attention minutes** (deciding, steering agents, reviewing):
     active working time only, never agent wall-clock or elapsed calendar time.
   - Review depth by codebase: the configured automation code gets little or no review; internal
     tools, scripts, and PoCs get a light pass; the configured organization core-app code gets a full
     review.
   - Third-party review latency (a the user-authored PR waiting days on a teammate's
     review) is not effort: note it in the description and park the task in
     Blocked or Delegated while it waits.
   - Bands: 15m fire-and-forget agent run he only skims; 30-60m agent-built change
     with light review or a QA pass; 120-240m multi-PR feature, infra change, or
     core-app work with full review; 480m+ only for initiative-scale work.
   - Impact: 16 moves the core KPI or unblocks a company priority now; 8 a visible
     needle-mover; 4 a solid improvement; 2 a papercut; 1 a nice-to-have.

   If the local task write fails, do **not** silently drop the task. Defer it to
   `pending.yml` with the exact failure so it surfaces next interactive session.
3. **Note / idea / reference** - durable knowledge (e.g. "X library does Y").
   File into the right vault folder; create or update a note with frontmatter
   (`type`, `related_to` wikilinks, `status: active`) and link it into the graph.
4. **Unclear** - ambiguous between categories or needs the user's judgment. Append
   to `profile.paths.brain/pending.yml` with `captured_at`, `text`, your best-guess
   `probability`, `confidence`, `candidate_realm`, and a one-line `reason`. Do
   NOT guess-file it.

## Rules

- **Confidence bar:** file only what you are clearly sure of. Deferring to
  pending.yml is a feature, not a failure.
- **Drain the inbox:** remove each entry from inbox.md once filed or deferred.
  The inbox should end empty (only keep an entry if you literally could not parse it).
- **Boundary:** you may read across personal and professional, but never copy
  personal content into professional-facing notes.
- **Commit after the run** so every gardening is reversible. Try `git -C profile.paths.brain
  commit -S` with the 30 second signing timeout from AGENTS.md; fall back to
  unsigned only if signing fails or times out. Summarize what
  you filed in the message. Do not add a Co-Authored-By line. No em-dashes or connector dashes.
- Keep changes small and human-readable; match the vault conventions in
  `vault/AGENTS.md`. Lifecycle states for notes: active / dormant / maybe / archived.

## Interactive (guided) gardening

When the user gardens interactively, first surface `pending.yml` ("last sessions I
could not place these") and resolve those with him before processing new inbox
entries.

## Task maintenance pass (interactive only)

After draining the inbox in an interactive session, offer a maintenance pass over
the Obsidian task board. This is **suggest, then apply on the user's confirmation** -
never auto-edit or auto-delete tasks. Skip it in headless runs.

1. List tasks with `profile.paths.scripts/tasks.py list`, using `--lane <name>` when
   useful. Look at the open lanes: To Do, Today, In Progress, Blocked,
   Maybe - not Done/Delegated.
2. Read each task **in the light of the whole brain**: the vault (active projects,
   notes, `related_to` links), recent journal themes, the other open tasks, and
   what is actually moving (recent commits, PRs). A task is not just its title.
3. Surface a short, numbered list of suggestions, each with a one-line reason:
   - **Stale** - sitting in To Do/Today/In Progress untouched for weeks, or
     superseded by work already done elsewhere. Suggest move to Maybe, Done, or
     delete (with `--id`).
   - **Priority** - `--impact {1|2|4|8|16}` looks wrong given current focus
     (e.g. a the configured organization-blocking task at impact 1 while idle ideas sit at 8).
   - **Effort** - `effort_minutes` missing or unrealistic for what the task
     really entails.
   - **Misfiled** - wrong realm, or belongs in a different lane.
4. Apply only what the user confirms with `tasks.py update` or `tasks.py move`. Read
   a task's current state before editing it. Archive rather than delete unwanted tasks.

Tasks live as individual Markdown files in `profile.paths.tasks`; there is no central `tasks.yml`.

Detecting *finished* work (a merged PR, a session that completed the task) is
not this pass's job: that is [[gardener-board]], which verifies the evidence
before closing. Here, limit "stale" suggestions to judgment calls and let the
board arm handle anything provable.
