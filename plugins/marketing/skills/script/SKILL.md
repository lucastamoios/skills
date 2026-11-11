---
name: script
description: Write or revise a short-video script (Reels, Shorts, TikTok) beat by beat as structured JSON, with exact lines, visuals, timing, CTA, sourced claims, and preparation. Use with an angle from marketing:angle; in revise mode, apply a critique from marketing:critique.
---

# Script

Write what the creator will say and what the camera will show, beat by beat. The script carries the angle's thesis through the reference's mechanism in the creator's voice.

## Contract

Follow [the marketing contract](../../protocol/contract.md). Input schema: [script.input](../../protocol/schemas/script.input.schema.json). Output schema: [script.output](../../protocol/schemas/script.output.schema.json). Output JSON only.

## Generate mode

1. **Hook (first 3 seconds).** Open with what changed for the viewer or what they will get, not with the creator's feat. Show something at the same time. One sentence.
2. **Promise and so-what early.** Within the first 8 seconds the viewer knows what they gain.
2b. **Start from the theme and return to it.** `creator.theme` is the purpose of every video. The hook or the promise puts the viewer inside the theme, and the beat before the CTA brings the fact back to it, in plain words. Videos can differ in subject, example and format, and a beat can drift a little from the theme; what stays the same is that the viewer ends on the theme. A life moment (family, faith, a past job) is a valid way into the theme when the video shows what it says about it. Naming the theme only in the CTA does not count. Do not add a lesson about the theme that `material` or the angle does not support.
3. **Structure.** Without a reference, use the content expert's default: hook from what changed for the viewer, how it works explained simply, the insight (the "sacada"), CTA.
3b. **Carry the mechanism, not the blocks.** If `reference_analysis` is given, reuse its `transferable_pattern` and respect its `execution_requirements`. If the creator's `assets` cannot meet them, change the visual and record why in `visual_alternatives`.
4. **Steps need examples when the niche is not visual.** A workout list works dry because the body shows each step. In dev or abstract niches, each step is: action, plus an example from the creator's case, plus what it avoided. Prefer fewer steps over vague ones.
4b. **Spoken examples are real.** Every example in a line comes from `material`. Do not invent a demo scenario (a discount rule, a fictional client) and narrate it as if it happened; the viewer cannot tell it apart from the creator's case. If the beat needs an example and `material` has none, return `needs_input` with a question that asks the creator for one.
4d. **Stop instead of writing half a case.** If the angle has no `outcome`, or a question in its `risks` blocks the video from closing, return `needs_input` with that question. Do not write a script that ends before the outcome.
4e. **Keep the creator's words.** A thesis or opinion of the creator is said with his wording, not softened or extended ("não é" stays "não é", not "não é só"). Any statement about what happened or what he thinks, not only numbers and dates, goes in `claims` with its source.
4c. **Connect the facts.** Each fact about the creator must connect to the next line and to the thesis. Two loose facts in one sentence (an employer and a team habit) read as one claim the creator did not make.
5. **Every beat has a `visual`.** The camera always shows something: the creator, a screen, an object, handwritten text, a before and after. Prefer a person on camera with proof on screen.
6. **Simple and spoken.** Short sentences, the creator's words from `voice_samples` and `brand`, no essay connectors. Read it aloud mentally; if it sounds written, rewrite.
7. **CTA names the audience's pain or desire, then offers the product** with where to find it. If `offer` is given, build the CTA from one of its `cta_lines` or from its `enemy`, `why_now` or `what_to_lose` answers, and pick the one that continues the angle's thesis. Do not invent a freebie, keyword reply, or deadline the creator did not offer.
8. **Claims.** Every number, employer, result, or date in a line appears in `claims`. Without a source in `material`, `creator.authority`, or `creator.brand`, use a bracketed placeholder in the line and `status: "needs_source"`. The `offer`, `angle` and `critique` inputs are not sources: a fact that only appears there stays `needs_source`.
8b. **Each beat says something new.** Never repeat an idea, a date, or a phrase in another beat. In `revise` mode, cutting counts as much as adding: when a new fact comes in, remove what it makes unnecessary.
9. **Length follows the content.** Say everything an outsider needs to understand the whole, and nothing that does not serve the idea. Do not cut a needed link to be short; a short script that leaves the viewer without the "what was it?" fails. Back each claim with the concrete thing behind it (the fact, the example, the reason), in plain words. Compute `estimated_seconds` at about 2.5 spoken words per second as information only. If `target_seconds` is given, it is the user's preference, not a limit; if the content clearly holds two ideas, propose a split in `visual_alternatives`.
10. Fill `preparation` with what to set up before recording and give two `visual_alternatives` with their trade-offs (e.g. talking head with screen behind; the creator playing two characters).

## Revise mode

Require `previous_script` and `critique`. Apply every `blocker` and `major` issue, keep everything listed in `critique.keep`, and follow `rewrite_brief`. When `expert_notes` holds the creator's own feedback, it overrides the critique. A fix that would bring a fact not in `material` is not applied; keep the fact out or mark it `needs_source`. Record each change in `changes` with the issue it answers. Do not rewrite beats that had no issue. If the critique's verdict is `rethink`, return `needs_input` pointing at the upstream step to redo.
