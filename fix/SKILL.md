---
name: fix
description: Use when a bug is reported from any source - Sentry alert, Linear issue, pasted stacktrace, or plain description. Diagnoses root cause with three-level cause analysis, writes a regression test, and fixes using RED-GREEN-REFACTOR.
user_invocable: true
allowed-tools: Bash(*), Read, Grep, Glob, Agent, AskUserQuestion, Edit, Write, mcp__linear-server__get_issue, mcp__linear-server__save_issue, mcp__linear-server__list_issues, mcp__linear-server__search_documentation
argument-hint: "[Sentry URL, Linear issue (<TEAM>-123), pasted stacktrace, or plain description of the bug]"
---

# Fix

This skill takes a bug report from any source, systematically diagnoses the root cause, writes a failing regression test, and fixes it.

Argument: `$ARGUMENTS`

<HARD-GATE>
No fix without a failing test first. If you wrote fix code before the test, delete it and start over. No exceptions.
</HARD-GATE>

## Step 1: Parse the input

`$ARGUMENTS` can contain any combination of:

- **Sentry issue URL** - fetch full details via Sentry MCP (stacktrace, error message, breadcrumbs, tags, environment, release, frequency, affected user count)
- **Linear issue identifier** (e.g., `<TEAM>-123`) - fetch issue details via Linear MCP
- **Pasted stacktrace** - extract file paths, line numbers, error message
- **Plain text description** - use as starting context

Identify which sources are present and fetch from all of them. Do not limit yourself to one source.

### Sentry-specific: claim the issue

If the input includes a Sentry issue, assign it to the current user immediately so others know it is being worked on.

## Step 2: Gather context

Now that you know what the bug is about, explore:

1. **Code referenced in the stacktrace** - read the files, understand what they do
2. **Related tests** - find existing tests for the affected code
3. **Recent commits** - check git log for recent changes to the affected files
4. **Requirements and design docs** - read any docs in `docs/requirements/` and `docs/design/` that relate to the affected area
5. **Similar Sentry errors** (only when a Sentry URL was provided) - search for related errors that might share the same root cause. Note them for later.

Be greedy. Pull everything available before starting diagnosis.

## Step 3: Three-level cause analysis

Diagnose the bug by identifying three levels of cause. Do not skip to fixing.

### a) Direct cause

The immediate technical failure. What line of code breaks? What value is wrong? What exception is thrown? This is what the stacktrace shows you.

### b) Root cause

Keep asking "why" until you hit something systemic:

- Why is the value null? Because the caller does not validate input.
- Why does the caller not validate? Because the interface contract is ambiguous.
- Why is the contract ambiguous? Because the design spec does not define error behavior.

Stop when you reach a design flaw, a missing invariant, an ambiguous interface, or a wrong assumption. This is what you will fix.

### c) Contributing factors

What allowed the bug to exist in the first place?

- Missing lint rule that would catch this pattern
- No test coverage for this path
- Ambiguous type (using `Any` or `Optional` without enforcement)
- Contradictions or gaps in requirements or design docs

These drive the preventive measures after the fix.

### Check docs for misalignment

Read any requirements and design docs for the affected area. Look for:

- Contradictions between docs and actual code behavior
- Gaps in requirements that left the behavior undefined
- Design decisions that made this class of bug possible

Flag anything you find - you will fix these in Step 7.

### Present the diagnosis

Before writing any code, present the three-level cause analysis to the user:

```
Direct cause: <what breaks>
Root cause: <why it breaks, the systemic reason>
Contributing factors: <what allowed it to exist>
```

## Step 4: Size gate

Estimate the fix size. If it would require more than 800 lines of code changes:

1. Stop.
2. Explain why the fix is large.
3. Create Linear issues to break the work into smaller pieces.
4. Do not implement the fix directly.

If the fix is within bounds, proceed.

## Step 5: Write the failing test (RED)

Write a test that reproduces the exact bug in its specific context. The same stacktrace can come from many different causes - your test must reproduce THIS specific failure, not just any failure that produces the same error message.

### Choose the right test type

The test type depends on where the bug lives:

- **Unit test** - bug is in isolated logic within a single function or class, no cross-layer dependencies
- **Integration test** - bug spans multiple layers (e.g., a view calls a service that queries a model incorrectly)
- **BDD scenario** - bug represents a violation of user-facing behavior described in requirements

Pick the type that gives you the most meaningful assertion for this specific bug. Do not default to unit tests.

### Write and verify

1. Write the test. Add a traceability comment:

```python
# Regression test: <brief description of the bug>
# Direct cause: <what was failing>
# Root cause: <why it was failing>
def test_<descriptive_name>():
    ...
```

2. Run the test. Confirm it fails.
3. Confirm it fails for the expected reason (the bug), not because of a typo, import error, or unrelated issue.

If the test passes immediately, your test does not reproduce the bug. Fix the test.
If the test errors instead of failing, fix the error and re-run.

## Step 6: Fix the bug (GREEN)

Write the minimal code to make the test pass. Nothing more.

Do not:
- Add features the test does not require
- Refactor surrounding code
- Add error handling for unrelated cases
- Fix other bugs you noticed along the way

Run the test. Confirm it passes. Run related tests to confirm nothing else broke.

## Step 7: Refactor and prevent

### Refactor

Review the code you wrote and the code around it:

1. **Code quality** - remove duplication, improve naming
2. **Architectural alignment** - does your fix match the patterns in the codebase?
3. **Codebase consistency** - follow existing conventions

Run tests again after refactoring.

### Preventive measures

Based on the contributing factors from Step 3c:

- **Linting rule** - if a lint rule or static analysis check could catch this pattern, add it
- **Type annotation** - if a stricter type would prevent this, add it
- **Doc updates** - if the diagnosis revealed contradictions or gaps in requirements or design docs, update them now

### Fix similar Sentry errors

If you found similar errors in Step 2 and the fix applies to them:

- Resolve those errors in Sentry
- If manual review is needed (the fix might not apply), flag them with a comment instead

## Step 8: Present results

Present the fix to the user:

- What was the bug (three-level cause analysis summary)
- What test was written and what type
- What code was changed
- What preventive measures were added
- Whether any docs were updated
- Whether any similar Sentry errors were resolved

### Sentry-specific: close the loop

If the input was a Sentry issue:

1. Mark the issue as resolved in Sentry
2. Add a comment with a summary of the root cause and the fix

## Red flags - STOP and return to Step 3

If you catch yourself thinking:

- "I know what the fix is, let me just do it" - you have not diagnosed yet
- "The test is hard to write" - the design might be the problem
- "I will test after" - delete the fix, write the test first
- "This is too simple to need a test" - simple bugs need regression tests too
- "Let me fix this and that other thing too" - one fix at a time
- "The stacktrace makes it obvious" - obvious direct cause does not mean you found the root cause

**All of these mean: STOP. Return to diagnosis.**

## Common rationalizations

| Excuse | Reality |
|--------|---------|
| "Obvious from the stacktrace" | Stacktrace shows direct cause, not root cause. Diagnose deeper. |
| "Too simple to need a test" | Simple bugs recur. The test takes 30 seconds. |
| "I will test after the fix" | Tests written after prove nothing - you never saw them catch the bug. |
| "Fix is just one line" | One-line fixes still need regression tests. The line count does not matter. |
| "Similar enough test already exists" | If the existing test did not catch this bug, it is not similar enough. |
| "The contributing factors are not worth addressing" | Contributing factors are why the bug existed. Skip them and the next bug is already waiting. |

## Rules

- **No fix without a failing test first.** If you wrote fix code before the test, delete it.
- **Three-level cause analysis before any code.** Direct cause, root cause, contributing factors.
- **One fix at a time.** Do not bundle fixes for other bugs you noticed.
- **Choose the right test type.** Unit, integration, or BDD - whichever gives the most meaningful assertion.
- **Size gate at 800 LOC.** If the fix is larger, create Linear issues instead.
- **Sentry lifecycle.** Assign at start, resolve and comment at end.
- **Preventive measures are not optional.** Address contributing factors.
- **Update docs when they contributed to the bug.** Requirements and design docs that are wrong or incomplete get fixed.
- **Do not use em-dashes.** Use hyphens, commas, or parentheses instead.
