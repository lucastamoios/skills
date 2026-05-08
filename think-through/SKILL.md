---
name: think-through
description: Structured reasoning skill for working through tricky design decisions, trade-offs, and "something feels off" moments. Uses proven frameworks (pre-mortem, inversion, three-property tests) to surface hidden assumptions and edge cases before committing to a design.
user_invocable: true
allowed-tools: Bash(git *), Read, Grep, Glob, Agent, AskUserQuestion, WebSearch, WebFetch
argument-hint: "<the thing that feels off, e.g., 'should the workflow ID include a timestamp?' or 'is this the right abstraction boundary?'>"
---

# Think Through

This skill helps you reason through a design decision that feels uncertain, off, or underexplored. It is not brainstorming (that's divergent). It is not requirements gathering (that's about what). It is structured convergent thinking about a specific choice and its consequences.

Use it when you have a gut feeling something is wrong but cannot articulate why, or when two valid options seem equivalent but you suspect they are not.

Argument: `$ARGUMENTS`

<HARD-GATE>
Do NOT jump to a solution. The entire point is to slow down and reason. Do not propose a fix until the analysis is complete. If the user asks for a fix mid-analysis, finish the current step first.
</HARD-GATE>

## When to use this skill

- "Something feels off about this design but I can't say what"
- "We have two options and I don't know which is better"
- "This works but I'm worried about edge cases I haven't thought of"
- "Is this the right abstraction / key / boundary / name?"

## Process

Work through these steps in order. Each step is its own message - do not combine them. Wait for the user's reaction before moving to the next step.

### Step 1: Frame the decision

State the decision clearly in one sentence. Then state the two (or more) options being considered. If the user gave a vague "something feels off," help them articulate what the actual decision point is.

Format:

> **Decision:** <one sentence>
>
> **Option A:** <description>
> **Option B:** <description>
> (more if needed)
>
> **Current leaning:** <which option and why, or "unsure">

Read relevant code, docs, and requirements to ground the framing in reality. Do not frame based on assumptions - verify what actually exists.

### Step 2: Three-property test (if the decision involves identity, keys, or dedup)

If the decision involves choosing what goes into an identifier, key, or dedup mechanism, run the three-property test:

| Property | Definition | Option A | Option B |
|----------|-----------|----------|----------|
| **Deterministic** | Same logical input always produces the same key | ? | ? |
| **Unique** | Different logical events produce different keys | ? | ? |
| **Stable** | Retries of the same event do not change the key | ? | ? |

Fill in pass/fail for each option and explain the implications. A key that fails any property has a specific class of bug:
- Fails deterministic: duplicate processing (same event, different keys)
- Fails unique: missed processing (different events, same key)
- Fails stable: duplicate processing on retry (same event, retry gets different key)

Skip this step if the decision is not about identity or keys.

### Step 3: Inversion

Flip the question. Instead of "which option is better?", ask:

> "What would make each option definitely wrong?"

For each option, list 2-3 concrete scenarios where it would break, fail, or cause pain. Ground these in the actual codebase and system - not hypothetical future requirements.

Format:

> **Option A breaks when:**
> 1. <concrete scenario grounded in the system>
> 2. <another scenario>
>
> **Option B breaks when:**
> 1. <concrete scenario>
> 2. <another scenario>

### Step 4: Second-order consequences ("and then what?")

For each option, trace the consequences two levels deep:

> **Option A:**
> - First order: <immediate consequence>
>   - Second order: <consequence of the consequence>
> - First order: <another immediate consequence>
>   - Second order: <what follows from that>

Focus on consequences that affect other parts of the system, future development, or operational behavior. Ignore cosmetic consequences.

### Step 5: Pre-mortem

Pick the option you are currently leaning toward (or the one the code currently implements). Assume it has been in production for six months and something went wrong because of this choice.

> "It is six months from now. This decision caused a production incident. What happened?"

Write 2-3 plausible failure stories. Be specific - name the component, the trigger, and the user-visible impact.

### Step 6: Synthesis

Summarize the analysis in a comparison table:

| Criterion | Option A | Option B |
|-----------|----------|----------|
| <criterion from the analysis> | <assessment> | <assessment> |
| ... | ... | ... |

Then state your recommendation with reasoning. If the analysis reveals that the current implementation is correct, say so and explain why the gut feeling was misleading (this is a valid and common outcome).

If the analysis reveals a real problem, describe the fix concisely but do NOT implement it. Ask the user if they want to proceed.

## Principles

- **Slow is fast.** The point is to think before acting. Five minutes of structured reasoning prevents days of rework.
- **Ground everything in code.** Read the actual files, check git history, look at how callers use the thing. Do not reason from assumptions.
- **Name the trade-off.** Every design decision trades something for something else. If you cannot name what you are giving up, you have not understood the decision.
- **Gut feelings are data.** When something "feels off," there is usually a real concern underneath. The skill's job is to surface it, not dismiss it.
- **"It depends" is not an answer.** State what it depends on, evaluate the actual context, and commit to a recommendation.
- **One message per step.** Do not rush through multiple steps. Each step deserves the user's attention and reaction.
- **Do not use em-dashes.** Use hyphens, commas, or parentheses instead.

## References

This skill draws on:
- **Pre-mortem analysis** (Kahneman, Klein) - prospective hindsight improves risk forecasting by ~30%
- **Inversion** (Munger, Farnam Street) - "tell me where I'm going to die, and I'll never go there"
- **Second-order thinking** (Farnam Street) - consequences of consequences
- **Three-property test for idempotency keys** (Stripe, Segment, Brandur Leach) - deterministic, unique, stable
- **Architecture Decision Records** (Nygard, Fowler) - structured decision capture
