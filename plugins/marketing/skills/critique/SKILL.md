---
name: critique
description: Judge a short-video script the way the content expert does and return a structured verdict (approve, revise, rethink), per-criterion scores, beat-level issues with concrete fixes, what to keep, and a rewrite brief. Use after marketing:script, in a loop with script revise mode.
---

# Critique

Replace the expert's manual back-and-forth ("better hook", "more visceral", "change these words") with a judgment that a script revision can act on. The expert's experience: the model knows the rules but does not follow them, so this skill checks each rule against the actual lines.

## Contract

Follow [the marketing contract](../../protocol/contract.md). Input schema: [critique.input](../../protocol/schemas/critique.input.schema.json). Output schema: [critique.output](../../protocol/schemas/critique.output.schema.json). Output JSON only.

## Method

1. Load the built-in [criteria](references/criteria.md). Criteria in `input.criteria` with the same `id` replace the built-in ones; new ids are added.
2. Score each criterion 0 (fails), 1 (partly), or 2 (meets), quoting the line or beat as `evidence`. Do not score from the angle or intentions; score what is written.
3. For each failure, write an issue anchored to a `beat_id` with a concrete `fix`: a replacement line, a new visual, or a cut. "Make it more engaging" is not a fix.
4. Severity: `blocker` when the viewer would scroll away or be misled (no promise in the hook, unsourced claim stated as fact, nothing to show); `major` when the expert would ask for a change; `minor` for polish.
5. List in `keep` what works, so the revision does not break it.
6. Verdict:
   - `approve`: no blocker or major issue.
   - `revise`: fixable by rewriting lines and visuals.
   - `rethink`: the problem is upstream: the material is an opinion with no case, the angle has no so-what, or the reference mechanism cannot be executed with the creator's assets. Say which step in `rethink_reason`.
7. Write `rewrite_brief` as direct instructions to marketing:script in revise mode, ordered by impact.
8. If `round` equals `max_rounds` and the verdict would still be `revise`, return the verdict anyway and add a warning that a human should decide.

Write `summary` as the expert would say it: two plain sentences, no scores.
