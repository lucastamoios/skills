---
name: fix
description: Use when a bug is reported from any source - Sentry alert, Linear issue, pasted stacktrace, or plain description. Diagnoses root cause with three-level cause analysis, writes a regression test, and fixes using RED-GREEN-REFACTOR.
user_invocable: true
allowed-tools: Bash(*), Read, Grep, Glob, Agent, AskUserQuestion, Edit, Write, mcp__linear-server__get_issue, mcp__linear-server__save_issue, mcp__linear-server__list_issues, mcp__linear-server__search_documentation, mcp__sentry
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

If the input includes a Sentry issue, offer to assign it to the user so others know it is being worked on, and wait for his yes before assigning (changing Sentry state is visible to the team; see the guardrails on outbound actions).

## Step 2: Gather context

Now that you know what the bug is about, explore:

1. **Code referenced in the stacktrace** - read the files, understand what they do
2. **Related tests** - find existing tests for the affected code
3. **Recent commits** - check git log for recent changes to the affected files
4. **Requirements and design docs** - read any docs in `docs/requirements/` and `docs/design/` that relate to the affected area
5. **Similar Sentry errors** (only when a Sentry URL was provided) - search for related errors that might share the same root cause. Note them for later.
6. **Migration history for existing data** - when the bug affects records created before the current code, inspect the schema and data migrations that created, renamed, transformed, or backfilled the relevant fields. Do not infer historical record shape from the current model alone.

Gather the evidence needed to explain this failure. Use an early reproduction when it helps distinguish causes, inspect state, or test an assumption. Otherwise, begin the cause analysis from the available code, logs, and history. Revisit either step as evidence changes.

### Reproduction tools and environments

Use local tests, HTTP scripts, browser automation, or replay harnesses against local services and sanitized captured inputs. Choose the smallest setup that exercises the relevant causal path. Diagnostic scripts and tests may be written before the diagnosis is complete; production fixes wait for the root-cause check below.

If the bug cannot be reproduced locally, explain what you tried and the missing condition. Ask the user to approve a UAT attempt, naming the environment, scenario, exact commands or browser actions, and any data changes. Wait for approval before running it, and respect the separate SSH approval rule. A local blocker does not authorize UAT or production access. Until the necessary check can run, report the cause as unverified rather than claiming a confirmed diagnosis.

## Step 3: Three-level cause analysis

Diagnose the bug by identifying three levels of cause. Do not skip to fixing.

### a) Direct cause

The immediate technical failure. What line of code breaks? What value is wrong? What exception is thrown? This is what the stacktrace shows you.

### b) Root cause

Trace why the failing state arose. Use Five Whys or another causal strategy suited to the case; five is a prompt to investigate, not a required number of answers. Support each causal link with evidence and label unsupported links as hypotheses.

For example, an exception on a null field is the direct cause. The investigation must establish which write path, migration, or caller produced that null and why the expected invariant was not enforced. A missing test or vague specification may be a contributing factor without being the technical root cause.

Stop at the actionable cause that explains the observed failure. Do not force a systemic explanation or invent missing links. State what a reproduction would show if this cause is correct and what observation would refute it.

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

Before changing production code, present the three-level cause analysis and its evidence to the user. Distinguish the proposed root cause from one verified by reproduction:

```
Direct cause: <what breaks>
Root cause: <causal mechanism, evidence, and verification status>
Contributing factors: <what allowed it to exist>
```

## Step 4: Check scope and integration risk

Assess whether the root-cause correction is one coherent, verifiable change within the authorized scope. Consider distinct outcomes, unresolved decisions, migration needs, dependencies, and integration risk. Line count does not determine whether the fix can proceed.

If the correction needs separate outcomes or a staged migration, present the proposed split and its dependencies. Create Linear issues only after approval. Otherwise, continue with the root-cause verification and fix.

## Step 5: Verify the root cause and write the failing test (RED)

Once you have a proposed root cause, run a reproduction that tests that explanation before implementing a fix. If an early reproduction already exists, rerun or refine it against the causal prediction. Reproduction timing is flexible during diagnosis; this check after identifying the cause is required.

Exercise the path that creates the faulty state and assert the resulting user-visible failure or violated invariant. Merely injecting a bad value at the failing line proves the direct cause, not why the system produced it. Use a comparison or controlled variation where useful to distinguish the proposed cause from competing explanations. If the reproduction contradicts the explanation, return to diagnosis.

Turn the supported reproduction into a durable regression test at the appropriate boundary. Keep any HTTP, browser, or replay harness needed to verify the original scenario. Record what was executed, which causal links it establishes, and any remaining uncertainty. A synthetic failure with the same exception text is not sufficient.

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
3. Confirm it reaches the proposed causal mechanism and fails for the expected bug, rather than a typo, import error, unrelated failure, or a fixture that bypasses the root cause.

If the test passes immediately, your test does not reproduce the bug. Fix the test.
If the test errors instead of failing, fix the error and re-run.

## Step 6: Fix the bug (GREEN)

Correct the verified causal mechanism with the smallest coherent change. Make the regression test pass without merely hiding the exception or suppressing the symptom.

Do not:
- Add features the test does not require
- Refactor surrounding code
- Add error handling for unrelated cases
- Fix other bugs you noticed along the way

Run the regression test and the original reproduction scenario. Confirm the causal invariant is restored and the reported symptom is resolved. Run related tests to check for regressions. If verification requires UAT actions outside the approved scope, ask the user before running them.

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

- Propose resolving those errors in Sentry and do it only after approval
- If manual review is needed (the fix might not apply), propose a flagging comment instead, also gated on approval

## Step 8: Present results

Present the fix to the user:

- What was the bug (three-level cause analysis summary)
- What reproduction verified the root cause, where it ran, and what uncertainty remains
- What regression test was written and what type
- What code was changed
- What preventive measures were added
- Whether any docs were updated
- Whether any similar Sentry errors were resolved

### Sentry-specific: close the loop

If the input was a Sentry issue, propose closing the loop and act only after approval:

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
- **Evidence-backed cause analysis before production fixes.** Explain the direct cause, root cause, and contributing factors. Diagnostic code may precede the analysis when it helps.
- **Verify the proposed root cause.** Run or refine the reproduction after identifying it, then fix the causal mechanism and rerun the original scenario.
- **Local reproduction first.** Local HTTP, browser, and replay harnesses are allowed. If local reproduction is not possible, ask the user before a UAT attempt.
- **One fix at a time.** Do not bundle fixes for other bugs you noticed.
- **Choose the right test type.** Unit, integration, or BDD - whichever gives the most meaningful assertion.
- **Split by scope and risk.** Propose separate issues when distinct outcomes or integration constraints justify them; obtain approval before creating issues.
- **Sentry lifecycle.** Offer to claim at start, propose resolve-and-comment at end; every Sentry state change waits for approval first.
- **Preventive measures are not optional.** Address contributing factors.
- **Update docs when they contributed to the bug.** Requirements and design docs that are wrong or incomplete get fixed.
- **No em-dashes or connector dashes.** Use the punctuation that means the same thing: commas, colons, periods, or parentheses. Hyphens inside compound words are fine.
