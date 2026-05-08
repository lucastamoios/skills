---
name: concept-review
description: Review code abstractions for conceptual correctness, completeness, and simplicity. Analyzes whether modules, classes, and variables represent coherent concepts - using ontological analysis (essential vs accidental properties, categorical division, four causes) to find misnamed, misplaced, or confused abstractions. Interactive - presents understanding before proposing changes.
user_invocable: true
allowed-tools: Bash(git *), Read, Grep, Glob, Agent, AskUserQuestion
argument-hint: "<a module, class, file, or folder to review, e.g., 'agents/' or 'src/models/workflow.py' or 'the ToolKit class in core/tools.py'>"
---

# Concept Review

Review code abstractions for conceptual correctness. The goal is not clean code or performance - it is whether the abstractions themselves represent coherent, well-bounded concepts. A toolkit that also manufactures tools is conceptually broken, even if the code works perfectly.

This skill is interactive. You present your understanding of what things *are*, the user corrects or confirms, and only then do you propose changes.

Argument: `$ARGUMENTS`

## Step 1: Understand the whole, then the target

Even when `$ARGUMENTS` points to a single class or function, your analysis must be grounded in the system it belongs to. A name that looks wrong locally might be exactly right when you see the full picture - and vice versa.

1. Parse `$ARGUMENTS` to identify the target: a module, class, file, or folder.
2. **Start from the top.** Read the project's directory structure, entry points, and key module boundaries. Understand what the system *is* and what its major parts *do* before reading the target. If there are docs (README, architecture docs, CLAUDE.md in the project), read them.
3. **Map the layer the target lives in.** Read the target's parent package, its sibling modules, and the packages it depends on or that depend on it. Understand the conceptual neighborhood - what role does this layer play in the system?
4. Read the target code thoroughly.
5. Find usage sites: Grep for imports and references to the target across the codebase. Read the most important callers to understand what the target *means to its consumers*. Do not read tests.
6. If `$ARGUMENTS` points to a folder or module, build a mental map of the full structure before analyzing individual pieces.

## Step 2: Ontological analysis

Think through the target's conceptual structure. Use these lenses fluidly - they are thinking tools, not a checklist. Apply whichever ones reveal something interesting about this particular abstraction.

### Essential nature

Ask: what is this thing *at its core*? Strip away everything accidental and find the substance. If you cannot state what it is in one sentence without using "and," it might be more than one thing.

### Categorical division

Divide the target's contents into categories. For each category, ask:
- What defines membership in this category?
- What is the *opposite* of this category? Does anything in the code belong to that opposite?
- What lives in the *complement* - things that are neither this category nor its opposite? Is the complement empty, or does it contain unnamed concepts that should be articulated?

Stop subdividing when further division does not reveal anything useful. The goal is pragmatic clarity, not exhaustive taxonomy.

### Permanent vs ephemeral

For each property, method, or subcomponent, ask: what is its mode of existence?
- Is it permanent across the system's lifetime (configuration, identity)?
- Is it permanent within one execution but different across executions (request-scoped state)?
- Is it something that changes continuously (accumulated learnings, mutable state)?
- Is it something that exists only in potential until activated?

When something is treated as permanent but is actually ephemeral (or vice versa), that is a conceptual error worth flagging.

### Purpose and belonging

For each piece of the target, ask: does this serve the target's essential purpose, or is it here by accident (convenience, historical reasons, unclear ownership)? Things that do not serve the purpose may belong somewhere else - or may reveal that the target's stated purpose is not its real purpose.

### The whole and its neighbors

Step back and look at the target in the context of the full system - not just its siblings, but its role in the architecture. Ask:
- **Does the target's concept align with the system's concept?** A "Session" that means something different from what "session" means in the rest of the system is a problem, even if it is internally coherent.
- Does this target overlap with its siblings? Do two modules cover the same concept with different names?
- Is there a concept that spans multiple modules but has no name? Sometimes the complement (the "not A and not B" space) reveals a missing abstraction that would make the whole structure clearer.
- Could distinct things that share a genus live together under a broader name? (A runner and a kit might both belong in a single "tools" module if the distinction is not load-bearing at this level.)
- **Does the target's boundary match the system's natural joints?** Sometimes a class or module draws a line through the middle of a concept that the rest of the system treats as one thing, or lumps together things the system naturally keeps separate.

## Step 3: Present your understanding

Share your conceptual analysis with the user in developer-friendly language. Use precise philosophical terms only when the developer-friendly version would lose meaning - and when you do, briefly explain them.

Structure your presentation as:

1. **The system context** - a brief statement of what the broader system is doing and how the target fits into it. This grounds everything that follows. Keep it to 2-3 sentences.
2. **What this thing is** - your one-sentence definition of its essential nature.
3. **The categories you found** - what groups of things live here, and what defines each group.
4. **What surprised you** - things that do not belong, unnamed concepts in the complement, properties with the wrong mode of existence, overlaps with neighbors. Always explain surprises in terms of the whole system, not just the local code. ("This is surprising because the rest of the system treats X as..." rather than "This method seems out of place.")

Do NOT propose changes yet. Ask the user: "Does this match your understanding, or am I reading something wrong?"

Wait for the user's response.

## Step 4: Propose changes

After the user confirms or corrects your understanding, propose concrete code changes. Each proposal should include:

- **What to change** - rename, move, split, merge, or restructure.
- **Why** - what conceptual problem it fixes, in plain language.
- **The new concept** - what the thing *becomes* after the change, stated clearly.

Group related changes together. If a change is small (a rename), say so. If it is large (splitting a module), outline the new structure.

Present all proposals at once and ask the user which ones to proceed with.

## Step 5: Implement (if the user approves)

If the user approves changes, implement them. After each logical group of changes, pause and ask the user to review before continuing.

If the user wants to stop at the analysis, that is fine. The conceptual understanding is valuable on its own.

## Principles

- **Whole first, always.** Even when the target is a single function, understand the system it lives in before forming opinions. A local abstraction can only be judged against the concepts the rest of the system uses. If you skip the whole, you will propose changes that make the part locally coherent but systemically wrong.
- **Interactive first.** Present understanding before proposing changes. The user's conceptual model matters more than yours - your job is to articulate it, challenge it, and help refine it.
- **Pragmatic correctness.** Aim for conceptual correctness that is good enough, not perfect. Things that naturally belong together can share a space even if they are categorically distinct, as long as the shared space has a coherent name.
- **Fluid thinking.** Use ontological lenses (essential nature, categorical division, four causes, permanent vs ephemeral) as thinking tools. Apply them when they reveal something. Skip them when they do not.
- **Developer-friendly language.** Say "this class is doing two unrelated jobs" rather than "the substance lacks unity." But when the precise term captures something the plain version misses, use it and explain it.
- **Usage over intention.** What consumers actually do with an abstraction reveals its real nature. Read usage sites, not just the target code.
- **Name what is unnamed.** The most valuable finding is often a concept that exists implicitly in the code but has no name. Naming it makes the whole structure clearer.
- **Stop when it is not useful.** Not every complement is interesting. Not every category needs subdividing. Pragmatism over completeness.
- **Do not use em-dashes.** Use hyphens, commas, or parentheses instead.
