# Review worker input

- Contract: `review/v1`.
- Run ID: `<run-id>`.
- Job ID: `<lens>-<attempt>`.
- Skill: `<lens>`.
- Mode: `<analyze | execute | findings-only | cleanup | prepare>`.
- Repository: `<absolute checkout>`.
- Snapshot: `<absolute snapshot.json>`.
- Snapshot ID: `<sha256>`.
- Base: `<resolved commit>`.
- Head: `<resolved commit>`.
- Model: `<exact model ID>`.
- Effort: `<supported effort>`.
- Backend: `<native agent tool or codex-exec>`.
- Output: `<absolute exclusive output.md>`.
- Attachments: `<absolute exclusive directory>`.

## Objective and scope

Describe the requested comparison, changed surfaces, included local changes, exclusions, and the question this lens answers. State whether production behavior changes and whether a path map is required. Include any explicit acceptance criteria; label inferences separately.

## Sources and context

| ID | Role | Absolute path | SHA-256 | Original source and retrieval time |
| --- | --- | --- | --- | --- |

List applicable repository instructions and contextual sources. Use `none` for unavailable optional sources and explain how their absence limits the review. Do not put secrets into the input.

## Upstream artifacts

| Role | Absolute path | SHA-256 | Job ID | Snapshot ID | Coverage |
| --- | --- | --- | --- | --- | --- |

State `none` when there are no dependencies. For verification, include the original review reports and primary sources. For consolidation, include the original reports and verification ledger. Both inputs carry an expected-jobs table with each selected analysis, execution, or prerequisite verification job, required or optional status, and completed, failed, canceled, or unavailable state. Include missing jobs instead of silently omitting them. Record later walkthrough preparation and cleanup in a separate subsequent-phases list; they cannot be prerequisites of the report they consume.

For verify and consolidation, declare the candidate scope as all findings from the listed reports or an explicit subset. Include a table of original run ID, job ID, finding ID, source report path and digest, and verification status or ledger reference when available. State an empty selection explicitly. Candidate omissions and missing source reports remain visible even when there are no findings to check.

## Access and execution

- Readable roots and permitted external retrieval: `<explicit paths and services>`.
- Operation: `<read-only, isolated-tests, isolated-qa, or explicit-cleanup>`.
- Scratch directory and environment: `<exclusive location and reuse-verified identity, provision-local plan, or none>`.
- Local provisioning: `<Docker workflow, namespace, permitted job-local dependencies/browser setup, writable runtime paths, or none>`.
- Setup budget: `<diagnostic/build allowance and whether the user imposed a hard limit>`.
- Execution budget: `<maximum runs and/or elapsed minutes for scenarios and exploration; zero means no execution>`.
- Cleanup ownership: `<resources this job may create and remove>`.
- Constraints and known gaps: `<concrete constraints, or none>`.

## Lens-specific context

Include the initiative stage for dead code, environment and scenario scope for QA, and intended audience or chosen topic for walkthrough. QA inputs include the surface map where available, a checkpoint location, provisioning access, and relevant runtime/browser instructions; an existing running stack is not required. Add only context needed by this job. The coordinator's hypotheses and other reviewers' verdicts are not default inputs to independent reviewers.

For `consolidate` in `prepare` mode, include the compatible consolidated report and captured PR identity, current head and diff, existing comments, selected findings, user edits, and requested event. Record publication authorization separately from preparation. The consolidated report retains the expected-jobs coverage; preparation does not rerun those jobs. Follow the [PR comment contract](../skills/consolidate/references/pr-comments.md).
