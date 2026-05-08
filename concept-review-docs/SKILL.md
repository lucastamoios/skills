---
name: concept-review-docs
description: Review requirements and design specs for conceptual correctness. Analyzes whether the domain concepts, entities, categories, and boundaries expressed in docs are coherent, complete, and consistent with each other and with the codebase. Interactive - presents understanding before proposing changes.
user_invocable: true
allowed-tools: Bash(git *), Read, Grep, Glob, Agent, AskUserQuestion
argument-hint: "<a requirements or design file, e.g., 'authorization' or 'docs/requirements/registration.md' or 'docs/design/dispatch.md'>"
---

# Concept Review (Docs)

Review requirements and design specs for conceptual correctness. The goal is not completeness of coverage or testability of requirements (those are the requirements and design-spec skills' jobs). The goal is whether the domain concepts expressed in these documents are coherent, well-bounded, and consistent - both internally and with the codebase they describe.

A requirements file that talks about "registrations" and "authorizations" as separate things when the codebase treats them as one concept is conceptually broken, even if every requirement is testable. A design spec that introduces a "dispatch service" when the domain actually has "routing" and "scheduling" as distinct concerns is masking a real distinction behind a convenient name.

This skill is interactive. You present your understanding of the conceptual model in the docs, the user corrects or confirms, and only then do you propose changes.

Argument: `$ARGUMENTS`

## Step 1: Read the docs and their world

1. Parse `$ARGUMENTS` to identify the target. It can be:
   - A topic name (e.g., "authorization") - look for both `docs/requirements/<topic>.md` and `docs/design/<topic>.md`.
   - A specific file path - read that file and also look for its counterpart (if you got the requirements, look for the design spec, and vice versa).
2. Read all target docs thoroughly.
3. Read `docs/index.md` to understand what other docs exist and how this topic relates to the broader documentation landscape.
4. Read related docs - if other requirements or design files reference the same entities, read them to understand how the concepts connect across boundaries.
5. Explore the codebase: Grep for the key domain terms used in the docs (entity names, module names, workflow names). Read the most relevant code to understand what these concepts *actually are* in practice, as opposed to what the docs say they are.

## Step 2: Ontological analysis of the domain model

Analyze the conceptual model expressed in the docs. Use these lenses fluidly - apply whichever ones reveal something interesting about this particular domain area.

### Vocabulary and identity

Map every distinct concept the docs name: entities, roles, states, actions, categories. For each one, ask:
- Is this concept used consistently throughout the docs? Does "registration" always mean the same thing, or does it silently shift meaning between requirements?
- Does the codebase use the same term for the same concept? If the docs say "authorization" but the code says "permit," that is a conceptual gap that will cause confusion.
- Are there synonyms - two different terms that refer to the same thing? If so, which one is the real concept and which is noise?

### Essential nature of each concept

For each key entity or concept, ask: what is this thing at its core? A requirement that says "the system shall manage registrations" is only meaningful if "registration" is a well-defined concept. Does the document make clear:
- What distinguishes this concept from related ones?
- What properties are essential to it (without which it would not be this thing)?
- What properties are accidental (they happen to be there but could change without changing what it is)?

### Categorical structure

Look at how the docs organize concepts into groups. Ask:
- Are the categories exhaustive? If the docs define three types of something, is there a fourth type hiding in the complement that nobody named?
- Are the categories mutually exclusive? Or do some concepts straddle two categories in a way that reveals the categories are wrong?
- Would a different way of carving up the domain be more natural? Sometimes the docs inherit a categorization from the existing code that was pragmatic but not conceptually right.

### Boundaries between concepts

Look at where the docs draw lines between entities, modules, or feature areas. Ask:
- Does this boundary reflect a real distinction in the domain, or is it an artifact of how the code happens to be organized?
- Are there concepts that the docs treat as separate but that are really aspects of the same thing?
- Are there concepts that the docs treat as one thing but that are really distinct? (A requirement that says "manage products" when the domain actually has "product definitions" and "product registrations" as fundamentally different activities.)

### Consistency between requirements and design

If both exist for this topic, check whether the conceptual model is the same in both:
- Does the design spec introduce new concepts that the requirements never mentioned? If so, are they implementation artifacts (acceptable) or domain concepts that should have been in the requirements (a gap)?
- Does the design spec rename or restructure concepts from the requirements? If so, which version is right?
- Do the requirements assume a domain structure that the design spec contradicts?

### Consistency with the codebase

Check whether the conceptual model in the docs matches what the code actually implements:
- Are there entities in the code that the docs do not mention? Those might be unnamed concepts that need to be articulated.
- Are there concepts in the docs that do not exist in the code? Those might be aspirational (fine) or fictional (a problem).
- Does the code's module structure reflect the same boundaries the docs describe? If not, which one is wrong?

## Step 3: Present your understanding

Share your analysis with the user in plain language. Structure it as:

1. **The conceptual model as I read it** - your summary of what the docs are saying about the domain. What are the key entities, how do they relate, what categories exist.
2. **Where the model is clear and coherent** - what works well conceptually. (Do not skip this - it grounds the conversation and confirms you understood the intent.)
3. **Where I see conceptual problems** - inconsistencies, unnamed concepts, blurred boundaries, vocabulary drift, gaps between docs and code. Be specific: cite requirement numbers, decision IDs, or code locations.

Do NOT propose changes yet. Ask the user: "Does this match your understanding of the domain, or am I misreading something?"

Wait for the user's response.

## Step 4: Propose changes

After the user confirms or corrects your understanding, propose concrete changes to the docs. Each proposal should include:

- **What to change** - rewrite a requirement, rename a concept, split a section, add a missing entity, reconcile vocabulary.
- **Why** - what conceptual problem it fixes.
- **The new concept** - what the docs will say after the change, stated clearly enough that the user can evaluate it.

If the problem is in the codebase rather than the docs (e.g., the docs are right but the code uses wrong names), note that and suggest the user run `/concept-review` on the relevant code afterward.

Present all proposals at once and ask the user which ones to proceed with.

## Step 5: Apply changes (if the user approves)

If the user approves changes, edit the docs. After each logical group of changes, pause and ask the user to review before continuing.

Preserve the existing format and conventions of the files (requirement numbering, decision IDs, traceability references). Use the deprecation format from the requirements and design-spec skills when replacing items rather than deleting them.

## Principles

- **Interactive first.** Present understanding before proposing changes. The user knows the domain better than you do.
- **Domain over code.** The docs describe what *should be*, the code describes what *is*. When they conflict, do not automatically assume the code is right. Ask the user.
- **Vocabulary matters.** Inconsistent naming is not a style issue - it is a conceptual issue. If two terms exist for one concept, the domain model is ambiguous.
- **Name what is unnamed.** The most valuable finding is often a domain concept that everyone talks around but nobody has articulated. Naming it makes the requirements and design clearer.
- **Pragmatic categories.** Stop subdividing when it is not useful. The goal is clarity, not taxonomy.
- **Cross-doc consistency.** Requirements and design specs must use the same conceptual model. If they diverge, one of them is wrong.
- **Cite evidence.** When you flag a problem, point to the specific requirement number, decision ID, code file, or term that shows it. Do not raise vague concerns.
- **Do not use em-dashes.** Use hyphens, commas, or parentheses instead.
