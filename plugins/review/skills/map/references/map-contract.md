# Map input and data contract

## Prepared input additions

Use the review/v1 input template, mode prepare. Add:

- Invocation role: worker (prevents recursive delegation).
- Audience and architecture question.
- Exact comparison: before commit, after commit plus included staged/unstaged/untracked source. Declare exclusions.
- Relevant product sources and accepted decisions with provenance. Do not pass the full parent transcript by default.
- Current HTML/data when refining a prior map, or none.
- Absolute map.json and standalone HTML output paths, in addition to the exclusive worker report. Default output mode is standalone; only request `--fragment` for an explicitly requested legacy inline map.
- Prompt audit: run-specific facts versus reusable guidance promoted to the skill or awaiting a decision.
- Model policy key and digest, including explicit review:walkthrough alias when used.

A map-only run has no dependency on paths, correctness findings, QA, verification or consolidation. Compatible existing path evidence can help orient the worker, but direct source inspection establishes this map.

## Data shape

The renderer accepts JSON containing these keys:

- `title`: concise architecture title.
- `source`: `{base, head, snapshot, scope}` with exact comparison identifiers and readable scope.
- `domains`: list of `{id, label, row, column, module_ids}`. Positions are nonnegative integers; module_ids lists only changed modules. An essential existing context domain may have an empty list and should say Existing in its label.
- `edges`: list of `{from, to, label}`. References are domain IDs. Labels distinguish calls, reads, writes, proposals or dependencies.
- `modules`: list of `{id, path, change_kind, functions}`. Use current repository-relative path and one of added, deleted, modified, renamed, moved. Include `previous_path` when relevant.
- `functions`: list inside each module of `{id, name, change_kind, business_rule, before, after, parts}`. Optional `kind` identifies function, method, model or block.
- `before`, `after`: each is `{path, start_line, source}`. Source is exact complete code, preserving line endings and the original terminal newline; do not strip the extracted text. start_line is its original one-based line. Use null or an object with an empty source for an absent side; never substitute a summary for code.
- `parts`: list of `{id, title, explanation, old_start, old_end, new_start, new_end}`. Ranges are one-based inclusive positions relative to the complete function source, not file line numbers. Use null for absent-side ranges. Every changed section needs an explanation. Unchanged moved functions can have a location-only explanation without pretending code changed.

Keep symbols unique by module plus function ID. Describe the same changed module consistently when it appears under multiple domains. Business rules belong to function entries; changed-section explanations belong to parts.

The renderer generates diff rows from complete before/after source. Do not manually fabricate diff output. Its validation checks references and ranges; the worker must still verify source provenance, semantic grouping, extraction completeness and the truth of explanations.

## Standalone presentation contract

`render_map.py` writes a complete self-contained HTML document by default, with high-contrast light styling and the existing domain/module/function drill-down. Source remains escaped text. The short source summary is followed by native details containing exact full provenance. `--fragment` is an explicit legacy option.

The worker does not start a long-running server. After inspecting the completed artifact, the coordinator runs `python3 <skill-directory>/scripts/serve_map.py <absolute architecture-map.html>` in its own foreground process/session, records the actual emitted `http://127.0.0.1:<port>/architecture-map.html` URL and ownership, verifies HTTP content, and opens that URL in Codex. Port 0 is the default; `--port` can request another port. The helper binds only loopback and exposes only that document, with no directory listing or arbitrary file serving. Keep the session alive during presentation and stop it explicitly when replaced or no longer needed. Do not use an inline artifact reference by default.
