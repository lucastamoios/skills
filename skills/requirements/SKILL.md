---
name: requirements
description: Capture testable user requirements and BDD scenarios for a feature area. Natural-language requests use the dev coordinator; prepared input/output files run only the requirements stage. Requirements describe user behavior and business needs, with stable IDs and one canonical documentation home.
user_invocable: true
argument-hint: "[feature area or ticket] | input=<absolute input.md> output=<absolute output.md>"
---

# Requirements

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Turn the assigned feature scope into structured, testable user requirements and
BDD scenarios. Capture the "what and why" from the user and business perspective.
Architecture and technology choices belong to the design stage.

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

## Load and bound the work

When supplied, reuse the validated `take` brief and clarification answers as
upstream context. Preserve established concepts, evidence limits, and question
IDs. Do not repeat resolved intake questions without new conflicting evidence.
Translate confirmed direction into testable requirements; do not treat proposals
or unanswered Product questions in the brief as accepted behavior.

1. Read the declared request, source snapshots, decisions, answers, and existing
   requirements. Use the repository baseline and relevant project guidance to
   establish current behavior. Follow project context tools before inspecting code.
2. Establish who is affected, what observable behavior is needed, why it matters,
   what is out of scope, and which failures or edge cases matter.
3. Resolve routine choices from evidence. Distinguish explicit user requirements,
   existing behavior, and assumptions.
4. For material unresolved choices, return `needs-input` with stable question
   IDs, evidence, a recommendation when useful, and the exact dependent work.
   Batch questions into one concise numbered set. Preserve useful drafts and
   continue independent permitted work without inventing answers or asking the
   user directly.

If the input names a ticket, use its supplied snapshot or permitted read access
and capture retrieved content as required by the contract. A ticket identifier
does not grant external mutation authority.

If the feature spans independent areas, propose a split with concrete reasons
in the output. Compare grouping options only when the split is materially
unclear. Create multiple files only when their scope and paths are assigned.
Consider splitting beyond roughly 20-25 requirements, but do not fragment a
small coherent feature to satisfy a size target.

## Reconcile vocabulary

Follow the shared [vocabulary reconciliation method](../dev/references/vocabulary.md)
before drafting and as concepts emerge. Reuse established domain terms, test
ambiguous meanings with concrete examples, and ask the user through the coordinator
when uncertain. Propose new or renamed domain terms before treating them as
canonical. Include resolved meanings and open vocabulary questions in the stage
output; keep accepted requirements and design terminology aligned.

## Draft requirements

Each requirement must:

- Have a stable sequential number local to the file, which acts as its namespace.
- Describe one observable behavior or constraint in one sentence.
- Be specific enough for automated or manual verification.
- Express the user's need independently from technology choices.

"Users can export data as CSV" is a requirement. "The system uses pandas to
generate CSV" is a design choice. Preserve technical constraints supplied by
the user in the worker output for the design handoff without presenting them
as behavior requirements.

Use this structure when the project has no established equivalent:

```markdown
# <Feature Area> Requirements

Last updated: YYYY-MM-DD

## Context

<What this feature area does and why it matters.>

## Requirements

1. <Observable behavior or constraint.>
2. <Observable behavior or constraint.>
```

The default artifact is `<doc-root>/requirements/<topic>.md`. Use its declared
absolute path. For an existing file, preserve useful content and existing
numbers. Append new requirements after the highest number. Preserve history
when replacing a requirement:

```markdown
3. ~~Original requirement text.~~ DEPRECATED (YYYY-MM-DD): Replaced by 3.1. Reason: <why it changed>.
3.1. <Replacement requirement.>
```

Do not add requirements that the request and evidence do not justify. A short,
complete set is sufficient for a small assigned scope.

## Generate BDD scenarios

Translate every active requirement in scope into one or more Gherkin scenarios.
Cover the relevant happy path, failure cases, and boundaries. Each scenario
must identify the requirement it validates:

```gherkin
Feature: <Feature Area>
  <Business context.>

  # REQ 1
  Scenario: <User action and expected outcome>
    Given <precondition>
    When <action>
    Then <observable outcome>
```

Save the feature file beside its requirements at the assigned canonical path,
normally `<doc-root>/requirements/<topic>.feature`. Executable feature files in
an existing BDD suite are test artifacts; do not create another documentation
copy there. Preserve useful scenario coverage when updating supplied artifacts,
and account for deprecated requirements explicitly.

## Review and challenge assumptions

Review both artifacts for testability, ambiguity, placeholders, scope, and BDD
alignment. Every active requirement must have a scenario; every scenario must
map to an active requirement in scope. Do not silently choose between materially
different product meanings to remove ambiguity.

Stress-test requirements against the relevant code, data model, existing tests,
and domain sources. Look for:

- Assumptions contradicted by current state, such as a supposedly required field
  that can be absent.
- Requested behavior that already exists or conflicts with current permission
  and tenancy rules.
- Missing failures, empty collections, deleted records, or concurrent changes
  that matter to the requested behavior.
- Scope that unexpectedly crosses modules or excludes a necessary dependency.

Record material challenges with a requirement reference, exact evidence, and
a concrete suggestion. For example:

> **Challenge 1 (REQ 3):** Requirement 3 assumes the field is always present. The cited model allows a blank value. The requirement needs an outcome for that case.

Resolve evidence-supported gaps within the assignment, then recheck affected
coverage. Return material product choices under questions. Do not turn an
unresolved source conflict or decision into an invented complete requirement.

## Stage payload and boundary

Return stable requirement IDs, observable criteria, BDD mapping, scope, product
sources, material challenges, assumptions, and questions. Include technical
constraints supplied for a later design stage. Documentation checks establish
consistency; generated Gherkin does not establish passing product tests.

`complete` means only the assigned requirements stage is complete. Recommend
design only when it is within the supplied scope and `stop_after` boundary.
The coordinator validates artifacts before deciding whether to dispatch it.

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
