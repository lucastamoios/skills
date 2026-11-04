---
name: gardener
description: Tend the brain's knowledge as the orchestrator for the gardener family. With no folder, drain the capture inbox, mine pending session transcripts, and reconcile Obsidian task notes against merged pull requests and recent sessions. With a folder, run inbox, transcript, audit, and pruning passes. Use for "garden", "tend the vault", "tend the project docs", "clean up <folder>", or "run the gardener".
argument-hint: "[folder] (omit to drain the inbox only)"
---

# Gardener (orchestrator)

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

The gardener family turns raw thought into filed, linked, lean knowledge, and
keeps it that way over time. This skill is the entry point that sequences the
three focused arms. It writes nothing itself: every write happens inside a
sub-skill, each of which commits or gates on its own.

| Arm | What it does | Writes? |
|-----|--------------|---------|
| [[gardener-inbox]] | Drain `profile.paths.brain/inbox.md`: classify each capture and file it (journal, Obsidian task, vault note, or pending.yml). | yes, commits |
| [[gardener-transcripts]] | Mine the session transcripts pending since the last watermark for meta-signals (repeated corrections, worries, orphaned knowledge, violated norms) and file the approved harvest. | yes, gated interactively; stages to pending.yml headless |
| [[gardener-board]] | Reconcile Obsidian tasks with reality: check each open task against pull requests, Linear, and recent sessions; close verifiably finished tasks and surface ambiguous ones. | yes to task notes; ambiguous findings gated or staged to pending.yml |
| [[gardener-audit]] | Read-only consistency sweep of a docs folder. Report only. | no (repo mode writes one report file) |
| [[gardener-prune]] | Dedupe, trim, and archive a docs folder down to the knowledge an agent actually needs; enrich cross-links between related notes; normalize frontmatter to the folder's conventions. | yes, after an approval gate |

## What to run

Invoke each arm through the Skill tool. Do not reimplement its logic here - each
one owns its own conventions, mode detection, and safety gates.

### No folder given (`/gardener`)

This is the everyday pass and the headless meaning. Run **`gardener-inbox`** to
drain the capture inbox, then run **`gardener-transcripts`** to mine the
sessions pending since its watermark (it exits on its own when there is too
little new material, so invoking it is always safe), then run
**`gardener-board`** to reconcile the Obsidian task board: it checks each open task
against PRs, Linear, and the recent claude/codex sessions, closes the
verifiably finished ones, and surfaces the ambiguous ones. Then stop. Do not
prune or archive on the bare invocation: inbox draining, transcript mining, and
board reconciliation are safe and frequent, pruning is deliberate and
destructive-ish. If the user wants a doc-tending pass he names a folder (below) or
asks explicitly.

### A folder given (`/gardener project`, `/gardener profile.paths.vault`, `/gardener .`)

Resolve the folder first. A bare name like `project` resolves to
`profile.paths.vault/project` when tending the brain; an absolute path or `.` is used
as-is. Then run a full tending pass in this order, pausing between steps:

1. **`gardener-inbox`** first. A pending capture may belong in the very folder you
   are about to tend, so file everything before you audit.
2. **`gardener-transcripts`**. Pending sessions may hold knowledge or corrections
   that belong in the folder you are about to tend; it self-skips when there is
   too little new material.
3. **`gardener-audit <folder>`**. Present its report to the user.
4. **Pause.** Given the audit findings, ask whether to proceed to pruning.
5. **`gardener-prune <folder>`**. It runs its own approval gate before writing.

## Rules

- Run the arms in sequence, never in parallel: prune depends on what the audit
  surfaced, and both depend on the inbox already being drained.
- Do not re-invoke an arm that is already running.
- This orchestrator commits nothing. `gardener-inbox` and `gardener-prune` handle
  their own commits (signed, no Co-Authored-By, no connector dashes); the user
  reviews.
