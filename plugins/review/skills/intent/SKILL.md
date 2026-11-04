---
name: intent
description: Compare a change with explicit product requirements and acceptance criteria. Produce an intent contract, requirement-to-evidence mapping, and scoped deviations in an independent file.
---

# Intent Review

Determine whether the change does what was requested. Keep requirement-to-assertion alignment here; tests owns assertion strength, mocks, flakiness, and consolidation.

## File interface

Read [the worker contract](../../protocol/contract.md). Accept `input=<absolute input.md> output=<absolute output.md>` with skill `intent` and mode `analyze`. Write the required report to this exclusive output. The input declares context, snapshot, sources, model, dependencies, access, and budget. Do not infer them from the parent conversation.

If invoked with a PR, branch, or diff instead of a prepared input, use `review:run` to prepare and dispatch this lens in its configured agent. Do not perform the worker analysis inline. Inside a worker, never dispatch another lens, discover a task, or edit shared review artifacts. Report missing prerequisites through the output.

Follow repository instructions and use Graft and LSP when required or available. Write artifacts in English. Verify the input snapshot before and after analysis. Keep the reviewed checkout unchanged and write only the assigned output and attachments, subject to this lens's explicit execution mode.

## Required context

Require a current path artifact for changed production behavior. For changes without executable paths, record why it is unnecessary. Read the declared intent sources; if they cannot establish the expected outcome, report the uncertainty rather than inventing requirements. Ignore style, naming, generic bugs, architecture, and security unless they prevent the stated outcome.

## Establish the evidence

Use the declared target and sources. Read the linked ticket or specification, repository requirements, implementation plan, the PR title and body, the diff, the minimum surrounding code needed to understand changed behavior, and tests that claim to prove the requested behavior.

Search repository requirement and plan locations referenced by the task, ticket, PR, or local project instructions. Compare the implementation with their stated behaviors, constraints, sequencing, and explicit design decisions. Treat a plan as implementation intent, not as stronger evidence than an explicit requirement or later accepted clarification.

Use this evidence order when sources conflict:

1. Explicit acceptance criteria or specification.
2. Repository requirements.
3. Ticket description and clarifying comments.
4. Accepted implementation plan.
5. PR description.
6. Intent inferred from the diff.

State when intent is inferred. Do not invent requirements.

## Build the intent contract

Reduce the evidence to the problem, expected outcome, explicit requirements, constraints, and non-goals. Persist this contract in the output so another agent can consume it without the conversation.

If the outcome is materially ambiguous, record one focused question in missing inputs and continue independent checks.

## Trace intent to evidence

For each explicit requirement, find the implementation that produces the behavior and the test assertion that proves the observable outcome. Identify behavior that contradicts a constraint and meaningful changes that cannot be traced to the intent.

Evaluate tests by observable result, not by coverage or file presence. Classify only real deviations:

- `Gap`: A required behavior is missing or contradicted.
- `Unproven`: The implementation may satisfy the intent, but no test proves the expected outcome.
- `Scope`: The diff adds meaningful behavior that the intent does not justify and that creates a concrete review risk.

Do not report harmless refactoring or incidental support work as scope drift.

## Output sections

Add the intent contract, requirement and accepted-plan alignment table, findings, and unresolved product questions to the common output. Each alignment row cites the source requirement, implementation, and actual assertion, or identifies the missing evidence. Use finding categories `Gap`, `Unproven`, and `Scope` as defined above.

Use verdict `Aligned`, `Partial`, `Misaligned`, or `Unclear` with a reason, independently of analysis coverage. Return the output link, verdict, and at most two material deviations. Keep the full contract and evidence in the file.
