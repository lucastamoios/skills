---
name: brainstorm
description: Explore rough ideas, hunches, and open questions, then use selective structured reasoning when a concrete decision emerges. Ground the discussion in evidence, examine trade-offs and consequences, and conclude when the question is sufficiently resolved or the user chooses to stop.
argument-hint: "<an idea, concern, or decision to explore>"
---

# Brainstorm

Help the user explore an idea and reach a useful understanding or decision. Begin
with the shape of the question: explore freely when the problem is unclear, and
reason more deliberately when the options become concrete. Move between these
approaches as the discussion requires. They are not separate mandatory phases.

Keep this conversational. Write files or implement changes only when requested.
A decision to prefer an option does not by itself authorize implementation.

## Explore the question

Identify the concern, desired outcome, and what remains uncertain. If the prompt
already contains a concrete decision, begin there rather than reopening broad
discovery. When code or project behavior matters, inspect relevant evidence using
the project's context tools. Use external sources when they can resolve a real
gap or supply a useful alternative.

Ask focused questions that clarify meaning, challenge a material assumption, or
open a promising direction. Prefer the next useful question; batch closely related
questions when answering them together is easier. Use what the user has already said
and avoid repeating settled questions.

Follow productive threads. Offer alternatives when they reveal a real choice.
Challenge an assumption once with evidence and explain its consequence. Do not
manufacture an opposing argument just because the user is leaning toward an answer.
Keep facts, hypotheses, illustrative cases, and preferences distinct.

## Reason through a concrete decision

When a decision emerges, state it briefly with the viable options, constraints,
and criteria that matter. Check that it captures the user's concern. Do not require
a separate confirmation turn when his intent is already clear.

Choose only the reasoning tools that could change the decision or expose a
material risk:

- **Trade-offs:** Compare what each option gains and gives up under the actual
  constraints. Include the current approach when retaining it is a viable choice.
- **Inversion:** Identify concrete conditions that would make an option fail or
  become unacceptable. Ground them in the system rather than invented scope.
- **Second-order consequences:** Trace important effects on callers, operations,
  data, or future changes beyond the immediate benefit.
- **Pre-mortem:** For a consequential or difficult-to-reverse choice, describe a
  plausible failure, its trigger, and its user impact. Use it to identify a
  preventive measure or a deciding question.
- **Identity and deduplication:** When relevant, check determinism for the same
  logical input, uniqueness across distinct events, and stability across retries.
  Define the intended identity first; these properties depend on that definition.
- **Evidence or experiment:** Identify the smallest code inspection, source check,
  or authorized prototype that would distinguish uncertain options. Say when the
  available evidence cannot settle the choice.

These are a toolkit, not a checklist. Skip irrelevant tools, combine related
reasoning in one response, and stop expanding a point once it is clear. If the
analysis exposes a mistaken framing, return to exploration. Scale depth to the
stakes and uncertainty; a simple choice may need only a short comparison.

## Conclude when useful

Offer a concise synthesis when there is enough evidence to answer the question,
when further exploration is unlikely to change the decision, or when the user asks
to wrap up. Do not keep asking questions or searching solely to prolong the chat.
If he wants to continue exploring, follow that direction.

State the conclusion or recommendation, its main reason, and any material
uncertainty. Use a comparison table when it makes the choice easier to assess.
If the current design is sound, say so. If the choice remains open, identify the
specific missing fact or preference and the smallest next step to resolve it.

Suggest requirements, design, planning, or an experiment only when it advances the
actual goal. Do not require a workflow handoff or a procedural closing question.
Respect a request to stop, change direction, or move to authorized implementation
without insisting on finishing an analysis sequence.
