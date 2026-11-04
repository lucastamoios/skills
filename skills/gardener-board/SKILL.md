---
name: gardener-board
description: Reconcile the configured task board with shipped outcomes, using pull requests, issue state and recent sessions. Use for board maintenance rather than starting or stopping current work.
user_invocable: true
allowed-tools: Read, Grep, Glob, Bash(python3 *), Bash(gh *), Bash(git *), Bash(jq *), Bash(find *), Bash(grep *), mcp__linear-server__get_issue, mcp__linear-server__list_issues
---

# Gardener: Board

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Tasks get finished outside the board all the time: a PR merges while the task
sits in Review, an agent session completes the work and nobody flips the lane,
a To Do item gets absorbed into a bigger branch. This arm closes that gap. It
looks at every open task, hunts for evidence that the work already happened
(PRs, Linear, session transcripts), and keeps the board honest: verifiably
finished tasks are closed, ambiguous ones are surfaced, nothing is deleted.

This is one arm of the gardener family. It only reconciles the board. Filing
new captures is [[gardener-inbox]]; mining transcripts for knowledge is
[[gardener-transcripts]]; the bare [[gardener]] skill orchestrates.

## Step 1: Pull the open board

List tasks per lane with `profile.paths.scripts/tasks.py list --lane <name>` for:
`To Do, Today, In Progress, Review, Blocked`. Skip Done and
Delegated. Scan Scheduled and Maybe too, but tasks there are deliberate
parking: they only ever get suggestions, never an automatic close.

For each task, run `tasks.py get --id <filename-slug>` and extract its identifiers. Identifiers to
collect:

- `git_url` (a pull request, issue, or branch URL)
- `linear_url` or a `<PREFIX>-####` reference
- `<PREFIX>-####` Linear references in title or description
- explicit PR or issue URLs in the description
- 2-3 distinctive title keywords as a fallback search term

If `tasks.py` fails, report it plainly and stop. Do not guess at board state.

## Step 2: Gather completion evidence

Work through the sources from strongest to weakest. Stop early per task once
the verdict is clear.

**PRs (conclusive when merged).** If the task points at a PR (`gitUrl` or a URL
in the description), run `gh pr view <url> --json state,mergedAt,url,title`.
For a `<PREFIX>-####` reference without a direct URL, search
`gh pr list --repo profile.work.github_repository --search "<issue-key>" --state all --json number,state,mergedAt,headRefName,url`
and match on the `profile.work.branch_prefix####` branch convention. Read the states as:

- **Merged**: the work shipped. Conclusive.
- **Open**: the work is in flight, not finished. If the task sits in a lane
  earlier than Review (To Do, Today, In Progress, Agents), suggest moving it to
  Review instead of closing it.
- **Closed without merge**: not completion. The task may be abandoned or
  superseded; flag it as a suggestion, never auto-close on this.

**Linear (conclusive when Done).** When the task references `<PREFIX>-####` and the
Linear MCP is available, fetch the issue and check its state. An issue in a
completed state (Done, Canceled counts as resolved-elsewhere) is conclusive for
closing the task; cite the issue state in the note.

**Sessions (suggestive, never conclusive alone).** Search recent transcripts
for the task's identifiers:

- Claude Code: `~/.claude/projects/*/*.jsonl`
- Codex: `~/.codex/sessions/*/*/*/*.jsonl`

Bound the sweep with `find ... -mtime -21` so it stays cheap, and grep for the
COM reference, PR number, or title keywords. For each hit, read the tail of the
session (the last few hundred lines) and judge what actually happened there. A
session that merged the PR or explicitly completed and verified the work
supports closing; a session that merely worked on it does not. Session evidence
alone is a suggestion: sessions end optimistically, and "I opened the PR" means
Review, not Done.

## Step 3: Decide per task

Sort every finding into one of two tiers:

- **Conclusive**: the task's own PR merged, or its Linear issue reached a
  completed state, or (for non-code tasks) the deliverable verifiably exists
  where the task said it would. These get closed.
- **Suggestive**: a session claims completion but nothing verifiable backs it,
  a PR is open (lane fix, not a close), a PR was closed without merging, or the
  work seems superseded. These get surfaced, not applied.

## Step 4: Act

**Closing a task** is always two calls, in this order, so the evidence lands
before the lane flips:

```
profile.paths.scripts/tasks.py note --id <filename-slug> --text "Closed by gardener: PR <url> merged <date>"
profile.paths.scripts/tasks.py move --id <filename-slug> --lane Done
```

The note must cite the concrete evidence (PR URL and merge date, Linear issue
and state, or the artifact checked). Never close without a note, and never
write a note claiming evidence you did not verify.

**Interactive runs**: present one numbered list covering both tiers, each line
with the task id, title, verdict, and evidence. Apply the conclusive closes
after showing them (the user can strike items by number before you run the
commands), and apply suggestive items only on his explicit confirmation.

**Headless runs**: apply conclusive closes directly; that is the point of this
arm. Append every suggestive finding to `profile.paths.brain/pending.yml` with the task id,
evidence, and proposed action, then commit that staging like the other arms do
(signed, no Co-Authored-By, no connector dashes).

## Rules

- Never delete a task and never edit its title or description; this arm only
  appends notes and moves lanes.
- Merged-PR and Linear-Done evidence must come from a live `gh` or MCP call in
  this run, not from memory or from what a transcript claims.
- One task can match several sources; the strongest one decides the tier.
- Degrade gracefully: if `gh` is unauthenticated or Linear is unreachable,
  downgrade the affected tasks to suggestive rather than skipping them silently.
- No em-dashes or connector dashes in notes or output.
