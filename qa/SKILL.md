---
name: qa
description: Run QA on a PR or branch - execute tests, verify test quality, check requirements coverage, explore the UI with Playwright, and test API endpoints with curl. It is aggressive with edge cases and accessibility.
user_invocable: true
allowed-tools: Bash(*), Read, Grep, Glob, Agent, AskUserQuestion, Edit, Write
argument-hint: "[PR number, branch name, or 'current' to QA the current diff]"
---

# QA

This skill runs quality assurance on a PR or branch. It has four phases: test execution and quality assessment, requirements coverage check, API endpoint testing, and UI exploration with Playwright. Both the API and UI phases are aggressive - they test not just the happy path but also edge cases, absurd inputs, and related areas that might break.

Argument: `$ARGUMENTS`

## Step 1: Identify the scope

1. **Identify the PR or diff.** If `$ARGUMENTS` is a PR number, run `gh pr view $ARGUMENTS --json baseRefName,headRefName,title,body` and `gh pr diff $ARGUMENTS`. If it is "current" or empty, use `git diff` against the base branch.
2. **List changed files.** Run `git diff <base>..HEAD --name-only`.
3. **Read requirements and plan** (if available). Check `docs/requirements/` and `docs/plans/` for files related to this work. These tell you what the code is supposed to do, which you will verify in all phases.
4. **Understand what changed.** Read the diff and the changed files. Categorize the changes:
   - **Backend only** (models, services, views, API endpoints, serializers)
   - **Frontend only** (templates, static files, JavaScript/TypeScript, CSS)
   - **Both backend and frontend**
   - **Tests only**
   This determines which exploration phases run:
   - Backend changes -> always run API testing (Step 5)
   - Frontend changes -> always run UI exploration (Step 6)
   - Both -> run both
   - Tests only -> skip both, just run test execution and quality

## Step 2: Test execution

### Run related tests first

Identify the test files related to the changed code. Run them:

```bash
# Targeted (Django app):
just dev-test <app>/tests/test_<file>.py -v

# Full suite (pytest):
just test
```

If they **fail**: stop and report the failures. Do not proceed to the next phases. The coding agent needs to fix the tests first.

If they **pass**: proceed to run the full test suite once.

### Run the full test suite

Run the project's full test command. If the full suite fails on tests unrelated to the change, note which tests failed and whether they were already failing before this PR (check by running them against the base branch if needed).

Report:
- Total tests run, passed, failed, skipped
- Any failures and whether they are related to this PR

## Step 3: Test quality assessment

Read the test files related to the changed code. For each test, evaluate:

### Are the tests testing the right thing?

- **Behavior vs implementation:** Does the test verify what the code does (behavior) or how it does it (implementation)? Tests that mock internal methods and assert they were called are testing implementation. Tests that call the public API and check the result are testing behavior.
- **Over-mocking:** Are the tests mocking so much that they are not testing anything real? If a test mocks the database, mocks the service, and mocks the response, it is testing that mocks return what you told them to return.
- **Coverage of functionality:** Do the tests cover the actual business logic, or do they only test the happy path with trivial inputs?
- **Edge cases:** Are boundary conditions tested? (Empty inputs, None values, maximum sizes, concurrent access, error paths.)

### Report test quality issues

For each issue found, report:
```
FILE: <test file path>
ISSUE: <what is wrong with the test>
SUGGESTION: <what a better test would look like, in plain language>
```

Do not modify tests. Just report.

## Step 4: Requirements coverage

If requirements or plan docs were found in Step 1:

1. List each requirement that this PR should implement.
2. For each requirement, check:
   - Is there at least one test that validates it? (Look for traceability comments like `# Implements REQ N` or test names that match the requirement.)
   - Does the implementation actually satisfy the requirement? (Read the code and compare against the requirement text.)
3. Flag any requirements that are:
   - **Untested:** No test covers this requirement.
   - **Unimplemented:** The code does not implement this requirement.
   - **Partially implemented:** The code handles some cases but not all described in the requirement.

## Step 5: API endpoint testing

Run this step when the change affects backend code (views, serializers, services, models, API endpoints). Even if the change is "just a model change," the API that serves that model's data might behave differently.

### Ensure the dev server is running

Check if the app is reachable:

```bash
curl -k -s -o /dev/null -w "%{http_code}" $DEV_URL
```

If it is not running, start it:

```bash
cd <web-client-dir> && just dev-start
```

Wait for it to be reachable (poll every 5 seconds, timeout after 2 minutes).

### Determine which endpoints to test

1. **Directly changed endpoints:** If views or serializers were modified, test those endpoints.
2. **Endpoints that use changed models or services:** If a model changed, find the views that serve data from that model and test them.
3. **Related endpoints:** If the change affects a shared component (a base serializer, a mixin, a permission class), test other endpoints that use it.

### Test with curl

For each endpoint:

1. **Happy path:** Make a valid request and verify the response shape and status code.
   ```bash
   curl -k -s -X GET "$DEV_URL/api/v1/<endpoint>/" -H "Authorization: Token <token>" | jq .
   ```

2. **Edge cases (be aggressive, use common sense):**
   - Send requests with missing required fields
   - Send requests with invalid data types (string where int expected)
   - Send requests with empty body
   - Send very long strings in text fields
   - Send special characters (`<script>`, SQL injection patterns, unicode)
   - Test pagination boundaries (page=0, page=999999, page=-1)
   - Test with no authentication (should get 401)
   - Test with a user that lacks permissions (should get 403)
   - If the endpoint creates data, try creating duplicates
   - If the endpoint deletes data, try deleting something that does not exist

3. **Verify response contract:** If the PR changes an API response shape, verify that the new shape matches what is documented or expected by consumers.

### Report API issues

For each issue:
```
ENDPOINT: <method> <URL>
REQUEST: <what was sent>
EXPECTED: <what should have happened>
ACTUAL: <what happened>
SEVERITY: must fix | recommendation
```

## Step 6: UI exploration with Playwright

Run this step when the change affects frontend code (templates, JavaScript, CSS) or when backend changes have user-facing impact (a new field on a model that appears in a form, a changed permission that affects what users see).

### Determine which pages to explore

1. **Directly affected pages:** Infer from changed files. If a template in `<some-app>/` changed, visit that app's pages. If a view or URL changed, visit those pages.
2. **Related pages:** Look at the broader context. If the change affects a shared component (a base template, a form widget, a CSS class), check other pages that use it.
3. **Requirements-driven pages:** If requirements describe user flows (e.g., "the user can export authorizations as CSV"), navigate through that flow.

### Explore and test

For each page, use Playwright to:

1. **Navigate and screenshot the initial state.** Save to `/tmp/qa-screenshots/<page-name>.png`.

2. **Test the happy path.** If there is a form, fill it with valid data and submit. If there is a list, check pagination. If there is a filter, use it. Screenshot the result.

3. **Test edge cases aggressively (with common sense):**
   - Submit forms with empty fields
   - Enter very long text (500+ characters) in text inputs
   - Enter special characters (`<script>`, `'; DROP TABLE`, unicode, emoji)
   - Click buttons multiple times rapidly (double-submit)
   - Navigate away and back (does state persist?)
   - Try actions without permission (if applicable)
   - Resize the browser to mobile width and check layout
   - Use the keyboard to navigate (Tab, Enter, Escape)

4. **Check accessibility:**
   - Are there missing alt attributes on images?
   - Can you Tab through all interactive elements?
   - Do form fields have labels?
   - Is there sufficient color contrast? (Use Playwright's accessibility snapshot if available.)

5. **Check related pages** that were not directly changed but could be affected. If the change touches a shared model or service, visit pages that display data from that model.

### Capture evidence

- **Screenshot** for static issues (layout broken, missing element, wrong text).
- **GIF recording** for interaction issues (click that breaks, form submission that fails, navigation that loops). Use Playwright's video recording or take a sequence of screenshots.
- Save all evidence to `/tmp/qa-screenshots/` with descriptive names.

## Step 7: Produce output

Structure the output in five sections:

### Test Results

```
RELATED TESTS: X passed, Y failed, Z skipped
FULL SUITE: X passed, Y failed, Z skipped
FAILURES RELATED TO PR: <list or "none">
PRE-EXISTING FAILURES: <list or "none">
```

### Test Quality Issues

```
FILE: <path>
ISSUE: <description>
SUGGESTION: <what to improve>
```

Or "No test quality issues found."

### Requirements Coverage

```
REQ N: Covered by test <test name> | UNTESTED | UNIMPLEMENTED | PARTIAL (<what is missing>)
```

Or "No requirements docs found for this work."

### API Testing

For each endpoint tested:
```
ENDPOINT: <method> <URL>
HAPPY PATH: OK | FAIL (<details>)
EDGE CASES: <list of issues found, or "all passed">
SEVERITY: must fix | recommendation (for each issue)
```

Or "No API changes detected, API testing skipped."

### UI Exploration

For each page explored:
```
PAGE: <URL or description>
STATUS: OK | ISSUES FOUND
SCREENSHOTS: /tmp/qa-screenshots/<filename>
FINDINGS:
  - <description of issue, with severity: must fix | recommendation>
```

Or "No frontend changes detected, UI exploration skipped."

## Rules

- **Tests must pass before anything else.** If related tests fail, stop and report.
- **Full suite runs once.** After related tests pass, run the full suite to catch regressions.
- **Do not modify tests.** Report quality issues, do not fix them.
- **Always test API endpoints** when backend code changes, even if the change seems internal.
- **Be aggressive with both API and UI testing.** Test edge cases, absurd inputs, and related areas. Use common sense (do not spend forever on a trivial endpoint or a static text page).
- **Always check accessibility** when exploring the UI.
- **Screenshot or GIF everything suspicious.** When in doubt, capture it. Screenshots for static issues, GIFs for interaction issues.
- **Save evidence to /tmp/qa-screenshots/.** Point to the files in the output.
- **Start the dev server if needed.** Check, start, wait for ready.
- **Check requirements coverage.** Flag untested and unimplemented requirements.
- **Do not use em-dashes.** Use hyphens, commas, or parentheses instead.
