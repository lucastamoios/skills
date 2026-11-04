---
name: dev
description: Coordinate the selected development stages as separate agents with explicit file inputs, exclusive outputs, configured models, and serial dependencies. Use for picking up an issue, requirements, design, planning, implementation, or accepted review corrections, including an ordinary invocation of one migrated skill.
---

# Dev

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Coordinate the user's requested development outcome. Use separate workers for take, requirements, design-spec, plan, code-tdd, and implement-review. Review lenses run through review:run and retain their own file contract. Keep user dialogue, run state, task persistence, and integration in the outer coordinator.

Read [the development contract](references/contract.md) and model policy from `profile.execution.model_policy` (the bundled [empty policy](references/models.json) has no defaults). Accept a natural-language request or `input=<request.md> output=<result.md>`. The coordinator request names the objective, target, requested stages, existing sources, and stopping boundary. It is not a worker packet. A prepared `development/v1` packet goes directly to its named worker and must never be wrapped in another dev.

## Resolve the smallest sufficient flow

For an ordinary request to develop or implement a feature, continue through the needed requirements, design, and planning work, implementation, and a general review through `review:run`, including QA, verify, and consolidation. Reuse sufficient existing inputs. Do not ask whether to include review or QA in this default flow. An explicit narrower request, such as "only plan", "requirements only", or "implement without review", sets the stopping boundary. A missing material decision can pause dependent work; completing a stage does not create another approval step.

1. Capture the user's actual objective, scope, current decisions, explicit restrictions, and requested stopping point. Preserve existing authorization; do not reinterpret a question or a plan-only request as an implementation request. If a material boundary is unclear, ask one focused question while continuing independent preparation.
2. Identify the repository and its applicable instructions. Resolve the established documentation home once, otherwise use `profile.paths.docs/<project>`. Record the fallback rule before writing. Respect the project's document organization and any request for a lightweight result rather than generating a full document set by default. For issue-backed work in the user's Brain workspace, find the matching Obsidian Kanban task by issue key. If none exists and the user has not explicitly chosen untracked work, create one with `profile.paths.scripts/tasks.py` and the task template. Keep the task note directly in `profile.paths.tasks/` so the board can display it.
3. Reuse sufficient current documents and explicit decisions. Verify their content, provenance, scope, and unresolved questions. Do not rerun completed stages merely because the user starts at plan or implementation. Request missing prerequisite work only when it materially affects the requested stage, within the user's scope.
4. Create a durable run directory outside the implementation checkout with `request.md`, `run.md`, pinned sources, and one directory per job attempt. For a Brain Kanban task with associated files, keep its note directly in `profile.paths.tasks/<task-stem>.md` and create a companion folder `profile.paths.tasks/<task-stem>/`. Put the run at `<task-stem>/dev/<run-id>/`. Keep canonical requirements, design, and plan documents in the project's established documentation tree. After validating each completed document, copy it into the matching subfolder of the task's companion folder and link the vault copy and run result from the task note. Refresh a vault copy whenever its canonical document changes; do not treat an old copy as current. If there is no Brain Kanban task, use another durable directory outside the checkout. Each attempt owns `input.md`, `output.md`, and `attachments/`. Record selected stage order, source identities, canonical document ownership, model choices, dependencies, the task note path when applicable, and the stopping boundary in `run.md`.
5. Prepare [explicit inputs](references/input-template.md), exclusive output paths, checkout ownership, permitted writes, and realistic setup and execution budgets. Capture baseline source content, including relevant uncommitted changes. Inputs list repository instructions explicitly. Keep secrets out of packets and logs.

## Pick up issue-backed work

An ordinary `/take` request selects only the `take` stage unless the user asks
for further stages. For issue-backed development, include `take` before
requirements when shared understanding is missing. Reuse a current sufficient
brief or equivalent context rather than forcing intake on already specified work.
An explicit requirements-only request retains its boundary; request missing
context only when it materially affects that assignment.

For an ordinary `/take` invocation, perform the coordinator-owned Linear updates
in [Take: Assign and start the issue](../take/SKILL.md#assign-and-start-the-issue)
before dispatch. Record the verified assignee and status, or the specific blocker,
in the run and related task note.

Assign `take` in `draft` mode an exclusive issue-brief path in the established
documentation home. Pass the full available ticket context, relevant sources,
existing decisions, and related task reference. Use the approved default worker
assignment recorded for `take`. Do not invoke `next-issue` or duplicate bug
diagnosis; route a reported bug through `fix` within the user's authorization.

After validation, present the brief's summary of what should change and why,
including the supporting business rules or technical reasoning. Surface material
Product questions as one concise batch with stable IDs and dependent work.
Ask the user for unresolved decisions or prepare questions for him to take to Product;
do not send them. Record answers and their sources before dependent continuation.

Update the related Obsidian task with the brief link, change summary and rationale,
open question IDs and owners, and next action. Read the vault and task conventions
before editing. Preserve existing content, reconcile answers instead of appending
duplicates, and do not mark the ticket Done because intake is complete. Respect
an explicit untracked choice rather than creating a task. Workers only propose
this update; the coordinator owns the write and records whether it succeeded.
Pass the validated brief and subsequent answers as pinned upstream artifacts to
requirements and other relevant stages. A proposed direction is not a confirmed
requirement. Keep all continuation within the original stopping boundary.

## Select and dispatch models

Read only approved assignments from the model policy or an explicit user override recorded in the request. Proposed profiles are decision material, not defaults. Match the exact skill and profile; never choose another model because an assignment is absent. Ask for missing assignments while preparing independent context. A chosen model remains fixed across that stage's question and resume attempts.

For `requirements:review` and `design-spec:review`, first apply the approved `document_review` routing in the model policy and the [cross-provider dispatch procedure](references/document-review-dispatch.md). It selects one reviewer, preferring the opposite provider of the initiating client and using the ordinary GPT-6.1 Sol review assignment as fallback. All other stages retain their exact assignments.

Each assignment configures `model` and `effort` independently. Validate both against the selected backend's current capabilities before dispatch; API and Codex effort options can differ. Pass the exact `effort` as the native tool's `reasoning_effort` or the CLI's `model_reasoning_effort`. An effort change is an explicit policy or run override and must be recorded in a new attempt, just like a model change. Do not silently substitute an unsupported level or change the parent conversation's effort.

Use a native agent backend only if it supports a fresh context and the exact selected model and effort. With `collaboration.spawn_agent`, use `fork_turns="none"`, explicit `model` and `reasoning_effort`, and a short prompt containing the skill, input, and output paths. Never use a user-owned task for internal workers. Record the returned agent ID and backend evidence.

If the current client cannot dispatch the selected model, inspect `codex exec --help` and use the installed Codex CLI when authorized and available. Start in the exclusive job directory, pass `--model`, `-c model_reasoning_effort=...`, `--ephemeral`, `--sandbox workspace-write`, `--skip-git-repo-check`, and `--output-last-message` with the job's dispatch-summary path. Pass the worker prompt through stdin using a process argument array or a safely quoted file. Grant `--add-dir` only for the declared writable checkout or documentation directories; preserve host approval and repository rules. Do not disable sandboxing, rules, or hook trust. A broad filesystem grant is not authorization to edit other files.

The CLI summary is not the worker output. Require the separate output artifact and verify it. Record requested versus observed model; do not infer the runtime model from UI metadata or the prompt. If no backend can enforce the assignment, report the exact missing capability and preserve the prepared packet. Do not silently run the worker inline or substitute a model.

## Schedule dependencies

For issue-backed work lacking sufficient context, prepend `take draft`. The ordinary dependency chain is `requirements draft -> requirements review -> design-spec draft -> design-spec review -> plan -> code-tdd`. Each is a separate agent. These stages run in series for the same scope; the downstream worker receives only validated relevant artifacts and decisions. Code-tdd owns the full red, green, refactor cycle for its assigned milestone. Do not split each test or helper into another agent.

After each newly authored requirements or design draft, dispatch the same skill in `review` mode using its approved review profile and the [document review method](references/document-review.md). Use a fresh context with the user's request, accepted decisions and answers, vocabulary sources, relevant code evidence, and pinned draft artifacts. The reviewer writes only its report and evidence, with no authority to edit the draft or decide product questions. A requirements-only or design-only request includes that stage's review unless the user explicitly excludes it; it does not authorize the next authoring stage.

Evaluate findings, return supported corrections to the original author, and ask the user about unresolved meanings or consequential choices. Recheck changed sections after substantive corrections before downstream work. Preserve disagreements and incomplete coverage instead of treating a completed review as approval. Reuse current compatible review evidence for unchanged artifacts rather than repeating reviews on every continuation. A different reviewer model is a source of another perspective, not a correctness guarantee. Independent competing designs are optional work for a material design choice, not a mandatory second implementation. Cross-provider dispatch follows the configured document-review policy; do not improvise provider or model substitutions.

Use the plan's parallel execution handoff to run all eligible independent implementation units concurrently, within available agent slots and approved model assignments. Revalidate dependencies, exclusive writes, shared contracts, and runtime isolation against the current source before dispatch. If a unit is unsafe to overlap, serialize it and record the concrete reason. If an existing plan lacks the handoff, obtain a focused planning update within the authorized scope rather than guessing independence. Keep canonical document and index writes sequential.

For each ready parallel wave:

1. Establish an integration checkout and pin the prerequisite source identity. Preserve existing user changes. Worktrees do not copy uncommitted files; capture relevant authorized changes in the pinned baseline without committing them unless authorized. Confirm every worker receives equivalent prerequisite content.
2. Create or reuse one isolated worktree and branch per unit from that baseline, following repository and managed-worktree conventions. Record absolute paths, branch names, baseline identities, exclusive file ownership, and isolated runtime resources in run.md. Give each code-tdd worker one complete unit, its own input/output paths, and the full TDD cycle. Workers do not create agents or perform Git publication.
3. Dispatch every ready unit as slots become available. Wait for all required outputs and verify artifact digests, actual changed paths, unit checks, and preserved baseline content. A failed or stale unit blocks its dependents, not unrelated ready units. Stop a worker before reassigning its writable resources.
4. Integrate validated results into the integration checkout in the plan's order. The coordinator owns commits and merges. Use branch merges when commits and merges are authorized. If local rules require approval, prepare exact commands and messages and obtain it before execution. Until then, compose validated diffs in the integration checkout for joint verification and report the branch merge as pending. Do not claim a diff integration is a completed Git merge. Resolve mechanical conflicts within scope; return conflicting behavior or design decisions to the user.
5. Record the integrated source identity and run the group's joint verification, including affected shared contracts and required repository checks. Passing isolated tests do not establish successful integration. Dispatch dependent waves only after their prerequisites pass. Review the integrated snapshot through review:run at the milestone boundary.

Retain recoverable worker state until integration and verification succeed. Then archive or remove worktrees created for the run using the applicable lifecycle tool, preserving unrelated worktrees and reporting retained resources or pending merges. Integration creates a new source identity; prior review evidence must be revalidated against it.

After a complete working milestone, pass a general-review request to review:run, including QA by default, unless the user explicitly restricted or excluded that phase. Name the selected lenses, current snapshot, requirement/design/plan artifacts and digests, approved review assignments from this policy, execution permissions, and output path. Preserve review:run's QA applicability rule and report any justified exclusion or blocker. Review:run prepares paths before dependent lenses, permits static reviewers in parallel, and isolates QA and test experiments. It then dispatches verify and consolidate in sequence, each in a fresh agent. Reuse compatible verification when its source and candidate identities still match. Do not copy a development output into a review input and pretend their contracts are identical.

For corrections, dispatch implement-review with explicit findings and the user's correction scope. Use evaluate mode when only assessment is requested. Use implement mode for already authorized actions; unresolved material decisions return to the coordinator. Keep correction, new snapshot, and revalidation in sequence. Recheck affected reviews after a source change without automatically rerunning every lens or a full test suite.

Walkthrough follows stable consolidated evidence when requested. Requests to draft or post review comments use review:consolidate through review:run, reusing current evidence and its publication reference. Keep the table, user edits, task persistence, and requested submission in the outer coordinator. PR creation, publishing, media, issue creation, and queue automation remain optional capabilities invoked only within the user's request. Start/stop, task updates, logs, and explicitly requested retro remain coordinator responsibilities. Run retro only when the user explicitly asks; session completion and other skills do not trigger it. Workers do not repeat them. Other personal skills are not silently added to this flow.

## Handle results and questions

Wait for workers and inspect their output files and artifact digests. Preserve failed or missing jobs rather than manufacturing a result. For `needs-input`, present the concise question batch to the user, record answers with stable IDs, and issue a new attempt packet to the same configured model. Only dependent stages wait. Completing a document or milestone is not a fresh approval requirement.

For a failure, inspect actual evidence and the last atomic checkpoint. Retry only after a concrete change or actionable recovery, within user limits. Verify a prior worker is no longer running before reusing writable resources. A larger-model attempt requires an approved profile or explicit user direction and is recorded as a separate attempt. Do not promise that escalation recovers every failure or that a cheaper model saves total time after retries.

Validate that source mutations stay within the assigned scope and preserve prior work. Update shared indexes and the existing task only after reconciling artifacts. Carry unresolved questions and incomplete checks into the final result. A stage marked complete does not settle unrelated stages or external actions.

## Consolidate the development result

Write the requested result or `result.md` in the run directory. List each selected stage, attempt, model, status, canonical artifact, and coverage. State what behavior is implemented, what was actually verified, remaining decisions, blocked work, and any separately authorized delivery actions. Reference review:consolidate's evidence instead of rewriting its findings as new independent evidence.

Before the final handoff, read the latest compatible consolidated review and reconcile its questions and pending verification with work already completed. Present every remaining question and pending check directly in the chat as one concise, deduplicated batch; recording them only in `result.md` or linking the report is insufficient. Preserve finding IDs and distinguish required checks, coverage limits, and optional improvements. For each question, state the decision needed and recommend an answer when the evidence supports one. For each pending check, state what to verify, which conclusion depends on it, and whether it blocks the claimed outcome; ask the user whether to run it or defer it, with a recommendation and any needed access. Complete already authorized, feasible verification before asking, and do not reopen settled decisions or resolved checks. Record his answers before dependent follow-up work. If neither questions nor pending verification remain, say so explicitly. If the final review is unavailable or incompatible, report that gap instead of implying it is clear.

Return the result path and concise outcome. Continue through authorized eligible stages automatically, stopping at the recorded boundary or a material dependency. Keep the parent conversation focused on decisions and outcomes rather than worker logs.
