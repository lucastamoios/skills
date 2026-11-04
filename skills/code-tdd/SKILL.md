---
name: code-tdd
description: Implement an assigned development milestone with outside-in test-driven development from a prepared input and output contract. Natural requests route through dev. Observe meaningful failures before behavior changes and finish a complete working slice.
---

# Code TDD

Build observable behavior through small red, green, refactor cycles. Finish the assigned working milestone and return evidence to the coordinator.

## Invocation and worker boundary

The prepared invocation is `input=<absolute input.md> output=<absolute output.md>`. Read the complete [development/v1 contract](../dev/references/contract.md) and the input before execution. The contract is authoritative for fields, source identity, permissions, status, budgets, and output structure.

The supported mode is `implement`. The input assigns one complete working milestone and its stop condition.

A natural task description, issue identifier, requirement, or plan step belongs to [dev](../dev/SKILL.md). Route it there without starting worker execution or inventing a prepared input. A prepared job remains a single job in this worker.

Validate the assigned skill and mode, scope, stop condition, baseline, source and upstream digests, decisions, model configuration, and allowed writes before changing anything. Use the supplied documentation root and evidence. Do not discover a different task or silently replace a stale source. Record the source identity before work and after work, separating expected edits from unrelated drift.

Keep requested and observed model, reasoning effort, and backend separate in the output. Report an unobservable setting as unknown. Do not claim that a requested setting was observed or silently escalate the model.

Execute only the assigned milestone and use only the input's permissions. Preserve existing user changes. Do not spawn agents, invoke a next skill, choose another model, ask the user directly, or update shared tasks, logs, run manifests, documentation indexes, or model policies. Return questions and scope decisions in the output for the coordinator. Implementation authority does not authorize commit, rebase, push, PR changes, or other publication actions. Return proposed external actions and their exact content for the coordinator to handle under the user's authorization.

When another prepared worker reads this file as a method resource, it uses the behavioral classification, test selection, TDD cycle, and milestone verification below within its existing job. It does not start a second job or route again.

## 1. Define the behavior and working milestone

Read the assigned behavior and relevant supplied specifications where they already live. Use issue descriptions and discussions identified by the input, with permitted retrieval when required. Resolve material conflicts through the recorded decisions. If an unresolved behavior or scope decision is necessary, return `needs-input` with a stable question ID, supporting evidence, and the exact dependent work.

Trace the intended entry point, dependencies, and affected callers. For a bug, reproduce the symptom and identify its cause. A shared fix is appropriate when the affected callers share the same contract; check sibling paths before changing their behavior.

Express the assigned milestone as a small, complete outcome that a user or caller can exercise. For example, "Submitting a valid form saves a record and displays confirmation." Identify the required validation, permissions, and failure behavior for that slice. A milestone may cover part of a larger feature, but its advertised behavior must work. If it cannot be completed within the allowed writes or budget, report that boundary rather than expanding the assignment.

Work from the entry point inward. Keep each user or caller action identifiable at the point that accepts it. Build helpers and lower layers as the slice needs them. A public library API is itself a valid entry point; do not invent an application just to provide a caller.

## 2. Classify the change

Classify by its effect, not its file type or line count. Configuration changes can alter runtime behavior, and one-line changes can break important contracts.

| Change | Approach |
|---|---|
| New behavior | Add a behavioral test and observe the intended failure before implementing it. |
| Changed behavior | Update or extend coverage to express the new expectation, then observe it fail before changing the behavior. Preserve assertions for contracts that still apply. |
| Bug fix | Reproduce the defect with a failing regression test before fixing its cause. |
| Another instance of an existing tested pattern | Confirm the existing test actually exercises the new instance and its relevant outcomes. Run that coverage before and after the change. If it misses the behavior, use the appropriate test-first path above. |
| Refactoring without behavior changes | Establish passing coverage first. Add characterization tests where coverage is missing and the risk warrants them. These tests should pass against the current behavior; do not manufacture a red step. |
| Documentation, formatting, or another low-impact edit that does not need new regression coverage | Use existing tests or appropriate checks. Do not add tests that merely assert the edit exists. |

For the test-first paths, an observed failure for the intended reason is required before production implementation. Exploration is allowed; do not turn an untested prototype into the implementation and call it TDD. Preserve existing user work.

## 3. Choose tests that prove behavior

- Start with the relevant entry point or public contract. Prefer integration coverage when correctness depends on permissions, validation, business rules, persistence, or wiring working together.
- Use focused unit tests when they make complex logic, edge cases, or failure conditions easier to exercise and diagnose. The same logic being reachable through an integration test does not disqualify a useful unit test.
- Extend the existing test organization and reuse its setup. Create separate cases or parameterized scenarios for distinct behaviors. Do not force a whole feature into one growing test, or require a dedicated test for every function.
- Assert observable outcomes and meaningful contracts. Multiple assertions can describe one coherent outcome, such as a rejected request producing an error and leaving the database unchanged.
- Prefer real internal components. Use test doubles where a boundary is impractical, unreliable, or unsafe to exercise directly. A test that mocks the behavior under change or all its connecting code does not prove the slice works.
- Use the project's existing test framework and fixtures. When relevant BDD scenarios and infrastructure exist, reuse or connect them. Do not add a second framework or duplicate coverage merely to label it BDD.
- Name tests for their behavior. Keep requirement IDs and ticket IDs out of code comments, test names, and docstrings. Put useful traceability in issue records, PR descriptions, commit messages, or supporting documentation.

## 4. Run the red, green, refactor cycle

### Red: establish the missing behavior

Write or change a test for one coherent behavior. Run the focused test and inspect the failure. It must fail because the intended behavior is absent or wrong, rather than because of unrelated setup, syntax, imports, or unavailable infrastructure.

If it passes immediately, investigate whether the behavior already exists or the test fails to exercise it. Do not change a correct expectation merely to force a failure. If the behavior already works, verify the requested contract and avoid redundant implementation.

### Green: implement the smallest correct solution

Select an implementation in this order, stopping at the first suitable option:

1. Reuse an existing implementation or established codebase pattern.
2. Use the standard library.
3. Use a native platform capability, such as a database constraint or browser feature.
4. Use an already installed dependency.
5. Write the small amount of custom code the behavior requires. Add a dependency only when its benefit justifies the additional maintenance.

Suitability includes the actual requirements, contracts, and operational constraints. Prefer focused functions and a path from entry point to observable result that is easy to follow. Extract a helper when it gives a distinct responsibility a clear name. Keep steps together when extraction only adds a call without clarifying the work. Function length, file count, and repeated lines are signals to examine, not targets to optimize.

Implement the behavior at the layer that owns it. Avoid speculative abstractions, options, scaffolding, and unrelated improvements. Include required validation, security, accessibility, and protection against data loss in the behaviors being tested; a narrow passing test is insufficient if the milestone still omits them.

Run the new or changed test and related coverage. Fix failures introduced by the change. Do not weaken a correct assertion to accommodate faulty code. Correct a mistaken test when the requirements or evidence establish that it is wrong.

### Refactor: simplify while preserving behavior

Trace a representative action from its entry point to its state change or result. Check whether a reader can tell which operation runs and why each call exists. Review naming, branching, boundaries, and consistency with the surrounding design. Consider splitting an entry point that handles distinct actions, or removing an indirection that hides a simple action. Treat repeated difficulty following a routine path as evidence that its structure needs another look.

Review repeated work in context before changing it. Checks that look alike may protect different moments in a flow, while repeated work at the same moment may be unnecessary. Extract helpers for a stable shared responsibility; repeated lines alone do not justify an abstraction.

Refactoring is a deliberate check, not a requirement to make another edit. If the implementation is already clear and appropriately scoped, continue. Rerun relevant tests after any refactoring, then start the next behavior.

## 5. Verify the working milestone

Before presenting a milestone for review, verify all of the following:

- Trace the advertised behavior from its intended entry point to its observable result. Confirm that the action and its important effects are clear where the code chooses them.
- Every dependency along that path exists and works. There are no undefined calls, placeholder implementations, disconnected helpers, or unfinished connections needed for that behavior.
- The relevant tests pass and demonstrate the observable result through the real application path. Supplement automation with a direct check when the behavior warrants one, such as a visual interaction.
- Affected callers and shared contracts have appropriate coverage, including relevant edge cases and failure paths.

Reuse integration coverage produced during the TDD cycles when it already proves the slice. Add another integration test only for a remaining gap.

Run required repository checks and the verification assigned in the input. Use focused tests and affected downstream coverage. Do not run the full suite by default; run it when the assigned scope, a mandatory repository check, or a concrete unresolved concern requires it and the budget allows it. Once the necessary checks pass, repeat or broaden them only for new changes, failures, or a concrete unresolved concern.

Distinguish newly introduced failures from pre-existing failures and environment problems. If execution is blocked, try relevant available remedies and report what could not be verified. Do not label an unexecuted test red or green, or present a blocked slice as a verified milestone.

## 6. Return a working milestone

Continue through intermediate functions, helpers, layers, and TDD cycles until the assigned milestone is complete. A line count, file count, passing helper test, or completed function is not a completed milestone.

For example, "The user can submit the form and the record is saved" can be reviewed. A validation helper waiting to be connected, or a handler calling an unimplemented service, is intermediate work.

Stop at the input's `stop_after` boundary. Do not continue to a later milestone, review, or publication step. The coordinator owns review checkpoints, human dialogue, subsequent workers, and any revalidation of review findings. Use the contract status that accurately describes the result, including `needs-input`, `blocked`, `partial`, `failed`, or `stale` when applicable. A budget limit does not make unfinished behavior complete.

Publish the complete contract output through a temporary sibling and atomic rename to the assigned absolute output path. Never overwrite a prior attempt. For longer mutation work, keep the contract's atomic checkpoint with completed work, test results, resource ownership, and next action. Include:

- What now works and how the reviewer can exercise it, including any necessary setup.
- The relevant failing and passing test evidence, final checks, and remaining limitations.
- The before and after source identity, changed artifacts and their digests, absolute paths, commands and results, and a runnable diff command. Include a PR URL and state only when verified and relevant to the input.
- Which agreed outcomes remain, if the milestone is part of a larger task.
- Any questions, permission limits, or unrelated source drift that the coordinator must resolve.

The final message identifies the output path and status. The output file contains the durable job result; a chat summary alone is insufficient.

## 7. Keep documentation useful

Update existing documentation when the implementation makes it inaccurate and the input permits those writes. Otherwise, report the required documentation change as residual scope. Explain non-obvious constraints and deliberate tradeoffs where future maintainers need them. Comments and docstrings should describe behavior or rationale.

Keep issue and requirement traceability outside code as specified above. Read specifications in place; do not automatically reconstruct, commit, graduate, or delete requirements, design, and plan documents as part of this skill.
