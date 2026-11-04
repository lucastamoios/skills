---
name: explain
description: Explain a pull request, branch, commit range, or current diff as an interactive top-down walkthrough, a short overview and part map first, then one part at a time, pausing for questions between parts. Use when the user invokes /explain, asks what a PR or branch does, or wants unfamiliar framework or syntax translated into familiar concepts. Accepts a PR number or URL, branch name, commit range, or "current".
---

# Explain

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Explain how a code change works, top-down and in conversation. Investigate fully up front, then deliver the explanation in short parts, yielding to the reader between parts so they steer the depth and the pace.

Argument: `$ARGUMENTS`

<HARD-GATE>
This is an explanation, not a review. Do not search for defects, recommend changes, or judge code quality unless the user explicitly asks. Do not explain from the PR description alone. Never deliver the whole walkthrough in one message unless the user explicitly asks for everything at once.
</HARD-GATE>

## 1. Resolve the target

Identify the exact change before explaining it.

- **PR number or URL:** inspect PR metadata, base, head, changed files, commits, and diff. Prefer `gh pr view` and `gh pr diff`. Use the repository named in the URL when present.
- **Branch:** resolve the local or remote ref. Diff from its merge base with the repository's default branch, normally `origin/main`.
- **Commit range:** use the supplied range directly.
- **`current` or empty:** inspect the current branch against its merge base with the default branch, plus relevant working-tree changes.

Prefer reading refs without changing the user's checkout. Verify remote state when it is cheap and relevant. State clearly if the target cannot be resolved or if the explanation is based on stale local refs.

## 2. Reconstruct the behavior before saying anything

The part map in your first message must come from real understanding, not from the diff's file list, so the investigation happens in full before any explanation starts.

1. List the changed files and group them by behavior, not directory.
2. Read the surrounding functions, templates, models, and tests.
3. Trace callers, imports, shared constants, generated markup, request handlers, and output consumers.
4. Identify:
   - the user or system trigger;
   - where state is stored;
   - every boundary crossing, such as browser to server, service to database, or workflow to activity;
   - the transformation performed at each stage;
   - the final user-visible or system-visible result.
5. Choose one small concrete example that can be carried through every part of the walkthrough.

## 3. Calibrate to the reader

Honor any experience level the user gives.

When the reader is the configured user, read `profile.user.technical_knowledge` if present. Calibrate each part to the relevant experience in that private note. Without a note, use the experience given in the current request; ask only when it changes the explanation materially.

If the reader is someone else and no level is given, assume they understand ordinary programming, functions, HTML, basic SQL, and common JavaScript, but may not know the specific framework or codebase.

Translate framework behavior into familiar equivalents:

- HTMX attributes into `fetch()` plus DOM replacement.
- ORM expressions into plain filtering or SQL-like terms.
- Signals, decorators, middleware, dependency injection, and framework reflection into explicit calls.
- Workflow engines into events, persisted state, retries, and transitions.
- Uncommon syntax such as `:=`, comprehensions, descriptors, or metaclasses into expanded equivalent code.

Explain only the concepts needed for this change.

## 4. First message: overview and part map, then stop

The first message contains exactly three things and nothing more:

1. **The outcome**, in two or three sentences: what behavior changed and why the supporting code exists.
2. **The part map**: a short numbered list of the parts you will walk through, in execution order, one line each. The main behavioral flow comes first, split into parts a reader can absorb in one sitting; supporting work (shared constants, migrations, configuration, compatibility, tests) is bundled into a single final part. A large change with several independent flows gets one part per flow.
3. **The handoff**: ask whether to start with part 1, jump somewhere else, or answer questions first.

Add a conceptual Mermaid flowchart to the overview only when the change crosses at least three components or the user asks for a visual. Keep it at the level of `user action -> request -> backend query -> visible result`.

Do not begin explaining part 1 in this message. The reader decides where to go.

## 5. One part per message

Each subsequent message explains exactly one part from the map, as a few numbered steps in execution order. A part should stay short, roughly three to five steps; if it needs more, split it and update the map. Each step contains:

1. **What happens**, as a short action title.
2. **Where it happens**, with an exact clickable file and line reference.
3. **The relevant code**, trimmed to the smallest useful excerpt.
4. **What the code means** in plain language.
5. **The running example or state change** at that moment.

Where the new behavior diverges from the old, mark the divergence inline at that exact step:

```text
Before: the request contained only the active widget.
After: the request also contains selected sibling filters.
```

Do not duplicate the walkthrough for the old implementation.

Close every part by yielding: name what the next part covers and invite questions, for example "Questions on this, or shall I continue with part 3, the backend query?".

## 6. Between parts: the reader steers

- Answer questions from inspected code, reading more of the codebase when the question needs it, then restate where the walkthrough stands and offer the next part.
- When the reader asks to go deeper on a step, expand that step: more surrounding code, the framework mechanics behind it, or the expanded equivalent of dense syntax.
- When the reader is having a hard time with a concept (repeated questions about the same mechanism, a stated confusion, a wrong mental model in their words), prefer an interactive explanation over more prose. Build a small widget the reader can manipulate (toggles, steppers, sliders, live state) that embodies the confused mechanism, using the inline visualization tool when available, otherwise a small self-contained HTML file they can open. Let the interaction demonstrate the rule, then restate the rule in one or two sentences grounded in what they just saw.
- When the reader says to skip ahead or stop, follow them; the map exists so they can navigate.
- When the reader asks for everything at once, deliver the remaining parts in a single message using the same part and step structure.

## Output rules

- Ground every claim in inspected code, and say when something is inferred or cannot be verified.
- Use exact local file links and line numbers when files are available.
- Prefer execution order over diff order.
- Explain names in domain language before using acronyms.
- Keep code excerpts small and each message short; the part map absorbs scale, not the individual message.
- Carry the same concrete example through every part so the reader never rebuilds context.
- Do not merely paraphrase changed lines.
- Do not turn the answer into a code review unless requested.
- Every message ends with the reader in control: a question, a next-part offer, or both.
