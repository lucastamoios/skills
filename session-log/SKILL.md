---
name: session-log
description: Capture session activity into a daily log file in logs/ for later review.
user_invocable: true
---

# Session Log

Capture what was done in this session and append it to today's daily log at `logs/YYYY-MM-DD.md`. This is a personal activity log - quick, factual, and scannable - so you can rewind what you did on any given day.

## Step 1: Gather context

Collect information from the session:

1. **Conversation scan** - what tasks were worked on, what decisions were made, what was investigated
2. **Git changes** - run `git diff --stat` and `git log --oneline -10` to see what files changed and recent commits
3. **Current time** - use `date '+%H:%M'` for the entry timestamp and `date '+%Y-%m-%d'` for the filename

## Step 2: Write the log entry

Determine the log file path: `logs/YYYY-MM-DD.md` (e.g., `logs/2026-04-14.md`).

If the file does not exist, create it with a top-level heading:

```markdown
# YYYY-MM-DD
```

Append a new entry to the file. Each entry follows this format:

```markdown

## HH:MM - Brief one-line description of the work

- What was done (2-5 bullet points, concise)
- Key files created or modified
- Related issues, PRs, or context if any
```

### Guidelines

- **Be concise** - this is a rewind log, not documentation. One sentence per bullet.
- **Focus on outcomes** - "added webhook retry logic" not "opened file X, read line Y, discussed approach".
- **Skip session mechanics** - do not log "ran session-distill", "compacted context", or other meta-actions.
- **Group related work** - if the session had one main task, write one entry. If it had clearly separate tasks, write separate entries.
- **Include blockers** - if something was attempted but failed or was blocked, note it briefly.
- **No em-dashes** - use hyphens.

## Step 3: Confirm

After writing, report the entry you added in one line. Do not read the file back.

## Important notes

- Do NOT run `/session-distill` from here - they are independent skills and may both be triggered by the same hook.
- If the session had no meaningful work (just a quick question, no code changes, no investigation), skip silently.
- Multiple entries per day are expected - each session or compaction adds its own timestamped entry.
