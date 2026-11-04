---
name: walkthrough
description: Explain a reviewed change by connecting its explicit requirements to implementation evidence, then trace one concrete case through the code interactively. Prepare requirement sections and connected explanations with a purpose for each next function and visible progress.
---

# Review Walkthrough

Teach the reviewed change from requested outcomes to their implementation. Use those requirements to organize the interactive code trail. Explain existing review evidence without running missing lenses or inventing findings.

## Start with checkout location

Before preparing or presenting an interactive walkthrough, the coordinator first shows the reviewed checkout's absolute folder path as a clickable link and its verified current Git branch. If HEAD is detached, say `detached HEAD` and show the short commit instead of inventing a branch or using the ticket's suggested branch name. Verify with `git -C <checkout> branch --show-current` and `git -C <checkout> rev-parse --short HEAD`. Record the same location in the teaching artifact. This short location preface precedes the business case and requirement sections.

## File interface

Read [the worker contract](../../protocol/contract.md). Accept `input=<absolute input.md> output=<absolute output.md>` with skill `walkthrough` and mode `prepare`. Write the required report to this exclusive output. The input declares context, snapshot, sources, model, dependencies, access, and budget. Do not infer them from the parent conversation.

If invoked with a PR, branch, or diff instead of a prepared input, use `review:run` to prepare and dispatch this lens in its configured agent. Do not perform the worker analysis inline. Inside a worker, never dispatch another lens, discover a task, or edit shared review artifacts. Report missing prerequisites through the output.

Follow repository instructions and use Graft and LSP when required or available. Write artifacts in English. Verify the input snapshot before and after analysis. Keep the reviewed checkout unchanged and write only the assigned output and attachments, subject to this lens's explicit execution mode.

## Required context

Require current paths when meaningful production behavior exists. Read the declared consolidated report and any listed current lens artifacts. Optional missing lenses are allowed; state which have not run. Read primary product sources for the business case and distinguish declared rules from software conventions. Never rely on the parent conversation to know what was reviewed.

## Research before teaching

Investigate the full change before the first explanation. Follow repository instructions and use Graft and LSP when required or available.

Build a top-down model:

1. The user, operator, or system problem.
2. The explicit requirements, their sources, and the expected product or business outcome.
3. One concrete case that makes the behavior visible.
4. The entrypoints and externally observable outputs.
5. The execution flow across boundaries and stored state.
6. The decisions, exceptions, and failure paths that matter.
7. The business rules encoded by validation, permissions, status changes, constraints, and tests.
8. Existing review findings and the evidence each lens contributed.

Read only the domain sources declared in the input, such as the configured direction, vocabulary and product-area notes. Follow relevant direct links within the packet's permitted access. Do not assume a particular organization's documentation layout or search personal journals.

Use real cases from tests, factories, seed data, task context, or cited vault notes. Label an invented teaching example as illustrative. Distinguish a legal or regulatory requirement from a the configured organization product or modeling decision. Do not imply regulatory authority when the evidence only shows a software convention.

## Establish the business rationale

Read the ticket description, acceptance criteria, relevant discussion and linked requirements. Explain what changed, who needs it, why the behavior exists, and what previous limitation or event made this work necessary. Attribute the rationale to these sources; do not invent motivation from the implementation. If the ticket is unavailable or silent, state the gap and distinguish inference from confirmed intent.

When the change concerns regulated behavior, consult relevant primary sources such as the regulator's official guidance or the applicable regulation. Verify jurisdiction, scope and effective date before using a source to explain a rule, and cite the specific supporting provision or passage. Explain how it connects to the ticket. A general regulation is not proof that a particular UI, default value or data model is legally required. If no applicable regulatory source is established, say so briefly and explain the sourced product rationale. Do not force a regulatory explanation onto ordinary technical work.

Prepare a brief opening business case with the relevant rules and exceptions and the before/after outcome. Follow it with the requirement sections described below. Separate legal obligations, explicit ticket requirements and the configured organization modeling decisions. Define domain terms before using acronyms. Link the implementation where it addresses a requirement; defer execution details and framework mechanics to the interactive code topics.

## Map requested outcomes to implementation

Extract the explicit requirements from the ticket, acceptance criteria, linked specifications and accepted clarifications. Preserve existing requirement IDs. When the sources have no IDs, assign local labels and identify them as walkthrough references. Cite each requirement's source and retain its conditions, exceptions and constraints. Do not derive requested behavior from the implementation alone.

Reuse a declared intent-review mapping when its sources and code snapshot match. Check its implementation citations against current source. If no compatible mapping exists, prepare the source-to-code explanation from the declared product sources and inspected implementation. This does not require running a missing review lens. If the sources cannot establish requirements, state that limitation and organize the walkthrough around observable behaviors, labeling inferred intent explicitly.

Prepare one short section per requirement, with its ID and requested outcome in the heading. Each section explains:

- What was requested, with a link to its source.
- Where the implementation produces or enforces that behavior, with exact clickable source lines and a brief explanation of each relevant function's responsibility. Include existing code when the change relies on it.
- What inspection, test assertions and recorded test or QA execution establish, and what remains uncertain. A located function or an unexecuted test does not establish satisfaction.
- Which walkthrough part explains the behavior in detail.

Use sections and short paragraphs, not a requirements table. Keep implementation evidence, verification evidence and explanation progress distinct. State partial implementation, missing code or unavailable evidence explicitly. Refer to existing canonical findings where applicable; record newly noticed concerns as unresolved follow-ups without creating walkthrough findings or implying approval.

## Establish connected contextual vocabulary

Define unfamiliar terms as they appear in the business case and requirement sections. Before the first detailed code explanation, prepare a short glossary for the running case using compact definitions rather than a table. Define ordinary words too when they have a specific meaning here, such as rule, assignment, candidate or baseline. Each definition explains what the term means in this feature and how it relates to another term: what contains it, produces it, compares it or changes it. Use precise terms when an umbrella word has several meanings. Distinguish domain meaning from its representation in code.

Keep the glossary small and introduce additional terms when the trail reaches them. Bold the relevant terms and their related terms in definitions and later prose so the reader can recognize the connections. Use the same names throughout. Explain differences between interface labels and stored values when relevant.

Ground inputs, intermediate state and returned data in the interface or observable workflow. Identify the control that supplies an input, the visible result that a return supports, and which actions change temporary or persisted state. Explain hidden fields only when they matter to the current behavior. For a backend-only flow, connect them to its caller, output or stored effect instead. Use current source or observed UI as evidence; do not claim a screen was exercised from template inspection alone. A recording or diagram is optional, not a prerequisite.

## Connect prior review evidence

At the relevant topic, explain existing review evidence rather than merely listing its status.

For each canonical finding, state:

- What behavior or invariant the finding concerns.
- Which lenses supplied evidence, using the consolidated mapping of run, job, lens, and original finding IDs.
- Why each lens exposed it in that context. For example, intent found a requirement gap, code traced the wrong branch, tests showed that a regression would escape or identified a flakiness trigger, QA reproduced the failure through Playwright, or risk identified an external consumer.
- How the evidence from the lenses complements rather than duplicates each other.

If a lens passed without findings, explain only what that pass establishes. Do not claim broader certainty. For example, a QA pass means the mapped scenarios matched their expected outcomes, not that no defect exists.

Never copy the same finding into a new walkthrough finding. Link or refer to its canonical heading in the declared consolidated report.

## Create the topic map

Use the business case and requirement sections as the opening topic. Derive the code topics from the requested outcomes, grouping requirements that belong to the same connected workflow. Choose a real entrypoint for the running case, such as a user request, import command, event handler or scheduled job. Prefer the main user flow over a helper or migration unless the change itself is a migration or background operation.

Within each workflow, organize the topics along its execution order: input and access checks, business decisions, calls and state changes, then output and failure paths. Keep supporting files with the behavior they serve. Choose three to seven topics as appropriate. Do not force one topic per requirement if that fragments the flow. A requirement can span several topics, and a function can serve several requirements. Explain shared logic once and refer back to it. Do not jump between unrelated files or present all entrypoints before tracing one complete flow. Retain the map in the artifact and link the requirement sections to its parts.

Express the topic map as a short list of behaviors with the associated requirement IDs and a concrete question to answer for each. Cover all explicit requirements, changed outcomes, independent actions and affected existing flows, including callers of shared or extracted code when relevant. Identify supporting behavior separately when it has no explicit requirement. Retain requirements with missing implementation or evidence as unresolved questions. Reading every function is not itself proof that every behavior was checked.

### Choose the most useful starting point

When several entrypoints exist, prioritize the one that best represents the ticket's main user outcome and exposes the important changed rules. Explain the choice briefly when starting the code discussion; defer secondary routes rather than touring them all.

Choose a function that helps the reader connect the case's inputs, decisions and outputs. This may be an entrypoint, a central business function or an orchestration function that reveals the surrounding responsibilities. Establish its importance from current source and callers, not function size or graph degree alone. Explain what understanding it unlocks without claiming that a fixed percentage of the change is covered. Connect it to the user action and summarize framework wiring until the reader asks to inspect it. Do not require a detour through every thin handler or signal before explaining the behavior it serves.

Record the chosen primary entrypoint, central functions, related requirements and teaching order in the artifact. Begin the teaching with the business case and requirement sections after the checkout-location preface.

## Produce the teaching artifact

Add the brief business case, requirement sections and their sources, applicable regulatory sources, connected glossary, chosen starting function, behavior questions, review-context sections, and a prepared explanation for each topic to the common output. Use headings and short prose for walkthrough content rather than tables. Each topic explanation stays below approximately 350 words. After the opening, state which requirements the topic addresses, then connect business meaning, contextual terms, exact source links, inputs, three to five execution steps, returned data and its observable effect, sourced business rule, and relevant existing review evidence. Record the requirements explained, a purpose for the next function, and what remains to understand or verify. Cite full finding provenance and current source lines. Do not create new canonical findings; record unreviewed concerns as follow-ups.

Use verdict `prepared` or `undetermined` independently of coverage. Return the output link and topic count. The background worker finishes after writing the artifact, without asking the user to select a topic.

For an interactive invocation, the coordinator then follows [presentation.md](references/presentation.md). It first gives the verified folder and branch, then the brief business case and requirement sections before tracing the code. Introduce connected vocabulary when needed. Later answers follow the reader's questions one topic at a time while retaining the requirement mapping and behavior questions as a coverage guide. This preserves the interactive walkthrough without coupling the worker's completion to the conversation.
