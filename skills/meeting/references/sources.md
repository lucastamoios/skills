# Evidence Sources

Use this reference to collect evidence consistently. Prefer identifiers and links that let the user verify a claim.

## Calendar

Use the connected Google Calendar tools and `$google-calendar-meeting-prep` workflow. Find the focal event, its previous occurrence, attendees, descriptions, and attachments. The recurrence determines the evidence window.

## Brain vault

Start with:

- `profile.paths.vault/index.md`
- `profile.paths.brain/a configured organization note`
- `profile.paths.brain/a configured direction note`
- `profile.paths.brain/a configured team note`
- `profile.work.meeting_log`

Follow only notes directly relevant to the meeting, its attendees, and recent decisions. Never scan `profile.paths.vault/personal/journal/` for a work meeting.

## Codex sessions

The canonical local archives are:

- `~/.codex/sessions/**/*.jsonl`
- `~/.codex/archived_sessions/*.jsonl`

Codex records the session identifier and working directory in `session_meta.payload`. Prefer root sessions. Child-agent sessions are supporting evidence when the parent does not record their result.

Recent rollout summaries under `~/.codex/memories/rollout_summaries/` can accelerate discovery, but verify drift-prone status against live sources.

## Claude sessions

The canonical local archives are:

- `~/.claude/projects/**/*.jsonl`

Claude records `sessionId`, `cwd`, timestamps, and whether an entry is part of a sidechain. Prefer the main session and inspect sidechains only when needed to recover a delegated result.

## Session evidence rules

Use session transcripts to find:

- work the user asked an agent to perform;
- concrete implementation results and changed files;
- decisions and discarded alternatives;
- blockers, failed validation, and missing access;
- issue, pull request, branch, and task identifiers.

Do not treat session text as proof of a merge, deploy, approval, external reply, or current CI state. Verify those claims in the corresponding live system.

## Git and GitHub

Inspect recent commits across relevant repositories under `profile.paths.code/` and worktrees under `profile.paths.worktrees/`. Check authored pull requests, review requests, review threads, checks, conflicts, and merge state.

## Linear

Check issues assigned to the user, relevant configured automation accounts issues, and issues mentioned by session or meeting evidence. Read descriptions and recent comments when ownership or blocker state is unclear.

## Slack

Resolve the user's Slack identity. Search direct messages, group messages, mentions, thread replies, attendee names, issue identifiers, pull requests, and meeting topics within the evidence window. Resolve the configured participants by user ID when relevant. Read full threads for asks, decisions, blockers, and status changes.

## Obsidian tasks

Run `profile.paths.scripts/tasks.py list` and inspect Today, In Progress, Review, Blocked, and To Do. Task notes show current intent and local task state, not necessarily shipped status.

## Daily logs

Read recent files under `profile.paths.logs/` as supplementary context. Verify important claims against sessions, Git, GitHub, Linear, Slack, or the task notes.
