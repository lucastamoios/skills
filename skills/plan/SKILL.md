---
name: plan
description: Create an implementation plan with tasks and verification traced to requirements and design decisions. Natural-language requests use the dev coordinator; prepared input/output files run only the planning stage. Planning does not authorize implementation.
user_invocable: true
argument-hint: "[initiative name] | input=<absolute input.md> output=<absolute output.md>"
---

# Plan

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Create a focused implementation plan for the assigned initiative. Trace tasks
to requirements and design decisions, and give every requirement a meaningful
verification method. Write enough context for a developer unfamiliar with the
initiative to execute it. Do not implement the plan or run its steps.

Argument: `$ARGUMENTS`

## Invocation and ownership

- For an ordinary natural-language request, route to
  [dev](../dev/SKILL.md). The coordinator resolves the
  requested scope and dispatches a fresh worker with the selected model. Do not
  execute this stage in the coordinator's context.
- With both `input=<absolute input.md>` and `output=<absolute output.md>`, act
  only as the assigned worker in `draft` mode. Read the
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

## Gather inputs and bound the plan

1. Read the declared requirements, designs, accepted upstream outputs, source
   snapshots, decisions, and answers. An initiative can cover selected requirements
   and decisions from several files; preserve those boundaries.
2. Read an existing plan for this initiative and preserve useful content and
   stable task and test IDs. Do not replace unrelated work or reset execution state.
3. Establish what the relevant code already does. Follow project context tools
   and inspect actual interfaces, callers, tests, and verification commands.
4. Use sufficient supplied documents even when their names or formats differ.
   Reference stable IDs or source anchors. If a material requirement or design
   decision is missing, return the gap rather than invoking another skill or
   inventing an upstream decision.

Resolve routine planning choices from evidence. For material unresolved choices,
return `needs-input` with stable question IDs, evidence, a recommendation when
useful, and the exact dependent work. Batch questions into one concise numbered
set. Preserve useful drafts and continue independent permitted work without
inventing answers or asking the user directly.

If the initiative covers independent subsystems or more than roughly 8-10
substantial tasks, consider a split into independently useful plans. Explain the
split in the output. Create multiple plans only when their paths and scope are
assigned. A small change may need only a short plan.

## Map responsibilities and order the work

Identify concrete files to create or change and their responsibilities. Use full
paths, verified symbols, and line references where useful. Distinguish existing
interfaces from proposed interfaces. Follow project patterns, and include a
targeted split only when it directly serves the design. Avoid unrelated restructuring.

Order behavior changes from the outside in:

1. Start from the relevant user entrypoint, such as a view, endpoint, CLI command,
   or UI interaction, and the behavior it must expose.
2. Introduce the needed services, persistence, and utilities through that caller.
3. Complete a working vertical slice before adding unrelated capabilities.

Avoid disconnected foundations with no planned consumer. Record necessary
prerequisites, such as migrations or external contract changes, and explain their
relation to visible behavior. Group tasks into complete, verifiable milestones.
State dependencies, the owner of each file, and which tasks can run independently
without shared writes. Do not assume parallelism merely because tasks have
separate names.

## Identify parallel implementation groups

Evaluate every implementation milestone for parallel execution. Give each complete
working unit a stable ID, explicit dependencies, exclusive writable files, runtime
resources, and a focused verification command. Group independent units into
parallel waves. A unit must retain its full red, green, refactor cycle; do not
split tests and implementation between agents.

Include an execution hint for every unit: `parallel` with its group ID, or
`serial` with the concrete dependency or shared resource that prevents overlap.
Separate file names alone do not prove independence. Check shared contracts,
migrations, generated files, dependency manifests, fixtures, and runtime state.
Schedule shared prerequisites first and shared edits as a separate serial unit.
If independence cannot be established, mark the unit serial and explain the gap.

Return this handoff in the canonical plan and reference it in the stage output:

| Unit | Milestone and tasks | Execution hint | Depends on | Exclusive writes | Runtime isolation | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| U1 | M1, Task 1 | parallel, G1 | <Unit IDs or none.> | <Exact paths.> | <Ports, databases, or other state.> | <Command and expected behavior.> |

For each group, name its prerequisite baseline, integration order, shared contract
assumptions, and joint verification after integration. Identify the next wave
that becomes ready when those checks pass. The dev coordinator creates worktrees,
dispatches all eligible independent units, and integrates their results. The plan
does not create worktrees, run agents, or authorize Git actions.

Keep each task small enough for a coherent implementation and verification cycle
without imposing a fixed duration. Include review checkpoints at complete working
milestones when they belong to the requested execution scope.

## Plan format

Use this structure when the project has no established equivalent. Replace paths
with actual canonical paths before saving:

```markdown
# Plan: <Initiative Name>

Created: YYYY-MM-DD
Status: draft

## Scope

**Requirements:** <absolute requirements path> (items 1-5)
**Design:** <absolute design path> (decisions D1-D3)
**Goal:** <The outcome this initiative delivers.>
**Architecture:** <The approach and its relevant design decisions.>
**Boundaries:** <Explicit exclusions and execution constraints.>

## Milestones

### M1: <Complete working outcome>

**Dependencies:** <Required earlier work, or none.>
**Ownership and parallelism:** <Assigned files and permitted independent tasks.>
**Verification:** <The check that demonstrates the complete outcome.>

## Tasks

### Task 1: <Observable behavior>

**Milestone:** M1
**Implements:** REQ 1, D1
**Files:** <Full paths and each file's responsibility.>
**Dependencies:** <Required earlier work, or none.>

- [ ] Add or extend a test through the existing entrypoint for <specific behavior>.
- [ ] Run <verified focused command> and confirm the assertion fails because <current observable behavior> differs from <required outcome>.
- [ ] Change <specific component and contract> so it produces <required outcome>.
- [ ] Run <verified focused command> and confirm the behavior passes.
- [ ] Refactor within the design boundaries while retaining behavior coverage.

**Acceptance:** <Observable evidence that the task satisfies its requirements.>
```

The default artifact is `<doc-root>/plans/<initiative>.md`. Use its assigned
absolute path. Describe inputs, outcomes, constraints, relevant interfaces, and
commands. Include a concise code example when it resolves a real ambiguity. A
plan need not contain the complete future implementation or duplicate code that
the implementer can derive from clear behavior and interfaces.

For a behavior change, the initial failure must demonstrate missing or incorrect
behavior at an existing entrypoint. An import error, missing symbol, syntax error,
or broken fixture does not establish a useful failing test. If an entrypoint is
new, state the observable absence to demonstrate through its real client or
boundary and the setup needed to make that check valid.

## Test design

Plan the smallest meaningful set of tests or manual checks that covers the
requirements and plausible regressions. Reuse or extend existing coverage before
adding a new test. Do not add tests solely to mirror a reversible, low-impact
edit or a file's current structure.

- Prefer integration tests through the relevant public entrypoint. In a web
  application, a view test often covers permissions, validation, persistence,
  and rendering together. Use focused unit tests for meaningful logic that
  broader tests cannot exercise clearly.
- Keep internal behavior real where practical. Mock external integrations or
  otherwise uncontrollable boundaries only when needed, and state what the mock
  prevents the test from proving.
- Test a reusable interaction with representative examples. If a change adds
  an instance of an existing pattern, extend its general behavioral coverage
  instead of asserting the new configuration entry by name.
- Cover relevant failures and boundaries without repeating the same assertion
  through many equivalent paths.
- Keep requirement and design traceability in the plan. Test names and docstrings
  describe behavior, not issue or requirement provenance.
- For each completed vertical slice, identify the integration check that proves
  the layers work together. Reuse an existing or planned check if it already
  establishes the result; do not mandate a duplicate test task.
- Identify temporary exploratory checks separately from durable regression tests.
  Retain tests that protect meaningful behavior, and avoid shipping redundant
  scaffolding merely because it helped during implementation.

Use repository-specific test runners and environment conventions. Do not present
a guessed command or expected output as verified. Record unavailable verification
prerequisites for the coordinator. These are instructions for future execution;
unexecuted tests have no observed red or green result.

Include a verification summary:

```markdown
## Tests

| ID | Validates | Method | Expected outcome |
|----|-----------|--------|------------------|
| T1 | REQ 1 | <Named automated test and command.> | <Observable result.> |
| T2 | REQ 2, 3 | <Named automated test and command.> | <Observable result.> |
| V1 | REQ 4 | <Concrete manual procedure and required setup.> | <Observable result.> |
```

Every active requirement in scope must have a verification method. Explain manual
verification when automation is unsuitable. Preserve existing test IDs when
updating a plan.

## Traceability and review

End the plan with a complete mapping:

```markdown
## Traceability

| Requirement | Design Decision | Milestone and Task | Verification |
|-------------|-----------------|--------------------|--------------|
| REQ 1 | D1 | M1, Task 1 | T1 |
| REQ 2 | D2 | M1, Task 2 | T2 |
| REQ 3 | D2 | M1, Task 2 | T2 |
| REQ 4 | D3 | M2, Task 3 | V1 |
```

Review the plan for:

1. Complete coverage of assigned requirements and design decisions.
2. A coherent outside-in sequence with consumers, dependencies, and file ownership.
3. Consistent paths, types, names, and interfaces across tasks.
4. Concrete outcomes and checks for errors, boundaries, and acceptance.
5. Unresolved placeholders or unsupported assumptions that block execution.

Phrases such as "add appropriate error handling" or "write tests for the above"
are insufficient without error cases or expected behavior. Replace them with
the information needed to act. Do not fill unknowns with fabricated code. Return
material gaps as questions or blockers with the corresponding status. Fix supported
issues and recheck affected mappings.

## Stage payload and boundary

Return complete milestones, sequence, allowed parallelism, file ownership,
verification commands and expected behaviors, traceability, dependencies, and
remaining questions. Documentation checks establish plan consistency, not
implemented behavior or passing product tests.

`complete` means only the assigned planning stage is complete. It does not mean
the plan was implemented. Recommend implementation only when it is within the
user's declared scope and `stop_after` boundary. The coordinator validates the
result before deciding any dispatch; the worker does not invoke code-tdd.

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
