---
name: map
description: Build an interactive architecture map for a PR, branch or local diff. Drill from a domain into changed modules, then functions with business rules and complete annotated diffs. Always prepare the map in a fresh subagent.
---

# Review Map

Help the user understand the architecture of a change before reviewing its implementation. Show responsibilities and real relationships first. Clicking a domain shows its changed modules; clicking a module shows its changed functions or code blocks; clicking a function shows its business rule and complete annotated diff.

This entrypoint has coordinator and worker roles. An ordinary invocation uses the coordinator steps below. An agent receiving `input=<absolute input.md> output=<absolute output.md>` runs the worker steps only, without spawning another map worker. This is an explanatory map, not a correctness verdict or a full review pipeline.

## Coordinator: prepare and delegate every run

1. Resolve the requested checkout, exact base/head and included local changes. Reuse established task decisions. For a PR use its resolved comparison; for an established task use its agreed base. Otherwise default to the merge base with the repository's verified default branch, including local changes, and state that scope. Ask only if different plausible targets materially change the map. Preserve staging and source files.
2. Read applicable repository instructions. Use the plugin's [source snapshot script](../../scripts/snapshot.py) to capture/check the source identity, including staged, unstaged and relevant untracked files. Give the worker an isolated read-only source copy if concurrent edits are likely. Store the unique run outside the reviewed checkout.
3. Prepare an explicit input using [the input template](../../protocol/input-template.md), mode `prepare`, and the [map input additions](references/map-contract.md). Pass sources rather than assuming the worker inherits the chat: repository, base/head, local scope, product requirements and accepted decisions, selected audience, relevant existing context, current visualization when refining it, and exclusive writable output paths. External source retrieval stays within the declared access boundary.
4. Audit the prompt before dispatch. Keep run-specific facts in the input. Put reusable behavior already authorized by the user in this skill or its references instead of repeatedly adding it to worker prompts. Treat speculative/generalized preferences as candidates, not automatic skill edits. Record what moved into the skill and why, or `none`. Never turn task facts into universal business rules.
5. Always launch a fresh native subagent with `fork_turns="none"`. Select the approved `review:map` assignment when present in the supplied/shared policy. Until it has a dedicated assignment, explicitly use the approved `review:walkthrough` assignment as its teaching-role alias, and record the alias and policy digest. Use the same supported-backend rules as [review:run](../run/SKILL.md). Do not silently invent a model or run in the parent instead. The spawn message contains only the skill path, input/output paths and access boundaries.
6. Wait for the worker and inspect its report and generated artifact. Check the source identity again and verify the domain/module/function drill-down and diff fidelity. Do not run unrelated review lenses or tests simply to draw the map. After the child has returned, start the bundled localhost server from a coordinator-owned foreground terminal/tool session: `python3 <skill-directory>/scripts/serve_map.py <absolute architecture-map.html>`. The default port is ephemeral and the helper prints the actual URL with flushing. Record that URL and the owning process/session ID in the run report so it can be stopped explicitly. Keep the session running through presentation; do not rely on a blocking child process surviving worker completion. Check that an HTTP GET returns the generated HTML, then open the actual URL in the Codex browser panel. Present the localhost link and artifact paths. Stop a replaced server or one no longer needed using its recorded owner. Do not emit an inline visualization reference by default. State material omissions or stale sources. Do not claim approval of the code.

The child owns architecture investigation, business explanations, function extraction, diff annotation and rendering. The parent owns context preparation, prompt audit, dispatch, inspection and presentation.

## Worker: establish the architecture from current source

Read the full input, [the plugin contract](../../protocol/contract.md), [the map contract](references/map-contract.md), and the bundled renderer/template. Use a self-contained standalone HTML document with readable high-contrast text and accessible controls, served by the coordinator at localhost. Use the bundled renderer rather than writing a new interface for each run. Inline output is an explicitly requested legacy option (`--fragment`); only for that option read and follow the available `visualize` skill and its output contract.

Inspect actual call sites, definitions and both sides of the comparison. Follow source-discovery instructions such as Graft or LSP when applicable. Distinguish call order, dependencies, reads, writes and generated data. Trace the change far enough to identify its inputs, business decisions, temporary state and persistence boundaries.

Group by meaningful domain responsibilities. Collapse folder chains into one path. Map the current implementation, including awkward boundaries, rather than presenting a proposed refactor as existing code. A module may serve multiple domains; list it in each relevant domain without inventing a single responsibility. Label essential unchanged supporting components as existing context, not changed modules. Exclude tests from the map by default. Explain migration effects through models; include deployment/configuration only when it changes meaningful runtime behavior.

Only changed modules appear in the domain's changed-module list. Only changed functions, methods, model declarations or meaningful code blocks appear under those modules. For template/configuration/module-level changes, name the real block and label its kind rather than inventing a function. Mark added, deleted, modified, renamed and moved entries accurately. A pure move must show identical code as context, with its location change explained.

## Function business rules and annotated diffs

Each displayed entry has a brief explanation: prefer the user-facing rule, decision or state change. Otherwise state its technical job plainly. Distinguish regulatory obligations, explicit product decisions and observed implementation. Do not infer law from software behavior. Attribute business rationale to supplied sources; mark uncertainty.

Extract the complete function on both sides, including its decorators, signature, body and relevant docstring. Match old/new identities across moves and renames. Keep exact source text and original path/line provenance. If a function is unchanged but its file moved, show that explicitly. If exact extraction is unavailable, report the missing side rather than fabricating code.

Show an accurate diff of the whole function, retaining unchanged context. Added/deleted functions have an empty opposite side. Separate changes into meaningful parts and explain what changed, the business effect and the reason when supported. Technical changes receive a technical explanation. Explain each changed section; related adjacent edits can share a part. Do not invent explanations for unchanged lines. Use part ranges to connect the explanation directly to affected old/new lines. Include a brief limitation when intent is unknown.

## Render and verify

Write `map.json` following [the data contract](references/map-contract.md), then run:

```sh
python3 <skill-directory>/scripts/render_map.py <absolute map.json> <absolute architecture-map.html>
```

The renderer defaults to a standalone document with all required CSS and JavaScript embedded; no external asset requests are needed. Keep the top source line concise and preserve the exact full provenance in the native expandable details. The worker renders and reports the artifact, while the coordinator starts and owns its server after worker completion.

Use the thread's explicitly writable visualization directory when available, or an authorized durable run directory. Do not mutate the reviewed source. Keep source code as escaped text, not executable markup. Preserve full functions; no ellipses or silent truncation. Keep long diffs readable, with old/new line numbers and added/deleted/context styling. Use one focused detail panel, not a folder tree or all function bodies at once.

Verify domain selection, module selection, function selection, notes and annotations. Check complete source on both sides and line ranges, not just generated labels. Use meaningful fixture checks for additions, deletions, moves and hostile HTML-looking source. Browser failure limits visual verification and never authorizes bypassing browser permissions.

## Worker report

Use the plugin output header with coverage separate from verdict; verdict is `not-assessed`. Include:

- Source identity, scope and changed-production coverage.
- Absolute standalone HTML/data paths and their digests; state the output mode. Server URL and process/session ownership are added by the coordinator after starting the helper.
- Domain responsibilities and meaningful architectural boundaries.
- Changed modules/functions included and material omissions.
- Business-rule sources, inferences and uncertainties.
- Diff fidelity and interaction checks actually performed.
- Prompt-to-skill candidates discovered during this run, with rationale, or `none`.

Do not publish, commit, modify source, update the skill or send messages to other chats from the worker. Return its report and artifact paths to the coordinator.
