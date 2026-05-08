# Next Issue

Pick the next unblocked Linear issue assigned to you, create a branch and worktree for it, and get ready to work.

Argument: `<epic-id or empty>`

## Step 1: Find the next issue

1. If `<epic-id>` is provided, list issues under that epic. Otherwise, list all backlog issues assigned to "me".

```
list_issues(assignee: "me", state: "backlog", parentId: "<epic-id if provided>", orderBy: "createdAt")
```

2. For each issue, fetch it with `includeRelations: true` to check its `blockedBy` relations.

3. **Determine which issues are unblocked.** An issue is unblocked if:
   - It has no `blockedBy` relations, OR
   - All its blockers are in the current branch stack (i.e., there is a local branch `<username>/<prefix>-<number>` for each blocker). Check with `git branch --list '<username>/<prefix>-*'`.

4. If no unblocked issues are found, tell the user and stop.

5. If multiple unblocked issues exist, pick the one with the lowest issue number (earliest created). Present it to the user for confirmation before proceeding.

## Step 2: Determine the base branch

Ask the user: "Should I branch from the current branch (`<current-branch>`) or from another branch?"

If the user says the current branch, use it. If they specify another, use that.

If the current worktree is inside your worktrees directory (e.g., `~/code/worktrees/`), extract the current branch name from git automatically and suggest it as the default.

## Step 3: Create branch and worktree

1. Extract the issue number from the identifier (e.g., `4313` from `<TEAM>-4313`).
2. Create the worktree (replace `$WORKTREES_DIR` with your conventional worktrees directory):

```bash
git worktree add $WORKTREES_DIR/<prefix>-<number> -b <username>/<prefix>-<number> <base-branch>
```

3. **(Optional) Copy a workspace file** if your repo uses a multi-root editor workspace (e.g., a Cursor or VS Code `.code-workspace` file at the repo root):

```bash
cp <repo>/<repo>.code-workspace $WORKTREES_DIR/<prefix>-<number>/<repo>.code-workspace
```

4. **Install dependencies** so the worktree is ready to use. If your repo is a monorepo with a root environment plus per-project environments, sync each one:

```bash
cd $WORKTREES_DIR/<prefix>-<number> && <package-manager> sync
# For each sub-project that has its own environment:
cd $WORKTREES_DIR/<prefix>-<number>/projects/<sub-project> && <package-manager> sync
```

5. **(Optional) Copy editor and type-checker config** from the main repo if they are gitignored (e.g., `.vscode/settings.json`, `pyrightconfig.json`). Each worktree needs its own copies because gitignored files are not carried over:

```bash
mkdir -p $WORKTREES_DIR/<prefix>-<number>/.vscode
cp <repo>/.vscode/settings.json $WORKTREES_DIR/<prefix>-<number>/.vscode/settings.json
# Repeat for pyrightconfig.json, sub-project .vscode dirs, etc., as needed.
```

6. Verify it was created:

```bash
cd $WORKTREES_DIR/<prefix>-<number> && git log --oneline -3
```

## Step 4: Report

Print:
- The issue identifier, title, and URL
- The branch name and worktree path
- A brief summary of what the issue requires (from its title and first few lines of description)

## Rules

- Always confirm the issue with the user before creating the branch.
- If the branch `<username>/<prefix>-<number>` already exists, tell the user and ask what to do (use existing, or pick a different issue).
- Do not start implementation. This skill only sets up the workspace.
- Do not use em-dashes. Use hyphens, commas, or parentheses instead.
