---
name: implement-review
description: Use when PR review comments need to be analyzed for validity, evaluated for interest, and implemented with test-first approach where the change alters behavior
user_invocable: true
allowed-tools: Bash(*), Read, Grep, Glob, Agent, AskUserQuestion, Edit, Write
argument-hint: "[PR number, branch name, or pasted review comments]"
---

# Implement Review

This skill takes PR review feedback, evaluates each comment for technical validity, and implements the accepted changes with tests where possible. It does not blindly comply - it pushes back when a suggestion is wrong, and it includes nice-to-haves when they genuinely improve the code.

Argument: `$ARGUMENTS`

## Step 1: Load the review

`$ARGUMENTS` can be one of:

- **Empty or "current"** - find the PR for the current branch and fetch its comments
- **PR number** - fetch comments from GitHub
- **Branch name** - find the associated PR, then fetch comments
- **Pasted review comments** - use them directly

When no argument is provided (or it is "current"), detect the current branch's PR:

```bash
gh pr view --json number,title,body,baseRefName,headRefName,url
```

If no PR exists for the current branch, tell the user and stop.

For PR-based input:

1. Get PR context: `gh pr view $PR --json number,title,body,baseRefName,headRefName,url`
2. Fetch inline review comments: `gh api repos/{owner}/{repo}/pulls/{number}/comments`
3. Fetch PR-level reviews: `gh api repos/{owner}/{repo}/pulls/{number}/reviews`
4. Read the diff: `gh pr diff $PR`

Collect all comments into a single list. For each comment, note the file, line, the reviewer's suggestion, and the **comment ID** (needed for replying later).

## Step 2: Understand the context

Before evaluating any comment:

1. Read the files referenced in the review comments - not just the diff, but the full files.
2. Read files that import or are imported by the changed files (to understand callers and dependencies).
3. Check recent history: `git log --oneline -10 <file>` for each affected file.
4. Load project learnings from `docs/codebase-learnings.json` if it exists, filtered by relevant tags (use jq to filter by tags matching the changed file areas).

## Step 3: Evaluate each comment

For each review comment, answer two questions:

### Is it technically correct?

- Does the suggestion work in this codebase?
- Would it break existing functionality?
- Does it conflict with established patterns or conventions?
- Does the reviewer have full context, or are they missing something?

If you cannot easily verify whether a suggestion is correct, say so. Do not guess.

### Classify it

- **Must fix** - bugs, security issues, correctness problems, clear improvements that the code needs
- **Nice to have (implement)** - style improvements, minor refactors, edge case handling, or robustness improvements that genuinely make the code better
- **Nice to have (skip)** - suggestions that are technically fine but do not add enough value to justify the change (explain why)
- **Disagree** - technically incorrect, would break things, violates codebase patterns, or solves a problem that does not exist

For "nice to have" items, lean toward implementing. If the suggestion improves readability, robustness, or maintainability, it is worth doing.

### Present the evaluation

Before implementing anything, present the full evaluation:

```
MUST FIX:
1. [file:line] <what to change and why you agree>

NICE TO HAVE (will implement):
2. [file:line] <what to change and why it is worth doing>

NICE TO HAVE (will skip):
3. [file:line] <what was suggested and why it is not worth doing>

DISAGREE:
4. [file:line] <what was suggested, why you disagree, and what you checked>
```

Wait for the user to approve, adjust, or override before proceeding.

## Step 4: Implement with tests

Work through the accepted changes one at a time. For each change:

### Decide: testable or not?

- **Testable:** logic changes, bug fixes, new validation, behavior changes, edge case handling, error handling changes
- **Not testable:** renaming, comment updates, import reordering, formatting, type annotation additions, moving code without changing behavior

### For testable changes: RED-GREEN-REFACTOR

1. **RED** - Write a test that captures the expected behavior after the change. Run it. Confirm it fails for the right reason (the behavior is not implemented yet), not because of a typo or import error.

2. **GREEN** - Implement the minimal change to make the test pass. Do not fix other things.

3. **REFACTOR** - Clean up if needed. Run tests again to confirm everything is still green.

Add a traceability comment on the test:

```python
# Review: <brief description of what the reviewer flagged>
def test_<descriptive_name>():
    ...
```

### For non-testable changes

Implement directly. These are mechanical changes that do not alter behavior.

### After each change

Run the related tests to confirm nothing broke. Do not batch multiple changes before running tests.

## Step 5: Draft replies

For each comment, draft a reply based on the commenter and the outcome:

### Bot comments (automated reviewers like Cursor Bugbot, CodeRabbit, etc.)

- **Implemented:** "Fixed in <commit>. <one-line description of what changed>."
- **Disagree (nonsensical or wrong):** No reply needed. Just resolve the thread silently.
- **Disagree or skip (valid point but not implementing):** Reply with a brief explanation of why it is not being addressed (e.g., "Valid concern but out of scope for this PR" or "This is intentional because <reason>").

### Human comments

- **Implemented:** "Fixed. <one-line description of what changed>." or "Fixed - also added a test for this."
- **Disagree or skip:** Reply respectfully with technical reasoning. Explain what you checked and why you see it differently. End with an opening for discussion (e.g., "Let me know if I am missing context" or "Happy to revisit if you see it differently").

No performative language. No "Great catch!", "You're right!", or "Thanks for flagging!". Be direct but respectful, especially with humans.

Present the replies to the user for review before posting them.

## Step 6: Present results

Summarize:

- Comments addressed vs. skipped vs. pushed back on
- Files changed
- Tests added or modified
- Any concerns or items that need further discussion

Wait for the user to review before committing.

**After the commit lands, Steps 7 and 8 are MANDATORY — do not consider the skill complete until both are done.** If the user pivots to a new task (another skill, a deploy, a code review), complete the pivot in whatever way the user wants, then return here and finish Step 7 and Step 8 before reporting done. Do not ask permission to finish them; the user already approved the implementation in Step 3, and posting replies + resolving threads is the baseline expected behavior for any review-implementation flow.

## Step 7: Rebase onto the base branch

After all changes are committed, rebase the branch onto the PR's base branch (usually `main`) to keep the history clean:

1. Fetch the latest base branch: `git fetch origin <base>`
2. Rebase: `git rebase origin/<base>`
3. If there are conflicts, resolve them preserving the PR's changes while incorporating upstream updates.
4. Force-push with lease: `git push --force-with-lease`

This ensures the PR stays up to date and avoids merge commits. Use `--force-with-lease` (never `--force`) to avoid overwriting changes someone else may have pushed.

## Step 8: Post replies and resolve threads

After the user approves, post the replies and resolve comment threads on GitHub.

### Post replies

For each comment, decide whether to reply based on the resolution rules from Step 5:

- **Implemented:** Always reply (bot or human).
- **Bot, disagree (nonsensical):** No reply. Just resolve silently.
- **Bot, skip (valid but not implementing):** Reply with brief reason.
- **Human, disagree or skip:** Reply respectfully with reasoning.

Post replies using:

```bash
gh api repos/{owner}/{repo}/pulls/{pr_number}/comments/{comment_id}/replies -X POST -f body="<reply>"
```

### Resolve threads

After replying, resolve all threads that are done (implemented, or bot-disagree). First, fetch the thread IDs:

```bash
gh api graphql -f query='
{
  repository(owner: "{owner}", name: "{repo}") {
    pullRequest(number: {pr_number}) {
      reviewThreads(first: 50) {
        nodes {
          id
          isResolved
          comments(first: 1) {
            nodes { databaseId }
          }
        }
      }
    }
  }
}'
```

Match each thread to its comment ID, then resolve it:

```bash
gh api graphql -f query='
mutation {
  resolveReviewThread(input: {threadId: "<thread_id>"}) {
    thread { isResolved }
  }
}'
```

**When to resolve:**

| Commenter | Outcome | Reply? | Resolve? |
|-----------|---------|--------|----------|
| Bot | Implemented | Yes | Yes |
| Bot | Disagree (nonsensical) | No | Yes |
| Bot | Skip (valid point) | Yes | Yes |
| Human | Implemented | Yes | Yes |
| Human | Disagree or skip | Yes | No (leave open for discussion) |

Note: GitHub auto-resolves threads when the commented lines change in a new push. If threads are already resolved after the force-push, skip the resolve step for those and just post the reply.

## Common rationalizations

| Excuse | Reality |
|--------|---------|
| "Reviewer is senior, so they must be right" | Seniority does not override codebase reality. Verify. |
| "Too small to test" | If it changes behavior, test it. It takes 30 seconds. |
| "I will test after implementing all changes" | Test each change individually. Batching hides regressions. |
| "The reviewer probably knows more context" | Maybe. Or maybe they missed something. Check. |
| "Disagreeing is confrontational" | Technical pushback with evidence is professional. Blind compliance is not. |
| "Nice to have means skip" | Nice to have means evaluate. If it improves the code, do it. |
| "I will just implement everything to be safe" | Implementing wrong suggestions introduces bugs. Evaluate first. |
| "Let me batch the replies" | Reply per comment, one at a time. Each deserves its own reasoning. |

## Rules

- **Evaluate before implementing.** Every comment gets technical scrutiny, regardless of who wrote it.
- **Present evaluation before acting.** The user decides what gets implemented.
- **Test when possible.** If the change alters behavior, write a test first.
- **One change at a time.** Implement, test, confirm - then move to the next.
- **Push back with evidence.** If a suggestion is wrong, say so and explain what you checked.
- **Lean toward nice-to-haves.** If a suggestion improves the code, implement it.
- **No performative language.** State facts, not feelings.
- **Do not commit on your own.** Present the work, wait for the user to review.
- **Rebase onto base branch.** After committing, rebase onto the PR's base branch and force-push with lease.
- **Always close the loop.** The skill is NOT done until every evaluated comment has either a posted reply or a resolved thread (see the completion checklist below). Replies and thread resolution are not optional cleanup - they are the deliverable.
- **Do not use em-dashes.** Use hyphens, commas, or parentheses instead.

## Completion checklist (run before reporting done)

The skill is complete only when every item below is true. Run through this list explicitly at the end. If the user redirects you to another task mid-flow (another skill, a deploy, a code review), do the redirect, then come back and finish this list before declaring the overall task done.

- [ ] Every "must-fix" and accepted "nice-to-have" from the evaluation is implemented.
- [ ] Every testable change has a test with a `# Review: <reason>` traceability comment, and the tests pass.
- [ ] All changes committed on the PR branch.
- [ ] Branch rebased onto the base branch and pushed with `--force-with-lease`.
- [ ] Every comment has a reply, EXCEPT bot-disagree-nonsensical (silent resolve is fine for those). Check with `gh api repos/{owner}/{repo}/pulls/{pr}/comments` and diff against the comment IDs you evaluated in Step 3.
- [ ] Every thread that is done is resolved via the GraphQL `resolveReviewThread` mutation, except human-disagree/skip threads (left open for human discussion). Verify with the `reviewThreads` GraphQL query and check `isResolved` is true for each target thread.
- [ ] Summary reported to the user: what was implemented, what was skipped, what is left open for discussion, and confirmation that replies and resolves are posted.

If you are unsure whether you completed a step, re-run the verification query. Do not assume. "I think I replied to all of them" is the failure mode this checklist exists to prevent.
