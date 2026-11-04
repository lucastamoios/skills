---
name: implement-review
description: Evaluate explicit review findings and implement authorized corrections from a prepared development input and output contract. Natural requests route through dev. Preserve technical disagreement, meaningful test-first behavior, and explicit publication permissions.
user_invocable: true
argument-hint: "input=<absolute input.md> output=<absolute output.md>"
---

# Implement Review

Evaluate the supplied review comments against the code and its requirements. Implement only corrections authorized by the prepared input, and return a classification and evidence for every assigned comment.

## Invocation and worker boundary

The prepared invocation is `input=<absolute input.md> output=<absolute output.md>`. Read the complete [development/v1 contract](../dev/references/contract.md) and the input before execution. The contract is authoritative for fields, source identity, permissions, status, budgets, and output structure.

A natural request, PR number, branch name, pasted feedback, or request to inspect the current PR belongs to [dev](../dev/SKILL.md). Route it there without starting worker execution or inventing a prepared input. The coordinator supplies the source comments, findings, decisions, and source identity for this job.

The supported modes are:

| Mode | Outcome |
|---|---|
| `evaluate` | Evaluate and classify each assigned comment. Write the result and any questions without changing production code or tests. |
| `implement` | Evaluate the assigned comments and apply only corrections authorized in the input. Return classification, changes, and verification evidence. |

Validate the assigned skill and mode, scope, stop condition, baseline, source and upstream digests, decisions, model configuration, and allowed writes before changing anything. Record the source identity before work and after work, separating expected edits from unrelated drift. Preserve existing user changes. Do not substitute current branch feedback or a different PR for the supplied sources.

Keep requested and observed model, reasoning effort, and backend separate in the output. Report an unobservable setting as unknown. Do not claim that a requested setting was observed or silently escalate the model.

Do not spawn agents, invoke a next skill, choose another model, ask the user directly, or update shared tasks, logs, run manifests, documentation indexes, or model policies. The coordinator owns human dialogue, subsequent workers, task persistence, and review revalidation. Correction authority does not authorize commit, rebase, push, posting replies, resolving review threads, or other publication actions. Return proposed external actions and their exact content for the coordinator to handle under the user's authorization.

## 1. Load the assigned evidence

Read the explicit comment or finding sources and their recorded digests. Preserve each source's identity: its comment or finding ID, author, original text, code location, and reviewed source revision when available. Local review files are valid sources; a PR is not required.

Use the input's snapshots and upstream outputs. Fetch a named source only when retrieval is permitted and needed to verify its current identity or context. Paginate a requested full comment collection, but do not expand a selected set of findings into all PR feedback. If required sources are missing or their identities do not match, use the contract's appropriate status and return the mismatch. Do not silently reinterpret an old finding against new code.

Read the relevant requirements and decisions in the supplied documentation root. Inspect referenced code, its entry points, affected callers, and dependencies with the repository's context tools. Read enough surrounding code and relevant history to evaluate the claim; a changed line alone may omit the contract that determines correctness. Use relevant project learnings where they exist, while checking their claims against the current sources.

## 2. Evaluate validity and value

For each assigned comment, determine:

- Whether the claimed behavior can be reproduced or established from the code and requirements.
- Whether the proposed correction preserves affected callers, intentional blanks, validation rules, and other existing contracts.
- Whether the comment identifies a real defect, a useful improvement, an unsupported claim, or a suggestion that conflicts with the intended behavior.
- Whether the input authorizes this correction and its required writes.

Distinguish a verified defect from a plausible concern and an unverified claim. State the evidence and its limits. Reviewer seniority, an automated label, or a repeated assertion does not establish correctness. If an ambiguity in the intended behavior affects the result, return a precise question for the coordinator.

Use these classifications:

| Classification | Meaning |
|---|---|
| Must fix | The evidence establishes a correctness, security, or required-contract defect. |
| Useful improvement | The suggestion is technically valid and its benefit justifies the maintenance and scope cost. |
| Skip | The suggestion is technically valid but does not justify the cost or belongs outside this assignment. Explain the tradeoff. |
| Disagree | The evidence contradicts the claim or the proposed change would violate a contract. Explain what was checked. |
| Unverified | The available evidence cannot establish validity. Record what is missing. |

Keep classification separate from action authorization. A must-fix label does not grant permission to change unrelated scope. A useful improvement does not authorize speculative cleanup. Record the proposed action, authorization source, actual action, and residual scope for every finding.

Save the evaluation in a permitted checkpoint or attachment before implementation. In `evaluate` mode, classification is the requested outcome; report completion when the assigned analysis is complete, with implementation proposals for the coordinator. In `implement` mode, proceed directly with corrections already authorized in the input. Do not introduce a blanket approval gate.

If an unanswered behavior decision, missing permission, or unapproved action is necessary to finish the assigned correction, return `needs-input`. Include a stable question ID, the decision and evidence, and the exact dependent work. Continue independently authorized work only when it does not depend on that answer. The output must distinguish finished corrections from pending ones.

## 3. Implement authorized corrections

Apply corrections within the assigned scope and stop condition. Preserve the underlying behavior requirements even when the reviewer's proposed implementation is unsuitable. If the input authorizes only a specific implementation and the evidence shows it is wrong, report the conflict instead of silently choosing a different action.

Read [code-tdd](../code-tdd/SKILL.md) as a method resource. Use its behavioral classification, test selection, red, green, refactor cycle, and milestone verification inside this same worker. Do not invoke a second worker or start another pipeline.

Classify changes by their effect, not by file type:

- For new or changed behavior and bug fixes, observe a focused behavioral test fail for the intended reason before production implementation.
- For refactoring, establish passing coverage and add risk-justified characterization coverage where needed. Do not manufacture a failing test when behavior is unchanged.
- For documentation, formatting, or low-impact changes that do not require new regression coverage, use appropriate checks. Do not add a test that merely asserts the edit exists.

Work through coherent corrections one at a time. Run their related coverage before moving on. Reuse tests and fixtures that prove the relevant entry point, wiring, permissions, persistence, and failure behavior. Keep comment IDs and review traceability in the output, not in code comments, test names, or docstrings.

Finish the assigned working behavior. A passing helper test does not establish that a user-facing correction is connected and complete. Run mandatory repository checks and the input's verification scope. Use focused and affected downstream coverage; do not run the full suite by default. Broaden testing only when the scope, mandatory checks, or a concrete unresolved concern requires it and the budget permits it.

Report pre-existing failures and environment problems separately from introduced failures. Do not call an unexecuted test red or green. If budget or infrastructure prevents completion, return the applicable contract status and preserve a precise account of the remaining work.

## 4. Prepare replies only within scope

When reply drafts are requested, write them into the output or an allowed attachment. Each draft must identify its destination comment and reflect what was actually verified or implemented.

- For an implemented correction, describe the behavior changed and the relevant verification. Mention a commit only if that commit exists and was verified.
- For a skipped or disputed suggestion, state the technical reason and supporting evidence. For a human reviewer, leave room for missing context or discussion without weakening a supported conclusion.
- For a bot comment that is demonstrably incorrect, a no-reply recommendation may be appropriate. Record the reasoning; do not silently resolve the thread.

Use direct, respectful language without performative praise. Do not confuse a drafted reply with a posted reply or an implemented correction with a resolved thread. The output can recommend replies or resolution and must identify the destination, exact content, and requested action. The coordinator handles publication and thread resolution under the user's authorization.

## 5. Return the correction result

Publish the complete contract output through a temporary sibling and atomic rename to the assigned absolute output path. Never overwrite a prior attempt. For longer mutation work, keep the contract's atomic checkpoint with completed work, test results, resource ownership, and next action. Include:

- The classification table for every assigned comment or finding, with source ID, validity evidence, proposed action, authorization, actual outcome, and residual scope.
- Before and after source identity, authorized changed artifacts and their digests, and any unrelated drift.
- Behavioral test evidence, commands and results, required checks, and any execution limitations.
- How to exercise each implemented correction, the absolute checkout path, changed files, and a runnable diff command.
- Requested reply drafts and proposed external actions, with their exact destinations and content.
- Pending questions and the exact work remaining within or outside the assignment.

Use `complete` only when the assigned mode and scope are complete. Completion of evaluation does not imply that corrections were implemented. Completion of implementation does not imply that a review was rerun, code was committed, a branch was pushed, or threads were resolved. Use `needs-input`, `blocked`, `partial`, `failed`, or `stale` according to the contract when the corresponding limitation applies.

Stop at `stop_after`. The final message identifies the output path and status. The output file contains the durable job result; a chat summary alone is insufficient.
