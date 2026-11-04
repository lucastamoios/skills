---
name: paths
description: Map changed production entrypoints, state, decisions, and basis scenarios into an independent evidence file for later review and QA. Exclude test code.
---

# Path Review

Create a reusable behavioral map of changed code. Use basis-path completeness, not a claim to enumerate unbounded loop or stateful paths.

## File interface

Read [the worker contract](../../protocol/contract.md). Accept `input=<absolute input.md> output=<absolute output.md>` with skill `paths` and mode `analyze`. Write the required report to this exclusive output. The input declares context, snapshot, sources, model, dependencies, access, and budget. Do not infer them from the parent conversation.

If invoked with a PR, branch, or diff instead of a prepared input, use `review:run` to prepare and dispatch this lens in its configured agent. Do not perform the worker analysis inline. Inside a worker, never dispatch another lens, discover a task, or edit shared review artifacts. Report missing prerequisites through the output.

Follow repository instructions and use Graft and LSP when required or available. Write artifacts in English. Verify the input snapshot before and after analysis. Keep the reviewed checkout unchanged and write only the assigned output and attachments, subject to this lens's explicit execution mode.

## Context and boundaries

Read the declared comparison and source snapshot. Analyze changed behavior and reachable callers. Do not inventory unrelated application code. Exclude tests, fixtures, helpers, snapshots, and test-only entrypoints. Do not use tests to derive or confirm the inventory. No upstream review is required.

## Map entrypoints

Start with every externally or internally callable entrypoint affected by the change. Examples include HTTP handlers, commands, tasks, event handlers, public methods, callbacks, scheduled jobs, and UI actions.

For each entrypoint, record:

- Signature and source location.
- Direct callers or trigger.
- Observable outputs, errors, state changes, and external calls.
- Parameters that influence a decision.
- Internal state that influences a decision, including persisted data, identity and permissions, feature flags, configuration, cache state, current time, dependency responses, and prior side effects.

Do not treat parameters as the only controllable dimensions. State setup and dependency behavior are first-class scenario inputs.

## Derive the basis paths

Inspect the control-flow decisions reachable from each entrypoint. Record conditionals, pattern branches, exception paths, early returns, loop zero/one/many behavior, and state-dependent dispatch.

Use cyclomatic complexity as a guide to the number of independent paths. Do not claim mathematical completeness when dynamic dispatch, recursion, generated code, or unresolved dependencies prevent it.

Create the smallest useful scenario set that covers every reachable decision outcome. Each scenario must specify:

- Entrypoint.
- Parameter values or equivalence classes.
- Required internal state and dependency behavior.
- Decisions and branches covered.
- Expected return value, response, or error.
- Expected state changes and side effects.

When a path is not covered, state exactly which parameter value, fixture state, permission, flag, clock value, or dependency response must change to reach it.

Mark paths as unreachable only when code evidence proves it. Mark uncertain reachability explicitly.

## Map impacted surfaces

Trace changed definitions and shared contracts outward to their user or system consumers. Include affected pages, API endpoints, exports, reports, emails, jobs, and operational commands. For fields or serialized shapes, inspect readers as well as writers. For shared UI, permissions, or base classes, enumerate relevant usage sites rather than selecting the first caller.

Record a surface table with stable `paths:Sxx` IDs, kind, changed definition, evidence of the impact chain, affected contract, and linked scenarios. Separate confirmed impact, unresolved impact, and excluded surfaces with reasons. Keep this scoped to the change and its consumers; do not claim a repository-wide audit.

Give each affected surface a focused observable smoke scenario. For adjacent existing behavior with a plausible regression mechanism, include one representative check. Group equivalent consumers only when their contracts and dispatch justify it, and identify unexecuted members explicitly. Reuse a basis scenario when it already provides that check; do not duplicate scenarios or invent a new automated test for every surface.

These regression scenarios describe expected checks, not test code. Preserve the exclusion of test files from this lens. Label expectations inferred from implementation so intent and QA can distinguish them from a sourced product requirement.

## Output sections

Add these sections to the common output:

- **Entrypoints:** Record each ID, signature, source location, trigger, parameters, relevant state, outputs, and side effects.
- **Basis scenarios:** Record each stable `paths:Pxx` ID, entrypoint, parameter values, state and dependencies, expected outcome, and decisions covered.
- **Impacted surfaces:** Record each `paths:Sxx` ID, impact chain, contract, applicable basis or regression scenarios, and justified exclusions or unknowns.
- **Coverage gaps:** Name each missing decision or scenario and the exact input or state adjustment needed.
- **Reachability:** Separate proven unreachable paths from unresolved reachability and cite the evidence.
- **Facts and inferences:** Label expected behavior inferred from code; it is not a product requirement.

Use verdict `mapped`, `gaps`, or `undetermined`, independently of coverage. Preserve scenario IDs from declared previous artifacts and explain removals. Return the output link, counts of entrypoints and scenarios, and at most two material gaps. Do not add generic code-review findings.
