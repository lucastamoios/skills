---
name: code
description: Find high-confidence correctness, security, contract, concurrency, and error-path defects in a declared change. Produce independent findings with source and learning evidence. Do not compare requirements.
---

# Code Review

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Find concrete defects in changed behavior. Do not perform intent, architecture, release-risk, or manual QA review.

## File interface

Read [the worker contract](../../protocol/contract.md). Accept `input=<absolute input.md> output=<absolute output.md>` with skill `code` and mode `analyze`. Write the required report to this exclusive output. The input declares context, snapshot, sources, model, dependencies, access, and budget. Do not infer them from the parent conversation.

If invoked with a PR, branch, or diff instead of a prepared input, use `review:run` to prepare and dispatch this lens in its configured agent. Do not perform the worker analysis inline. Inside a worker, never dispatch another lens, discover a task, or edit shared review artifacts. Report missing prerequisites through the output.

Follow repository instructions and use Graft and LSP when required or available. Write artifacts in English. Verify the input snapshot before and after analysis. Keep the reviewed checkout unchanged and write only the assigned output and attachments, subject to this lens's explicit execution mode.

## Required context

Require a current path artifact when production behavior changes. For a static or test-only change, record why no production map applies. Read the declared diff, surrounding code, mapped entrypoints, callers, dependencies, and relevant history. Do not read requirements or plans to judge alignment; intent owns that work.

The coordinator declares the configured organization learning retrieval in the input. If it is unavailable or outside the permitted access, record that limitation. A tests artifact is optional and does not replace independent inspection of a concrete test defect found here.

## Retrieve the configured organization learnings broadly

For the configured organization reviews, use `<configured-learnings-command>`. Never read `docs/codebase-learnings.json` or another learnings JSON file.

Select every applicable learning type from the changed surfaces:

- Models and querysets: `orm`, `multi_tenancy`, `security`, `permissions`, `performance`.
- Views and APIs: `api_design`, `permissions`, `security`, `multi_tenancy`, `error_handling`.
- Services and workflows: `code_review`, `error_handling`, `performance`.
- Tests: `test_patterns`.
- Celery tasks: `celery_async`, `error_handling`, `observability`.
- Migrations and persistence: `database`, `migrations`.
- Frontend behavior: `frontend`, `security`, `api_design`.

Favor recall during retrieval. For every applicable type, run:

```bash
<configured-learnings-command> list --limit 100 --type <type> --json
```

Identify key changed functions from the path artifact and call graph. Include entrypoints, high fan-in or high fan-out symbols, authorization or tenancy boundaries, state transitions, persistence operations, external calls, and concurrency-sensitive functions.

For each key function, run both an exact symbol search and a semantic behavior search:

```bash
<configured-learnings-command> search "<function-or-class-name>" --limit 20 --json
<configured-learnings-command> similar "<symbol name, purpose, data flow, and suspected failure modes>" --limit 20 --json
```

Also run up to three broad semantic queries for the change's main behavioral surfaces, with `--limit 20`. Deduplicate all results by learning ID. Use `<configured-learnings-command> show <id>` when a relevant result needs full detail.

Retrieve generously, but do not turn retrieval volume into findings. A learning becomes review evidence only when its pattern, boundary, and failure mechanism apply to the current code. Record the queries, retrieved IDs, and applied IDs in the output.

If `<configured-learnings-command>` fails, record the exact failure and continue without learnings. Do not fall back to JSON and do not claim that learnings were checked.

## Investigate defects

Trace suspicious behavior through callers and dependencies. Check:

- Null, empty, boundary, duplicate, malformed, and unexpectedly large inputs.
- Incorrect boolean logic, defaults, types, early returns, loops, and exception handling.
- Authorization, tenant isolation, input validation, injection, XSS, secrets, and path traversal.
- Race conditions, non-atomic changes, retries, duplicate delivery, partial failure, and stale state.
- Changed signatures, return shapes, serialized contracts, cache formats, and all affected consumers.
- Resource leaks, swallowed failures, misleading success responses, and inconsistent persistent state.
- Tests that assert implementation details, omit changed outcomes, or would also pass before the fix.

Use the path scenarios to avoid missing changed decisions. Run focused read-only checks when useful. Do not perform the environment-changing execution owned by `review:qa`.

Report only high-confidence defects with a concrete failure scenario and smallest corrective action. Do not flag uncertainty as a finding. Put unresolved questions in the output only when they materially limit the review.

Classify findings as:

- `Must fix`: A real correctness, security, data-integrity, isolation, or critical contract failure.
- `Should fix`: A credible lower-impact defect or test weakness that can let changed behavior regress.

## Output sections

Add findings, learning queries and retrieved/applied IDs, and material open questions to the common output. Each finding identifies the input or state that triggers the wrong outcome, exact location, evidence, impact, and smallest fix. Point out suspected overlaps by ID; consolidation owns merging.

Use verdict `FAIL` for Must fix findings, `CONCERNS` for Should fix findings, and `PASS` when neither exists within sufficient coverage. Use `undetermined` when evidence prevents a conclusion. A known defect can coexist with partial coverage. Return the output link, verdict, and at most two high-impact findings.
