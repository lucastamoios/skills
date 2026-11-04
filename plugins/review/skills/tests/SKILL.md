---
name: tests
description: Assess whether tests protect changed business behavior, detect plausible regressions, and remain reliable. Report weak assertions, bypassing mocks, flakiness evidence, and safe consolidation in an independent file.
---

# Test Review

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Determine what the tests protect, what could break without detection, and which tests can fail without a product regression. Ask: if the business rule were wrong, would these tests notice?

## File interface

Read [the worker contract](../../protocol/contract.md). Accept `input=<absolute input.md> output=<absolute output.md>` with skill `tests` and mode `analyze`. Write the required report to this exclusive output. The input declares context, snapshot, sources, model, dependencies, access, and budget. Do not infer them from the parent conversation.

If invoked with a PR, branch, or diff instead of a prepared input, use `review:run` to prepare and dispatch this lens in its configured agent. Do not perform the worker analysis inline. Inside a worker, never dispatch another lens, discover a task, or edit shared review artifacts. Report missing prerequisites through the output.

Follow repository instructions and use Graft and LSP when required or available. Write artifacts in English. Verify the input snapshot before and after analysis. Keep the reviewed checkout unchanged and write only the assigned output and attachments, subject to this lens's explicit execution mode.

## Scope and context

Review relevant existing and changed tests, fixtures, helpers, snapshots, and runner configuration. Do not audit the entire repository unless requested. Require current paths when production behavior changes; a test-only or declarative change may proceed without them with a reason. An intent contract is optional; read the declared primary requirements and label inferred rules. Do not derive a requirement from an existing assertion.

Intent owns fulfillment of requested scope. This lens owns test protection. QA owns broad application execution. Do not fix tests or product code. Experiments require the input's isolated scratch copy and budget; include the exact target's local changes. Continue static checks when execution is unavailable and state the effect on conclusions.

For the configured organization work, consult declared `test_patterns` learnings through `<configured-learnings-command>`. Reuse a declared current retrieval where applicable; otherwise start with `<configured-learnings-command> list --limit 100 --type test_patterns --json` and follow up on relevant patterns. Record applied IDs or the exact failure. Do not substitute a learnings JSON file or treat a pattern as proof without matching the current mechanism.

## Map behavior to evidence

Trace each material changed rule and relevant path scenario to the real production code exercised, test data, substituted dependencies, and assertion that proves the outcome. Inspect fixtures and helpers when they can change what the test runs.

Use a compact matrix in the output:

| Rule or scenario | Source | Test and assertion | Real code exercised and mocks | Protection or gap |
| --- | --- | --- | --- | --- |

Distinguish code that executes from behavior that is asserted. A test file, high line coverage, or a green suite does not establish protection by itself. Note tests that are skipped, uncollected, quarantined, or excluded by the normal runner. Existing coverage at another appropriate layer counts; do not demand duplicate tests at every layer.

## Evaluate test value

For each candidate weakness, name a plausible incorrect implementation that would still satisfy the test. Reject findings that cannot identify a concrete missed defect or maintenance cost.

- **Regression sensitivity:** Check whether removing validation, inverting a decision, dropping a filter, or returning a constant would escape. For a bug fix, determine whether the claimed regression test distinguishes the broken behavior from the fix. Do not require every existing test to fail on the old code.
- **Mock boundaries:** Verify that the subject and changed decision execute. Mocks may isolate external dependencies; their number is not a quality metric. Flag a mock that supplies the decision or result the test claims to prove. Check that doubles preserve relevant dependency contracts and error behavior.
- **Observable outcomes:** Check output values, membership, counts, persisted state, errors, and required or forbidden side effects. A status code or mock call alone is inadequate when the contract includes more. Interaction assertions are valid when the interaction itself is the contract.
- **Discriminating data:** Check whether fixtures separate allowed from denied, matching from nonmatching, and current-tenant from other-tenant data. Empty fixtures, coincidentally equal values, or a single record can make broken filters and ordering invisible.
- **Independent expectations:** Check whether expected values copy the implementation's formula or use the same helper under test. Prefer expectations derived independently from the rule. Shared setup helpers are not inherently a problem.
- **Relevant boundaries:** Cover distinct allowed and denied outcomes, empty cases, thresholds, invalid states, and dependency failures when the changed rule makes them meaningful. Explain which defect an additional case would detect instead of requesting generic edge cases.
- **Actual failure propagation:** Check swallowed exceptions, broad exception assertions, unawaited asynchronous work, missing assertions, and snapshots that omit the decisive field or encode an unverified result.
- **Configuration and refactoring:** A test that only repeats a constant may provide little protection; a test that proves a setting changes observable behavior can protect an important contract. Identify the specific cost before recommending removal. Internal assertions can be valid when the internal interface is an intentional contract.

## Check flakiness explicitly

Inspect relevant tests and fixtures for mechanisms that make outcomes vary without a product change:

- The test depends on wall-clock time, time zones, date rollover, expiry boundaries, or inconsistent clock reads.
- Random data, generated identifiers, hash iteration, filesystem enumeration, or database results have uncontrolled ordering or collisions.
- Tests leak global settings, environment variables, mocks, cache entries, database records, files, ports, or other state into later tests or parallel workers.
- Background jobs, asynchronous work, or concurrent operations race with assertions or cleanup. Fixed sleeps may assume completion without observing it.
- Live network services or uncontrolled resources affect the result. Timeouts or performance thresholds depend on machine load without supporting controls.
- Retries, reruns, quarantine, or broad exception handling hide the first failure instead of explaining it.

Distinguish these evidence states:

- **Confirmed flaky:** Comparable runs on the same target show both pass and fail, or a controlled reproduction demonstrates dependence on order, scheduling, time, seed, or external state. Cite the runs and trigger.
- **Flakiness risk:** Code or fixture evidence identifies an uncontrolled dependency and a concrete failure condition, but intermittent behavior has not been demonstrated. State that it is a risk, not a reproduced failure.
- **Inconclusive:** A failure lacks enough context to attribute it. Record the limitation, not a confirmed finding.

A single failure does not establish flakiness. Repeated passes do not prove stability. Distinguish a nondeterministic product bug from a test defect; do not weaken a valid assertion to silence a real race. Separate runner or environment failures from assertion failures, and say when a problem predates the change.

## Look for safe consolidation

Identify tests that exercise the same contract and differ only in data, or duplicate protection without an independent purpose. Suggest parametrization or removal only after comparing scenarios, boundaries, assertions, and isolation.

Preserve distinct business cases, layer-specific contracts, negative assertions, readable case names, and failure localization. Do not combine unrelated behaviors into one large test or remove tests merely because they execute the same lines. Specify which tests can be consolidated and what coverage must remain. Keep optional maintenance suggestions separate from blocking protection gaps.

## Use focused execution when it resolves uncertainty

Start with analysis. Run relevant tests or a targeted experiment when it materially changes confidence in a finding. Do not run the full suite or introduce mutation-testing infrastructure by default.

Before execution, verify that the documented runner targets a local disposable environment and cannot call live services or change shared data. Preserve the user's checkout and pre-existing state. If isolation or dependencies cannot be established, record the execution blocker and continue the static review.

For a defect-sensitivity experiment:

1. Establish a passing baseline and confirm that the relevant test was collected and exercised the target.
2. In the disposable copy, introduce one small plausible defect, such as removing the rule being tested. Preserve the exact target, including in-scope uncommitted changes.
3. Run the relevant test again. A syntax, import, collection, or unrelated setup failure does not prove defect detection. A surviving change is meaningful only if it changes the intended behavior and reaches the subject under test.
4. Restore the temporary change and verify the baseline. Record commands, patch, outcomes, and cleanup. Never reset or discard the user's changes.

For flakiness, vary the suspected cause rather than rerunning blindly. Compare relevant order, seeds, clock values, worker counts, or synchronized schedules. Choose a bounded run count or time budget before starting; stop when the mechanism is demonstrated or the budget is exhausted. Record individual first-attempt outcomes, retries, order, seed, and environment details needed to reproduce. Report an unsuccessful reproduction as inconclusive, not stable.

Remove only state and processes created for the experiment. Verify cleanup and report anything that remains. Never silently turn an experiment into a source or test fix.

## Classify evidence

Each finding must identify the rule or contract, source and test location, concrete defect that escapes or failure trigger, evidence, impact, and smallest corrective action. Label static reasoning, executed experiments, CI evidence, and flakiness risks separately.

- **Must fix:** A central changed business rule or critical contract has no effective regression protection, with a concrete defect that would escape; or a demonstrated reliability failure makes a required test gate unusable. This blocks approval of the test protection, not proof that product code is already broken.
- **Should fix:** A concrete lower-impact protection gap or reliability problem exists. A well-supported flakiness risk can qualify, but speculation cannot.
- **Suggestion:** Consolidation or maintenance would reduce a demonstrated cost without changing protection. It does not block approval.

Use `FAIL` for Must fix findings, `CONCERNS` for Should fix findings, and `PASS` when neither exists. Suggestions alone do not change a PASS. Use `INCOMPLETE` when missing evidence prevents a material conclusion, unless a confirmed finding already warrants FAIL; always disclose remaining limits. A static review may be complete without execution when its conclusions do not depend on a run. PASS does not claim that tests ran or that the suite is free of flakiness.

## Output sections

Add the rule-to-assertion matrix, classified findings, consolidation suggestions, execution and reliability evidence, and limits to the common output. Each suggestion names the candidate tests, maintenance benefit, and behavior that must remain protected. Keep static reasoning, experiments, CI evidence, confirmed flakiness, and flakiness risk distinct.

Use the verdict rules above independently of coverage. Return the output link, verdict, material execution limits, and at most two findings or suggestions. Do not claim stability from unsuccessful reproduction or imply that a static PASS means tests ran.
