---
name: risk
description: Trace changed production boundaries to real consumers, deployment failure modes, monitoring signals, and rollback limits. Produce an independent release-risk report.
---

# Risk Review

Determine what the rest of the system will observe when the change ships. Report risk only with a changed artifact, named consumer, and concrete failure mode.

## File interface

Read [the worker contract](../../protocol/contract.md). Accept `input=<absolute input.md> output=<absolute output.md>` with skill `risk` and mode `analyze`. Write the required report to this exclusive output. The input declares context, snapshot, sources, model, dependencies, access, and budget. Do not infer them from the parent conversation.

If invoked with a PR, branch, or diff instead of a prepared input, use `review:run` to prepare and dispatch this lens in its configured agent. Do not perform the worker analysis inline. Inside a worker, never dispatch another lens, discover a task, or edit shared review artifacts. Report missing prerequisites through the output.

Follow repository instructions and use Graft and LSP when required or available. Write artifacts in English. Verify the input snapshot before and after analysis. Keep the reviewed checkout unchanged and write only the assigned output and attachments, subject to this lens's explicit execution mode.

## Required context

Read the declared diff, deployment context, ticket and PR claims, and relevant source evidence. Claims describe intent, not proof of production behavior. Require current paths for changed application logic. Static or declarative changes with no meaningful behavioral decisions can skip paths; enumerate their boundaries directly and explain why. Do not set another lens's applicability status.

For the configured organization work, read the declared copy of `review-risk-learnings.md` when available and apply only matching boundary/consumer patterns. Propose reusable learnings in the output; the worker never edits the learning store. Missing environment or external-consumer evidence remains an explicit uncertainty.

Never deploy or run a production probe. Describe the exact proposed probe and required authorization in the report. Local execution also requires declared access and budget.

## Trace production boundaries

Inspect only boundary artifacts created, removed, or changed by the diff:

- HTTP requests and responses: status codes, redirects, headers, cookies, content types, body shapes, host and client-address interpretation.
- Browser behavior: CSP, CORS, cookie scope, HTMX or fetch semantics, cached assets, and frontend contracts.
- Proxy and topology behavior: forwarding, buffering, timeouts, body limits, WebSockets, compression, and path normalization.
- Cross-process contracts: cache keys and values, sessions, task payloads, events, log formats, and files.
- Persistence: migrations, backfills, constraints, production data shape, and ordering relative to deploys.
- Configuration: settings, environment variables, defaults, secrets, flags, and differences between environments.
- External consumers: APIs, webhooks, emails, exports, partners, and clients running older code.
- Observability: logs, metrics, status codes, Sentry grouping, dashboards, alerts, and runbooks.

For each changed artifact, find the real consumer in repository configuration, callers, infrastructure, deployment scripts, frontend code, or monitoring-as-code. Use LSP for symbols and repository-required context tools such as Graft. Name external consumers that the repository cannot prove.

## Test the release model

For each candidate risk, answer:

1. What artifact changes?
2. Which consumer observes it?
3. What exactly fails?
4. Why might staging or automated QA miss it?
5. Is old and new code overlap possible during deployment?
6. What observable signal would reveal the failure?
7. What safe probe can confirm behavior?
8. Does rollback restore behavior, or has durable state already escaped?

Drop risks that lack a named consumer or concrete failure. Prefer a few high-confidence risks.

## Output sections

Add these sections to the common output:

- **Change before release:** Record artifact, consumer, trigger, failure, evidence, and smallest corrective action for each finding.
- **Watch after release:** Record signal, location, bad threshold or pattern, and watch window.
- **Safe probes:** Describe the exact probe, environment, expected result, and required approval. A proposed probe is not execution evidence.
- **Residual unknowns:** Name inaccessible consumers or environment facts and their mitigation.
- **Rollback:** State whether revert is sufficient and whether durable state needs repair.
- **Proposed learnings:** Separate optional learning-store changes from review findings.

Use verdict `LOW`, `MEDIUM`, or `HIGH`, with explicit uncertainty and independent coverage. Use `undetermined` when a material missing fact prevents assessment. Return the output link, verdict, and at most two consequential items. Mention when paths did not apply.
