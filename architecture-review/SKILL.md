---
name: architecture-review
description: Review a PR or diff for architectural quality - SOLID principles, codebase consistency, dependency direction, error handling, data flow, test architecture, performance, and security. It reads the code review output for context, checks alignment with design docs, and produces actionable findings for the coding agent to fix.
user_invocable: true
allowed-tools: Bash(git *), Bash(gh *), Read, Grep, Glob, Agent, AskUserQuestion, mcp__linear-server__save_issue
argument-hint: "[PR number, branch name, or 'current' to review the current diff]"
---

# Architecture Review

This skill reviews a PR or diff for architectural quality. It runs after the code review and focuses on broader design concerns that the code review does not cover: SOLID principles, codebase consistency, dependency direction, error handling patterns, data flow, test architecture, performance, and security architecture.

The output is actionable: inline comments for specific issues in the code, and a summary for broader observations. Everything is written so the coding agent (or a human) can act on it without further clarification.

Argument: `$ARGUMENTS`

## Step 1: Load context

1. **Identify the PR or diff.** If `$ARGUMENTS` is a PR number, run `gh pr view $ARGUMENTS --json baseRefName,headRefName,title,body` and `gh pr diff $ARGUMENTS`. If it is "current" or empty, use `git diff` against the base branch. If it is a branch name, diff against main.
2. **Understand the sequence.** This skill runs after the code review. The coding agent has already applied the code review's findings, so the code you are reviewing has already been corrected for correctness issues. Your job is to look at the architectural quality of the result.
3. **Read project documentation.** Check for:
   - `docs/design/<topic>.md` - design decisions that the code should align with
   - `docs/requirements/<topic>.md` - requirements the code should satisfy
   - `docs/plans/<initiative>.md` - the plan this work is part of
   - `.architecture-review.yml` or `.architecture-patterns.yml` - project-specific patterns (if it exists)
4. **Understand the broader context.** Do not just read the changed files. For each changed file, also look at:
   - What imports it and what it imports (to understand dependency direction)
   - The module or package it belongs to (to understand if it fits its current location)
   - Similar files in the codebase (to check consistency)
   Use Grep and Glob to search for callers, related modules, and patterns.

## Step 2: Review against architectural patterns

Check the diff against each of the following categories. For each finding, determine if it is an inline comment (specific to a line or block of code) or a summary observation (broader than any single line).

### SOLID and design patterns

- **Single Responsibility:** Does each class/module/function do one thing? Look for god classes, functions over 50 lines, modules that mix concerns (e.g., a serializer that triggers side effects).
- **Open/Closed:** Is the code open for extension but closed for modification? Are there switch/if chains that should be polymorphism?
- **Liskov Substitution:** If subclasses are used, can they substitute the parent without breaking behavior?
- **Interface Segregation:** Are interfaces (or abstract classes) focused, or do they force implementers to depend on methods they do not use?
- **Dependency Inversion:** Do high-level modules depend on abstractions, or do they import concrete low-level implementations directly?

### Codebase consistency

- Does the new code follow the same patterns as existing code in the same area?
- If the codebase uses a repository pattern, does the new code go through repositories or bypass them?
- If the codebase uses a service layer, does the new code put business logic in the service or scatter it across views/serializers?
- Are naming conventions consistent (file names, class names, function names)?
- If the new code introduces a pattern that differs from existing patterns, is there a good reason?

### Dependency direction

- Are dependencies pointing the right way? (Domain should not depend on infrastructure, inner layers should not know about outer layers.)
- Are there circular imports or circular dependencies between modules?
- Does the change introduce a new dependency between packages that were previously independent?

### Error handling strategy

- Is there a consistent error handling pattern? Are errors caught at the right level?
- Are there silent swallows (bare `except`, `except Exception: pass`)?
- Is the boundary between internal errors and user-facing errors clear?
- Are errors logged with enough context to debug them?

### Data flow and transformation

- Is data transformed too many times between layers?
- Are there unnecessary intermediate representations?
- Is the boundary between serialization and domain logic clean?
- Are there places where raw dicts are passed when a typed model would be clearer?

### Test architecture

- Are tests testing behavior or implementation details? (Tests that break when you refactor internals without changing behavior are testing implementation.)
- Are test helpers well-organized (shared fixtures, factories, builders)?
- Is the test-to-production code ratio reasonable?
- Are integration tests isolated from unit tests (separate directories, separate run commands)?
- Do tests follow the project's naming conventions?

### Naming and boundaries

- Do module/package names match what they actually do?
- Are there modules that have grown beyond their original purpose and should be split?
- Are boundaries between features clear, or is there tangling (feature A imports internal details of feature B)?

### Performance implications

- **N+1 queries:** Look for ORM loops that trigger a query per iteration without `select_related` or `prefetch_related` (Django) or `joinedload` (SQLAlchemy).
- **Missing indexes:** New query patterns that filter on columns without indexes.
- **Unbounded operations:** Loops without limits, queries without pagination, file reads without size limits.
- **Sync vs async:** Synchronous I/O operations in async code paths (or vice versa).

### Security architecture

- Are authorization checks at the right layer (not just at the view level, but also in services if called from multiple entry points)?
- Is input validation happening at the system boundary?
- Are internal details exposed in API responses (stack traces, internal IDs, database column names)?
- Are secrets or credentials handled correctly (not logged, not in URLs, not in error messages)?

### Single source of truth

- Is any piece of data, logic, or configuration defined in more than one place? Look for duplicated constants, repeated validation rules, business logic copied across layers, and configuration values hardcoded in multiple files.
- If two components need the same value or rule, does one derive it from the other, or do they each define it independently? Independent definitions will inevitably drift.
- Are there derived values that could be computed from existing data instead of being stored or passed separately?
- When a fact changes (a business rule, a threshold, a label), how many files need to be updated? If the answer is more than one, the source of truth is split.

### Design document alignment

- If design docs exist for this area, does the code match the documented decisions?
- If the code deviates from a design decision, is the deviation justified and documented?
- If requirements exist, does the code satisfy them?

## Step 3: Classify findings

For each finding, assign one of two severity levels:

- **Must fix:** Issues that should be resolved before merging. These are architectural problems that will cause real pain if they land (data leaks, broken abstractions, dependency cycles, missing error handling that will crash in production).
- **Recommendation:** Improvements that would make the code better but are not blocking. These are opportunities for cleaner design, better naming, or improved consistency.

## Step 4: Determine refactoring scope

For each "must fix" finding that requires refactoring:

- If the refactoring keeps the PR under 400-500 total LOC and the issue was introduced by this PR, it should be fixed in the same PR. Include clear instructions for the coding agent.
- If the refactoring is larger or the issue predates this PR, create a Linear issue for it instead:
  ```
  save_issue(
    title: "<description of the refactoring>",
    team: "<your-linear-team>",
    labels: ["agent issue"],
    assignee: "me",
    description: "<what needs to change, why, and which files are affected>",
    priority: 4
  )
  ```
  Note the created issue identifier in the review summary.

## Step 5: Produce output

Structure the output in two parts:

### Inline comments

For each finding that applies to a specific location in the code:

```
FILE: <path>
LINE: <number>
SEVERITY: must fix | recommendation
CATEGORY: <one of the categories from Step 2>
COMMENT: <what is wrong and what to do about it, written so the coding agent can act on it>
```

### Summary

A higher-level section covering:

1. **Overall assessment** (1-2 sentences): Is this architecturally sound, or does it have structural issues?
2. **Broader observations:** Patterns that span multiple files or are not tied to a specific line. For example: "The new service mixes data access and business logic, which is inconsistent with how other services in the project are structured."
3. **Design document alignment:** If design docs were found, note any deviations.
4. **Follow-up issues created:** If any Linear issues were created for larger refactoring, list them here.

## Project-specific patterns

The skill loads project-specific patterns from `.architecture-patterns.yml` if it exists in the project root. This file defines additional checks specific to the project. Example:

```yaml
# .architecture-patterns.yml
patterns:
  - name: "Service layer for mutations"
    description: "All data mutations must go through services.py, not views or serializers"
    check: "Look for Model.objects.create(), .save(), .delete() calls outside of services.py files"
    severity: must_fix

  - name: "Tenanted querysets"
    description: "All queries on tenanted models must use TenantedManager or TenantedQuerySet"
    check: "Look for .objects.all() or .objects.filter() on models that extend BaseModel"
    severity: must_fix

  - name: "Repository pattern for data access"
    description: "Data access should go through repository classes, not direct ORM calls in services"
    check: "Look for direct ORM queries in workflow activities or agent code"
    severity: recommendation
```

If no file exists, the skill uses only the general architectural patterns from Step 2.

## Rules

- **Code review is already applied.** The code you see has already been corrected for correctness issues. Focus on architectural quality.
- **Be actionable.** Every finding must tell the reader what to do, not just what is wrong.
- **Two severity levels only.** "Must fix" or "recommendation." No ambiguity.
- **Small refactors in the same PR.** If the fix keeps the PR under 400-500 LOC and the issue was introduced by the PR, include it. Otherwise, create a Linear issue.
- **Read the broader context.** Do not review the diff in isolation. Understand the module, its callers, and its dependencies.
- **Check design docs.** If they exist, check alignment. If the code deviates, flag it.
- **Do not use em-dashes.** Use hyphens, commas, or parentheses instead.
