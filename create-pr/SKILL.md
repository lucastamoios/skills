---
name: create-pr
description: Create or update a GitHub PR for the current branch. It handles branch creation from main, rebases the full branch chain up to main, pushes with --force-with-lease, and generates a PR with a smart title and description focused on business rules and architecture changes. It can also screenshot the affected UI if the change touches frontend code.
user_invocable: true
allowed-tools: Bash(git *), Bash(gh *), Bash(.claude/skills/create-pr/*), Bash(npx playwright *), Bash(just *), Bash(docker *), Bash(curl *), Read, Grep, Glob, Agent, AskUserQuestion, mcp__linear-server__authenticate
argument-hint: "[<TEAM>-123 (optional Linear ticket number, only when on main)]"
---

# Create PR

This skill creates or updates a GitHub PR for the current branch. If you are on main, it creates a feature branch first. It handles the full rebase chain, push, and PR creation with a description focused on what deeply changed.

Scripts live in `.claude/skills/create-pr/`:
- `build-chain.sh` discovers the branch chain from the current branch to main (JSON output).
- `rebase-branch.sh <branch> <base>` rebases a single branch onto its base, then pushes it.

Argument: `$ARGUMENTS`

## Step 0: Detect the current state

```bash
CURRENT_BRANCH=$(git branch --show-current)
```

- If you are on `main`, go to **Step 1**.
- Otherwise, skip to **Step 2**.

## Step 1: Branch creation (only from main)

You need to create a new branch with the pattern `<username>/<prefix>-<ticket-number>` (where `<prefix>` is the lowercased Linear team key).

1. **Get the ticket number:**
   - If `$ARGUMENTS` contains a ticket number (e.g., `<TEAM>-123`), extract the number from it.
   - If no argument was provided, use the Linear MCP tools to fetch the user's currently assigned tickets. Present them to the user and let them pick one.

2. **Create the branch:**
   - Check if `<username>/<prefix>-<number>` already exists locally or on the remote (`git branch -a | grep <username>/<prefix>-<number>`).
   - If it does not exist, run `git checkout -b <username>/<prefix>-<number>`.
   - If it already exists, ask the user for a short suffix, then run `git checkout -b <username>/<prefix>-<number>-<suffix>`.

3. **Stop here.** Tell the user which branch was created. They will make commits and invoke the skill again later.

## Step 2: Check for an existing PR

```bash
gh pr view --json number,url,title,state,baseRefName 2>/dev/null
```

- **If a PR exists and it is open:** Ask the user whether they want to "update it (re-push and update the description)" or "skip".
  - If they choose update, continue to Step 3 and then update the PR in Step 6.
  - If they choose skip, stop.
- **If a PR exists but it is closed or merged:** Tell the user and stop.
- **If no PR exists:** Continue to Step 3.

## Step 3: Determine the base branch and verify commits

### 3a: Detect stacked PRs

The correct PR base is not always `main`. If the current branch is part of a stack (its commits build on top of another feature branch), the PR base should be the parent branch in the stack, not `main`.

Use this algorithm to find the correct base:

1. **If an existing PR was found in Step 2**, use its `baseRefName` as the base. It was already set correctly (or the user explicitly chose it).

2. **Otherwise, detect the stack.** List all local branches that share the same naming pattern (e.g., `<username>/<prefix>-*` for a branch named `<username>/<prefix>-4315`). For each candidate branch, check whether its tip commit message appears in the current branch's history:

   ```bash
   # Get all sibling branches (same prefix pattern)
   CURRENT_BRANCH=$(git branch --show-current)
   PREFIX=$(echo "$CURRENT_BRANCH" | sed 's/[0-9]*$//')  # e.g., "<username>/<prefix>-"
   SIBLINGS=$(git branch --list "${PREFIX}*" | grep -v "^\*" | sed 's/^[ +]*//')

   # For each sibling, check if its tip is in our history (by commit message, since rebases change SHAs)
   for branch in $SIBLINGS; do
     TIP_MSG=$(git log --oneline -1 "$branch" --format="%s")
     # Check if this message appears in our history between main and HEAD
     if git log main..HEAD --oneline --format="%s" | grep -qF "$TIP_MSG"; then
       # This branch's tip is in our history - it is a potential parent
       # Record it with its position (commit count from HEAD)
       POSITION=$(git log main..HEAD --oneline --format="%s" | grep -nF "$TIP_MSG" | tail -1 | cut -d: -f1)
       echo "$branch $POSITION"
     fi
   done
   ```

   The branch with the **lowest position number** (closest to HEAD) is the immediate parent. If no sibling branch's tip is found in the history, the base is `main`.

3. **Announce the detected base.** Print: "Detected stack: base is `<base_branch>`" (or "Base: main (no stack detected)"). Do not ask for confirmation - just proceed.

### 3b: Verify there are commits

```bash
git log <base>..HEAD --oneline
```

If there are no commits ahead, tell the user "There is nothing to PR because there are no commits ahead of <base>" and stop.

## Step 4: Rebase the chain and push

### 4a: Build the chain

```bash
.claude/skills/create-pr/build-chain.sh
```

This outputs a JSON array of `{"branch", "base"}` pairs, ordered from the branch closest to main down to the current branch.

### 4b: Rebase and push each branch

Loop through the chain. For each entry, run:

```bash
.claude/skills/create-pr/rebase-branch.sh <branch> <base>
```

Handle the exit codes:

- **Exit 0 (success):** Move to the next branch.
- **Exit 1 (conflict):** The rebase is left in progress. Parse the JSON output to get the list of conflicted files. Read those files, understand the conflict markers, and attempt to resolve them. After resolving all files, run `git add` on them and then `git rebase --continue`. If you cannot resolve a conflict, run `git rebase --abort`, ask the user for help via AskUserQuestion, and stop the entire flow.
- **Exit 2 (push failure):** Stop immediately. Tell the user which branch failed and include the error from the JSON output. Do not continue and do not retry.
- **Exit 3 (diverged from origin):** Stop immediately. The local branch and `origin/<branch>` have both advanced with different commits, so a force-push would drop remote work. The JSON output includes the local and remote SHAs. Tell the user, show both SHAs, and ask via AskUserQuestion whether to (a) reset local to origin and lose local-only commits, (b) rebase local onto origin/<branch> first to combine, or (c) abort. Do not pick an option yourself.

After the loop completes, make sure you are back on the original branch by running `git checkout <CURRENT_BRANCH>`.

## Step 5: Capture UI evidence (screenshot or video)

Check whether the diff touches frontend-visible code (Django templates, Alpine.js widgets, CSS, or view functions that render templates). If it does not, skip this step entirely.

If it does, decide which artifact suits the change:
- **Screenshot** for a single static state (a layout fix, a new page, a single rendering change). Use the screenshot path below.
- **Video walkthrough** for an interactive flow, a before/after comparison, or a bug reproduction. **Stop and tell the user**: "this PR would benefit from a walkthrough video; run `/record-pr-video <ISSUE-ID>` first, then re-invoke `/create-pr`." Do not record the video yourself - that skill owns the recording standard, the Playwright scripting, and the encoding. When `/record-pr-video` has run, its artifacts will be at `~/work/tasks/<ISSUE-ID>/` (mp4 + gif). Reference them in the description in Step 6.

If you cannot tell which is right, ask the user via AskUserQuestion.

### Screenshot path

1. **Check if the dev server is running** by curling `$DEV_URL` (allow insecure certificates). If it is not running, start it with `just dev-start` from the project's web-client directory and wait for it to be reachable.

2. **Infer the URL** to screenshot by looking at the changed files. For example, if a template in `<some-app>/` was modified, navigate to the relevant page. If you cannot infer the URL, ask the user which URL to visit.

3. **Take a screenshot** using Playwright:
   ```bash
   npx playwright screenshot --browser chromium "$DEV_URL/<inferred-path>" /tmp/pr-screenshot.png
   ```

4. **Upload the screenshot** and get a URL you can embed in the PR description. Use `gh` to upload it as part of the PR body (you can include it as a Markdown image in the description).

## Step 6: Create or update the PR

### Generate the title

Read the diff between the base branch and the current branch:

```bash
git diff <base>...<CURRENT_BRANCH>
```

Generate a short title (under 70 characters) that captures what the change does. Use conventional commit style (e.g., "feat: add user search endpoint"). Do not ask for approval.

### Generate the description

Read the diff and the commits:

```bash
git diff <base>...<CURRENT_BRANCH>
git log <base>..HEAD --oneline
```

Write the description using exactly this structure — only these two sections, nothing else:

```
## Business Rules

<bulleted list where each item starts with "Added:", "Changed:", or "Removed:">
<if there are no business rule changes, write "No business rule changes.">

## Architecture

<bulleted list where each item states what changed and how>
<if there are no architectural changes, write "No architectural changes.">
```

Do not add a summary paragraph, a "what changed" preamble, a screenshot block, or a walkthrough block in the description itself. The title carries the headline; the diff carries the file-level detail. If a screenshot or video walkthrough was captured (Step 5 or via `/record-pr-video`), upload it as a PR comment instead of putting it in the description — keeps the description focused on the two sections reviewers care about.

Focus on what is deeply being changed, not surface-level file edits. Think about what a reviewer needs to understand about the intent and impact of this change.

### Create or update the PR

- **For a new PR:**
  ```bash
  gh pr create --title "<title>" --base "<base_branch>" --body "<description>" --assignee "@me"
  ```
- **For an existing PR:**
  ```bash
  gh pr edit --title "<title>" --body "<description>"
  ```

## Step 7: Report

Print the PR URL and a one-line confirmation. Nothing more.

## Rules

- A push failure is a hard stop. Do not retry and do not try workarounds. Just tell the user and stop.
- Conflict resolution is best-effort. Try to resolve conflicts, but if you cannot, abort the rebase and ask the user.
- Never create draft PRs. They should always be ready for review.
- Always assign yourself with `--assignee "@me"`.
- Do not use em-dashes. Use hyphens, commas, or parentheses instead.
- When on main, only create the branch and stop. Do not proceed to PR creation.
- If there are no commits ahead of the base, there is nothing to PR. Stop and tell the user.
