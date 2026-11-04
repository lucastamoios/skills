---
name: reference
description: Explain why a short video that performed well worked, as structured JSON. Extract the mechanisms (reason why), hook promise, viewer job, functional structure, and what a creator must be able to show to reuse the pattern. Use when analyzing a reference Reel, Short, or TikTok.
---

# Reference analysis

Find the reason a video worked, not only what it contains. A script that copies the blocks of a reference and loses its mechanism fails (the expert called the result "dissertativo": an essay with no demonstration).

## Contract

Follow [the marketing contract](../../protocol/contract.md). Input schema: [reference.input](../../protocol/schemas/reference.input.schema.json). Output schema: [reference.output](../../protocol/schemas/reference.output.schema.json). Output JSON only.

## Method

1. Read the transcript with timestamps, the frame descriptions, the caption, and the metrics. If `notes` from the expert exist, they outrank your inference: record them with `source: "expert_notes"`.
2. Write `hook`: the first line, what is on screen, and the promise. The promise is what the viewer is told they will get, in their own terms. If there is no promise, say so.
3. List `reason_why` mechanisms in order of weight. Each needs evidence: a quote or a timestamped visual. Typical ones: demonstration while talking, result promise up front, simplicity, identification with the viewer's situation and constraint, concrete or visceral contrast, proof (before and after), a list worth saving, a geographic hook, authority. Do not list a mechanism without evidence.
4. Score `jobs`: what the video does for the viewer. One of: make me laugh; that's so me; that's so us (I send it to someone); help me do something; make me feel or think. Weights are independent and need not sum to 1.
5. Describe `structure` by function. For each segment, say what happens and why it matters to the viewer. Do not just label blocks.
6. Fill `execution_requirements`: what a creator in another niche must have to reuse it. A workout demo needs a visible body result; a dev needs a screen, an artifact, or a before and after.
7. Write `transferable_pattern` as the mechanism without the niche, and `not_transferable` for elements tied to this creator or niche.
8. Compute `success.views_per_follower` when both numbers exist. It measures reach beyond the creator's audience, not shareability. Mention shares and saves when given.

Return `needs_input` only when there is no transcript and no frames. A silent video with frames is valid.
