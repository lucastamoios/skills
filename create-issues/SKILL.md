---
name: create-issues
description: Split requirements, design specs, and plans into self-contained Linear issues targeting ~200-300 LOC each. It reads from the project's docs/requirements/, docs/design/, and docs/plans/, creates issues with the full spec embedded in the body, tags them with "agent issue", and creates an epic parent issue when more than two issues are generated. It deletes the repo docs files after the issues are created.
user_invocable: true
allowed-tools: Bash(git *), Read, Grep, Glob, Agent, AskUserQuestion, mcp__linear-server__save_issue, mcp__linear-server__get_issue, mcp__linear-server__list_issues
argument-hint: "[initiative or plan name, e.g., 'authorization-export' or path to plan file]"
---

# Create Issues

This skill reads the requirements, design specs, and plans from the project repo and splits them into self-contained Linear issues. Each issue targets ~200-300 lines of implementation code, contains its own requirements, design decisions, and tasks directly in the body, and is tagged with "agent issue."

Argument: `$ARGUMENTS`

## Step 1: Read the source material

1. Identify the project directory. If `$ARGUMENTS` points to a specific plan file (e.g., `docs/plans/learning-system.md`), use that. Otherwise, scan `docs/plans/` for plan files and ask the user which one to use.
2. Read the plan file. It should reference specific requirements and design files in its Scope section.
3. Read the referenced requirements files from `docs/requirements/`.
4. Read the referenced design files from `docs/design/`.
5. If there is no plan but there are requirements and design files, read those directly and work from them.
6. If there are only requirements files (no design, no plan), read those and work from them. The issues will contain only requirements and will need design and planning done within the issue itself.

## Step 2: Estimate implementation size

For each plan task (or group of related requirements if no plan exists), estimate the lines of code that will be produced:

- If the plan has code blocks, count the lines in those blocks as a rough estimate.
- If the plan has file paths with line ranges for modifications, use those ranges.
- If no plan exists, use heuristics: each requirement typically produces 20-50 LOC depending on complexity (a simple validation is ~20, a new endpoint with serializer is ~50, a new service with multiple methods is ~80-100).
- **Test code counts as only 50-100 LOC regardless of actual size.** Tests and test helpers can be verbose, so they should not inflate the estimate. Cap test LOC at 100 when calculating issue size.
- The target is ~200-300 LOC per issue. Some issues will be smaller and some larger, but the average should land in that range.

## Step 3: Group into issues

Split the work into issues. Each issue should:

- **Be cohesive.** It should tackle one thing, not multiple unrelated concerns. Group requirements and tasks that belong together (e.g., "authorization export endpoint" = the endpoint, the serializer, the permissions check, and the tests).
- **Be self-contained.** Someone working on this issue should not need to read another issue to understand what to do. All relevant requirements, design decisions, and tasks must be in the issue body.
- **Target ~200-300 LOC.** Use the estimates from Step 2 to split. If a single task is already ~300 LOC, it becomes its own issue. If three small tasks together are ~250 LOC, group them.
- **Follow outside-in order.** If issue B depends on code from issue A, mark that dependency.

Present the proposed grouping to the user:

> "I plan to create N issues:
> 1. <title> (REQ 1-3, D1, Tasks 1-2, ~250 LOC)
> 2. <title> (REQ 4-5, D2, Task 3, ~200 LOC)
> ...
> Does this grouping look right?"

Wait for approval before creating anything.

## Step 4: Create the epic parent issue (if more than 2 issues)

If you are creating more than two issues, first create a parent issue that serves as the epic:

```
save_issue(
  title: "<Initiative Name>",
  team: "<your-linear-team>",
  description: "<overview>",
  labels: ["agent issue"],
  assignee: "me",
  priority: 3
)
```

The epic description should contain:
- A summary of the initiative and its overall goal.
- The full list of sub-issues as a checklist with markdown links, updated after creation with actual identifiers and URLs (e.g., `- [ ] [<TEAM>-123](https://linear.app/.../<TEAM>-123): Title (~200 LOC)`).
- The expected total scope.

If you are creating one or two issues, skip the epic.

## Step 5: Create the issues

For each issue in the grouping, create a Linear issue with this body structure:

```markdown
## Requirements

<The specific requirements this issue addresses, copied verbatim from the requirements file.>
<Use unordered list with bold REQ numbers to prevent Linear from auto-renumbering.>
<Format: "- **REQ 1.** The system must..." instead of "1. The system must...">

## Design Decisions

<The specific design decisions this issue addresses, copied verbatim from the design file.>
<Each decision keeps its original ID (D1, D2, etc.).>
<If no design file exists, write "No design decisions yet - design will be done as part of this issue.">

## Tasks

<The specific tasks from the plan, with TDD steps, file paths, and acceptance criteria.>
<If no plan exists, write a brief task outline based on the requirements.>

## Tests

<The specific test descriptions relevant to this issue, copied from the plan's Tests table.>
<Format: "- **TN.** Description of what the test validates">
<Every test referenced in the Traceability table must be described here.>

## Traceability

| Requirement | Design Decision | Task | Test |
|-------------|-----------------|------|------|
| REQ 1 | D1 | Task 1 | T1 |

## Acceptance Criteria

<Derived from the requirements. Each criterion maps to a specific requirement number.>

## Notes

<Any additional context, dependencies on other issues, or things to watch out for.>
```

For each issue:

```
save_issue(
  title: "<short descriptive title, no conventional commit prefix>",
  team: "<your-linear-team>",
  description: "<the structured body above>",
  labels: ["agent issue"],
  assignee: "me",
  parentId: "<epic issue identifier, only if epic was created>",
  priority: 3
)
```

If there are dependencies between issues (issue B needs code from issue A), set them:

```
save_issue(id: "<issue B>", blockedBy: ["<issue A identifier>"])
```

If an epic was created, update its description to include the actual issue identifiers in the checklist.

After all issues are created, add links between them so they are easy to navigate. For each sub-issue, add a link to the epic. For each epic, add links to all sub-issues:

```
save_issue(
  id: "<sub-issue identifier>",
  links: [{"url": "<epic Linear URL>", "title": "Epic: <epic title>"}]
)
```

```
save_issue(
  id: "<epic identifier>",
  links: [{"url": "<sub-issue Linear URL>", "title": "<sub-issue title>"}]
)
```

## Step 6: Delete the repo docs files

After all issues are created successfully, delete the source files from the repo:

- Delete the plan file from `docs/plans/`.
- Delete the design file from `docs/design/`.
- Delete the requirements file from `docs/requirements/`.
- Delete the `.feature` file from `docs/requirements/` (if it exists).
- Update the project's `docs/index.md` to remove the entries for the deleted files.
- Commit the deletions.

The content now lives in the Linear issues. When each issue is completed, `/code-tdd` will move the requirements, design, and plan content back into the repo docs.

## Step 7: Report

Print a summary:

> "Created N issues in Linear:
> - <TEAM>-XXXX: <title> (~250 LOC)
> - <TEAM>-YYYY: <title> (~200 LOC)
> ...
> [Epic: <TEAM>-ZZZZ: <name> (<url>)]
> 
> Source files have been deleted from the repo."

Include the Linear URLs so the user can review them.

## Rules

- **Self-contained issues.** Every issue must have its own requirements, design, and tasks in the body. No "see file X" or "see issue Y" references for essential information.
- **Target ~200-300 LOC.** Test code counts as only 50-100 LOC regardless of actual size.
- **One concern per issue.** Do not mix unrelated features or areas.
- **Outside-in order.** Mark dependencies between issues when they exist.
- **Always tag with "agent issue."** The label already exists in Linear.
- **Epic for 3+ issues only.** Create a parent issue when there are more than two sub-issues. Sub-issues use `parentId` to link to the epic.
- **Delete repo files after creation.** The issues are the source of truth now.
- **Ask before creating.** Always present the grouping and get user approval first.
- **Do not use em-dashes.** Use hyphens, commas, or parentheses instead.
- **Requirement completeness check.** Before creating each issue, verify that every requirement referenced in any design decision ("Addresses: REQ X, Y") is listed in the Requirements section of that issue. If a design decision says it addresses REQ 21 but REQ 21 is not in the requirements list, add it.
- **Use bold REQ format.** Requirements must use `- **REQ N.** text` format (unordered list with bold prefix) to prevent Linear from auto-renumbering.
- **No title duplication in epic checklist.** Linear auto-renders issue links with the title, so the epic checklist should use `- [ ] [<TEAM>-123](url) (~N LOC)` without repeating the title text.
