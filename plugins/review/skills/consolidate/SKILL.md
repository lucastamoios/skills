---
name: consolidate
description: Consolidate completed review evidence or prepare editable PR comments from it. Preserve coverage and provenance, and let the coordinator submit the finalized GitHub review when the user requests publication.
---

# Consolidate Review

Produce one readable decision surface without erasing the evidence behind it. Read [the worker contract](../../protocol/contract.md). Accept `input=<absolute input.md> output=<absolute output.md>` with skill `consolidate`. Use mode `analyze` to aggregate listed review outputs, or `prepare` to turn an existing consolidated report into editable PR comments. A direct request without a prepared input routes through `review:run`, including requests to prepare or post PR comments from completed reviews.

Read the declared files completely, verify digests and identity, and write only the assigned output and attachments. Do not rediscover the task, dispatch more agents, edit source reports, update the vault, post comments, or perform fixes. Missing user decisions become follow-ups for the coordinator.

For `prepare`, read [PR comment preparation and publication](references/pr-comments.md) and follow its worker section instead of repeating aggregation. The coordinator uses the same reference for editing, task persistence, and requested publication. A comment-only request reuses sufficient current evidence; it does not launch another full review. The sections below apply to `analyze`, whose input lists expected jobs and supplied outputs.

## Check compatibility first

- Compare contract, run, snapshot, declared scope, and input identities. A matching commit alone is insufficient when local edits differ.
- Require the expected-jobs list for the evidence phase being consolidated. A missing or failed required analysis or execution job leaves coverage incomplete even if the supplied reports contain no findings. Subsequent walkthrough preparation and cleanup are not prerequisites; record them separately without treating them as missing review evidence.
- Reject stale, unreadable, wrong-snapshot, or modified files as current evidence. List each exclusion and its reason. Preserve usable matching reports and the gaps separately.
- A partial report can contain a supported defect. Keep that finding with its limits; do not promote its unexamined scope to a pass.
- A path correction proposed by another lens does not silently amend the original map or count as QA execution. Record the correction and affected evidence as an unresolved dependency.
- Retain QA's actually executed exploratory scenarios with their job and `qa:Exx` IDs, even when paths has not incorporated them. Keep their results separate from mapped coverage. A checkpoint from an interrupted job supplies attributed partial evidence and cleanup state, not a completed job or inferred pass.
- A cleanup report for a changed snapshot is not a compatible peer of analyses on the original source.

## Reconcile independent verification

Read the original reports together with the `review:verify` ledger. Match every verification result to its original run/job/finding IDs, report digests, current snapshot, and declared candidate scope. Preserve both original review coverage and candidate verification coverage. An omitted candidate, missing verifier, stale ledger, or changed primary source leaves that candidate unverified and limits the conclusion; it never implies refutation or confirmation.

Use current supported results and their evidence when identifying confirmed problems and required corrections. Preserve refuted findings in a separate audit table with the decisive counterevidence and original IDs; exclude them from required corrections and proposed PR comments. Carry unresolved or unverified claims into the exact technical checks or user decisions needed. Keep a supported observation separate from the verifier's conclusion about impact, required correction, or an optional improvement.

If the ledger itself lacks support for its label or conflicts with current evidence, state the disagreement and request focused revalidation. Do not blindly prefer the verifier, silently override it, or reinstate an original rejected claim as a proven defect. A supported claim can remain actionable while unrelated verification is incomplete. An empty ledger does not fill missing upstream reports or establish that no defects exist.

## Merge with provenance

Group findings only when they describe the same trigger, affected behavior, and failure mechanism. Similar titles or nearby lines are not sufficient. Preserve distinct impacts and complementary evidence, and assign a stable consolidated ID such as `C01`. Keep a source mapping to every original run, job, lens, and finding ID.

Use the strongest classification justified by the combined evidence, with its reason. Do not count agent votes or treat an upstream artifact repeated by several agents as several confirmations. Keep intent gaps, test-protection gaps, product defects, release risks, and optional maintenance suggestions distinguishable even when they concern the same behavior.

When reports disagree, state both claims, their sources, what evidence differs, and the concrete check needed to resolve them. Do not silently choose the more confident wording. A source-based correction may resolve a duplicate or clerical mismatch; a new investigation is a follow-up for verification, not work this aggregation claims to have performed.

## Separate corrections, decisions, and missing evidence

Classify each retained finding by what must happen next, independently of severity and review coverage:

- **Confirmed problem, correction required:** The supplied evidence establishes a concrete failure against an explicit requirement or established contract. Identify the trigger, impact, evidence type, and smallest correction. A deterministic code path can establish a defect without runtime reproduction; say which proof exists and which execution did not occur. Partial overall coverage does not erase a supported defect. Do not ask the user whether an already established violation is a problem. Unsettled repair choices may still need a separate decision.
- **Decision required from the user:** The conclusion or remedy depends on intended product behavior, scope, a tradeoff, priority, or another decision that the evidence cannot settle. State the established facts separately from the open choice. Do not present an assumption, preference, or unanswered product question as a mandatory correction.
- **Verification still required:** The evidence is missing, stale, contradictory, or only supports a hypothesis. Name the exact technical check and which conclusion depends on it. Request that check from the coordinator instead of asking the user to prove a technical claim that tools or a focused review can establish.

Keep optional improvements separate. A confirmed defect and an unresolved repair decision can coexist; link both to the same finding ID without downgrading the defect or implying that the implementation is already authorized.

End the report with one concise list of questions for the user, deduplicated across lenses and ordered by which decisions unblock work. Give each question a stable ID, related finding IDs, the relevant fact, the exact choice needed, and its consequence. Offer concrete alternatives and an evidence-based recommendation when useful. Reuse decisions already supplied in the input; do not ask again about settled models, effort, or scope. If there are no user decisions, state that no questions remain. The worker returns this list; the coordinator presents it to the user and records the answers before dependent work continues.

## Output

Use the common output identity and add:

1. **Review coverage:** A table of every expected job, requested model, actual model or unknown, snapshot, coverage, verdict, execution, and output link. Include not requested lenses in a separate applicability note when needed to bound a general review claim.
2. **Canonical findings:** IDs, category, impact, trigger, action, evidence, limits, and complete provenance. Keep optional suggestions separate.
3. **Verification and excluded evidence:** Candidate counts and per-finding verification links, refuted findings with counterevidence, unresolved or unverified claims, opposing evidence, incompatible artifacts, missing jobs, and their effect on the report.
4. **Execution coverage:** The mapped scenarios, surface regressions, applicable UI checks, exploration, actual results, substantiated setup blockers, proposed map corrections, and cleanup residue. Keep categories and denominators explicit. Reused evidence remains attributed to its original job.
5. **Required corrections:** Confirmed problems, evidence, impact, and the smallest required action, with linked open repair decisions when applicable.
6. **Pending verification and optional improvements:** Concrete technical checks and their dependent conclusions, followed by nonessential suggestions in a separate group.
7. **Questions for the user:** The final decision list described above, or an explicit statement that none remain.

Use overall verdict `action-required` when the compatible evidence requires a corrective decision, `no-action-found` only within sufficient declared coverage, and `undetermined` when missing evidence prevents that conclusion. Coverage remains independent: `complete`, `partial`, `blocked`, or `stale`. A complete consolidation of partial reviews is still partial review coverage. No result is automatic approval to merge or deploy.

Return the output link, coverage, verdict, and at most two consequential findings or blockers. The coordinator owns task persistence and user-facing presentation.
