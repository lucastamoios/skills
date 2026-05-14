---
name: code-tdd
description: Implement features and bugfixes using strict outside-in TDD. Each cycle traces back to requirements and design docs when available. It includes a deliberate refactoring phase and generates integration tests when a vertical slice is complete. It wires up BDD step definitions when feature files exist. It can receive a Linear issue as input, rebuilds docs (requirements, design, plan) from the issue into the repo before coding, and graduates them into permanent knowledge after the implementation is complete.
user_invocable: true
allowed-tools: Bash(*), Read, Grep, Glob, Agent, AskUserQuestion, Edit, Write, mcp__linear-server__get_issue, mcp__linear-server__save_issue
argument-hint: "[<TEAM>-123 (Linear issue), task description, plan step reference, or requirement reference]"
---

# Code TDD

This skill implements features and bugfixes using strict outside-in Test-Driven Development. Every cycle starts from user-facing behavior and works inward, so you never build something that has no caller yet.

Argument: `$ARGUMENTS`

<HARD-GATE>
No production code without a failing test first. If you wrote code before the test, delete it. Not "set aside," not "use as reference" - delete it and start over. There are no exceptions to this rule.
</HARD-GATE>

## Step 1: Understand what you are building

`$ARGUMENTS` can be one of several things. Determine which path to follow:

### Path A: Linear issue (e.g., `<TEAM>-123`)

If `$ARGUMENTS` matches a Linear issue identifier:

1. Fetch the issue using `get_issue(id: "<TEAM>-123")`.
2. The issue body contains structured sections: Requirements, Design Decisions, Tasks, Traceability, and Acceptance Criteria. Parse these sections - they are your source of truth.
3. **Create a branch and worktree.** Extract the issue number (e.g., `4280` from `<TEAM>-4280`). Check if branch `<username>/<prefix>-<number>` already exists (where `<prefix>` is the lowercased team key). If it does not, create it from the current default branch. Then create a git worktree for it so you work in isolation:
   ```bash
   git worktree add /tmp/<repo>-worktrees/<prefix>-<number> -b <username>/<prefix>-<number>
   ```
   If the branch already exists, check it out in a worktree instead:
   ```bash
   git worktree add /tmp/<repo>-worktrees/<prefix>-<number> <username>/<prefix>-<number>
   ```
   All subsequent work (file reads, edits, test runs) happens inside the worktree directory.
4. **Rebuild docs from the issue into the repo.** The `/create-issues` skill embeds requirements, design, and plan content into the issue body and deletes the repo docs files. Rebuild them now so they are available as reference during implementation:
   - Extract the **Requirements** section and write it to `docs/requirements/<topic>.md`.
   - Extract the **Design Decisions** section and write it to `docs/design/<topic>.md`.
   - Extract the **Tasks** section (including traceability and tests) and write it to `docs/plans/<topic>.md`.
   - Update `docs/index.md` to list the new files.
   - If any of these files already exist in the worktree, read them first and merge the issue content in (the issue is the source of truth for any conflicts).
   - Derive `<topic>` from the issue title or the initiative name. Keep it consistent with how the original docs were named (check `docs/index.md` or git log for clues).
   - Commit these docs files before starting implementation so the rebuild is a clean, separate commit.
5. Note the issue identifier - you will need it in Step 8 to graduate docs after implementation.

### Path B: Repo docs (no Linear issue)

If `$ARGUMENTS` is a plain description, a plan step reference, or a requirement reference:

1. Find and read any related documentation:
   - If a plan file is referenced, read it and identify which requirements and design decisions the task implements.
   - If a requirement is referenced, read `docs/requirements/<topic>.md` and `docs/design/<topic>.md` if it exists.
   - If neither exists, that is fine. Work from the description.

### Common steps (both paths)

1. Explore the relevant parts of the codebase to understand the current state. Use Glob and Grep to find related code, tests, and patterns.
2. Check if BDD is set up: look for a BDD framework (behave, pytest-bdd, cucumber, or similar) by checking for a `features/` directory, BDD dependencies in requirements files or package.json, or existing `.feature` files. Also check if there are `.feature` files in `docs/requirements/` related to the current task.

## Step 2: Plan the outside-in order

Before writing any code, plan the order of TDD cycles from the outside in:

1. **Start with the outermost layer** that the user or caller interacts with (API endpoint, view, CLI command, UI component).
2. **Work inward** through each dependency: services, repositories, models, utilities.
3. Each cycle should produce something that connects to what was built in the previous cycle.

If you find yourself about to write a test for something that has no caller yet, stop. You are going in the wrong direction. Reorder so you start from the outside.

Present the planned order to the user briefly: "I will start with X (the user-facing part), then implement Y (which X calls), then Z (which Y depends on)."

## Step 3: The TDD cycle

For each piece of behavior, follow this cycle strictly.

### Step 0 - Classify the change before writing anything

Not every change needs a new test. Before you reach for RED, pick one of four cases:

- **New behavior in a feature with no integration test yet.** Write the integration test that will grow with this feature. Your first failing assertion is RED.
- **New behavior in a feature that already has an integration test.** Extend that test with a new failing assertion or scenario. That new assertion is RED. Do not create a parallel test file.
- **New instance of an already-tested pattern** (one more YAML row, one more registry entry, one more permission for an existing role). There is no RED step. Locate the existing pattern test, run it, confirm it still passes after your change. That is your full cycle.
- **Modification of existing behavior.** Update the existing assertion so it fails with the new expectations. That update is RED. Then change the code.

The "grow integration tests, don't spawn them" rule is the default for the first two cases. One growing test per feature is the goal, not a constellation of narrow ones.

### RED - Produce the failing assertion

For the cases that need one, produce a single failing assertion (new test, new assertion in an existing test, or updated assertion) that describes one behavior.

Pick the right target before writing it:

- **Prefer integration tests against the user-facing layer** (views, HTTP handlers, public function). A view test covers permissions, validation, business rules, persistence, and templating in one shot. Reach for a unit test only for pure-function logic that the view cannot reach.
- **Pin user-observable behavior, not file structure.** A test that asserts a YAML key exists, a field sits at a specific index, or a key is absent from a config file is pinning the diff, not behavior. Skip it. If the behavior cannot be observed through the view or public API, the test almost never earns its maintenance cost.
- **Do not mock unless you must.** External APIs (Stripe, SendGrid, Twilio) get mocked. Database, cache, internal services do not.

Then the assertion itself must:
- Test one behavior only. If "and" appears in the test name, split it.
- Have a clear name that describes the expected behavior.
- Use real code, not mocks (unless mocking is unavoidable, like external APIs).
- Put imports at the top of the file, not inside the test body.
- Be traceable. Add a comment at the top of the test referencing what it implements:

```python
# Implements REQ 3 from docs/requirements/authorization.md
def test_only_org_admins_can_export():
    ...
```

Or if no docs exist:

```python
# Implements: users with expired sessions are redirected to login
def test_expired_session_redirects_to_login():
    ...
```

### Verify RED - Watch it fail

Run only the tests related to the files you are working on (not the full test suite). Confirm:
- The test fails (not errors due to syntax or import problems).
- The failure message is what you expected.
- It fails because the feature is missing, not because of a typo.

If the test passes immediately, you are testing existing behavior. Fix the test.
If the test errors instead of failing, fix the error and re-run until it fails correctly.

### GREEN - Write minimal code to pass

Write the simplest code that makes the test pass. Nothing more.

Do not:
- Add features the test does not require.
- Refactor other code.
- "Improve" things beyond what the test asks for.
- Add error handling for cases the test does not cover (those come in later cycles).

### Verify GREEN - Watch it pass

Run only the related tests and confirm:
- The new test passes.
- Other related tests still pass.
- The output is clean (no warnings, no errors).

If the new test fails, fix the production code, not the test.
If other tests fail, fix them now before moving on.

### REFACTOR - Deliberate cleanup

This is a mandatory, deliberate phase, not an afterthought. After green, review the code you just wrote and the code around it:

1. **Code quality:** Remove duplication, improve naming, extract helpers if the same pattern appears three or more times.
2. **Architectural alignment:** Read the relevant design decisions in `docs/design/` (if they exist). Does your code match the module boundaries, interfaces, and patterns described there? If it drifts, correct it now.
3. **Codebase consistency:** Look at existing patterns in the codebase for similar code. Does your new code follow the same conventions (naming, file organization, error handling style)? If it introduces an inconsistency, align it with the existing patterns.

After refactoring, run the related tests again to confirm everything is still green.

### Repeat

Move to the next behavior in your outside-in order. Each cycle adds one behavior.

## Step 4: Pause for review

After completing one logical piece of behavior (roughly 100 lines of code, but use judgment), pause and ask the user to review the work before continuing. This is the point where the user decides whether to commit.

Present:
- A brief summary of what was implemented in this chunk.
- Which requirements or design decisions it covers (if applicable).
- The files that were changed.

Wait for the user's response before continuing. If they request changes, make them. If they approve and commit, move on to the next chunk.

Do not batch up large amounts of work. The goal is frequent, small review points so the user stays in control.

## Step 5: Integration test (when a vertical is complete)

When you have completed a full vertical slice (from the user-facing layer down to the deepest dependency it touches), write an integration test that exercises the entire path end-to-end.

This test should:
- Call the outermost entry point (the API endpoint, the view, the CLI command).
- Go through all the real layers (no mocking the internals).
- Verify the final observable outcome (response body, database state, side effect).
- Reference the requirements it validates:

```python
# Integration test for REQ 1, 2, 3 from docs/requirements/authorization.md
def test_admin_can_export_records_as_csv():
    ...
```

Run the related tests and confirm it passes.

## Step 6: Wire up BDD step definitions (if applicable)

If you found existing `.feature` files related to the current task (either in the test directory or in `docs/requirements/`):

1. Read the `.feature` file to understand the scenarios.
2. Write the step definitions that wire each Given/When/Then step to the actual code.
3. Run the BDD tests and confirm they pass.

If no `.feature` files exist for this task, skip this step entirely. Do not create them here (that is the requirements skill's job).

## Step 7: Sync docs after implementation (Linear issue path only)

If the input was a Linear issue (Path A from Step 1), the docs were rebuilt into the repo at the start (Step 1, item 4). After all implementation and tests are complete, verify they are still accurate:

1. **Review the docs you rebuilt** in `docs/requirements/<topic>.md` and `docs/design/<topic>.md`. If any requirements or design decisions changed during implementation (e.g., you discovered a requirement was wrong, or a design decision needed adjustment), update the docs to reflect what was actually built.
2. **Delete the plan file** from `docs/plans/<topic>.md`. The plan was consumed by the implementation and the code is the record now.
3. **Update `docs/index.md`** to remove the plan entry.

Commit these updates before moving to Step 8.

## Step 8: Graduate implemented docs (when a plan is fully complete)

When all tasks in a plan are implemented and tested, the requirements, design spec, and plan files have served their purpose. They were useful during the brainstorm-plan-implement cycle, but their "currently we do X, we want to change to Y" framing becomes confusing for future readers. The knowledge must flow into permanent docs.

**Only run this step when:**
- All tasks in the plan are complete (not just the current chunk)
- All tests pass
- The user has approved the implementation

**Process:**

1. **Read the remaining docs** - the requirements and design spec files for the completed initiative (the plan was already deleted in Step 7).

2. **Identify knowledge worth keeping** - conventions, patterns, trade-off rationale, operational behavior that is not obvious from reading the code.

3. **Discard transitional framing** - anything written as "currently we do X, we want to change to Y" is stale. The "Y" is now the current state. Drop the "before" context entirely.

4. **Route each piece of knowledge to the right doc:**
   - **Specific patterns or conventions** (e.g., workflow ID formats, soft-delete rules, retry behavior) get their own focused doc or update an existing focused doc. Do NOT dump everything into `architecture.md` or `decisions.md`.
   - **System-wide architectural changes** (e.g., "replaced the dedup table with Temporal-native dedup") update `architecture.md`.
   - **Key decisions with rationale** that are not obvious from the code go into `decisions.md`.
   - **Gotchas or non-obvious behavior** go into `gotchas.md`.
   - **New component documentation** gets its own file (e.g., `docs/dispatch.md` for a new dispatch module).

5. **Delete the design spec and requirements files.** Ask the user for permission first - list which files you intend to delete and where the knowledge is going. (The plan file was already deleted in Step 7.)

6. **Update `docs/index.md`** to reflect the changes (new docs added, old ones removed).

## Common rationalizations (and why they are wrong)

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. The test takes 30 seconds to write. |
| "I'll test after" | Tests that pass immediately prove nothing. You never saw them catch the bug. |
| "Deleting X hours of work is wasteful" | Sunk cost fallacy. Keeping unverified code is technical debt. |
| "I need to explore first" | Fine. Throw away the exploration, then start with TDD. |
| "The test is hard to write" | Listen to that signal. Hard to test means hard to use. Simplify the interface. |
| "I'll keep it as reference" | You will adapt it. That is testing after. Delete means delete. |
| "This is different because..." | It is not. Start with the test. |

## When stuck

| Problem | Solution |
|---------|----------|
| Do not know how to test it | Write the assertion first. What should the outcome be? Work backward from there. |
| Test is too complicated | The design is too complicated. Simplify the interface. |
| Must mock everything | Code is too coupled. Use dependency injection. |
| Test setup is huge | Extract test helpers. Still complex? Simplify the design. |

## Verification checklist

Before presenting work for review:

- [ ] Every new function or method has a test that was written before the implementation.
- [ ] Each test was watched failing before the code was written.
- [ ] Each test failed for the expected reason (feature missing, not a typo).
- [ ] Minimal code was written to pass each test (no over-engineering).
- [ ] Related tests pass.
- [ ] Output is clean (no errors, no warnings).
- [ ] Tests use real code (mocks only when unavoidable).
- [ ] Edge cases and error conditions are covered.
- [ ] Refactoring was done deliberately (code quality, architectural alignment, codebase consistency).
- [ ] Integration test exists for each completed vertical slice.
- [ ] BDD step definitions are wired up (if `.feature` files exist).
- [ ] Each test has a traceability comment pointing to the requirement, design decision, or plain description it implements.

If you cannot check all boxes, you skipped something. Go back and fix it.

## Rules

- **Outside-in order.** Start from user-facing behavior, work inward. Never build something that has no caller.
- **One behavior per cycle.** If "and" appears in the test name, split it.
- **Run only related tests.** Do not run the full test suite during the TDD cycle. Run only the tests for the files you are working on.
- **Refactoring is mandatory.** It covers code quality, architectural alignment, and codebase consistency.
- **Integration test per vertical.** When a full slice is complete, test it end-to-end.
- **BDD is conditional.** Wire up step definitions only if `.feature` files already exist.
- **Traceability is always.** Every test must reference what it implements, whether that is a requirement, a design decision, or a plain description.
- **Pause for review.** After completing a logical piece of behavior (roughly 100 LOC), stop and ask the user to review. The user decides when to commit.
- **Do not commit on your own.** Present the work, wait for approval, let the user commit.
- **Do not use em-dashes.** Use hyphens, commas, or parentheses instead.
