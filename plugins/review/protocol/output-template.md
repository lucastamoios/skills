# <Lens> review

## Identity

- Contract: `review/v1`.
- Run ID: `<run-id>`.
- Job ID: `<job-id>`.
- Lens: `<lens>`.
- Input: `<absolute path>`.
- Input SHA-256: `<sha256>`.
- Snapshot ID: `<sha256>`.
- Started and finished: `<timestamps with timezone>`.
- Requested model and effort: `<configuration>`.
- Dispatch evidence: `<agent ID or launch record>`.
- Actual model: `<runtime-confirmed ID or unknown>`.

## Assessment

- Coverage: `<complete | partial | blocked | not-applicable | stale>`.
- Verdict: `<lens-specific verdict and reason, or undetermined>`.
- Execution: `<not-run, or commands and evidence reference>`.

## Coverage and evidence

Identify examined surfaces, source and scenario IDs, inferred facts, excluded surfaces, unresolved dependencies, and their effect on the conclusion. Add the lens-specific tables and sections required by its SKILL.md.

## Findings

For each finding, record its stable ID, category, impact, trigger, exact locations, evidence type, source and scenario references, uncertainty, and smallest proposed action. State `None within the examined scope` if appropriate. Separate maintenance suggestions from defects.

## Execution and cleanup

Record commands, environment identity, individual outcomes, evidence files, and cleanup results when execution occurred. For QA, link the checkpoint and resource ledger, list setup and recovery attempts, and separate mapped, regression, UI, and exploratory coverage. Otherwise state that execution did not run and why. A blocked setup identifies the failing layer, concrete error, applicable attempted recovery, remaining runnable work, and exact next action or missing access. Do not infer execution from a green result reported by another agent.

## Missing inputs and follow-ups

Name the exact source, upstream correction, question, or execution needed. Use `none` when no material dependency remains. A failed worker still writes this report when possible, with its failure and partial evidence preserved.
