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
3. **Carry the mechanism, not the blocks.** If `reference_analysis` is given, reuse its `transferable_pattern` and respect its `execution_requirements`. If the creator's `assets` cannot meet them, change the visual and record why in `visual_alternatives`.
4. **Steps need examples when the niche is not visual.** A workout list works dry because the body shows each step. In dev or abstract niches, each step is: action, plus an example from the creator's case, plus what it avoided. Prefer fewer steps over vague ones.
5. **Every beat has a `visual`.** The camera always shows something: the creator, a screen, an object, handwritten text, a before and after. Prefer a person on camera with proof on screen.
6. **Simple and spoken.** Short sentences, the creator's words from `voice_samples` and `brand`, no essay connectors. Read it aloud mentally; if it sounds written, rewrite.
7. **CTA names the audience's pain or desire, then offers the product** with where to find it. If `offer` is given, build the CTA from one of its `cta_lines` or from its `enemy`, `why_now` or `what_to_lose` answers, and pick the one that continues the angle's thesis. Do not invent a freebie, keyword reply, or deadline the creator did not offer.
8. **Claims.** Every number, employer, result, or date in a line appears in `claims`. Without a source in `material`, `creator.authority`, or `creator.brand`, use a bracketed placeholder in the line and `status: "needs_source"`.
9. **Timing.** About 2.5 spoken words per second. Hit `target_seconds` (default 30) within 20 percent. If the content needs more, keep it and add a `visual_alternatives` entry proposing a split into two short videos.
10. Fill `preparation` with what to set up before recording and give two `visual_alternatives` with their trade-offs (e.g. talking head with screen behind; the creator playing two characters).

## Revise mode

Require `previous_script` and `critique`. Apply every `blocker` and `major` issue, keep everything listed in `critique.keep`, and follow `rewrite_brief`. Record each change in `changes` with the issue it answers. Do not rewrite beats that had no issue. If the critique's verdict is `rethink`, return `needs_input` pointing at the upstream step to redo.
