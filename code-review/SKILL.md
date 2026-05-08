---
name: code-review
description: Review a PR or diff for bugs, logic errors, security issues, edge cases, test quality, and requirements alignment. It uses an agentic approach (dynamically investigate suspicious patterns) backed by a checklist for completeness. It loads project-specific learnings from codebase-learnings.json filtered by area tags.
user_invocable: true
allowed-tools: Bash(git *), Bash(gh *), Bash(jq *), Read, Grep, Glob, Agent, AskUserQuestion
argument-hint: "[PR number, branch name, or 'current' to review the current diff]"
---

# Code Review

This skill reviews a PR or diff for bugs, logic errors, security vulnerabilities, edge cases, test quality, and alignment with requirements. It uses an agentic approach: dynamically investigate suspicious patterns, follow imports, check git history, and trace dependencies. After the investigation, it runs through a checklist to ensure nothing was missed.

The output is actionable: every finding tells the coding agent (or human) exactly what is wrong and what to do about it. If you are not sure about a finding, say so explicitly in the comment.

Argument: `$ARGUMENTS`

<HARD-GATE>
Do NOT delegate to any superpowers agents or skills (superpowers:code-reviewer, superpowers:requesting-code-review, etc.). This skill is self-contained. Do all review work directly.
</HARD-GATE>

## Step 1: Load context

1. **Identify the PR or diff.** If `$ARGUMENTS` is a PR number, run `gh pr view $ARGUMENTS --json baseRefName,headRefName,title,body` and `gh pr diff $ARGUMENTS`. If it is "current" or empty, use `git diff` against the base branch. If it is a branch name, diff against main.

2. **Read the changed files list.** Run `git diff <base>..HEAD --name-only` to understand the scope.

3. **Load project learnings.** Check if `docs/codebase-learnings.json` exists (or a similar path). If it does, filter learnings by tags relevant to the changed files. For example, if the diff touches models or querysets, load learnings tagged with `orm`, `multi_tenancy`, `security`, `permissions`. Use jq to filter:
   ```bash
   cat docs/codebase-learnings.json | jq '[.[] | select(.tags | any(. == "security" or . == "orm" or . == "multi_tenancy"))]'
   ```
   Determine the relevant tags from the changed file paths:
   - Models, querysets, managers -> `orm`, `multi_tenancy`, `security`, `permissions`
   - Views, API endpoints -> `api_design`, `permissions`, `security`
   - Services -> `architecture`, `error_handling`
   - Tests -> `test_patterns`
   - Celery tasks -> `celery_async`
   - Migrations -> `database`
   - Templates, static files -> `code_style`
   - Performance-sensitive paths -> `performance`

4. **Read requirements and plan** (if available). Check for `docs/requirements/` and `docs/plans/` files related to the work being reviewed. If this PR implements a specific plan task or requirement, read them to check alignment.

5. **Read the surrounding code.** For each changed file, also read:
   - Files that import it (to understand who depends on the change)
   - Files it imports (to understand its dependencies)
   - Similar files in the same package (to check consistency)
   Use `git log --follow -5 <file>` to understand the file's recent history.

## Step 2: Agentic investigation

Before running the checklist, investigate the diff dynamically. Look at the changes with fresh eyes and follow anything suspicious:

- **Trace data flow.** If a function receives input, trace where that input comes from and where the output goes. Are there places where it could be None, empty, or an unexpected type?
- **Check boundary conditions.** If there are loops, what happens with 0 items? 1 item? The maximum expected count? If there are string operations, what about empty strings?
- **Follow the error paths.** If an exception is caught, what happens next? Is the error logged? Is the user notified? Is the system left in a consistent state?
- **Check concurrency.** If the code accesses shared state (database, cache, files), could two concurrent requests conflict? Are there race conditions?
- **Verify the contract.** If the function signature or return type changed, check all callers. If an API response shape changed, check all consumers.
- **Check git history.** Run `git log --oneline -10 <file>` for changed files. If the file was recently modified, check if this PR conflicts with or builds on that change correctly.

Flag everything suspicious. If you are not sure whether something is a bug, flag it anyway and say "this may be intentional, but..." in the comment. Let the coding agent evaluate.

**When something is hard to understand or review**, do not skip it or give it the benefit of the doubt. Instead, load more context: read the full file (not just the diff), read the files it interacts with, check git blame for recent changes, and search for similar patterns in the codebase. If after loading context you still cannot determine whether something is correct, flag it with your concern and the context you checked.

## Step 3: Structured checklist

After the agentic investigation, run through this checklist to catch anything you missed. Skip items that do not apply to the diff.

### Bugs and logic errors
- [ ] Off-by-one errors in loops, slices, ranges, pagination
- [ ] Null/None handling (missing null checks, optional fields accessed without guards)
- [ ] Type mismatches (string where int expected, list where single item expected)
- [ ] Incorrect boolean logic (inverted conditions, missing parentheses in compound expressions)
- [ ] Resource leaks (unclosed files, database connections, HTTP sessions)
- [ ] Exception handling (bare except, wrong exception type, swallowed errors)
- [ ] Race conditions (TOCTOU, concurrent access to shared state)
- [ ] Incorrect defaults (mutable default arguments, wrong fallback values)

### Security
- [ ] Input validation at system boundaries (user input, API parameters, webhook payloads)
- [ ] SQL injection (raw SQL with string interpolation, ORM filter with user-controlled kwargs)
- [ ] XSS (user content rendered without escaping in templates)
- [ ] Authorization (missing permission checks, data accessible across tenant boundaries)
- [ ] Secrets (hardcoded credentials, API keys in code, tokens logged or exposed)
- [ ] Path traversal (user-controlled file paths without sanitization)

### Test quality
- [ ] Every non-trivial behavior change has a test
- [ ] Tests test behavior, not implementation (would they break on a refactor that does not change behavior?)
- [ ] Edge cases are covered (empty input, boundary values, error paths)
- [ ] Bug fixes have a regression test
- [ ] Tests use real objects (factories, not raw `Model.objects.create()` unless the test specifically tests creation)
- [ ] Test names describe what they verify, not what they call

### Requirements alignment
- [ ] The code implements what the requirements ask for (check against `docs/requirements/` if available)
- [ ] No scope creep (features not in the requirements)
- [ ] No missing requirements (behaviors implied by the requirements but not implemented)

### Learnings alignment
- [ ] The code does not violate any loaded learnings from the project
- [ ] If a learning is relevant but the code handles it differently, flag it for discussion

## Step 4: Classify findings

For each finding, assign one of two severity levels:

- **Must fix:** Bugs, security issues, data corruption risks, missing error handling that will crash in production, test gaps for critical paths, violations of project learnings marked as security or multi_tenancy.
- **Recommendation:** Code that works but could be clearer, edge cases that are unlikely, test improvements, naming suggestions. Also use this level when you are not sure if something is a bug (and say so).

## Step 5: Produce output

### Inline comments

For each finding tied to a specific location:

```
FILE: <path>
LINE: <number>
SEVERITY: must fix | recommendation
COMMENT: <what is wrong, why it matters, and what to do about it>
```

If you are flagging something you are not sure about:

```
FILE: <path>
LINE: <number>
SEVERITY: recommendation
COMMENT: This may be intentional, but <describe the concern>. If it is intentional, consider adding a comment explaining why.
```

### Summary

1. **Findings count:** N must-fix, M recommendations
2. **Key concerns:** The 2-3 most important issues in plain language
3. **Test coverage assessment:** Are the critical paths tested? Are there gaps?
4. **Requirements alignment:** Does this implement what was asked? (Only if requirements/plan were found.)
5. **Learnings violations:** Any project-specific patterns that were violated

## Rules

- **Flag everything suspicious.** If you are not sure, flag it as a recommendation and say you are not sure. The coding agent or human will evaluate.
- **Be specific.** Every finding must include the file, line, what is wrong, and what to do.
- **Two severity levels only.** Must fix or recommendation.
- **Agentic first, checklist second.** Investigate dynamically, then verify with the checklist.
- **Load learnings by area.** Filter the learnings JSON by tags matching the changed files.
- **Check requirements.** If requirements or plan docs exist for this work, verify alignment.
- **Do not check architecture.** SOLID, dependency direction, codebase consistency, and design patterns are the architecture review's job. Focus on bugs, security, correctness, and test quality.
- **Do not use em-dashes.** Use hyphens, commas, or parentheses instead.
