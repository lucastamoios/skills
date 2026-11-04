# Independent requirements and design review

This is the `review` mode for requirements and design-spec under development/v1.
The coordinator dispatches a fresh reviewer after the corresponding draft. The
reviewer receives the request, accepted decisions and answers, vocabulary sources,
relevant code evidence, and exact draft artifact digests. It does not receive the
author's private reasoning or inherit the authoring conversation.

The coordinator selects one reviewer using the approved model policy and
[cross-provider dispatch procedure](document-review-dispatch.md). For
`captured-final-response` delivery, return the complete contract report as the
final response; the coordinator saves it verbatim at the exclusive output path.

## Review the assigned artifact

Validate the packet, model policy, source identity, and exclusive output ownership
before reviewing. Read the [vocabulary method](vocabulary.md). Treat the draft as
a proposal to assess against evidence, not as authoritative proof of user intent.

For requirements, check:

- Whether the requirements express the actual requested outcomes and boundaries.
- Whether terms match accepted domain meanings and uncertain meanings remain open.
- Whether relevant actors, permissions, state changes, failure cases, and limits
  are covered without inventing scope.
- Whether acceptance criteria are observable and BDD scenarios test the intended
  behavior, with complete and accurate requirement mapping.

For design, check:

- Whether every in-scope requirement has a coherent implementation approach.
- Whether responsibilities, interfaces, data flow, and invariants are clear.
- Whether proposed components and dependencies fit actual code and constraints.
- Whether compatibility, migration, concurrency, failure behavior, and operational
  risks that matter to this change have been addressed.
- Whether the design preserves accepted vocabulary and product decisions, and
  whether a simpler alternative would materially improve the result.

Findings must cite exact requirement or decision IDs and supporting evidence.
Distinguish a confirmed inconsistency, an unresolved user decision, and an
optional improvement. Explain the consequence and recommend a bounded change.
Return no findings when none are supported; do not invent alternatives or new
terminology to fill the report. Current code may contradict intended behavior
without invalidating the requirement.

## Keep review separate from authorship

Write only the assigned output and evidence attachments. Do not edit canonical
requirements, feature files, designs, glossaries, code, or shared state. Do not
launch workers or ask the user directly. Return material questions with stable IDs,
competing meanings or options, evidence, and dependent work for the coordinator.

Use the shared output template. Include a coverage table identifying each reviewed
requirement or decision and any unreviewed scope, plus a findings table with stable
IDs, classification, source anchor, evidence, consequence, and recommendation.
`complete` means the review ran to completion, not that the document has no issues.
Return `needs-input` for material questions, or the appropriate incomplete status
when access, evidence, or budget prevents coverage. Report document consistency
separately from runtime verification.

## Coordinator resolution

The coordinator evaluates each finding against the evidence. Send supported
corrections to the original author in a new draft attempt using its fixed model;
record a reason when declining a finding. Ask the user about unresolved product,
vocabulary, or consequential design choices. Neither reviewer nor author may
settle these by majority vote or by silently changing the request.

Recheck affected sections after substantive corrections against the new artifact
digests. Reuse unaffected coverage with an explicit provenance link. If a bounded
correction and recheck still leaves disagreement, present the evidence and open
choice to the user rather than cycling indefinitely. Continue downstream only when
material issues are resolved or explicitly deferred within the user's scope.

A document review is not Design It Twice. Independent alternative designs are an
optional investigation for a consequential interface choice. They require a
shared problem statement and constraints without the author's candidate solution,
then comparison against the same requirements. Do not add that extra work to every
draft or treat a different model as proof that a design is better.
