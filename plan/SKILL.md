---
name: plan
description: Create an implementation plan for an initiative. It references specific requirements and design decisions from docs/requirements/ and docs/design/, produces a plan in docs/plans/, and generates test cases traced back to requirements. It bridges "what to build" and "building it."
user_invocable: true
allowed-tools: Bash(git *), Bash(gh *), Read, Grep, Glob, Agent, AskUserQuestion
argument-hint: "<initiative name, e.g., 'csv-export-revamp'>"
---

# Plan

This skill creates an implementation plan for an initiative. It reads the requirements and design specs, then produces a focused plan in `docs/plans/<initiative>.md` that a developer (or the executing-plans skill) can follow step by step.

The plan is the bridge between the structured "what and why" (requirements and design) and the actual work. Every step traces back to specific requirements and design decisions, and every requirement gets at least one test.

Argument: `$ARGUMENTS`

<HARD-GATE>
Do NOT write any implementation code or execute any plan steps. This skill produces a plan document only. Execution happens through `/code-tdd`, the executing-plans skill, or subagent-driven-development.
</HARD-GATE>

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for the codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, and how to verify it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Outside-in order. Frequent review points.

Assume they are a skilled developer, but know almost nothing about the toolset or problem domain. Assume they do not know good test design very well.

## Checklist

You MUST create a task for each of these items and complete them in order:

1. **Gather inputs** - read requirements, design specs, existing plans, and relevant codebase
2. **Scope the initiative** - confirm which requirements and design decisions this plan covers
3. **Map file structure** - identify which files will be created or modified
4. **Plan outside-in order** - start from user-facing behavior, work inward
5. **Draft the plan** - step-by-step tasks with traceability, tests, and acceptance criteria
6. **Build the traceability table** - link every requirement to its design decision, plan step, and test
7. **Verify completeness** - every requirement has a step and a test, no gaps in the table
8. **Self-review** - check for placeholders, type consistency, missing code
9. **Write plan file** - save to `docs/plans/<initiative>.md`
10. **User reviews written plan** - ask user to review the file before proceeding
11. **Offer execution handoff** - code-tdd, subagent-driven, or inline execution

## Gathering inputs

1. Ask the user which requirements and design files this plan covers. An initiative might span parts of multiple files (e.g., "requirements 1-5 from authorization.md and decisions D1-D3 from design/authorization.md").
2. Read all referenced files from `docs/requirements/` and `docs/design/`.
3. Read `docs/plans/` to check if a plan for this initiative already exists. If it does, read it and ask the user whether they want to update it or start fresh.
4. Explore the relevant parts of the codebase to understand what already exists and what needs to change. Use Glob and Grep to find models, views, serializers, services, and tests.

## Scope check

If the initiative covers multiple independent subsystems, suggest breaking it into separate plans (one per subsystem). Each plan should produce working, testable software on its own. If the initiative is too large (more than 8-10 steps), suggest splitting it.

## File structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- Prefer smaller, focused files over large ones that do too much. You reason better about code you can hold in context at once, and edits are more reliable when files are focused.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, do not unilaterally restructure, but if a file you are modifying has grown unwieldy, including a split in the plan is reasonable.

## Outside-in ordering

Tasks MUST be ordered from the outside in:

1. **Start with the outermost layer** the user interacts with (API endpoint, view, CLI command, UI component).
2. **Work inward** through each dependency: services, repositories, models, utilities.
3. Each task should produce something that connects to what was built in the previous task.

Never plan a task that builds something with no caller yet. If you catch yourself doing this, reorder.

## Plan document format

Every plan MUST start with this header:

```markdown
# Plan: <Initiative Name>

> **For agentic workers:** Use `/code-tdd` to implement each task. Use subagents for parallel execution or execute tasks inline. Steps use checkbox syntax for tracking.

Created: YYYY-MM-DD
Status: draft | in-progress | completed

## Scope

**Requirements:** docs/requirements/<topic>.md (items 1-5)
**Design:** docs/design/<topic>.md (decisions D1-D3)

**Goal:** <One sentence describing what this initiative delivers.>

**Architecture:** <2-3 sentences about the approach, referencing key design decisions.>

---
```

## Task structure

Each task follows TDD and includes exact file paths, complete code, and acceptance criteria tied to requirements:

````markdown
### Task N: <Component Name>

**Implements:** REQ 1, D1

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**

```python
# Implements REQ 1 from docs/requirements/authorization.md
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Refactor**

Review for code quality, architectural alignment with D1, and codebase consistency.

**Acceptance:** <How to verify this task is done. Reference the requirement it satisfies.>
````

Steps should be bite-sized (2-5 minutes each):
- "Write the failing test" is one step.
- "Run it to make sure it fails" is another step.
- "Implement the minimal code to make it pass" is another step.
- "Run the tests and make sure they pass" is another step.
- "Refactor" is another step.

## Integration test tasks

When a full vertical slice is complete (a task that connects the outermost layer to the deepest dependency), include an integration test task:

````markdown
### Task N: Integration test for <vertical description>

**Validates:** REQ 1, 2, 3

- [ ] **Step 1: Write integration test**

```python
# Integration test for REQ 1, 2, 3 from docs/requirements/authorization.md
def test_admin_can_export_records_as_csv():
    # Calls the API endpoint, goes through all real layers, verifies final outcome
    ...
```

- [ ] **Step 2: Run and verify it passes**

Run: `pytest tests/integration/test_authorization_export.py -v`
Expected: PASS
````

## Tests section

After the tasks, include a tests summary that ties every test back to requirements:

```markdown
## Tests

| Test | Validates | Description |
|------|-----------|-------------|
| T1 | REQ 1 | <What the test checks.> |
| T2 | REQ 2, 3 | <What the test checks.> |
| T3 | REQ 4 | <What the test checks.> |
```

Every requirement listed in the scope must have at least one test. If a requirement cannot be tested automatically, note how it should be verified manually.

## Traceability table

The plan MUST end with a traceability table that ties everything together:

```markdown
## Traceability

| Requirement | Design Decision | Plan Step | Test |
|-------------|-----------------|-----------|------|
| REQ 1 | D1 | Task 1 | T1 |
| REQ 2 | D2 | Task 2 | T2 |
| REQ 3 | D2 | Task 2 | T2 |
```

Every requirement in scope must appear in this table. If any requirement is missing, it means the plan has a gap that must be fixed.

## No placeholders

Every step must contain the actual content an engineer needs. These are plan failures that you must never write:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" or "add validation" or "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code because the engineer may be reading tasks out of order)
- Steps that describe what to do without showing how (code blocks are required for code steps)
- References to types, functions, or methods not defined in any task

## Self-review

After writing the complete plan, review it with fresh eyes:

1. **Traceability check:** Skim each requirement in scope. Can you point to a task that implements it and a test that validates it? List any gaps.
2. **Outside-in check:** Are the tasks ordered from user-facing behavior inward? Is there any task that builds something with no caller yet?
3. **Placeholder scan:** Search for any of the patterns from the "No placeholders" section above. Fix them.
4. **Type consistency:** Do the types, method signatures, and property names used in later tasks match what was defined in earlier tasks? A function called `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.
5. **Completeness:** Does the traceability table have a row for every requirement? If not, add the missing tasks or tests.

Fix any issues inline. No need to re-review, just fix and move on.

## User review gate

After the self-review passes, ask the user to review the written plan:

> "Plan saved to `docs/plans/<initiative>.md`. Please review it and let me know if you want to make any changes before we start implementation."

Wait for the user's response. If they request changes, make them and re-run the self-review. Only proceed once the user approves.

## Execution handoff

After the user approves the plan, offer the execution choice:

> "Plan complete. Three execution options:
>
> **1. Code TDD** - Run `/code-tdd` for each task manually. Best for careful, hands-on work.
>
> **2. Subagent-Driven (recommended for larger plans)** - I dispatch a fresh subagent per task, review between tasks, fast iteration.
>
> **3. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints.
>
> Which approach?"

- If code-tdd: the user will run `/code-tdd` themselves for each task.
- If subagent-driven: dispatch a fresh Agent per task, review between tasks.
- If inline: execute tasks sequentially in the current session with review checkpoints.

## Key principles

- **Traceability is mandatory.** Every requirement must have a design decision, a plan step, and a test. The traceability table must be complete.
- **Outside-in order.** Start from user-facing behavior, work inward. Never plan something with no caller.
- **TDD always.** Write the failing test first, then implement.
- **Bite-sized steps.** Each step should take 2-5 minutes.
- **No placeholders.** Every step has actual code, actual commands, and actual expected output.
- **Exact file paths.** Always include the full path to every file being created or modified.
- **DRY, YAGNI.** Do not add features or abstractions that are not required by the requirements.
- **Integration tests per vertical.** When a slice connects all layers, test it end-to-end.
- **Do not use em-dashes.** Use hyphens, commas, or parentheses instead.
