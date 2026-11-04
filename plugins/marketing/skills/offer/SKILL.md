---
name: offer
description: Build a creator's offer as structured JSON with a One Belief and answers to the 10 offer questions (difference, why care, how true, problem mechanism, enemy, why now, why trust, solution mechanism, how to start, what to lose), plus ready CTA lines and the gaps in proof. Use to define or strengthen what a video's CTA sells.
---

# Offer

Turn a product description into an argument the viewer can accept in seconds. The CTA of every script draws from this: the enemy becomes the pain it names, why-now becomes the urgency, the proof becomes the reason to trust.

## Contract

Follow [the marketing contract](../../protocol/contract.md). Input schema: [offer.input](../../protocol/schemas/offer.input.schema.json). Output schema: [offer.output](../../protocol/schemas/offer.output.schema.json). Output JSON only.

## Method

The model is the expert's (the configured editor's) offer template: one belief, then ten questions. Answer each in the creator's voice, short enough to say aloud.

1. **One Belief.** One sentence: "X is the key to Y, and that is only possible through Z", where Y is what the audience wants and Z is the product's mechanism. If the viewer accepts it, buying or joining is the obvious next step.
2. **The ten answers**, in this order and with these ids:
   - `difference`: how this differs from everything the audience has seen. Prefer what cannot be copied: the creator's experience, judgment, personality.
   - `why_care`: the concrete gain for the audience, in their terms (money, job, time, status), not features.
   - `how_true`: the proof. Only cases, numbers and results present in `material` or `creator.authority`. Otherwise `strength: "missing"` and say which case to collect.
   - `problem_mechanism`: why the audience is not succeeding today, as a cause they did not see, not "lack of effort".
   - `enemy`: who or what is to blame, outside the viewer. It must fit the creator's own stated enemies and constraints.
   - `why_now`: what changed that makes waiting costly.
   - `why_trust`: the creator's verifiable credentials and history.
   - `solution_mechanism`: how the product works, in 3 to 7 named steps.
   - `how_start`: the exact first action, where, and the price or "grátis".
   - `what_to_lose`: what staying put costs the viewer.
3. **Strength.** Mark each answer `strong`, `weak` (plausible but generic or unproven) or `missing`, and fill `to_strengthen` for every non-strong answer.
4. **Claims.** Every number, employer, date or result goes in `claims`, with `needs_source` when the input does not support it. Never invent cases, testimonials, students, prices, deadlines or bonuses.
5. **CTA lines.** Write at least three, each leaning on a different answer (`enemy`, `why_now`, `what_to_lose`, `why_care`...). At most 25 spoken words: the pain or desire first, then the product and where to find it.
6. **Tensions.** List every conflict between the offer and the creator's brand (beliefs, enemies, constraints), the expert's notes, or the product data (e.g. a free product marked paid). Example: the expert wants a fear-of-replacement CTA, but the creator rejects selling fear of AI. Do not resolve a tension silently; propose a wording that respects the creator and record it.
7. **Next steps.** Ordered actions that would turn weak or missing answers into strong ones.

Return `needs_input` only when `product` has no offer or audience at all. Missing proof is not missing input: answer with `strength: "missing"`.
