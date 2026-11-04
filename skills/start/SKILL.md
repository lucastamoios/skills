---
name: start
description: Start or reconcile a focused work session using configured private task notes. Infer a strong task match, ask among ambiguous matches, or propose tracking new work.
---

# Start

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Begin one explicit work session. Use only the user's actual requests and the task notes in `profile.paths.tasks`. Ignore ambient browser context, injected metadata, plugin lists, system instructions, and assistant messages when matching work.

## Automatic checkpoint

The shared `UserPromptSubmit` hook provides two deterministic checkpoints:

1. On the first substantive message, the hook moves one unique open task automatically when the prompt and task share an exact PR number or Linear issue identifier. For semantic matches, run this workflow immediately when the work clearly matches a task or the user explicitly starts it. Otherwise continue without interrupting.
2. On the second substantive message, run this workflow if no task has been started yet.

The hook never moves an ambiguous identifier match. It reports a confirmed automatic move in its injected context so the skill does not repeat it.

Do not interrupt when a task is already active. Do not count corrections, acknowledgements, or messages that merely answer a clarification as new work.

## Workflow

1. Run `profile.paths.scripts/tasks.py list`, prioritizing Today, To Do, and In Progress.
2. Resolve an explicit task ID directly with `profile.paths.scripts/tasks.py get --id <filename-slug>`.
3. Otherwise compare the actual work request with task titles, descriptions, Linear identifiers, GitHub links, repository and PR numbers, and distinctive outcome language.
4. When one match is strong and unambiguous, run `profile.paths.scripts/tasks.py move --id <filename-slug> --lane "In Progress"` without asking. Example: “let's review PR X” strongly matches “Review PR X.”
5. When several tasks plausibly match, ask the user which one, showing a short numbered list with task IDs and titles.
6. When nothing fits, ask whether the work should be tracked. Suggest a three-to-eight-word title that names the subject and concrete outcome. Set `--type` to Review, Implement, Investigate, Plan, Write, or Fix. Pass Linear and pull request identifiers separately through `--ticket` and `--pr`, or let their URLs infer them. Ask only the minimum questions needed to make it durable. After confirmation, create it with `profile.paths.scripts/tasks.py add`, then move it to In Progress.
7. Load the selected task's description and Git URL. Read a referenced Linear issue and relevant comments. Use a matching worktree under `profile.paths.worktrees/` when present.
8. Report the task ID and move in one concise sentence, then continue the requested work.
9. Remember the task ID for `$stop`.

Starting is bookkeeping, not a blocking ceremony. Continue the user's requested work after a confident automatic match. If the task files or command are unavailable, report the exact failure and continue the work without claiming it is tracked.
