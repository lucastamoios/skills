---
name: business-rules
description: Extract the business rules behind an issue, pull request or code change, using concrete examples from the target project before explaining the general rule.
allowed-tools: Bash(gh *), Bash(git *), Read, Grep, Glob, Agent, WebFetch, mcp__linear-server__get_issue, mcp__linear-server__list_issues, mcp__linear-server__list_comments
argument-hint: "[issue-url, PR-number, or file-path (optional, defaults to current diff or last commit)]"
---

# Business Rules Extraction

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Help the user understand the business rules behind their current project, using its configured domain context.

**This reader learns from examples.** Never open with a tour of regulatory frameworks or an abstract rule statement. Open with a concrete case, show that case inside our app, then generalize. The framework names and the legal citations arrive later, when the example has already created a reason to care about them. The output contract below is not a suggestion: follow the order.

**He also reads by interrupting.** This is a conversation, not a document you hand over. Deliver the answer in short beats and stop between them so he can ask, redirect, or say enough. See step 5.

## Input

The user provides one of:
- A **Linear issue** identifier matching the pattern `<PREFIX>-<number>` (e.g., `<PREFIX>-<number>`)
- A **GitHub PR** number or URL
- A **file path** or description of code they changed
- A **plain question** about a domain concept ("what is a brand here", "how do renewals work")
- **Nothing**, see default behavior below

Argument: `$ARGUMENTS`

### Default Behavior (no argument provided)

1. Run `git diff` to check for uncommitted changes.
2. If there is a diff, use that as the context.
3. If there is no diff, use the last commit (`git log -1 --format="%H" && git diff HEAD~1..HEAD`) as the context.

## Terminology

Read the project's declared vocabulary and relevant private context. Keep its domain terms precise and distinguish them from standard industry language. Do not apply another organization's model to the current project.

## Step 1: Resolve the target

- **Linear issue** (matches `<PREFIX>-<number>`): use the Linear MCP tools to fetch the issue, its description, its comments, and any linked issues.
- **GitHub PR**: run `gh pr view $ARGUMENTS` and `gh pr diff $ARGUMENTS`.
- **File path or description**: read the referenced files or search the codebase.
- **Plain question**: identify the models and product areas the question is about, then treat those as the target.
- **No argument**: use the diff or last commit as described above.

## Step 2: Read domain documentation

Read the relevant sources in `profile.work.direction_notes` and `profile.work.knowledge_root`. Use the configured vault index to find additional domain notes. Load only notes relevant to the question and verify claims against their original source. Do not assume a particular product model, regulatory domain or team structure.

## Step 3: Trace the rules in code

Use the current repository or `profile.work.checkout` when the request names the configured work project. Search for:

- Models, views, serializers, managers, and services for the entities in scope.
- Validation logic, permission checks, status transitions, conditional branching.
- Comments and docstrings that explain rationale rather than mechanics. Inline comments next to a field often carry the only written statement of a business rule.
- Tests, which encode expected business behavior more reliably than any doc.
- `on_delete` behavior, uniqueness constraints, and nullability, which are business rules expressed as schema.

Prefer LSP tools over Grep when following code relationships.

## Step 4: Hunt for concrete instances

This step is what makes the output work, so do not skip it. Before writing anything, collect real, citable instances:

- **Tests and factories** (`*/tests/factories.py`, `*/tests/test_*.py`): fixtures name concrete values and encode the exact edge cases the team decided mattered.
- **Seed and scaffold data** (the repository's documented fixtures, seed commands and data migrations): real product names, real agency names, real scale values.
- **Vault meeting notes**: real client and consumer names, real incidents with dates and the person who reported them, real operational constraints.
- **The regulation itself**: if you cite a rule, cite the section (for example 40 CFR 156.10(b)), and use WebFetch to confirm rather than reciting from memory.

An example counts as real only if you can say where it came from. If no real instance exists and you need one to teach the shape, invent it and label it `(illustrative, not from our data)`. Never present an invented client, product, incident, or regulation as real. A fabricated "real case" is worse than no example, because it will be repeated in a meeting.

## Step 5: Deliver it in beats, never as one report

Do all of the research in steps 1 to 4 **before** you write a single word to the user. The pauses
below are for the reader's benefit, not yours: by the time you open your mouth you should already be
able to answer whatever he interrupts with, without going back to look.

Then deliver in four beats. **Stop after each one and hand the floor back.** The reader forms
questions while he reads, and a nine-section wall of text buries them. He would rather ask at beat 1
than discover at beat 4 that beats 2 and 3 answered the wrong question.

Rules for every beat:

- Keep it readable in under a minute. Aim for 150 to 350 words. One small table at most.
- Do not announce the whole structure up front. Naming nine sections makes it a document again.
- End with a real question about the thing you just explained, not a procedural "shall I continue".
  Then, in one line, say what the next beat covers, so he can redirect it or skip it.
- If he interrupts with a question, answer it from the research you already did, then re-offer the
  next beat. Do not restart, and do not re-explain what he just read.
- If he asks for the whole thing at once ("just dump it", "give me all of it"), abandon the beats and
  write the full report in section order.
- If a beat turns out to be one line ("no state-level dimension applies here"), say the one line and
  roll straight into the next beat instead of pausing on nothing.

**Beat 1, the idea and the example.** Sections 1, 2 and 3 below. This is the whole point of the
skill: he should finish beat 1 knowing what the rule is and having a concrete case in his head, with
no code yet. Most conversations should be steerable from here.

**Beat 2, the mechanism.** Sections 4 and 5. The trace down, then the generalized rule and its
exceptions. If the exceptions are numerous, give the ones that change his decisions and offer the
rest.

**Beat 3, the reasons and the limits.** Sections 6 and 7.

**Beat 4, the failures and the gaps.** Sections 8 and 9.

Once the beats are done, offer to write the assembled report to
`profile.paths.artifacts/<slug>/business-rules.md` so he keeps it. Do not write the file unprompted.

### 1. The answer in two sentences

Plain language, no model names, no acronyms, no framework names. What is this thing, or what is the rule. Give the reader somewhere to stand before any detail arrives.

### 2. Start with a case in the world

A concrete scenario outside the software. Named actors, a real artifact, a sequence of events: a registrant submits a label to a state, a distributor sells the same product under its own name, a data provider sends a specimen label and its state registrations. No code, no model names, no field names in this section. If the case is real, cite the source (a vault note with its date and reporter, a test, a regulation). If it is illustrative, say so.

### 3. The same case inside our app

Where the case shows up for a user. The screen, the URL or click path, which records exist and what is in their fields. Still no internals: this is the view over the shoulder of someone using the product. If there is a settings page, an API endpoint, or a form involved, name it.

### 4. Trace one instance all the way down

Now go to code, and carry the single instance from section 2 through every layer: user action, validation, stored state, output. Cite `file:line` at each step and keep excerpts small. One example carried all the way through beats five examples that each stop at the surface. Do not switch examples mid-trace.

### 5. The rule, generalized

Only now state the rule the example demonstrated. Immediately follow it with its exceptions and edge cases, and give each exception the concrete case that makes it visible. A rule with no attached case is a rule the reader will not retain.

### 6. Why the rule exists

Separate, explicitly and under its own labels:

- **Hard regulatory requirement**: a legal mandate, with the citation and the agency. What happens legally if it is violated.
- **the configured organization product decision**: how the software chose to model the domain. Who decided, if the vault records it, and what the alternative would have been.

Say plainly when a concept that sounds regulatory carries no regulatory weight in our code. That correction is often the most valuable part of the report.

### 7. The constraints your code must respect

A short list, each item phrased as a consequence rather than a category: multi-tenancy (org scoping), publication state, cumulative-freshness propagation to API consumers, permissions and `viewable_by`, configurable per-org settings, and state-by-state differences (registration requirements, renewal timelines, reporting obligations, fee structures, California specifics) when they apply. If a dimension does not apply, say so in one line rather than padding the section.

### 8. What breaks, as incidents

Prefer a real past incident from the vault, with its date and who reported it. Failing that, walk through a concrete failure: this input, this state, this wrong output, this consequence for a client or for a filing. Do not write "compliance failure" or "data integrity issue" as a bare category.

### 9. What you could not verify

What you looked for and did not find, what you are inferring rather than confirming, and who to ask (from `project/team.md`).

## Guidelines

- Cite file paths with line numbers, model fields, and regulation sections. Every claim traces to something inspected.
- Concrete values over placeholders. A named state, an actual product name from seed data, a real registration-number shape.
- Depth is earned in order: case, then app, then code, then rule, then law. Never invert it.
- Weight sections by what the reader needs, not by symmetry. A one-line "no state-level dimension here" is correct when true.
- Keep the distinction between what the law requires and what the configured organization chose visible throughout, not just in section 6.
- Do not review the code or propose changes unless asked. This skill explains the constraints the code must respect.
- No em-dashes and no dash used as a connector in the output. Use commas, colons, or parentheses.
- Brevity per beat is a hard requirement, not a style preference. If a beat will not fit, cut the
  supporting detail and offer it, rather than shipping the long version and hoping he reads it.
- If your research contradicts something you told him earlier in the session, lead the relevant beat
  with the correction. Do not bury it in a later section.
