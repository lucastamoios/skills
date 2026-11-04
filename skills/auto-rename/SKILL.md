---
name: auto-rename
description: Rename the current Codex task with an emoji-prefixed work status and a concise outcome title. Use for task-title updates, not file, branch, or identifier renames.
---

# Auto-rename a Codex task

Rename the current Codex task so its sidebar title shows the work status and
the specific outcome. Use `set_thread_title` for the current task.

## Choose the title from the whole session

Before choosing a title, review the session from its beginning, including earlier user requests, clarifications, completed work, and the final outcome. Name the main goal and result that explain why this task exists. Do not title the task after the most recent message, tool call, or small follow-up when it is only part of the larger task. Fold supporting steps and side requests into the main outcome unless the user clearly replaced the original objective with a new one.

Choose the status marker from the state of that overall goal, not from the latest subtask. A completed side task does not make the session Done while its main goal remains active. Keep the title concise and searchable, and include the main PR or issue identifier when it helps identify the session.

Use exactly one status marker:

- `🔎 Research:` for investigation, discovery, or analysis with no intended code change.
- `🛠️ Building:` for implementation in progress.
- `👀 Review:` for code or pull-request review.
- `🧪 QA:` for validation, testing, or reproduction work.
- `🙋 Action needed:` when the user must answer, approve, or take another action before the main work can continue.
- `⏸️ Blocked:` when progress depends on someone or something other than the user, such as a third-party decision, unavailable access, or an external system change.
- `✅ Done:` for a completed outcome that will remain visible briefly before archival.

Write the rest as a concise, searchable outcome. Include the issue or PR
identifier when it materially helps identification. For example:

`👀 Review: PR #5041 Product Use reorder`

If the requested status or subject is unclear, inspect the current task
context and choose the most accurate marker. Do not rename files, branches,
directories, database records, or external resources. Do not archive, pin, or
otherwise change task state unless separately requested.
