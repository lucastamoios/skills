# Fix Skill Requirements

Last updated: 2026-10-14

## Context

The `/fix` skill is a bug-fixing workflow that takes any error report (Sentry link, Linear issue, pasted stacktrace, or plain description), systematically diagnoses the root cause, writes a failing test that reproduces the bug, and fixes it using RED-GREEN-REFACTOR. It integrates with Sentry and Linear when available, and includes preventive measures to reduce the chance of recurrence.

## Requirements

### Input and Context Gathering

1. The skill accepts a free-form argument that can contain any combination of: a Sentry issue URL, a Linear issue identifier, a pasted stacktrace, or a plain text description of the problem.
2. When a Sentry issue URL is provided, the skill fetches the full issue details via Sentry MCP - including stacktrace, error message, breadcrumbs, tags, environment, release, frequency, and affected user count.
3. When a Linear issue identifier is provided, the skill fetches the issue details via Linear MCP.
4. Regardless of input source, the skill explores the relevant parts of the codebase (files referenced in the stacktrace, related tests, recent commits) and reads any existing requirements and design docs that relate to the affected area.
5. The skill gathers relevant evidence and chooses whether an early reproduction will help the cause analysis. It may begin diagnosis from code, logs, and history, and iterate between analysis and reproduction.

### Diagnosis

6. The skill distinguishes the direct failure, the technical root cause, and contributing factors. It uses Five Whys or another suitable causal strategy, supports each link with evidence, and labels hypotheses. It does not require exactly five answers or force a systemic explanation.
7. After identifying a proposed root cause, the skill runs or refines a reproduction that exercises the causal path and checks the explanation before fixing production code. Triggering only the direct failure with an injected bad value is insufficient. Contradictory evidence sends the skill back to diagnosis. Contributing factors inform preventive measures.
8. The skill checks requirements and design specs for contradictions, gaps, or misalignments that may have caused the bug. If found, it flags them for correction.
9. When a Sentry issue URL is provided, the skill searches Sentry for similar or related errors that might share the same root cause.

### Test and Fix

10. The skill turns the supported reproduction into a failing regression test that exercises the root-cause mechanism in its specific context. Local HTTP scripts, browser automation, and replay harnesses are valid diagnostic tools. If local reproduction is not possible, the skill reports attempts and missing conditions, proposes a specific UAT attempt, and waits for the user to approve it before execution. Unexecuted checks remain explicitly unverified.
11. The test type (unit, integration, or BDD scenario) is chosen based on what makes sense for the bug's context - where it occurs in the system, what layers it crosses, and what the most meaningful assertion is.
12. The skill verifies the test fails for the expected reason (the bug) before writing any fix code.
13. The fix follows RED-GREEN-REFACTOR: correct the verified causal mechanism, make the regression test pass, and then perform deliberate cleanup. Suppressing the symptom alone does not establish a root-cause fix.
14. After the fix, the skill reruns the regression test and original reproduction to verify the causal invariant and reported symptom, then runs related tests. UAT actions require approval for their specific scope.

### Scope and Integration Risk

15. The skill assesses coherent outcomes, unresolved decisions, migration needs, dependencies, and integration risk. It proposes a split when those constraints justify separate work and creates issues only after approval. It does not use line counts as a metric or constraint.

### Sentry-specific Behavior

16. When the input includes a Sentry issue, the skill assigns the issue to the current user at the start of the process.
17. When the fix is complete and the input was a Sentry issue, the skill marks the issue as resolved and adds a comment with a summary of the root cause and the fix.
18. When the input includes a Sentry issue, the skill searches for similar errors and, if the fix applies to them as well, resolves those too (or flags them if manual review is needed).

### Preventive Measures

19. After fixing the bug, the skill checks whether a linting rule, type annotation, or similar automated check could prevent the same class of error from recurring. If so, it adds it.
20. If the diagnosis revealed contradictions or gaps in requirements or design docs, the skill updates those docs to correct them.
