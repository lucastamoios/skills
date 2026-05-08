---
name: autopilot
description: Run the full issue-to-PR workflow autonomously across a list of Linear issues or a Linear filter. Orchestrates next-issue, code-tdd, code-review, architecture-review, implement-review, qa, and create-pr, plus a post-PR bot-comment polling window. After each issue it runs /compact and re-invokes itself from saved state until the queue drains.
user_invocable: true
allowed-tools: Bash(*), Read, Grep, Glob, Edit, Write, Skill, mcp__linear-server__list_issues, mcp__linear-server__get_issue
argument-hint: "[<TEAM>-123 <TEAM>-124 ... | --epic <TEAM>-X | --assignee me --state backlog | --resume]"
---

# Autopilot

Thin orchestrator that runs the standard issue-to-PR workflow across many Linear issues without pausing for input. It persists queue state to a file so it survives `/compact`.

Argument: `$ARGUMENTS`

## Pre-approval contract

By invoking autopilot the user has pre-approved, for every issue in the queue:

- All confirmation gates inside downstream skills - `next-issue` branch confirmation, `code-tdd` Step 4 pause-for-review and Step 8 doc-graduation permission, `implement-review` evaluation gate, `create-pr` prompts. Treat them as "approved, continue".
- Commits (without co-author lines, GPG-signed per CLAUDE.md).
- Branch pushes, PR creation (including WIP PRs on failure), and force-with-lease pushes from `implement-review`.

No existing skill files need changes. This clause is all autopilot needs to unblock them.

## State file

Path: `tasks/autopilot/state.json`. Shape:

```json
{
  "started_at": "2026-04-18T10:22:00Z",
  "queue": ["<TEAM>-4310", "<TEAM>-4311", "<TEAM>-4312"],
  "blocked_by": { "<TEAM>-4311": ["<TEAM>-4310"] },
  "results": {
    "<TEAM>-4310": { "status": "shipped", "pr_url": "..." }
  }
}
```

`status`: `pending` | `in-progress` | `shipped` | `shipped-wip` | `needs-attention` | `skipped`.

Persist state after every stage transition. Never run `/compact` before persisting.

## Step 1: Fresh run or resume

Read `tasks/autopilot/state.json`.

- If `$ARGUMENTS` contains `--resume`, or the file exists with non-terminal items (`pending`, `in-progress`), treat as **resume** and skip to Step 3.
- If the file exists and all items are terminal, archive to `tasks/autopilot/state.<iso>.json` and proceed to Step 2.
- Otherwise proceed to Step 2.

## Step 2: Build the queue

Parse `$ARGUMENTS`:

- Explicit list: `<TEAM>-4310 <TEAM>-4311 ...` in given order.
- `--epic <TEAM>-X`: `list_issues(parentId, state: "backlog", orderBy: "createdAt")`.
- Other filters (`--assignee me`, `--state ...`, `--label ...`, `--project ...`): pass through to `list_issues`.
- Empty: same as `--assignee me --state backlog`.

For each issue, call `get_issue(id, includeRelations: true)`. Build `blocked_by`. Drop issues whose blockers are neither in the queue nor already merged/branched (report them).

Write the state file. Print the resolved queue (IDs, titles, blockers) so the user can scan it. Do not wait for input.

## Step 3: Pick the next eligible issue

At the start of this step, abort if state file has `"abort": true`.

Find the first item whose `status` is `pending` or `in-progress` and whose `blocked_by` entries are all `shipped`, `shipped-wip`, or already merged. If a candidate's blocker is `needs-attention` or `skipped`, mark the candidate `skipped` (note: `"skipped: <blocker> did not complete"`) and keep scanning.

If nothing is eligible, go to Step 10.

Mark the picked issue `in-progress`, persist, and continue. Call it `<ISSUE>`.

## Step 4: Run the per-issue pipeline

Invoke each skill via the `Skill` tool in order. Do not duplicate their logic here. Apply the pre-approval contract - every gate is pre-approved. When a skill produces output that the next skill needs (e.g., review findings, PR URL), capture it and pass it through.

| # | Skill | Argument | Condition | On failure |
|---|-------|----------|-----------|------------|
| 4a | `next-issue` | `<ISSUE>` | always | WIP path (Step 5), cascade-skip dependents |
| 4b | `code-tdd` | `<ISSUE>` | always | WIP path if tests can't go green after 3 focused attempts on the same behavior; abort entirely on destructive action outside pre-approval |
| 4c | `code-review` + `architecture-review` | (current diff, implicit) | always | record findings; do not fail |
| 4d | `implement-review` | the concatenated findings from 4c, passed as pasted comments (no PR exists yet) | only if 4c produced anything blocking or any nice-to-have worth doing | abort entirely if it decides every finding is wrong-or-disagree |
| 4e | `qa` | current branch | only if diff touches frontend (templates, Alpine.js, CSS, rendering view fns) or adds/changes an API endpoint handler | if QA produces blocking findings, loop back to 4d at most once; a second loop takes this issue to WIP path |
| 4f | `create-pr` | (no arg; it reads the current branch) | always | abort entirely on unresolved rebase conflict or push failure |

After 4a, `cd ~/work/code/worktrees/com-<N>/` so the rest of the pipeline runs inside the worktree.

Between steps, update `state.json` with the current stage so a `/compact` crash can resume.

## Step 5: WIP path (soft failures only)

If Step 4b or 4e decides the issue cannot reach a clean state:

1. Commit whatever progress exists (or leave the WIP tree in-place if code-tdd already committed).
2. Invoke `create-pr` with an instruction to prefix the title with `WIP: ` and prepend this block to the body:

   ```
   ## Status: WIP - needs human attention

   Autopilot stopped at stage `<stage>` for the reason below.

   ### Reason
   <one paragraph summary + last error output>
   ```

3. Set `results[<ISSUE>] = { status: "shipped-wip", pr_url: <url>, stopped_at: "<stage>" }`.
4. Run the cascade (see below). Skip Step 6 (bot polling). Go to Step 7.

**Hard failures** (unresolved rebase conflict, push failure, destructive action) do NOT take the WIP path - they stop autopilot entirely so the user can inspect.

## Step 6: Post-PR bot comment polling (normal path only)

Parameters: window = 120s, interval = 10s, max cycles = 3.

```
pr=<PR number from create-pr>
baseline_comments = gh api repos/{o}/{r}/pulls/$pr/comments --jq '[.[].id]'
baseline_reviews  = gh api repos/{o}/{r}/pulls/$pr/reviews  --jq '[.[].id]'
deadline = now + 120s
cycles = 0

while now < deadline:
    sleep 10s
    new = current comments/reviews minus baseline, filtered to bots only
    if new is empty: continue
    cycles += 1
    if cycles > 3:
        add note "bot polling exceeded 3 cycles - see <pr_url>"
        break
    invoke Skill(implement-review, "<the bot comments, pasted>")
        # implement-review commits, rebases, and pushes with --force-with-lease
    baseline = current
    deadline = now + 120s   # give the bot a chance to re-review
```

Bot detection: `author.login` ends with `[bot]`, OR `author.type == "Bot"`, OR login is in the known set (`cursor`, `coderabbitai`, `github-actions`, `codecov-commenter`, plus the login stored in the `project_github_bot_identity` memory entry).

Human comments during the window are ignored by autopilot (they stay on the PR for the user to address after the run).

On exit, set `results[<ISSUE>] = { status: "shipped", pr_url: <url>, finished_at: <iso> }`.

## Step 7: Cascade on failure

Only runs when the issue ended as `needs-attention` or `shipped-wip`.

Walk the remaining queue. For each item still `pending` or `in-progress`, check if the failed issue is in its transitive `blocked_by` chain. If yes, set it to `skipped` with a note pointing at the failed issue. Non-dependent items keep their status.

## Step 8: Compact and self-invoke

Read state. Are there more eligible items (Step 3 rules)?

**Yes:**

1. Print: `Autopilot: finished <ISSUE> -> <pr_url>. <count> eligible issues left. Compacting and continuing.`
2. `cd ~/work`.
3. Run the built-in `/compact` command with hint: `"autopilot is running; state in tasks/autopilot/state.json; next turn invoke /autopilot --resume"`.
4. After compact, invoke `Skill(autopilot, "--resume")`. Execution re-enters at Step 1.

**No:** go to Step 10.

## Step 10: Final report

Print:

```
Autopilot finished.
  Shipped:    <n>  (PR URLs)
  WIP:        <n>  (PR URLs + stage where it stopped)
  Needs attn: <n>  (issue IDs + notes)
  Skipped:    <n>  (issue IDs - dependent on a failure)
```

Archive `tasks/autopilot/state.json` to `tasks/autopilot/state.<iso>.json` as the run log. Do not delete.

## User interrupt

At every Step 3 entry, abort if `tasks/autopilot/state.json` has top-level `"abort": true`. The user can trigger this mid-run with:

```bash
jq '. + {"abort": true}' tasks/autopilot/state.json > /tmp/s.json && mv /tmp/s.json tasks/autopilot/state.json
```

## Failure modes (summary)

| Situation | Response |
|-----------|----------|
| `code-tdd` can't green after 3 focused attempts | WIP PR + cascade-skip dependents + continue |
| QA loops back to `implement-review` twice | WIP PR + cascade-skip dependents + continue |
| `next-issue` branch conflict | mark `needs-attention`, cascade-skip, continue |
| `implement-review` disagrees with every finding | stop autopilot entirely |
| Rebase conflict in `create-pr` that can't be auto-resolved | stop autopilot entirely |
| Push failure | stop autopilot entirely |
| Bot polling > 3 cycles | ship as normal, add note, continue |
| Linear/GitHub API error | retry once after 30s, else stop |
| State file `"abort": true` | stop at next Step 3 check |

## Rules

- **Thin orchestration.** Do not re-implement downstream skill logic here. Invoke each skill via the `Skill` tool and let it run.
- **Pre-approval is the whole mechanism for silencing gates.** Do not modify existing skills.
- **Persist state before every stage transition, always before `/compact`.**
- **Run `code-review` and `architecture-review` in parallel** (two tool calls in one response).
- **Soft failure = WIP + cascade-skip. Hard failure = stop.**
- **2-minute bot poll after every non-WIP PR**, with one deadline reset per review cycle, capped at 3 cycles.
- **Do not use em-dashes.** Hyphens, commas, or parentheses only.
