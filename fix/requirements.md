# Fix Skill Requirements

Last updated: 2026-04-08

## Context

The `/fix` skill is a bug-fixing workflow that takes any error report (Sentry link, Linear issue, pasted stacktrace, or plain description), systematically diagnoses the root cause, writes a failing test that reproduces the bug, and fixes it using RED-GREEN-REFACTOR. It integrates with Sentry and Linear when available, and includes preventive measures to reduce the chance of recurrence.

## Requirements

### Input and Context Gathering

1. The skill accepts a free-form argument that can contain any combination of: a Sentry issue URL, a Linear issue identifier, a pasted stacktrace, or a plain text description of the problem.
2. When a Sentry issue URL is provided, the skill fetches the full issue details via Sentry MCP - including stacktrace, error message, breadcrumbs, tags, environment, release, frequency, and affected user count.
3. When a Linear issue identifier is provided, the skill fetches the issue details via Linear MCP.
4. Regardless of input source, the skill explores the relevant parts of the codebase (files referenced in the stacktrace, related tests, recent commits) and reads any existing requirements and design docs that relate to the affected area.
5. The skill gathers as much context as possible from all available sources before starting diagnosis. It does not limit itself to a single source.

### Diagnosis

6. The skill performs a three-level cause analysis: (a) the direct cause - the immediate technical failure, (b) the root cause - found by asking "why" repeatedly until hitting something systemic (design flaw, missing invariant, ambiguous interface), and (c) contributing factors - what allowed the bug to exist (missing lint rule, no test coverage for this path, ambiguous contract).
7. The direct cause drives the test (what to reproduce), the root cause drives the fix (what to change), and the contributing factors drive preventive measures (what to add so it does not happen again).
8. The skill checks requirements and design specs for contradictions, gaps, or misalignments that may have caused the bug. If found, it flags them for correction.
9. When a Sentry issue URL is provided, the skill searches Sentry for similar or related errors that might share the same root cause.

### Test and Fix

10. The skill writes a failing test that reproduces the exact bug in its specific context, not just any test that triggers the same error message.
11. The test type (unit, integration, or BDD scenario) is chosen based on what makes sense for the bug's context - where it occurs in the system, what layers it crosses, and what the most meaningful assertion is.
12. The skill verifies the test fails for the expected reason (the bug) before writing any fix code.
13. The fix follows RED-GREEN-REFACTOR: minimal code to make the test pass, then deliberate cleanup.
14. After the fix, the skill runs related tests to confirm nothing else broke.

### Size Gate

15. If the fix would require more than 800 lines of code changes, the skill stops and creates Linear issues to break the work into smaller pieces instead of implementing the fix directly.

### Sentry-specific Behavior

16. When the input includes a Sentry issue, the skill assigns the issue to the current user at the start of the process.
17. When the fix is complete and the input was a Sentry issue, the skill marks the issue as resolved and adds a comment with a summary of the root cause and the fix.
18. When the input includes a Sentry issue, the skill searches for similar errors and, if the fix applies to them as well, resolves those too (or flags them if manual review is needed).

### Preventive Measures

19. After fixing the bug, the skill checks whether a linting rule, type annotation, or similar automated check could prevent the same class of error from recurring. If so, it adds it.
20. If the diagnosis revealed contradictions or gaps in requirements or design docs, the skill updates those docs to correct them.
