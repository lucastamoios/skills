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
   - `thesis`: one sentence the video defends.
   - `viewer_before` and `viewer_after`: the viewer's situation, not the creator's.
   - `so_what`: the gain in the viewer's currency (money, time, safety, status, belonging).
   - `job`: the main job for the viewer.
   - `proof`: claims with `status: "sourced"` and their source, or `"needs_source"`.
   - `authority`: only from `creator.authority`; empty if none fits.
   - `demonstrable`: what the camera can show. If nothing, the angle is weak; say so in `risks`.
   - `fit_with_reference`: how a `reference_analysis` mechanism applies, if given.
   - `cta_bridge`: how the thesis leads to the product.
3. Respect `creator.constraints` and the creator's enemies (e.g. do not sell fear if the creator rejects selling fear; naming the viewer's real worry is different from inventing a threat).
4. Recommend one angle and say why in one or two sentences.

Return `needs_input` when `material` holds only opinions with no event, number, or scene. Ask for the missing case with a concrete question.
