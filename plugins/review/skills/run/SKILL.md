---
name: run
description: Coordinate review lenses as independent agents with explicit file contracts and models. Use for a review pipeline, a single lens, consolidation of existing evidence, or preparation and requested publication of PR comments.
---

# Run Review

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Prepare the context once, dispatch each selected lens in a fresh agent, and consolidate only compatible results. This skill coordinates work; it does not substitute its own analysis for the workers.

Read [the file contract](../../protocol/contract.md), [the model policy locator](../../protocol/models.json), and the requested lenses. Accept `input=<request.md> output=<consolidated.md>` or an ordinary PR, branch, or diff request. The request must establish the target and desired lenses; material ambiguity becomes one focused user question. Record accepted decisions in a run manifest before dispatch.

## Architecture maps

For a map-only request, use [review:map](../map/SKILL.md). Its coordinator dispatches a fresh preparation worker with exact source identity and produces an interactive domain/module/function map with full annotated diffs. It does not require paths, QA, finding verification or consolidation. Do not add it to a general review unless requested.

## Prepare the run

For a consolidation-only or PR-comment request, reuse the completed evidence and any compatible verification. Run only missing verification and consolidation work. Use `analyze` to aggregate individual reports and `prepare` to draft comments from an existing compatible verified report. A legacy report without verification needs the selected findings verified and its conclusions reconciled before comment preparation. Read [the consolidation publication workflow](../consolidate/references/pr-comments.md) for PR context capture, user editing, task persistence, and explicit publication. Do not dispatch paths or repeat other lenses merely to format existing findings, and do not recursively verify a verifier or repeat consolidation without new evidence. An explicit verify-only request ends with the verification artifact. Preserve missing coverage as a limitation.

1. Resolve the repository, exact comparison base and head, local changes in scope, applicable repository instructions, purpose, product sources, and permitted retrieval. Do not silently substitute the current branch for a named target. The default source identity includes all local changes; when the user specifies a subset, prepare an isolated copy containing exactly that target. Leave the user's checkout untouched.
2. Create a unique run directory outside the reviewed checkout. Keep `request.md`, `run.md`, `snapshot.json`, captured `sources/`, and one directory per job attempt with `input.md`, `output.md`, and `attachments/`. Persist useful artifacts outside temporary storage before ending a tracked review. Never reuse another run's writable directory.
3. Capture and immediately verify the source manifest with `scripts/snapshot.py` from the plugin. Use an isolated copy if edits may occur concurrently. Pin relevant ignored runtime configuration and dependencies separately for execution. Record concrete isolation evidence, never secret values.
4. Capture the minimum external context with original source, retrieval time, and SHA-256. Give each worker explicit context using [the input template](../../protocol/input-template.md). List missing sources rather than inventing requirements. Include the permitted the configured organization learning service or captured learnings where relevant. Repository instructions still apply; a worker uses scratch space if graph generation would mutate the reviewed source.
5. Record selected lenses, applicability, dependencies, mode, model, effort, execution budget, output paths, and required or optional status in `run.md`. A request for one lens selects that lens and its genuine prerequisites, not the whole suite. For a general review, include paths where applicable, intent, code, tests, risk where boundaries change, dead-code in findings-only mode, and QA by default, followed by verify and consolidation. Do not ask whether to include QA. Walkthrough runs when requested. State the selected coverage before dispatch.

Exclude default QA only when the user explicitly narrows the review or when source inspection establishes that the change has no executable behavior to exercise. Record the exclusion and its concrete reason in the run manifest and consolidation input. A missing environment, setup failure, unavailable access, or absent UI is not evidence that QA is inapplicable. API and CLI behavior still receive scoped execution; browser checks apply to changed UI. A blocked QA job remains an expected job and limits coverage. Requests limited to existing-evidence consolidation, comments, verification, or a specific lens retain their stated scope.

Task tracking is optional context for the coordinator, never a worker prerequisite. When using the Brain task workflow, read vault conventions, resolve exact ticket or PR matches, and create a missing review task as already authorized by the invocation. Ask only among ambiguous existing matches. Pass task-derived facts as explicit sources, not an instruction for every worker to rediscover the task. If task persistence would write inside the reviewed repository, review an isolated copy so those writes cannot invalidate its source identity.

For QA selected by this default or by an explicit request, prepare a `provision-local` input unless a suitable isolated environment already exists. Allocate an execution copy, a unique resource namespace, job-local dependency and browser setup access, and separate setup and scenario budgets proportional to the change. Reuse the repository's Docker and frontend workflows. Do not dispatch QA with an empty environment field or a zero execution allowance and present the predictable failure as completed QA. Respect explicit user constraints. Running the full automated suite is not a default prerequisite for QA.

## Select and enforce models

Use the request's explicit model-policy file when provided; otherwise use `profile.execution.model_policy`, resolving the configured path through `skill-config`. Record its resolved absolute path and SHA-256. The locator contains no independent model choices. If the personal coordinator is not installed, an external runner can supply its own policy file or explicit assignments without installing it. Never guess a policy path in the reviewed project.

Use only approved `assignments` from that policy or an explicit user override captured in this run. Canonical keys are `review:paths`, `review:code`, and the equivalent names for each worker, including consolidate and walkthrough. `proposed_assignments` and `proposed_profiles` are decision aids and are not executable defaults. Dev can pass approved assignments with their policy provenance; validate the supplied policy digest before dispatch. If an assignment is missing, prepare the context and ask for the missing choices before dispatch. Do not infer a model from `agents/openai.yaml`; that file describes the interface and does not enforce routing.

Check the active agent tool's supported model IDs and efforts. Each worker starts without inherited conversation and receives only its skill path, input path, output path, and permitted work boundaries. Use a native subagent tool when it supports both a fresh context and explicit model selection. With `collaboration.spawn_agent`, set `fork_turns` to `none`, `model` and `reasoning_effort` to the approved assignment, and pass the paths in the task message. Record the returned agent ID. Do not use a user-owned Codex task for internal workers.

If native dispatch cannot select that model, use a verified local Codex CLI adapter when available. Check its current help before constructing arguments. The invocation shape is:

```text
codex exec --model MODEL -c model_reasoning_effort=EFFORT --ephemeral --cd JOB_DIRECTORY --skip-git-repo-check --sandbox workspace-write --output-last-message JOB_DIRECTORY/dispatch-summary.txt -
```

Pass the worker prompt through stdin using a process API argument array or a safely quoted file. Keep the working directory at the exclusive job directory. Source paths remain read only by instruction; runtime sandbox grants must also permit the needed reads. Do not disable sandboxing or approval rules. Existing access rules, credentials, and approvals still apply. The configured model must actually be passed to the dispatch tool, not merely named in the prompt.

An unavailable model or backend leaves the job blocked. Do not substitute a model, provider, or effort silently. Report requested and actual models separately; actual may be unknown when runtime evidence is unavailable. Never claim that installing this plugin changes the parent agent's model.

## Schedule dependencies

Run paths first when changed production behavior warrants it. Validate its output identity and coverage before passing it downstream. If a required map is incomplete, request the missing evidence and block only affected conclusions; let workers proceed with independently valid scenarios. Invalid source identity still prevents using the artifact. Reuse a prior output only after its input, snapshot, source digests, and scope pass the same checks.

Intent, code, tests, risk, and dead-code can then run independently. Give them the current path evidence and their primary sources. Do not feed one reviewer's verdict to another by default. An existing intent contract or learning retrieval may be supplied explicitly as reusable context; receiving it does not establish independent corroboration.

QA consumes current paths. It can overlap static readers only with a separate execution copy and isolated mutable services. Tests experiments need separate state too. Serialize execution jobs when independent databases, caches, ports, and fixtures cannot be proven. A time or run budget ends execution with remaining scenarios reported, not fabricated as passing.

Every job owns its output. Wait for completion and read the files. A crash without output is an explicit failed job in `run.md`. Preserve completed peers. Retry only when a concrete change can resolve the failure, within the remaining budget, and use a new attempt ID and directory. Do not enter an unlimited repair or extraction loop.

For a blocked or interrupted QA job, inspect its setup attempts, checkpoint, and resource ledger. Reject a generic "cannot run full QA" conclusion when Docker startup, assets, browser access, fixtures, or an applicable recovery were simply not attempted. Repair omitted provisioning input, route a concrete access request through the available approval mechanism, or dispatch the next evidenced recovery in a new attempt. Extend your own setup allowance when useful work remains and the user has not imposed a conflicting hard cap. Preserve the boundary when missing credentials, denied access, unavailable required artifacts, a product defect, or an explicit limit actually prevents progress. Report partial coverage and the exact remaining action instead of treating the entire QA as optional.

Do not overlap a recovery attempt with a still-running worker using the same resources. Reuse resources only after their ownership and current state are verified. Carry the previous checkpoint as attributed partial evidence, not as a completed output. QA-discovered surface or path omissions go back to paths for a scoped correction; revalidate only affected conclusions and scenario coverage on the same source snapshot. A new map version does not authorize unlimited review loops.

## Verify findings before consolidation

After the selected analysis and execution jobs finish, dispatch `review:verify` in a fresh agent with its approved model and effort. Supply the current snapshot, original reports and digests, primary sources and decisions, a complete candidate table keyed by original run/job/finding ID, and the expected upstream jobs including failures or missing outputs. Preserve the exact claims and evidence rather than supplying the coordinator's preferred verdict. The default verification scope is every finding in the selected reports; an explicit narrower request records its exclusions.

Give focused experiments their own isolated resources and bounded allowances when necessary. Verification runs after mutable reviewer experiments finish. It never overlaps workers that share those resources. A packet with zero candidates still records the empty selection and all missing review coverage. Verification does not rerun every lens or require a full test suite.

Reuse a prior verification only when snapshot, upstream report digests, primary sources, decisions, and candidate scope match. New or changed findings require a new verification attempt for the affected scope. Preserve failed, missing, stale, and unresolved verification in the manifest. Do not silently bypass it or repeat the loop until a preferred verdict appears. A failed verifier still permits a partial consolidation that names the unverified findings and blocker.

## Consolidate and present

After verification finishes or records its failure, prepare a new input for `review:consolidate`. Include the original reports and the verification ledger, their digests, and the expected candidate scope. Include every expected job in that evidence phase, including verify and any failed, canceled, missing, or inapplicable job. List walkthrough preparation and cleanup as subsequent phases, not missing prerequisites for their own input report. Dispatch consolidation in its own configured agent. It writes the requested consolidated report and never edits worker outputs or the task. Verification coverage cannot substitute for original lens coverage.

Verify the source again before presenting a current result. If it changed, preserve the report as stale. Do not report overall approval from incomplete, stale, or incompatible results. If walkthrough was selected, dispatch its `prepare` job after consolidation with the current evidence and then follow its presentation reference interactively in this parent conversation. Add a pointer to its completed teaching artifact in the run manifest; do not treat it as another correctness verdict.

The coordinator alone may update the matching task's review table and companion resource with the consolidated report and run links. Preserve unrelated task content and useful prior evidence. Use task status `Complete`, `Blocked`, `Not applicable`, or `Stale`, while stating verdict separately. Mark old snapshot rows stale unless revalidated. Do not let parallel workers merge shared notes.

When PR comments are requested, dispatch `review:consolidate` in `prepare` mode from the compatible report and current PR context. Reuse a valid existing proposal instead of creating a duplicate job. The coordinator presents the table and follows [the publication workflow](../consolidate/references/pr-comments.md) for finalized user-requested submission. A consolidation worker never posts or updates the task. A request to consolidate alone does not authorize publication.

Learning-store edits and fixes require their own explicit workflow. A requested dead-code cleanup runs as a separate exclusive job after the review workers finish; its input selects cleanup and its result gets a new snapshot. Revalidate affected evidence before presenting a review of the cleaned code.

Return the consolidated report link, selected-lens coverage, significant findings, and material missing work. Include the run manifest so the user can inspect which model and input each agent received. Never claim that all eight lenses ran when only a subset was selected.
