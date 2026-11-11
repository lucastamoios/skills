---
name: angle
description: Turn a creator's concrete case into video angles that say why the viewer should care, as structured JSON. Each angle states the thesis, the viewer's before and after, the "what do I gain" answer, the job, sourced proof, what can be shown, and the bridge to the product. Use after collecting a case and before writing a script.
---

# Angle

The expert's main correction: the viewer does not care what you built. They ask "what do I gain?". An angle that tells the creator's feat fails. An angle that contrasts the viewer's before and now works: "five years ago this app needed a whole team; today I built it in 7 days. Building is easy now; getting people to use it is the hard part, and that is where devs still earn money."

## Contract

Follow [the marketing contract](../../protocol/contract.md). Input schema: [angle.input](../../protocol/schemas/angle.input.schema.json). Output schema: [angle.output](../../protocol/schemas/angle.output.schema.json). Output JSON only.

## Method

1. Read `material` first. It is the only source of facts. Read `creator` for voice, beliefs, enemies, authority, and assets, and `product` for the offer.
2. Propose two or three materially different angles. For each:
   - `thesis`: one sentence the video defends, taken from the creator's own words in `material`. Fill `thesis_basis` with the quoted words it comes from, or with `inference: ...` when it goes beyond them; an inferred thesis also goes in `risks` as a question to the creator. Do not close a thesis the creator did not say.
   - `outcome` and `outcome_basis`: the desfecho the thesis stands on (what changed after, for whom), quoted from `material`. Read the thesis and the outcome together: the thesis must follow from the outcome, and the video tells the outcome to earn the thesis. An angle without an outcome in `material` is not offered.
   - `viewer_before`, `viewer_after` and `so_what` follow the same rule: they may describe the viewer, but they must not put a lesson in the creator's mouth that `material` does not hold.
   - `viewer_before` and `viewer_after`: the viewer's situation, not the creator's.
   - `so_what`: the gain in the viewer's currency (money, time, safety, status, belonging).
   - `job`: the main job for the viewer.
   - `proof`: claims with `status: "sourced"` and their source, or `"needs_source"`.
   - `authority`: only from `creator.authority`; empty if none fits.
   - `demonstrable`: what the camera can show. If nothing, the angle is weak; say so in `risks`.
   - `fit_with_reference`: how a `reference_analysis` mechanism applies, if given.
   - `cta_bridge`: how the thesis leads to the product.
   - Substance: prefer the aspect with concrete content to fill the video (facts, an example, a line of reasoning the creator actually gave) over the most general thesis. The thesis can be abstract if the material behind it is consistent; a thesis with nothing behind it makes a slogan, not a video.
   - One main aspect: each angle is built around one aspect of the material (one idea, one turn). Bring in other facts or cases only when they serve that aspect and the whole still makes sense. List the aspects you left out in `risks` as "future angle: ...", so they become other videos instead of crowding this one.
2b. **Start from the fact, land on the theme.** `creator.theme` is the direction of every video. Each angle connects the fact in `material` to the theme: the viewer must leave with something about the theme, not only with the creator's story. The fact can come from any moment of the creator's life (a bug, a family night, a book); the thesis is what that moment says about the theme. A video that drifts a little from the theme is fine. A personal moment is inside the theme, not outside it, when the video shows what it says about the theme: the same theme can be told through many moments of the creator's life. What fails is a video whose lesson is about something else, with the theme only in the CTA. Say the bridge in one line in `thesis_basis` or `cta_bridge`. Do not offer an angle that never reaches the theme; if no angle from this material reaches it, say so in `warnings` and still recommend the closest one. Do not invent a link the creator did not make: when the bridge is an inference, mark it `inference: ...` and add it to `risks` as a question.
2c. **Do not repeat an earlier script.** Read `previous_scripts`. Do not offer an angle whose thesis matches one already made, even with other words or another fact. Staying in the same theme is expected; what must change is the thesis and the example. When a fact was used before, find what it says that the earlier script did not, or say in `warnings` that the fact is spent. Name the closest earlier script in `risks` for each angle, with one line on what is new.
3. Respect `creator.constraints` and the creator's enemies (e.g. do not sell fear if the creator rejects selling fear; naming the viewer's real worry is different from inventing a threat).
4. Recommend one angle and say why in one or two sentences.

Return `needs_input` when `material` holds only opinions with no event, number, or scene, or when no angle has both a thesis and an outcome from the creator's words. Ask for the missing part with a concrete question that quotes what the creator already said. A question that blocks the video goes in `missing_inputs`, never only in `risks` or `warnings`.
