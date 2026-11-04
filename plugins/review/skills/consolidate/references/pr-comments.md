# PR comments from consolidated evidence

This reference serves two roles. A `consolidate` worker in `prepare` mode writes a proposed review. The outer coordinator presents it, applies user edits, persists the task, and submits it only when requested. The worker never waits for user answers or writes to GitHub or the vault.

## Prepare the input, coordinator

Resolve the PR from the request, current task, review artifacts, and Git state. Ask for a URL only when the target remains ambiguous. Reuse a compatible consolidated report and its verification evidence. If only individual or legacy review outputs exist, verify the selected findings and run `analyze` once before preparing comments. Capture informal completed findings as attributed input with their actual scope and evidence limits; do not claim that importing them reran or verified a lens. Missing verification remains a blocker for presenting a claim as a confirmed PR defect.

Use the standard `review/v1` packet with `skill: consolidate`, `mode: prepare`, and the configured `review:consolidate` model. Include:

- The consolidated report path, digest, run and job IDs, snapshot ID, and coverage.
- The PR URL, repository identity, comparison base, current head SHA, and captured diff with retrieval time and digest.
- Current review comments for duplicate detection, or an explicit retrieval gap.
- The user's requested rows, wording, dispositions, overall event, and publication authorization, if any. Absence of authorization means prepare only.
- Exclusive output and attachment paths. Output remains a proposal even when publication was requested.

Check that the reviewed content corresponds to the PR diff. Uncommitted local changes or a different PR head require revalidation of the affected findings before presenting them as current PR defects. Capture the revalidation evidence as a new attributed source; do not overwrite previous artifacts. Dispatch only the missing preparation stage, without repeating other lenses.

## Produce the proposal, worker

Read the consolidated report and the captured PR sources. Preserve coverage limits, unresolved disagreements, finding IDs, and source provenance. Do not promote a hypothesis into a confirmed defect or invent QA reproduction steps. Keep distinct findings separate and identify existing comments that already cover the same issue.

Preserve the distinction between confirmed problems requiring correction, user decisions, pending technical verification, and optional improvements. Keep the finding-to-verification mapping. Exclude refuted claims and preserve their audit reason. Carry unresolved questions into a final `Questions for the user` section with their stable IDs. A user decision or an unverified hypothesis is not a blocking defect and does not enter the submission payload as one. If a confirmed defect has an unresolved repair choice, its evidence remains valid, but do not prescribe an unchosen remedy in the comment. The coordinator resolves material publication decisions before submitting affected rows.

Use the standard output identity, assessment, and follow-ups. Preserve the upstream review coverage and verdict separately from proposal readiness. Add the target PR, reviewed and current head SHAs, and this editable table:

| ID and source findings | Finding and evidence | Observed QA reproduction | PR location | Draft comment | Disposition | Include |
| --- | --- | --- | --- | --- | --- | --- |

Use stable consolidated IDs. Each inline location must identify a path, diff side, and valid line in the captured diff, with a link when possible. Prefer changed lines. When the evidence is current but no sound inline anchor exists, propose a PR-level comment. When the finding itself is stale or unsupported, exclude it from submission and request revalidation instead of disguising it as a PR-level comment. Do not submit duplicate comments; state which existing thread covers them and whether a user-requested follow-up is needed.

Write in a warm, direct colleague voice. Use common words and full sentences. Make the trigger, consequence, and requested change clear. A helpful question is appropriate when it expresses the actual concern. Keep observed reproduction steps concise and avoid tool narration.

Use `Blocking`, `Comment`, or `Approve` as row dispositions. These are editing labels, not separate GitHub review events. Any included blocking row implies `REQUEST_CHANGES`; otherwise included feedback implies `COMMENT`. Propose `APPROVE` only when the user chose approval and no blocking item remains. Report a conflict if an explicit overall event disagrees with included rows. No findings or incomplete coverage never implies approval.

Save a proposed submission payload in the assigned attachments. Identify the PR, current head SHA as `commit_id`, one overall event, inline comment bodies and anchors, and any PR-level comments in the review body. Keep provenance and row IDs in the output even when they are omitted from the public wording. If a decision is missing, label the payload not ready rather than inventing it. Return the output path, proposal readiness, and material follow-ups. Do not publish.

## Present and refine, coordinator

Show the table and proposed overall event. Apply the user's edits to specific rows, preserve the finding IDs, and show substantive changes. Keep the finalized text and payload together in the run artifacts. Reuse an already finalized table and existing explicit publication instruction; do not ask for the same authorization again. If the user is still refining the table or has only asked for a draft, do not submit it.

Before posting in the user's Brain workflow, read the vault conventions and task index. Use `scripts/tasks.py list --all` and `get` to resolve the Review task by exact PR number or URL. Create a missing Review task when authorized by this workflow; ask only among ambiguous matches. Use `tasks.py note` to record the PR and head SHA, source reviews, evidence and observed QA steps, finalized comment text and anchors, dispositions, and overall event. Preserve existing task content and confirm that persistence succeeded. A failed required task update blocks publication. An external runner without Brain records this evidence in its declared task or run artifact instead.

## Submit and verify, coordinator

Submit only the finalized review that the user explicitly requested. Immediately recheck the PR head, anchors, and existing review comments. A changed head requires an explicit revalidation against the new diff, a refreshed source identity and proposal, and user review of material content or anchor changes. Recheck duplicates after any delay. Do not substitute another PR or silently reuse stale anchors.

Use the verified current head as `commit_id`. Create one GitHub review with the agreed event and inline comments; place unanchored PR-level feedback in its body. Use a structured API payload or a safely written JSON file, preserving exact text and newlines. Do not post anything as part of routine consolidation. Replies to existing threads require their own explicit request and are not implied by detecting a duplicate.

If submission fails or the result is uncertain, inspect what GitHub accepted before retrying. Do not blindly duplicate a review. After confirmed success, save the review URL, outcome, and accepted comment count in the same task or run artifact. Report that link and the actual result. The worker output remains the preparation record; publication results belong to the coordinator.
