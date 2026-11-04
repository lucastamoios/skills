---
name: qa
description: Prepare an isolated Docker environment, exercise changed UI with Playwright, and execute mapped and exploratory QA scenarios. Persist setup attempts, results, and cleanup; substantiate blockers after recovery attempts. Do not run the full automated suite by default.
---

# QA Review

Try to break changed behavior across every mapped basis scenario. A reproducible failure that exposes a system flaw is a successful QA finding.

## File interface

Read [the worker contract](../../protocol/contract.md). Accept `input=<absolute input.md> output=<absolute output.md>` with skill `qa` and mode `execute`. Write the required report to this exclusive output. The input declares context, snapshot, sources, model, dependencies, access, and budget. Do not infer them from the parent conversation.

If invoked with a PR, branch, or diff instead of a prepared input, use `review:run` to prepare and dispatch this lens in its configured agent. Do not perform the worker analysis inline. Inside a worker, never dispatch another lens, discover a task, or edit shared review artifacts. Report missing prerequisites through the output.

Follow repository instructions and use Graft and LSP when required or available. Write artifacts in English. Verify the input snapshot before and after analysis. Keep the reviewed checkout unchanged and write only the assigned output and attachments, subject to this lens's explicit execution mode.

## Required context and execution boundaries

Require a current paths artifact for the declared scope. Do not recreate it. Stale identity prevents reliance on that map. Incomplete coverage blocks the affected conclusions, not independent scenarios whose inputs and expectations are sound; identify the repair needed. Read the input's scratch resources, setup and execution budgets, and cleanup ownership. The input may authorize provisioning a new local environment instead of supplying one already running. Missing containers, assets, browser binaries, or fixtures are setup work, not proof that QA cannot run.

Use only verified local, test, or disposable environments. Never target production, shared staging, or an environment whose isolation is uncertain. Never use SSH without explicit user approval. Do not broadly overwrite existing local data, change product source or committed tests, or mutate external systems. If a needed action exceeds the input's authorization, report it to the coordinator. Track narrowly scoped records and keys, restore created state, and report residue. Use Playwright for browser-facing scenarios; source inspection cannot substitute for execution.

## Establish the QA environment

Read and follow [the local setup and recovery procedure](references/local-setup.md). Attempt Docker setup using the repository's supported workflow. Start its application and exercise the real interface when one exists in the affected surface. A documented frontend process outside Docker is compatible with containerized backing services; do not redesign the project's development stack merely to put every process in a container.

Inspect actual Docker availability and repository startup commands before claiming the environment is unavailable. Try applicable safe recovery actions and verify their result. Use an isolated execution copy, preserve the reviewed source, and prove service and data isolation before migrations or fixture writes. Lack of an existing environment does not require a user to build it first.

Write the `QA setup` section in the output. Record:

- The reviewed commit and environment identity.
- Required services and exact start commands.
- Setup phase, attempted commands, observed errors, recovery actions, and verification results.
- Health checks and reachable endpoints.
- Fixture or authentication setup.
- Database, Redis, and dependency isolation.
- Reset, cleanup, and stop commands.
- Setup blockers and manual steps.

For browser-facing paths, locate and use the repository's existing Playwright configuration, browser project, authentication fixtures, and base URL. Start any frontend or asset-build process that the documented Playwright workflow requires.

If Playwright is unavailable or cannot reach the flow, follow the installation, asset, networking, authentication, and browser recovery steps before marking it blocked. An API response does not replace execution of a required UI scenario. A CLI or API-only project does not need an invented UI; state that scope explicitly.

Do not run the full automated suite as part of this skill. Use focused tests only when needed to diagnose readiness, distinguish an environment failure from a product defect, or reproduce a scoped finding. Explicit user requests or mandatory repository checks still apply. A related test failure can be a useful defect to investigate; continue independently executable QA instead of stopping solely because a test is red.

## Persist progress as it happens

Before setup, create `attachments/progress.md` in the assigned job directory with the planned scope and resource ledger. Update it after each setup or recovery attempt, fixture mutation, scenario, exploratory finding, and cleanup action. Write each updated checkpoint to a temporary sibling and rename it atomically so interruption does not destroy the previous checkpoint. Record commands, observed results, evidence links, and the next action. Keep credentials and raw authentication state out of the report.

Checkpoints are partial evidence, not a published verdict. Publish `output.md` atomically as required by the common contract. If interrupted, the coordinator can inspect the checkpoint and resource ledger to resume safely or arrange cleanup. Never turn a partially written checkpoint into a completed QA report.

## Build the execution matrix

Use every required basis and surface-regression scenario from the declared path artifact. Prioritize changed decisions without omitting the setup paths needed to reach them. Link each scenario to its affected surface and source expectation. Reuse overlapping cases; code-path coverage alone does not establish that an export, email, or neighboring UI still works.

For each scenario, define the exact:

- Entrypoint invocation.
- Parameter values or equivalence classes.
- Database state.
- Redis or cache state.
- Identity, permissions, tenancy, flags, configuration, and clock state.
- Dependency responses and failure modes.
- Expected output, error, state transition, and side effects.

If a scenario cannot run, record the concrete blocker. Do not mark it as passed.

Plan applicable UI checks and a bounded exploratory pass in the same matrix. Keep mapped scenario IDs, UI-check IDs, and exploratory IDs distinct. A missing surface map becomes a specific upstream coverage request while valid existing scenarios continue.

## Execute every mapped path

Run each basis scenario and compare observed behavior with every expected outcome. Capture commands, requests, responses, relevant logs, state before and after, and cleanup evidence.

### Exercise browser paths with Playwright

For every scenario whose behavior requires navigation, clicks, typing, selection, drag operations, keyboard input, dialogs, downloads, or visible UI state:

1. Use Playwright to perform the real user interaction from the scenario's required initial state.
2. Prefer accessible roles, labels, and visible text for locators. Use implementation selectors only when the UI exposes no stable user-facing locator.
3. Check the visible result, URL or navigation state, relevant network response, browser console errors, and persisted state when applicable.
4. Exercise decision-changing UI states such as disabled controls, validation errors, empty results, pagination, loading, retries, and permission-dependent elements.
5. Preserve a Playwright trace for a complex or intermittent failure when the repository tooling supports traces.

For affected UI, also plan and execute applicable checks for keyboard navigation, visible focus, field labels, dialogs closing with Escape, and meaningful image alternatives. Exercise the main changed flow at desktop and a narrow mobile viewport. Inspect relevant hover, tooltip, popover, empty, loading, validation, and disabled states, capturing an element screenshot when the detail is subtle. Inspect the rendered evidence, not just whether a screenshot file exists. Report inapplicable checks with a reason; this scoped pass does not claim a full accessibility audit.

Store browser evidence under:

```text
<assigned attachment directory>/
```

Use stable names based on the path scenario, such as `P03-failure.png` and `P03-trace.zip`. Do not capture secrets, access tokens, or unrelated personal data.

Actively vary the dimensions that control changed decisions:

- Boundary, empty, null, malformed, duplicate, very large, and unexpected parameter values.
- Missing, stale, contradictory, partially migrated, duplicated, and cross-tenant database records.
- Missing, expired, stale, malformed, colliding, and partially written Redis values.
- Anonymous, unauthorized, least-privileged, privileged, and wrong-tenant identities.
- Disabled, enabled, missing, and inconsistent flags or configuration.
- Boundary timestamps, time zones, expiry points, and reordered events.
- Dependency timeouts, errors, malformed responses, retries, duplicates, and partial success.
- Concurrent, repeated, and interrupted operations when state can race or become partially applied.
- Loop behavior with zero, one, and several items when each case produces a distinct decision outcome.

Use focused variations that challenge an invariant or decision. Do not generate random load without a hypothesis.

When a variation breaks the system, reproduce it once from a known state. Identify the smallest parameter and state combination that triggers it. Record the violated invariant and the observable impact.

For each browser failure, document:

- The required user, permissions, feature flags, and data state.
- Numbered steps starting from a stable URL or application state.
- The expected visible behavior and the observed behavior.
- A screenshot taken at the failure point, or a Playwright trace when a still image cannot show the flaw.
- Relevant console errors and failed network requests.

## Explore beyond the supplied scenarios

After the planned pass, probe plausible omissions within the declared changed surfaces. Choose and record a bounded set of interactions proportional to scope and remaining execution budget. Examples include repeated submission, two tabs editing one record, stale or direct URLs, combined filtering and export, interaction during loading, and keyboard or viewport changes mid-flow. Reuse earlier evidence when it already exercises the hypothesis.

Create a `qa:Exx` row with the surface, hypothesis, setup, and expected outcome before executing a newly discovered scenario. Compare actual behavior, reproduce failures from a known state, and preserve evidence. Distinguish a new regression from a pre-existing defect when the available baseline supports that classification.

These observations can expose a missing path or incorrect expectation. Report a proposed map correction with source evidence and the affected scenario IDs; do not edit the upstream artifact. The coordinator owns re-extraction and any dependent revalidation. Executed exploratory evidence remains valid for its identified snapshot even before the map is updated, but it does not silently count as completion of an omitted basis scenario. Areas outside the declared scope become follow-ups.

## Substantiate blockers

Do not end with only "full QA could not run" or "the environment is unavailable." For each blocked portion, report the setup phase or scenario, exact attempted command or action, sanitized error, diagnosis, applicable recovery attempt and result, remaining runnable scenarios, and the precise next action or missing access. A preflight restriction may prevent a startup attempt; name the observed restriction rather than inventing an attempted run.

Distinguish a failed product scenario, a recoverable setup issue, an external dependency or authorization blocker, and budget exhaustion. If a concrete routine recovery remains but the setup allowance is spent, return that recovery request to the coordinator with the checkpoint. The coordinator can extend its own allowance or schedule the next attempt within the user's limits. Do not call an unattempted recovery impossible. Continue independent scenarios, and preserve partial results and cleanup status when a genuine blocker remains.

## Clean up

Stop only job-owned processes and containers. Starting a shared local Docker runtime does not make the daemon or desktop app job-owned; record that it was started and leave it running unless stopping it is separately authorized. Remove only this job's records, cache keys, files, and other state. Verify cleanup instead of assuming it succeeded.

Do not delete pre-existing state. If cleanup cannot restore the initial state safely, stop and tell the user exactly what remains.

## Output sections

Add QA setup and recovery attempts, the complete execution matrix, affected surfaces, applicable UI checks, exploratory results, proposed map corrections, failures, substantiated blockers, and cleanup to the common output. Keep path IDs unchanged. Each matrix row records parameters, internal state, expected and observed outcomes, result, and evidence links. Failures include preconditions, numbered reproduction, violated invariant, impact, source location, and screenshot or trace where appropriate. Link the checkpoint and resource ledger.

Use verdict `Failed` for demonstrated failures, `Passed` only when required mapped, regression, and applicable UI checks passed and the declared exploratory pass is complete, and `Blocked` when execution cannot establish that result. Material unresolved map corrections prevent a claim of complete coverage. Preserve known failures even when coverage is partial. Return the output link, separate mapped and supplementary execution counts, failure count, and at most two findings or concrete blockers. Keep detailed setup and logs in the file and assigned attachments.
