---
name: critique
description: Judge a short-video script the way the content expert does and return a structured verdict (approve, revise, rethink), per-criterion scores, beat-level issues with concrete fixes, what to keep, and a rewrite brief. Use after marketing:script, in a loop with script revise mode.
---

# Critique

Replace the expert's manual back-and-forth ("better hook", "more visceral", "change these words") with a judgment that a script revision can act on. The expert's experience: the model knows the rules but does not follow them, so this skill checks each rule against the actual lines.

## Contract

Follow [the marketing contract](../../protocol/contract.md). Input schema: [critique.input](../../protocol/schemas/critique.input.schema.json). Output schema: [critique.output](../../protocol/schemas/critique.output.schema.json). Output JSON only.

## Method

1. Load the built-in [criteria](references/criteria.md), including its calibration examples. Criteria in `input.criteria` with the same `id` replace the built-in ones; new ids are added.
2. Check every claim and every spoken example against the text of `material` (and `creator.authority`, `creator.brand`), not against the source the script declares. A claim sourced only from `offer`, `angle` or another skill's output fails `claims_sourced`. A spoken example that is not in `material` fails `claims_sourced` even when `preparation` calls it a demo.
2b. Score each criterion 0 (fails), 1 (partly), or 2 (meets), quoting the line or beat as `evidence`. Do not score from the angle or intentions; score what is written. Do not score length. Count the spoken words yourself (about 2.5 per second) and report the count and seconds in `warnings`, compared with the reference duration when `reference_analysis` gives one and with the calibration examples in the criteria. A script is never better for being shorter.
3. For each failure, write an issue anchored to a `beat_id` with a concrete `fix`: a replacement line, a new visual, or a cut. "Make it more engaging" is not a fix. A fix never introduces a fact, number, date or example that is not in `material`; when one is needed, the fix is a question to the creator.
4. Severity: `blocker` when the viewer would scroll away or be misled (no promise in the hook, unsourced claim stated as fact, nothing to show); `major` when the expert would ask for a change; `minor` for polish.
5. List in `keep` what works, so the revision does not break it.
6. Verdict:
   - `approve`: no blocker or major issue.
   - `revise`: fixable by rewriting lines and visuals.
   - `rethink`: the problem is upstream: the material is an opinion with no case, the angle has no so-what, or the reference mechanism cannot be executed with the creator's assets. Say which step in `rethink_reason`.
7. Write `rewrite_brief` as direct instructions to marketing:script in revise mode, ordered by impact.
7b. When every blocker and major fix needs a fact only the creator can give (an outcome, a real example, how the thesis connects), return `status: "needs_input"` with the exact questions in `missing_inputs`, quoting his words. Keep the full `result` (scores, issues, verdict) for the record. Another script round without the fact only produces placeholders.
8. If `round` equals `max_rounds` and the verdict would still be `revise`, return the verdict anyway and add a warning that a human should decide.

Write `summary` as the expert would say it: two plain sentences, no scores.
