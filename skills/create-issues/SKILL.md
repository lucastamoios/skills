---
name: create-issues
description: Split requirements, design specs, and plans into self-contained issues organized as independently verifiable outcomes. It reads from the project's docs/requirements/, docs/design/, and docs/plans/, creates the issues in Linear for the configured organization projects or as Obsidian task notes for a configured project and personal projects, embeds the full spec in each body, tags them as agent issues, and creates an epic parent when more than two issues are generated. It leaves the source docs in place and asks at the end whether to delete or move them.
user_invocable: true
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(python3 *), Bash(git remote *), Bash(git branch *), Agent, AskUserQuestion, ToolSearch, mcp__linear-server__save_issue, mcp__linear-server__get_issue, mcp__linear-server__list_issues, mcp__linear-server__list_teams, mcp__linear-server__list_issue_labels
argument-hint: "[initiative or plan name, e.g., 'authorization-export' or path to plan file]"
---

# Create Issues

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

This skill reads the requirements, design specs, and plans from the project repo and splits them into self-contained issues. Each issue delivers a coherent, verifiable outcome, contains its own requirements, design decisions, and tasks directly in the body, and is tagged as an agent issue.

Argument: `$ARGUMENTS`

## Step 1: Read the source material

1. Identify the project directory. If `$ARGUMENTS` points to a specific plan file (e.g., `docs/plans/learning-system.md`), use that. Otherwise, scan `docs/plans/` for plan files and ask the user which one to use.
2. Read the plan file. It should reference specific requirements and design files in its Scope section.
3. Read the referenced requirements files from `docs/requirements/`.
4. Read the referenced design files from `docs/design/`.
5. If there is no plan but there are requirements and design files, read those directly and work from them.
6. If there are only requirements files (no design, no plan), read those and work from them. The issues will contain only requirements and will need design and planning done within the issue itself.

## Step 2: Choose the destination

Resolve the project against `profile.work.task_destinations` using its Git remote, issue prefix, and current branch. Each route declares `linear` or `vault` and its destination. Read the destination's own instructions and template. If no route matches, ask where to create the tasks. Never infer that an unfamiliar organization belongs in the package author's workspace.

For Linear, discover the connected tools, team and label before creating issues. For a vault, read its root and project instructions and task template. Use the configured task helper where available. Report conflicting or unavailable routes instead of falling back to another destination.

## Step 3: Identify outcomes and dependencies

For each requirement or related group, identify the observable behavior it delivers, the layers needed to make it work, and the verification that establishes completion. Use these outcomes and real blocking dependencies to choose ticket boundaries. Do not estimate, target, or constrain lines of code.

The main criterion is comprehensibility. A reader of the issue must understand exactly what it delivers, and a reviewer of the resulting change must be able to understand what the code does and how it delivers that outcome. An issue does not need to be small. A large issue is fine when its outcome is one clear idea and its change reads as one coherent story.

Prefer a complete vertical slice through the relevant layers, including its tests. Each slice should be independently demoable or verifiable once its declared prerequisites are complete. Split only when one issue would mix outcomes that a reader must understand separately, or when independent outcomes, unresolved decisions, or integration risk justify it. Do not split a coherent outcome only to make the issues smaller.

A broad mechanical migration may need an expand, migrate, contract sequence instead. Add the compatible new form first, migrate consumers in coherent batches, and remove the old form only after all consumers have moved. Keep intermediate changes working where feasible. If independent integration is not possible, state that limitation and identify the final joint verification rather than promising each ticket can ship alone.

## Step 4: Group into issues

Each issue must:

- **State its outcome clearly.** The title and the first lines of the body say what the issue delivers and why, so a reader understands the goal before the details.
- **Deliver one coherent outcome.** Include all relevant layers required for that behavior, rather than creating separate schema, API, UI, and test tickets by default.
- **Be self-contained.** Include the relevant requirements, design decisions, tasks, and acceptance criteria in its body.
- **Include its verification.** Keep implementation and the tests that establish its behavior together. Scope tests by meaningful behavior and risks.
- **Declare actual blockers.** Mark a dependency only when the preceding outcome is necessary to start or verify this issue. Unrelated tickets can proceed independently.
- **Expose uncertainty.** Resolve or identify decisions that prevent implementation. Do not present unresolved product choices as agent-ready work.

Present the destination and the proposed grouping as a numbered list with each ticket's outcome, acceptance check, requirement references, and blockers:

> I plan to create N issues in <Linear team | a configured project vault, project folder | personal vault>:
> 1. <title>: <observable outcome>. Verification: <check>. Covers: <REQ IDs>. Blocked by: <ticket title or none>.
> 2. <title>: <observable outcome>. Verification: <check>. Covers: <REQ IDs>. Blocked by: <ticket title or none>.
> Does this grouping capture the right outcomes and dependencies?

Wait for approval before creating anything.

## Step 5: Create the epic parent (if more than 2 issues)

If you are creating more than two issues, first create a parent that serves as the epic. Its body contains:

- A summary of the initiative and its overall goal.
- The list of sub-issues as a checklist, filled in after creation. Do not repeat the title next to the link, because both Linear and Obsidian render the title from the link.
- The expected total scope.

In Linear:

```
save_issue(
  title: "<Initiative Name>",
  team: "<team from list_teams>",
  description: "<overview>",
  labels: ["agent issue"],
  assignee: "me",
  priority: 3
)
```

The checklist uses `- [ ] [<TEAM>-123](<url>)`.

In Obsidian, the epic is a task note created from the destination's template, with the `agent-issue` tag. The checklist uses `- [ ] [[<sub-issue note>]]`.

If you are creating one or two issues, skip the epic.

## Step 6: Create the issues

Every issue uses this body structure:

```markdown
## Requirements

<The specific requirements this issue addresses, with the text copied verbatim from the requirements file.>
<Only the list marker changes: write "- **REQ 1.** The system must..." instead of "1. The system must...". This keeps the original number when Linear or Obsidian renumbers ordered lists.>

## Design Decisions

<The specific design decisions this issue addresses, copied verbatim from the design file.>
<Each decision keeps its original ID (D1, D2, etc.).>
<If no design file exists, write "No design decisions yet. Design will be done as part of this issue.">

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

### Linear

```
save_issue(
  title: "<short descriptive title, no conventional commit prefix>",
  team: "<team from list_teams>",
  description: "<the structured body above>",
  labels: ["agent issue"],
  assignee: "me",
  parentId: "<epic issue identifier, only if epic was created>",
  priority: 3
)
```

If issue B needs code from issue A, set the dependency:

```
save_issue(id: "<issue B>", blockedBy: ["<issue A identifier>"])
```

### Obsidian

Create one task note per issue in the destination's task folder, from its template:

- Follow the destination's naming rule, initial lane, and language.
- Add the `agent-issue` tag.
- Set `parent` to a wikilink to the epic note, if an epic was created.
- Set `depends_on` to wikilinks for the blocking issues.
- Fill the template's outcome section with the observable outcome, and put the structured body after it.

In the personal vault, create each note with `profile.paths.scripts/tasks.py add --title ... --type Implement --realm ...`, and then edit the note to set `parent`, `depends_on`, the tag, and the body. In the a configured project vault, copy the project's template with `Write`.

After all issues exist, update the epic's checklist with the real links.

## Step 7: Report and ask about the source docs

Print a summary:

> "Created N issues in <destination>:
> - <identifier or note>: <title>. Delivers <outcome>. Blocked by <issue or none>.
> - <identifier or note>: <title>. Delivers <outcome>. Blocked by <issue or none>.
> ...
> [Epic: <identifier or note>: <name> (<url or path>)]"

Include the Linear URLs or the note paths so the user can review them.

Then ask the user what to do with the source files (the plan, design, requirements, and any `.feature` file): keep them, delete them, or move them somewhere else. Do nothing to them until the user answers. If the user chooses to delete or move them, also update `docs/requirements/index.md` and `docs/design/index.md` so that they do not list missing files. Do not commit. The user decides when to commit.

The work is picked up later through `dev`, which reads the issue or task note.

## Rules

- **Self-contained issues.** Every issue must have its own requirements, design, and tasks in the body. No "see file X" or "see issue Y" references for essential information.
- **Size by comprehensibility.** Split work so that each issue's goal and each resulting change are easy to understand. Size alone is never a reason to split, and line counts are not a planning metric or constraint.
- **One concern per issue.** Do not mix unrelated features or areas.
- **Outside-in order.** Mark dependencies between issues when they exist.
- **Always tag as an agent issue.** Use the `agent issue` label in Linear and the `agent-issue` tag in Obsidian.
- **Epic for 3+ issues only.** Create a parent when there are more than two sub-issues. Sub-issues point to it through `parentId` in Linear or `parent` in Obsidian.
- **Keep the source docs.** Never delete, move, or commit the source files on your own. Ask at the end.
- **Ask before creating.** Always present the destination and the grouping, and get user approval first.
- **No em-dashes or connector dashes.** Use the punctuation that means the same thing: commas, colons, periods, or parentheses. Hyphens inside compound words are fine.
- **Requirement completeness check.** Before creating each issue, verify that every requirement referenced in any design decision ("Addresses: REQ X, Y") is listed in the Requirements section of that issue. If a design decision says it addresses REQ 21 but REQ 21 is not in the requirements list, add it.
- **Verbatim requirements in bold REQ format.** Copy the requirement text exactly. Only the list marker changes to `- **REQ N.**`.
