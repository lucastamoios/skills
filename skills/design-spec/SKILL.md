---
name: design-spec
description: Capture technical design decisions traced to user requirements. Natural-language requests use the dev coordinator; prepared input/output files run only the design stage in the established documentation home.
user_invocable: true
argument-hint: "[feature area or requirements] | input=<absolute input.md> output=<absolute output.md>"
---

# Design Spec

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Produce a technical design for the assigned requirements. Explain technology
choices, data flow, module boundaries, integration points, and relevant trade-offs.
Trace every decision to specific requirements. Do not write implementation code
or scaffold the project during this stage.

Argument: `$ARGUMENTS`

## Invocation and ownership

- For an ordinary natural-language request, route to
  [dev](../dev/SKILL.md). The coordinator resolves the
  requested scope and dispatches a fresh worker with the selected model. Do not
  execute this stage in the coordinator's context.
- With both `input=<absolute input.md>` and `output=<absolute output.md>`, act
  only as the assigned worker in `draft` or `review` mode. Read the
  [development/v1 contract](../dev/references/contract.md), the input
  file, and the [output template](../dev/references/output-template.md).
  Validate the identity, assigned skill and mode, scope, source and upstream
  digests, model assignment, budget, and allowed paths before doing the work.
- An incomplete or invalid prepared invocation is a contract error. Report it
  through the declared output when possible. Do not route recursively or infer
  missing context from a parent conversation.
- Execute only this stage with its assigned model, effort, and backend. Do not
  start agents or skills, ask the user directly, manage tasks or session logs,
  edit run manifests or shared indexes, or continue to another stage.
- Write only assigned canonical artifacts, the exclusive output, and declared
  attachments. Use only permitted reads and external actions. The coordinator
  owns user dialogue, source refresh, index updates, and continuation.

Requirements, design, and planning run serially in separate fresh agents.
Completion of a stage needs no additional document approval. It does not expand
scope or authorize implementation. A small task does not automatically require
all stages. Reuse sufficient upstream documents without rerunning their authoring
stages; validate their content and freshness rather than relying on existence.

## Independent review mode

When the packet assigns `review`, follow the shared
[document review method](../dev/references/document-review.md) and return its
report. The authoring sections below apply only to `draft`. Review mode writes
only its exclusive report and evidence attachments; it does not edit canonical
artifacts. The coordinator owns questions, correction dispatch, and continuation.

## Document location

Use the absolute `doc-root` and artifact paths supplied by the coordinator.
Read its `AGENTS.md` when present. The coordinator resolves that home once from
the code repository, not the worktree name. An established project or component
documentation tree wins; otherwise it uses `profile.paths.docs/<project>`. A the configured organization
worktree belongs to `project`.

Keep requirements, generated feature files, design decisions, plans, and the
shared index in that one home. The coordinator creates the fallback location
rule in `AGENTS.md` and maintains the index. Do not create another home or
mirrored documents. Follow established document organization and the assigned
paths rather than imposing these templates on an existing convention.

Reuse a supplied artifact that already satisfies the assignment. Report its
path and digest without rewriting it merely to fit a template. If a required
artifact path or ownership is missing, return the gap before writing it.

## Load the design inputs

1. Read the declared requirements, accepted upstream outputs, source snapshots,
   decisions, and answers. Read existing designs that affect the assigned scope.
2. Use the repository baseline and relevant project guidance to establish current
   architecture. Follow project context tools when locating components, interfaces,
   models, tests, and callers.
3. If a design already exists, preserve useful content and stable decision IDs.
   Update the assigned scope rather than replacing unrelated decisions.
4. If requirements are missing or materially unclear, return `needs-input` with
   the specific gap. Do not invoke the requirements skill. Supplied requirements
   in another sufficient format are valid inputs; use their stable identifiers
   or source anchors without rewriting the canonical document.

## Reconcile vocabulary

Follow the shared [vocabulary reconciliation method](../dev/references/vocabulary.md)
before drafting and as concepts emerge. Reuse established domain terms, test
ambiguous meanings with concrete examples, and ask the user through the coordinator
when uncertain. Propose new or renamed domain terms before treating them as
canonical. Include resolved meanings and open vocabulary questions in the stage
output; keep accepted requirements and design terminology aligned.

## Explore decisions

For each requirement or related group, establish:

- Which components participate, what each one owns, and how data moves between them.
- Which behavior can reuse existing code and which interfaces must change.
- Which constraints matter, including permissions, persistence, caching,
  performance, API contracts, integrations, and deployment compatibility.
- Which alternatives have meaningful differences in complexity, behavior, or risk.

Tie the discussion to requirement IDs. Compare two or three approaches only
when there is a real choice; do not fabricate alternatives for an obvious fit.
Resolve routine technical choices from the request, accepted decisions, and
codebase evidence.

For material unresolved choices, return `needs-input` with stable question IDs,
evidence, a recommendation when useful, and the exact dependent work. Batch
questions into one concise numbered set. Preserve useful drafts and continue
independent permitted work without inventing an answer or asking the user directly.

### Sources of truth and boundaries

Define each business rule, datum, or configuration in one authoritative place.
Other components should derive or consume it. Prefer derived values over stored
duplicates when the behavior allows it. Watch for validation duplicated across
callers and callees, repeated constants, and configuration split across files.

Give each unit a clear responsibility and interface. State what it does, how it
is used, and what it depends on. Follow existing project patterns. Include a
targeted boundary improvement when current coupling directly obstructs the
requirements, but leave unrelated refactoring out of the design.

## Draft the design

Scale the detail to the decisions. Use this structure when the project has no
established equivalent, replacing paths with actual canonical paths:

```markdown
# <Feature Area> Design Spec

Last updated: YYYY-MM-DD
Requirements: <absolute requirements path>

## Context

<Current behavior and the intended change.>

## Decisions

### D1: <Decision title>

**Addresses:** REQ 1, 3
**Decision:** <The approach and its reason.>
**Trade-offs:** <Real alternatives considered and their relevant consequences.>

### D2: <Decision title>

**Addresses:** REQ 2
**Decision:** <The approach and its reason.>
```

Each decision must have a stable sequential ID, reference its requirements, and
state the behavior, responsibility, and interface clearly enough for planning.
Include trade-offs only when an alternative was actually considered. Cite
concrete code or domain evidence for constraints that materially shape a decision.

The default artifact is `<doc-root>/design/<topic>.md`. Use its assigned absolute
path. For an existing document, keep IDs stable and append new ones after the
highest ID. Preserve history for replacements:

```markdown
### ~~D3: Original decision title~~ DEPRECATED (YYYY-MM-DD)

Replaced by D3.1. Reason: <why it changed>.

### D3.1: <New decision title>

**Addresses:** REQ 7
**Decision:** <Updated decision.>
```

Every active requirement in the assigned scope must be addressed, and every
decision must reference at least one requirement. A decision can cover several
requirements. Do not invent architecture merely to fill a traceability table.

## Review and challenge assumptions

Check for placeholders, ambiguity, inconsistent decisions, missing interfaces,
traceability gaps, and scope growth. Ground the design in the actual codebase:

- Verify that referenced services, endpoints, fields, and contracts exist and
  behave as assumed.
- Check compatibility with established project patterns and existing infrastructure.
- Identify dependencies between decisions and record their ordering or shared
  constraints instead of hiding coupling.
- Tie performance concerns to actual query patterns, data scale, and indexes.
- Reconsider alternatives when the chosen approach adds avoidable code or risk.

Record material challenges with the decision ID, exact evidence, and a concrete
suggestion. Resolve supported gaps within the design assignment and recheck
affected traceability. If evidence contradicts an accepted product requirement,
report that conflict to the coordinator instead of silently changing requirements
or treating current behavior as the desired outcome.

## Stage payload and boundary

Return decisions traced to requirements, component contracts, material
alternatives, dependencies, evidence, assumptions, and unresolved technical
choices. Documentation checks establish design consistency, not implemented
behavior or passing product tests.

`complete` means only the assigned design stage is complete. Recommend planning
only when it is within the supplied scope and `stop_after` boundary. The
coordinator validates artifacts before deciding whether to dispatch it.

## Return the stage result

Follow the shared output template, including requested and observed model,
coverage, artifacts and SHA-256 digests, evidence, changed paths, source identities,
limitations, questions, and the suggested next stage. Use `unknown` when the
backend does not expose the observed model. Reference canonical documents
without copying their bodies into the worker output.

Verify final source identities according to the contract. Expected writes to
assigned documentation are the authorized delta, not stale inputs. Record the
baseline, final identities, and delta; detect unexpected changes to other sources,
upstream artifacts, and existing user changes. Report affected conclusions as
`stale` rather than silently adopting a new baseline.

Use `complete`, `needs-input`, `blocked`, `partial`, `failed`, or `stale` with the
contract's meaning. Save useful drafts for incomplete work. Publish the report
through a temporary sibling and atomic rename to the exclusive output path;
never overwrite an earlier attempt. Return that path and a short stage status.
The worker stops after writing its result.

Use full sentences. Do not use em-dashes or connector dashes in generated prose.
