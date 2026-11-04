---
name: take
description: Pick up a specified ticket or piece of work by understanding its context, explaining what should change and why, and preparing Product clarification before requirements. Produce a reusable issue brief through dev, without implementing the change.
argument-hint: "[ticket or work description] | input=<absolute input.md> output=<absolute output.md>"
---

# Take

Establish enough shared understanding to start the selected work responsibly.
Explain the current situation, the proposed change, and its business or technical
reason. Preserve concepts and evidence for subsequent development stages.

## Invocation and ownership

For an ordinary invocation, route through [dev](../dev/SKILL.md) with `take` as
the requested stage and stopping boundary unless the user explicitly requests
further work. Picking up an issue does not authorize implementation. If the target
is ambiguous, the coordinator asks the user which work he means. Do not select a
backlog ticket, create a branch, or set up a runtime merely to start this stage.

With `input=<absolute input.md> output=<absolute output.md>`, execute only the
assigned `take` worker in `draft` mode. Read the [development contract](../dev/references/contract.md),
packet, and [output template](../dev/references/output-template.md). Validate
ownership, scope, digests, model, and permissions. An incomplete packet is a
contract error, not permission to route recursively.

Write only assigned artifacts and the exclusive report. The coordinator owns
user dialogue, task updates, shared indexes, and subsequent dispatch. Return
material questions with stable IDs rather than asking the user from a worker.

## Assign and start the issue

An ordinary `/take` invocation authorizes the coordinator to assign the selected
Linear issue to the user and move it to the issue team's `In Progress` status before
dispatching the intake worker. Resolve the user's Linear user identity and the
team's actual status ID from live data. Use the authenticated user only after
confirming that it is the user. Honor an explicit assignee or status override.

Read the current assignee and status, update only those fields that differ, and
verify the resulting values. Record the outcome in the run and related task note.
If identity, status, or access cannot be resolved, report the specific blocker
and continue independent intake work without claiming the update succeeded.
Prepared workers do not mutate Linear. Requests to edit this skill or inspect an
issue without taking it do not trigger these updates.

## Understand the issue

Read the full available ticket and relevant comments, attachments, linked work,
and decisions. Pin retrieved sources through the contract. Identify unavailable
sources and conflicting or superseded statements. Separate the original problem
from a suggested solution; a ticket is evidence of a request, not proof of behavior.

Explain who is affected, what they are trying to accomplish, and the current
workflow through one concrete example. Inspect relevant documentation, code,
existing changes, or permitted UI evidence to establish what already exists.
Distinguish observed behavior from code inference and user reports. Check relevant
existing work before assuming the feature is absent; branch existence does not
prove delivery or dependency readiness. Keep investigation proportional to the
uncertainty. Route bug diagnosis to `fix` rather than duplicating root cause work.

Follow the shared [vocabulary guidance](../dev/references/vocabulary.md).
Capture established concepts, their relationships, and applicable rules with
sources. Reuse existing definitions, retain meaningful context differences, and
ask when meaning is uncertain. Mark new terms or rules as proposals. Do not
create a glossary or promote a hypothesis into shared knowledge by default.

## Explain what should change and why

The coordinator's first substantive explanation to the user must state what the
work is about, what will change for the affected user compared with today, and
why that change matters in business terms. Use one short paragraph or three
short bullets. Present this overview before clarification questions, technical
details, or handoff status. Base it on available evidence and label uncertainty;
do not wait for every open question to be answered before explaining the scope.
The worker must put the same overview at the start of the brief so the
coordinator can relay it directly.

Connect each proposed change to the current limitation, affected workflow, and supporting
business rule or technical reasoning. Distinguish restoring an existing rule,
changing a rule, and changing the implementation while preserving a rule.

Explain technical reasons in terms of consequences, such as incorrect results,
reliability, compatibility, or maintainability. Do not invent business value to
justify a technical task. Cite evidence and identify assumptions. If the right
change remains unknown, state the alternatives and the decision needed rather
than writing a confident prescription. This is a proposed direction, not accepted
requirements or a technical design.

## Explain decisions and recommendations

Answer questions from available evidence first. Return only uncertainties that
materially affect scope, meaning, priority, or the next step. Present the result
as explanatory sections and subsections after the overview, not as a question
list or a decision table. Give each material decision a descriptive heading and
retain its stable ID for subsequent stages.

For each decision, explain:

- Where it applies in the user workflow, screen, or downstream operation, and
  whether this issue or a related issue owns that behavior.
- One concrete example that makes the alternatives and their consequences clear.
  Label invented examples as illustrative, not actual regulatory rules.
- What the evidence already settles and what remains uncertain or contradictory.
- The recommended behavior, why it fits the business need and existing behavior,
  and any material tradeoff or alternative. Do not force a recommendation when
  evidence is insufficient.
- The degree of confidence and its basis. Distinguish confidence in the
  recommendation from certainty about the intended or approved behavior.
- The precise choice still needed, its owner, and what depends on it. Put this
  after the explanation instead of making the reader reconstruct context from a
  bare question.

Use enough prose to make each decision understandable on its own. Keep the
opening overview succinct, but do not compress the decision context merely to
keep the result short. The coordinator must relay these sections in the chat,
not replace them with a count of unresolved questions or only a link to the brief.
The coordinator's assignee and status updates above are authorized by `/take`.
Do not send messages or make other external ticket changes without explicit
authorization.

Use `needs-input` when a material answer is required for dependent work. Preserve
the useful brief and identify independent work that can proceed. Optional
questions do not block the stage. Preserve question IDs and confirmed answers
across attempts; do not ask settled questions again without conflicting evidence.

## Deliver and hand off

Write the assigned issue brief using the [brief template](references/brief-template.md).
Reference it with a digest from the development output's stage result. Record
coverage, missing evidence, questions, and a recommended next stage. Stop once
there is enough understanding to explain the work and choose that stage.

Requirements owns agreed behavior, acceptance criteria, and BDD. Design owns
technical choices. This stage does not generate those artifacts, implementation
steps, or exhaustive edge cases. Reuse sufficient existing specifications and
recommend verification or closure when evidence shows no new change is needed.

Return the related task reference and a proposed update for the coordinator:
brief link, what should change and why, open question IDs and owners, and next
action. The coordinator persists this after validating the report. Completion of
intake does not mean completion of the ticket.
