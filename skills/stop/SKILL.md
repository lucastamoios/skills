---
name: stop
description: Stop and reconcile the active Obsidian task note. Use when the user says "stop", "stop task N", "wrap up", "pause this task", "I am done", invokes $stop, clearly ends tracked work, or before tracked implementation or review work in the brain is declared complete. Record material progress and move the task to Done when the outcome is complete or To Do when work remains, asking when the context is ambiguous.
---

# Stop

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Close one explicit work session tracked in `profile.paths.tasks`. Never act on a task merely because automatic session metadata mentioned it.

Before declaring tracked implementation or review work in the brain complete, reconcile its active Obsidian task through this workflow. A final answer is not a substitute for the task update.

## Workflow

1. Resolve the task started through `$start`, or accept an explicit ID. If unknown, list In Progress tasks and ask the user.
2. Inspect what this session actually completed.
3. Choose `Done` when the requested outcome is clearly complete. Choose `To Do` when work remains, including pauses, review handoffs, blockers, or unfinished follow-ups.
4. Use an explicitly supplied valid lane when the user deliberately requests one. Otherwise infer Done or To Do from the session. Move without asking when the evidence is clear; ask a short clarifying question when it is not.
5. Append a concise note only for a material result, decision, blocker, handoff, or next step with `profile.paths.scripts/tasks.py note --id <filename-slug> --text "<note>"`.
6. Move the task with `profile.paths.scripts/tasks.py move --id <filename-slug> --lane "<lane>"`. This updates `status`, `updated`, `completed`, and the task history.
7. Report the note and final lane. For a review handoff, also report the absolute worktree path, one exact copy-paste review command, and the pull request URL and current live state when one exists. Suggest `$retro` when durable project knowledge or a concrete workflow lesson was produced. State the reason briefly, and run it only if the user explicitly asks.

If nothing material happened, skip the note. If the task files or command are unavailable, report the exact failure and do not claim an update.
