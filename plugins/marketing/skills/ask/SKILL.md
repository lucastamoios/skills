---
name: ask
description: Generate questions that pull a concrete, filmable case out of a creator (scene, numbers, before and after, mistake, decision) instead of opinions, as structured JSON. Use before writing a script, when the creator has a topic or brand but no specific story yet.
---

# Case-eliciting questions

Opinions become essay scripts. Cases become videos. "What do you know that few people notice?" produced a thesis the expert rejected. "When was the last time AI made you waste time, what did you change, and how much did it save?" produced a scene, steps, and proof.

## Contract

Follow [the marketing contract](../../protocol/contract.md). Input schema: [ask.input](../../protocol/schemas/ask.input.schema.json). Output schema: [ask.output](../../protocol/schemas/ask.output.schema.json). Output JSON only.

## Method

1. Read `creator.brand`, `audience`, `product`, `goal`, `topic`, and `previous_questions`. Do not repeat a question already answered.
2. Write `count` questions (default 3). Each asks for one specific past event: "the last time", "the day you", "what happened when". Avoid "what do you think", "what is your opinion", "what do you know".
3. Each question should make it easy to answer with a scene, a number, a before and after, a mistake, a decision, proof, or steps someone can see. Tag them in `elicits`.
4. Aim at the audience's pain or desire, through the creator's real history. Prefer topics that lead to the product without forcing it.
5. Add two or three `follow_ups` for when the answer comes back abstract: "what exactly did you see on the screen?", "how long did it take before and after?", "what would you do differently?".
6. Write in the creator's language, short and conversational. One question per item.
