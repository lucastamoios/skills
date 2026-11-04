---
name: verify
description: Independently check review findings against the declared code snapshot and primary sources. Return supported, refuted, or unresolved results with evidence before consolidation, without fixing code or publishing comments.
---

# Verify Review Findings

Validate the supplied claims, including evidence that could disprove them. Read [the worker contract](../../protocol/contract.md). Accept `input=<absolute input.md> output=<absolute output.md>` with skill `verify` and mode `analyze`. A direct request without a prepared input routes through `review:run` for this verification scope. It does not require repeating the original review lenses.

Use the declared candidates, source reports, primary requirements, repository snapshot, and permitted execution resources. Work in a fresh agent under the configured `review:verify` assignment. Write only the assigned output and attachments. Do not fix source code, edit upstream findings, publish, update shared notes, create agents, or ask the user directly.

## Establish the verification scope

Validate the packet, artifact digests, and source snapshot. Enumerate each candidate by its original run, job, and finding ID. If the packet selects all findings, enumerate them from every listed report and reconcile the candidate table against that set. Report missing reports and candidates explicitly. A report with no findings is different from a report that never completed.

Keep stale or incompatible candidates visible with the reason they cannot be decided. Do not treat them as current evidence or silently rebase their claims onto newer code. A globally changed snapshot makes the attempt stale. An unavailable primary source or upstream report limits the affected candidates while independent valid candidates can proceed.

An explicitly empty candidate set produces a report with zero evaluated findings and the upstream gaps preserved. It does not prove the change has no defects. This skill validates supplied claims; it does not establish the completeness of the original review.

## Investigate each claim

1. Restate a falsifiable claim: the actor or input, reachable entrypoint, required state, expected contract, observed or alleged behavior, and claimed impact. Split materially different subclaims while retaining their original ID and mapping. Distinguish an explicit requirement from a reviewer inference or preference.
2. Inspect the primary sources and real execution path. Prefer available semantic tools for callers, definitions, and inherited behavior. Check relevant managers, base classes, middleware, validation, transactions, framework guarantees, and consumers. A protection counts only when it applies to this operation and identity; a nearby safeguard is not enough.
3. Look for both supporting and contrary evidence. Check whether the trigger is reachable and whether preconditions can coexist. Compare the baseline when the finding alleges a regression. Record a pre-existing issue as such without dismissing it solely because it predates the diff. Reject unsupported extrapolation from one path to all callers.
4. Reassess the consequence and smallest corrective action supported by the evidence. Separate an established failure from an unsettled product or repair decision. A supported observation does not automatically establish the reviewer's severity, proposed remedy, or claim that a correction is required.
5. Run a focused experiment only when it resolves a material uncertainty and the input permits it. Use an isolated execution copy, the project's supported test workflow, explicit setup and execution budgets, and job-owned resources. Keep harness files in attachments. A deterministic static proof may suffice. Failure to reproduce is not proof of absence; refutation needs a concrete counterargument, applicable protection, or a representative check that actually disproves the claim.

Preserve original observations and identify what this verifier checked independently. A command failure, missing dependency, time limit, or unavailable credential leaves the relevant claim unresolved. Report the exact next check; do not reinterpret environmental failure as product behavior or keep retrying without a changed condition. New issues outside the candidate scope become follow-ups, not an unrequested broad review.

## Decide each candidate

Use exactly one evidence result for each claim:

| Result | Meaning |
| --- | --- |
| `supported` (sustentado) | Current evidence establishes the stated claim under concrete reachable conditions. State the proof and its limits. |
| `refuted` (refutado) | Current evidence disproves the claim, such as an applicable safeguard or an invalid alleged path. State the decisive counterevidence. |
| `unresolved` (não resolvido) | The available evidence cannot settle the claim. Name the missing source, technical check, or user decision and its consequence. |

Classify the next action separately: `correction-required`, `user-decision`, `technical-check`, `optional-improvement`, or `none`. A proven defect with an open repair choice remains supported; link the repair question without treating the defect itself as uncertain. A disputed product rule cannot become a mandatory correction through reviewer confidence. Technical gaps go to the coordinator for investigation; product intent and material tradeoffs become concise questions for the user. Reuse decisions already supplied, including model and effort.

Do not merge away source IDs. The same check can inform overlapping candidates, but each candidate receives a result and all mappings remain visible. Do not count repeated claims or agent votes as independent proof.

## Output

Use the [common output template](../../protocol/output-template.md) and include:

1. **Candidate coverage:** The expected and received report identities, selected candidate IDs, checked and unresolved counts, excluded artifacts, and missing jobs. Keep this separate from original review coverage.
2. **Verification ledger:** For each stable verification ID such as `verify:V01`, record the original run/job/finding IDs, exact claim, evidence result, next action, original and reassessed impact, current source locations, supporting and contrary evidence, evidence type, and limits. Include a row for every selected candidate, even when blocked or refuted.
3. **Focused checks:** Commands or static traces, preconditions, expected and observed results, environment identity, artifacts, and cleanup. Distinguish executed results from source reasoning and reused evidence.
4. **Follow-ups and questions:** Concrete technical checks and user decisions, linked to candidate IDs. No model or effort question is needed when the packet provides its approved assignment.

Use verdict `action-required` when a supported defect requires correction, `no-action-found` only when the selected claims were settled without required correction, and `undetermined` when no such conclusion is supported. Coverage and verdict remain independent; supported defects can coexist with unresolved candidates and partial coverage. An empty input has verdict `undetermined` with an explicit zero-candidate explanation. Refuting every received candidate does not approve the PR or cover undiscovered defects.

Recheck the snapshot and write the output atomically. Return its path, candidate coverage, supported/refuted/unresolved counts, and material blockers. Consolidation consumes this ledger together with the original reports; it must not replace the original coverage with verification coverage.
