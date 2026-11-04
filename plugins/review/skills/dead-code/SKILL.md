---
name: dead-code
description: Assess dead-code candidates using runtime reachability and concrete planned consumers. Produce an independent decision table; remove confirmed dead code only in a separately selected cleanup mode.
---

# Dead Code

Remove code only when scoped usage and planning evidence establish that no real consumer needs it. An empty caller list or hypothetical future reuse is insufficient.

## File interface

Read [the worker contract](../../protocol/contract.md). Accept `input=<absolute input.md> output=<absolute output.md>` with skill `dead-code` and mode `findings-only or cleanup`. Write the required report to this exclusive output. The input declares context, snapshot, sources, model, dependencies, access, and budget. Do not infer them from the parent conversation.

If invoked with a PR, branch, or diff instead of a prepared input, use `review:run` to prepare and dispatch this lens in its configured agent. Do not perform the worker analysis inline. Inside a worker, never dispatch another lens, discover a task, or edit shared review artifacts. Report missing prerequisites through the output.

Follow repository instructions and use Graft and LSP when required or available. Write artifacts in English. Verify the input snapshot before and after analysis. Keep the reviewed checkout unchanged and write only the assigned output and attachments, subject to this lens's explicit execution mode.

## Mode and context

The parallel review pipeline always uses `findings-only`. A direct request to this skill retains its cleanup workflow unless the user asks for findings only, but `review:run` must dispatch cleanup as a separate exclusive job after analysis workers have finished. The cleanup input explicitly names mode `cleanup`, permitted edits, and the exclusive checkout. Do not infer cleanup authorization from an input that requests analysis.

Current paths and intent artifacts are useful optional inputs; this lens does not require another review. The input must declare initiative stage and planning sources, or identify those gaps. In findings-only mode, leave source, graph, and tests unchanged and report proposed actions. In cleanup mode, the explicit write permission overrides the general read-only worker rule only for the named scope. Capture a new result snapshot and mark prior evidence stale instead of combining it with the cleaned state.

## Establish scope and implementation stage

Identify the repository, checkout, comparison base, and requested PR, branch, epic, or directory. Inspect local changes before editing. Preserve unrelated user work. For a branch review, inspect changed code and code made obsolete by those changes; do not silently expand into repository-wide cleanup. Search consumers across the repository even when deletion scope is narrow.

Determine whether the review is at the end of the initiative or during implementation. A final PR does not necessarily complete its epic. Use the user's context and the actual delivery state. If the stage remains unclear, inspect both epic and implementation plans before classifying future use.

- At the end, start with the epic's scope, acceptance criteria, remaining children, follow-up work, and explicit deferrals. Open requirements or individual tickets where the epic leaves a candidate's intended use unclear. Completed or canceled tickets do not justify keeping scaffolding by themselves.
- During implementation, also inspect the relevant requirements, design or plan, pending tickets, dependencies, and stacked PRs. A helper can be unused in this checkout while its consumer is scheduled in the next ticket.

Use the project's established documentation home and available issue tools. Link every planned-use exception to a specific requirement, epic section, ticket, or consumer implementation. Check that the cited work actually needs this code; sharing a topic or epic is insufficient. A TODO or hypothetical reuse is not a plan. Do not claim to know all future needs: report that no planned consumer was found in the inspected sources.

## Gather usage evidence with Graft

Read repository instructions. Run `graft map` when unfamiliar with the repository. Check freshness with `graft check`; rebuild only in assigned scratch space if the graph is stale or missing; do not change the reviewed checkout in findings-only mode. Check the installed command's help when options differ. If Graft is unavailable or incomplete, report the coverage gap and use available LSP and focused source searches. Do not install or upgrade tools implicitly.

Use these queries according to the question:

```bash
graft ask "<feature, symbol, or candidate>" --source
graft skeleton <file>
graft callers <symbol> --depth all
graft callers <symbol> --direction out --depth all
graft grep --fixed "<symbol or registration key>"
```

Use qualified symbols and path filters to resolve ambiguous matches. Keep incoming-consumer searches broad enough to include other packages. Read exact source spans when the graph truncates a definition or omits a needed detail.

Ranked `graft ask` results are not exhaustive. Use `graft grep` for indexed occurrences and `rg` for unindexed configuration, templates, scripts, manifests, and documentation. Use LSP references or implementations, when available, to resolve semantic relationships the graph does not establish.

For each candidate, trace incoming references back to a real entrypoint. A group of helpers that only calls itself can be dead even though every helper has callers. Separate production reachability, test-only reachability, and legitimate development or operational tooling. Outgoing calls identify dependencies that may become orphaned after deletion; they do not prove that the candidate is used.

Check indirect and external consumers relevant to the candidate before deleting it:

- Framework routes, signals, lifecycle hooks, decorators, dependency injection, and plugin registration can invoke code without direct callers.
- Jobs, scheduled tasks, CLI commands, templates, dynamic imports, string-based dispatch, and import side effects can supply runtime entrypoints.
- Public exports, API clients, compatibility paths, feature flags, and stored configuration can have consumers outside the checkout. A disabled flag or lack of recent execution does not prove dead code.
- Historical migrations and serialized names can remain necessary for deployment, replay, or loading old data. Treat their removal as a separate lifecycle decision.
- Tests that only exercise an otherwise unreachable production helper do not establish production use. Test fixtures, build tools, and operational scripts can still have legitimate non-production consumers.

For unreachable branches, unused parameters, and unused return values, verify control flow, contracts, and side effects. A discarded result does not mean the call can be removed. Duplicated or unattractive code that is still used is outside this skill's dead-code criterion.

## Classify and act

Assign each candidate one of these outcomes:

| Outcome | Evidence and action |
|---------|---------------------|
| Remove | The scoped investigation found no live entrypoint or external contract, and inspected planning sources provide no concrete future consumer. Propose removal in findings-only mode; remove only in explicit cleanup mode. |
| Keep: used | A runtime, external, development, or operational consumer needs it. Record the consumer when its usage was non-obvious. |
| Keep: planned | A specific active requirement or ticket needs this implementation. Record the source and expected consumer. |
| Unresolved | Missing planning access, uncertain dynamic usage, incomplete indexing, or an external contract prevents a reliable decision. Preserve this candidate and identify the missing evidence. |

Missing evidence is not evidence of absence. Continue independent candidate assessments while leaving uncertain candidates intact. Perform supported removals only in cleanup mode. Record information or a decision that materially blocks a candidate in missing inputs. Do not keep everything merely because it might be useful someday, and do not remove currently used behavior merely because no future ticket mentions it.

In cleanup mode, delete confirmed dead implementations together with exclusively supporting imports, registrations, dependencies, and obsolete tests when those are also proven unused. Preserve tests that cover surviving contracts. Follow newly orphaned dependencies to a fixed point within scope. Do not replace removed code with commented copies, speculative abstractions, or compatibility stubs without consumers.

## Verify and report

In cleanup mode, run the relevant existing tests, type checks, build checks, or framework discovery checks for affected entrypoints. Add regression coverage only when a meaningful surviving contract needs protection. Passing tests alone do not prove that deletion is safe. If a check cannot run, state the limitation instead of claiming validation.

In cleanup mode, rebuild the graph after cleanup, search for remaining references, and inspect the final diff for dangling configuration and unrelated edits. Do not claim repository-wide absence when only a branch or directory was reviewed.

## Output sections

Add the reviewed scope and stage, candidate table, usage evidence, specific planning sources, proposed or completed removals, and validation to the common output. Use `Remove`, `Keep: used`, `Keep: planned`, and `Unresolved` for candidate decisions. Distinguish proposed deletion from performed deletion.

Use verdict `candidates-found`, `no-candidates`, `cleaned`, or `undetermined`, independently of coverage. For cleanup, include both input and result snapshot IDs, final diff, checks, and remaining candidates. A cleanup output cannot be consolidated as evidence for the original unchanged snapshot. Return the output link, mode, outcome, and material limits.
