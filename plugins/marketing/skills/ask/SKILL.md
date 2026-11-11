---
name: ask
description: Generate questions that pull a concrete, filmable case out of a creator (scene, numbers, before and after, mistake, decision) instead of opinions, as structured JSON. Use before writing a script, when the creator has a topic or brand but no specific story yet.
---

# Case-eliciting questions

Opinions become essay scripts. Cases become videos. "What do you know that few people notice?" produced a thesis the expert rejected. "When was the last time AI made you waste time, what did you change, and how much did it save?" produced a scene, steps, and proof.

## Contract

Follow [the marketing contract](../../protocol/contract.md). Input schema: [ask.input](../../protocol/schemas/ask.input.schema.json). Output schema: [ask.output](../../protocol/schemas/ask.output.schema.json). Output JSON only.

## Conversation

`ask` is a conversation, not a single questionnaire. The caller sends back every turn of the current case in `conversation`, and `ask` decides what to ask next until the case is whole. It has two modes in the same conversation and reports the current one in `mode`:

- `discover`: the creator does not know what to talk about (no `topic` and no `conversation`, or he says so). Interview him to find it: the first question must come from an opener in [the interview questions](references/perguntas.md): pick the one that best fits his history, style and enemies and leads to a topic not yet used, rewrite it with his words, and quote it in `source_opener`. Do not invent an opening outside the bank. In later turns, follow what he answered. Skip `previous_questions` and `used_topics`. Vary the source between turns (a recent event, an old project, a mistake, something he disagrees with). When an answer reveals a real case, fill `case.topic` and move to `complete`. If it holds several, ask which one he wants to tell.
- `complete`: the creator came with a topic, or an answer revealed one. Close the case below. If he starts by talking about something, go straight here.

Every question asks one thing. Ask it in one short sentence, the way a person talks, and leave the next thing for the next turn: "O que estava na sua tela, o que você deixou de fazer e o que fez depois?" is three questions. Do not open by quoting his brand back at him; a short bridge is enough when it follows what he just said. The rest of what you want goes in `follow_ups`.

The interview joins everything: the topic, the case, how he would show it, and his way of saying it. His literal sentences are his voice, so ask him to tell it the way he would tell a colleague, and do not rewrite his answers.

A case is whole when the creator's own words hold, together:

- `what_happened`: the event or scene, and what the creator did in it.
- `outcome`: the desfecho, what changed after and for whom (a number or proof when there is one).
- `thesis`: what the creator says the case means, usually what he thinks most people get wrong.
- `format_evidence`: how he would show it, from the scene he lived: who he was with, what he used or showed, where. Ask for it last, with the matching question in [the interview questions](references/perguntas.md), and only the part still vague.
- `viewer_action`: when the video tells the viewer to do something, what the creator recommends in his own words, and what he did himself, concretely (who he contacted, how, what he asked). Never let a later skill turn his story into advice he did not give.
- the link between them: the thesis must follow from the outcome. A thesis with no outcome behind it is an opinion; an outcome with no thesis is an anecdote.

On every call with `conversation`:

1. Fill `case` from the answers only, quoting the creator's words. Do not complete a part yourself; leave it empty and list it in `missing`.
2. If something is missing, ask only about the gap: one question (two at most), short and concrete, that build on what the creator just said, using his words ("Você disse que perdia uma tarde por semana montando orçamento. Quando passou a usar a planilha, o que mudou?"). Prefer the `follow_ups` already prepared for that question.
3. If the thesis and the outcome do not connect, ask how one leads to the other.
4. List in `uncertain_terms` any word that looks like a transcription error, and ask to confirm it inside the next question. If he skips the confirmation more than once, stop asking: keep the word in `uncertain_terms`, say in `warnings` that later steps must not use it, and do not hold the case for it.
5. When he says he did not measure something, do not ask for that number again. A demonstration he can show on screen, or a mechanism explained so that anyone can check it, counts as `proof` and as the `outcome`: quote the mechanism in his words in `outcome`, and describe in `proof` what the screen would show, marked as not measured. Never write the number for him.
6. Set `done: true` and return no questions only when nothing is missing. `angle` runs only after that.

Without `conversation` and with a `topic`, start in `complete` with the method below. Without either, start in `discover`.

## Method

1. Read `creator.brand`, `audience`, `product`, `goal`, `topic`, and `previous_questions`. Do not repeat a question already answered.
2. Write `count` questions (default 1, two at most in a conversation). Each asks for one specific past event: "the last time", "the day you", "what happened when". Avoid "what do you think", "what is your opinion", "what do you know".
3. Each question should make it easy to answer with a scene, a number, a before and after, a mistake, a decision, proof, or steps someone can see. Tag them in `elicits`.
4. Aim at the audience's pain or desire, through the creator's real history. Prefer topics that lead to the product without forcing it.
5. Add two or three `follow_ups` for when the answer comes back abstract: "what exactly did you see on the screen?", "how long did it take before and after?", "what would you do differently?".
6. Write in the creator's language, short and conversational. One question per item, one thing per question.
