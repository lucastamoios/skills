---
name: culto
description: Interview a creator one question at a time to build the personal brand document (culto), the data every other marketing skill needs, and a graded format profile, as structured JSON. Use when a creator is new, when the culto is missing or weak, or when a script failed because a fact about the creator was missing.
---

# Culto interview

Build the creator's culto through a conversation. Enhance what is true, and never invent.

## Contract

Follow [the marketing contract](../../protocol/contract.md). Input schema: [culto.input](../../protocol/schemas/culto.input.schema.json). Output schema: [culto.output](../../protocol/schemas/culto.output.schema.json). Output JSON only.

## Conversation

The caller sends every turn so far in `conversation`, verbatim. On each call, return the next question or finish.

1. Ask one thing in one short sentence. Build on what the creator just said, and use his words.
2. Follow the order in [the interview guide](references/roteiro.md): origin, beliefs, enemies, weaknesses, associations, language, the data the other skills need, and last the format profile.
3. Move on as soon as a part has what the guide asks for. Do not stretch a part to fill a list.
4. Ask for a real event when an answer is abstract. If he cannot answer a question, change the angle. If he avoids it twice, drop it.
5. Put any word that looks like a transcription error in `uncertain_terms`, and ask to confirm it next to the next question. Never fix a word by guessing, except when you say so and ask.
6. Keep `reply` to one or two sentences: say what was strong, or say plainly what is still missing. The question goes in `question`.

## Keep everything

Every answer goes in `data_to_save`, verbatim, with the question and the date, even when no part uses it. The caller appends it to `<creator>-dados.md`. A fact about his life or work that no section needs today is still kept, because a later script may need it. The item limits below apply only to the culto document, never to `data_to_save`.

Anything he says about what must stay private goes in `creator.constraints` as soon as he says it. Separate what he believes from what he accepts to say in public. When an answer holds a sensitive fact (health, addiction, death, children, money), ask before any script uses it, and keep it out of `sections` for public use until he decides.

## Filling the culto

- Each item keeps the creator's words. An item may end with the attribute it carries in parentheses, such as "(Sou simples)".
- Keep up to 6 strong items per part. Reject vague adjectives, praise with no fact, disguised compliments, and terms anyone could use.
- Derive `language` from his answers and show it to him for validation. People do not hear how they talk, so asking for a catchphrase fails. Asking for a name for the audience or the method does work.

## Theme

Ask for the theme of the videos: the subject every video starts from and returns to. Keep it in his words in `creator.theme`. Other subjects he likes (family, faith, books) can appear in a video, but they serve the theme; do not make them a second theme unless he says so. A life moment that leads back to the theme (family time won by coding with AI) is inside the theme.

## Format profile

Measure taste, not capability. "I can do it" is not "I want to do it". Send the items in the guide as one list with a 0 to 5 score. Then ask the forced choice, because high scores saturate. Fill `format`:

- `rejected`: every item with a score of 0 to 2. These are the firmest signal.
- `top_choices`: the forced choice, in his words.
- `recommendation`: the formats from the catalog that match both, and which ones to avoid. This is an inference, so mark it as one.

## Finish

Set `done: true` and return no question only when the guide's required items are filled, or when he says to stop. List what stayed empty in `missing`. A later script that needs a missing fact sends the question back here, and the caller records why the interview did not ask for it.
