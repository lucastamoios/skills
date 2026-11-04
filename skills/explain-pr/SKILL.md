---
name: explain-pr
description: Write or update a structured pull request explanation for a configured local reader service, following its contract and current PR head. Use explain for a conversational walkthrough in chat.
---

# Explain PR for Lighthouse

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. For shell examples, set `SKILL_CONFIG` to the installed `skill-config/scripts/config.py` absolute path. The examples query the private profile at runtime; verify required fields before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Produce one `lighthouse.pr-explanation/1` JSON document for a the configured organization pull request and deliver it to a running Lighthouse server, either by posting it (a manual run) or through a handoff file that Lighthouse reads (a run that Lighthouse started). The document is read in Lighthouse's source reader: the overview first, then a tree that the reader expands one level at a time, with anchors that open the code.

Arguments: `$ARGUMENTS`

```
/explain-pr <number-or-PR-URL> [--url <lighthouse-base-url>] [--token-file <path>]
```

- `--url` defaults to `$LIGHTHOUSE_URL`, then to `profile.integrations.lighthouse.url`.
- `--token-file` defaults to `${ENGINEERING_ATTENTION_HOME:-$HOME/.engineering-attention}/ingest-token`. It is used only in post mode.

The delivery mode comes from the environment:

- **File mode**, when `LIGHTHOUSE_EXPLANATION_FILE` is set and not empty. Lighthouse started the run and reads the document from that path when the run ends. The skill validates the document without a token and writes the file. It never reads the ingest token and never calls `POST /api/explanations`, also when `--token-file` is given.
- **Post mode** otherwise (a manual run). The skill posts the document with the ingest token.

In file mode, the document is written in one of two ways:

- **Update mode**, when `LIGHTHOUSE_BASE_EXPLANATION_FILE` and `LIGHTHOUSE_UPDATE_DIFF_FILE` both name readable files. Lighthouse gives the old explanation and the diff from its head to the current head, and the skill revises the old explanation for the new head. "Update mode" below says what changes in each phase.
- **Scratch mode** otherwise. The skill writes a new document, as the phases describe. When only one of the two variables is set, or a file cannot be read, use scratch mode and say why in the closing lines.

Post mode always uses scratch mode.

The contract is `profile.integrations.lighthouse.contract`. Read it in full before you write the document, because it is the only authority on keys, shapes, and limits. This file tells you how to produce a good document; it does not restate every rule.

<HARD-GATE>
This skill reads GitHub and writes only to the Lighthouse server named by `--url` (post mode) or to `$LIGHTHOUSE_EXPLANATION_FILE` and its `.tmp` sibling (file mode). It only reads `$LIGHTHOUSE_BASE_EXPLANATION_FILE` and `$LIGHTHOUSE_UPDATE_DIFF_FILE`, and never writes them. Never comment on, review, label, or edit the pull request, and never post to Linear or Slack. Use `gh api` for reads only (no `-X`, `-f`, or `--method` other than GET). This is an explanation, not a review: do not hunt for defects or recommend changes.

The skill runs without a person present. Lighthouse can start it headlessly and show its progress. Never ask a question, never wait for approval, and never offer choices. When something is ambiguous, make the reasonable choice and continue. When something blocks the run, stop and end with the failure line from "Final line".
</HARD-GATE>

## Progress and the final line

Each phase below starts with one line of text, exactly `explain-pr phase: <name>`, before its first tool call. The names, in order, are `resolve head and merge base`, `read diff`, `read code`, `write explanation`, `deliver`, and `fix rejections` (only when Lighthouse rejected the document). Lighthouse turns these lines into progress steps. Keep the other text between tool calls short.

The last line of the run is one of these, with nothing after it:

```
explain-pr result: success explanation_id=<id> pr=<number> head=<12-char head sha>
explain-pr result: written <explanation_id from validation, or unknown>
explain-pr result: failure phase=<name> reason=<one sentence>
```

The `success` line ends post mode and the `written` line ends file mode. Failures that end the run: the arguments have no PR number, a `gh` read fails or the PR does not exist, Lighthouse refuses the connection, Lighthouse answers `401`, `500`, or `503` (post mode), the token file is missing or unreadable (post mode), the handoff file cannot be written (file mode), or Lighthouse still rejects the document after five posts. Never print the token, also not in a failure reason.

## Update mode

Update mode uses the same phases and the same phase lines as scratch mode. Only the work inside the phases changes. Apply this section in place of the matching steps below, and keep every step that this section does not replace.

### Check the inputs

Read both files at the start of "resolve head and merge base". The base file is the old explanation, exactly as Lighthouse stored it. The diff file is a JSON object with `old_head_sha`, `old_merge_base_sha`, `head_sha`, `merge_base_sha`, `merge_base_moved`, `status`, `files`, and `truncated`. Each entry in `files` has `filename`, `status`, `previous_filename`, `additions`, `deletions`, and `patch` (`previous_filename` and `patch` can be `null`).

Use scratch mode for the whole run, and keep the reason for the closing lines, when one of these is true:

- A file is not valid JSON, or it does not have the keys above.
- The base file's `repository` or `pr_number` is not the pull request in the arguments.
- The base file's `head_sha` is not the diff file's `old_head_sha`.
- The diff file's `status` is not `ahead`.

### Phase changes

- **resolve head and merge base**: take `head_sha` and `merge_base_sha` from the diff file, and do not run the two reads of the contract. Lighthouse prepared the diff for exactly these commits, so the document must name the same pair. Set `HEAD`, `MERGE_BASE`, `OLD_HEAD` (`old_head_sha`), and `OLD_MERGE_BASE` (`old_merge_base_sha`) from the file.
- **read diff**: the diff file is the diff from the old head to the new head. Read the PR metadata as in scratch mode, but do not read the full PR diff. Find the changed files:
  - When `merge_base_moved` is `false`, the changed files are the files in the diff file.
  - When `merge_base_moved` is `true`, the head-to-head diff also contains the base branch changes that the PR merged or rebased in. Compare the PR's own patch per file, before and after:

    ```sh
    gh api "repos/$REPO/compare/$OLD_MERGE_BASE...$OLD_HEAD" --paginate --jq '.files[] | {filename, previous_filename, patch}' > old-pr.json
    gh api "repos/$REPO/compare/$MERGE_BASE...$HEAD" --paginate --jq '.files[] | {filename, previous_filename, patch}' > new-pr.json
    ```

    A file is changed when its patch differs between the two reads, or when it is in only one of them. Ignore differences in the `@@` hunk line numbers, because base branch changes above a hunk move them. A file that changed only in the head-to-head diff is base branch work. Use it as context, and do not revise its explanation.
  - When `truncated` is `true`, the diff file does not have every file or every patch. Read the missing patches with `gh api "repos/$REPO/compare/$OLD_HEAD...$HEAD"`, paging with `--paginate`.
- **read code**: read only the changed files at `HEAD`, and the code that you need to understand their changes. Do not read again the code of items that you keep.
- **write explanation**: copy the base file to `draft.json`, then revise it:
  - Set `head_sha` and `merge_base_sha` to `HEAD` and `MERGE_BASE`, set `produced_at` to the current time, and set `producer` as in scratch mode.
  - Keep the items, the `files` entries, and the anchors for code that the changed files do not touch.
  - Revise the items and the `files` entries that the changed files affect. Add a `files` entry for each file that the PR now changes, and remove the entry of a file that the PR no longer changes when no item depends on it.
  - Add items for added behavior, and remove items for removed behavior. Remove anchors that nothing references any more. Make sure that `overview.main_entry_point` still names an item with an anchor and `entry_point: true`.
  - Revise the overview only when the purpose, the business rules, or the entry point changed.
  - Write `comments` again for the new head. Keep an old comment only when its line still holds the same code, and move its line number when the code moved. Lighthouse replaces the suggestions of the older explanation that the user has not kept, so write every comment that still applies.
  - For an anchor whose code changed, write it again without `text`, as in scratch mode, so that the helper copies it from the new head.

  Then run the helper with `--relocate`:

  ```sh
  python3 "$(python3 "$SKILL_CONFIG" get paths.skills --path)/explain-pr/fill_anchors.py" --relocate draft.json explanation.json
  ```

  With `--relocate`, an anchor whose text moved to another line, and occurs only once in the file, gets the new line. The helper prints the move as a warning, and it is not a problem. An anchor whose text is missing or occurs more than once is still a problem: rewrite that anchor in the draft and run the helper again.
- **deliver** and **fix rejections**: as in file mode. Update mode never reads the ingest token.

## Phase: resolve head and merge base

Parse the arguments. The repository is `profile.work.github_repository` unless a PR URL names another one (Lighthouse will then reject it, which is correct). Run exactly the reads from the contract, nothing else:

```sh
REPO="$(python3 "$SKILL_CONFIG" get work.github_repository)" NUMBER=<pr>
read -r HEAD BASE < <(gh api "repos/$REPO/pulls/$NUMBER" --jq '.head.sha + " " + .base.sha')
MERGE_BASE=$(gh api "repos/$REPO/compare/$BASE...$HEAD" --jq '.merge_base_commit.sha')
```

`head_sha` is `HEAD` and `merge_base_sha` is `MERGE_BASE`. Never put `BASE` (`base.sha`), `baseRefOid`, or the base branch tip in the document, and never compute the merge base with local `git merge-base`. Write every anchor against `HEAD`, never against a local checkout, which can be at another commit.

Work in a scratch directory (the session scratchpad when there is one, otherwise `mktemp -d`). Keep the draft there; nothing goes into a repository.

## Phase: read diff

- PR metadata and ticket: `gh api "repos/$REPO/pulls/$NUMBER" --jq '{title, body, base: .base.ref, head: .head.ref}'`. Take ticket IDs (`<PREFIX>-1234`) from the title, branch, or body. When the Linear MCP is available without a prompt, read the ticket for the requirement and the business rule; only the human-written Requirements section is authoritative. When it is not available, continue with the PR body.
- The diff: `gh api "repos/$REPO/compare/$MERGE_BASE...$HEAD" --jq '.files[] | {filename, status, previous_filename, additions, deletions, patch}'`. For a large PR, page with `--paginate` or read file by file.

## Phase: read code

- Whole files at the head, including code the PR does not change: `gh api -H "Accept: application/vnd.github.raw" "repos/$REPO/contents/<path>?ref=$HEAD"`. Save them in the scratch directory and use `grep -n` or `nl -ba` for line numbers. Read the callers, the models, the templates, and the tests that make the change understandable.
- The old version of a file, when the change is a rewrite: the same call with `ref=$MERGE_BASE`.

When the code touches regulatory domain logic and the business rule is not obvious, the `business-rules` skill and `profile.work.knowledge_root/` notes can explain it. Calibrate the explanation with `profile.user.technical_knowledge` when configured, or with the experience stated in the request.

Before you write, you must be able to say in two sentences why the PR exists, what rule it enforces, where execution starts, and which few functions carry the behavior.

## Phase: write explanation

### Choose the structure

The structure is yours, and it should follow the change, not the file list. Choose the shape that explains this PR best:

- A feature: entry point first, then the path the request takes, then the supporting pieces.
- A performance change: the slow path and why it was slow, then the new path, then what guards correctness.
- A refactor: the concept that moved, the old shape against the new shape, then the call sites.
- A bug fix: the failing scenario, the root cause, then the fix and its regression test.

Lead with what matters most. The reader expands one level at a time, so the top-level items must make sense alone, and detail goes deeper. Put code outside the PR in the tree whenever it is needed to understand the change (the caller that triggers it, the model it reads); the reader shows unchanged code as a normal subject. Give tests their own item near the end unless a test is the clearest statement of the rule. Give minor mechanical changes (imports, renames, fixtures) one short item, or only a file explanation.

Mark the handful of places a reader must understand: `entry_point` where execution enters the behavior, `key_function` where the important decision is made. Three to six marks is typical; marking everything marks nothing. Set `overview.main_entry_point` to the single best entry point item (it must have an anchor and `entry_point: true`).

State only what you read in the code or the PR. When a claim is a guess, leave it out.

### Write the document

Write a draft JSON file. Use the contract's example as the shape. Rules that are easy to miss:

- `overview.purpose` answers why the PR exists, `overview.business_rules` states the rule in domain terms (who, what, when, which limit), and `overview.summary` says how the code achieves it, with `[[anchor]]` links to the key places. Add an `example` that follows one concrete case through the change, and a `glossary` for domain terms. Omit an optional part instead of leaving it empty.
- `produced_at` is `date -u +%Y-%m-%dT%H:%M:%SZ` at the time you write it. `producer` is `explain-pr (Claude Code)` or `explain-pr (Codex)`.
- Every item has a unique `id`, a `parent` (`null` for top level), a `title`, and `text`. Order siblings in reading order.
- A title is one plain sentence that says what changed and why, for example "Runs the commands before the deployment, so the order matches the requirement". Never a bare noun phrase such as "The new deployment order", because the reader sees only the titles until it expands an item. Titles stay under 160 characters and may use backticks, but not `[[anchor]]`.
- An item's text starts with the WHY in one or two sentences (the rule, the bug, or the requirement that makes the change necessary), then the HOW in one or two sentences (which code does it, and in which order). Keep it short and descriptive; put more detail in child items.
- Put every code identifier in backticks, in titles, in text, in the overview, and in file explanations: variables, functions, methods, classes, modules, fields, settings, commands, and file names. Use `[[anchor-id]]` instead when the reader should be able to open that code.
- Text is plain: paragraphs, `- ` lists, backticks, and `[[anchor-id]]` or `[[anchor-id|label]]`. No Markdown headings, emphasis, links, or URLs. The id inside `[[...]]` must be a key of `anchors`, never an item id; to point at an item, point at its anchor.
- Anchors: a file anchor is `{"path": ...}`. A symbol anchor needs `line` and `text` copied exactly from the head. In the draft, write a symbol anchor as `{"path": ..., "symbol": ..., "line": N, "span": K}` with no `text`; the helper below copies `K` lines (default 2) from the head. Use the signature line, plus enough following lines to make the text unique in the file. A file or symbol that the PR removes is `{"path": ..., "absent": true}`. For a renamed file, use the new path.
- `files` gives one explanation for every changed file (what the file is, and what this PR does in it), plus unchanged files that the tree depends on.
- `comments` is optional. It holds review comments that Lighthouse shows to the user as suggestions on their lines, which he keeps, edits, or dismisses before he submits a GitHub review. Each entry is `{"path": ..., "line": N, "body": ...}`, with an optional `start_line` lower than `line` for a range. Lines are head lines. Prefer lines that the PR adds or changes, because only lines inside a diff hunk become inline GitHub comments. Write a comment only where a careful reviewer would really write one: a likely bug, a missing case, a risky assumption, or a question that the code does not answer. Write it in plain words, addressed to the author, with code in backticks. Omit `comments` when you have none, and never write more than 100.

Then fill and check the anchors against the head:

```sh
python3 "$(python3 "$SKILL_CONFIG" get paths.skills --path)/explain-pr/fill_anchors.py" draft.json explanation.json
```

It prints every anchor whose text is not at its line, every path that is not a file at the head, and every `[[id]]` in a text that is not an anchor id, and a warning when the text also occurs elsewhere in the file (widen the span). Fix the draft and rerun until it writes `explanation.json`.

## Phase: deliver

Print `explain-pr phase: deliver` in both modes, then follow the mode.

### File mode

Validate the document. This call needs no token and stores nothing:

```sh
URL=${LIGHTHOUSE_URL:-$(python3 "$SKILL_CONFIG" get integrations.lighthouse.url)}  # or --url
curl -sS -w '\n%{http_code}\n' -X POST "${URL%/}/api/explanations/validate" \
  -H "Content-Type: application/json" \
  --data-binary @explanation.json
```

- `200` `{"valid": true, "explanation_id": ...}`: write the handoff file. Copy the document to the temporary sibling and rename it, so that Lighthouse never reads a partial file:

  ```sh
  cp explanation.json "$LIGHTHOUSE_EXPLANATION_FILE.tmp" && mv "$LIGHTHOUSE_EXPLANATION_FILE.tmp" "$LIGHTHOUSE_EXPLANATION_FILE"
  ```

  Then end with `explain-pr result: written <explanation_id>`, or `written unknown` when the `200` carried no `explanation_id`.
- `422`: go to "fix rejections", and validate again with the same command.
- Connection refused or any other status: end with the failure line, naming the status and the server's message. Do not write the handoff file, and do not fall back to post mode.

### Post mode

```sh
URL=${LIGHTHOUSE_URL:-$(python3 "$SKILL_CONFIG" get integrations.lighthouse.url)}  # or --url
TOKEN_FILE="${ENGINEERING_ATTENTION_HOME:-$HOME/.engineering-attention}/ingest-token"  # or --token-file
curl -sS -w '\n%{http_code}\n' -X POST "${URL%/}/api/explanations" \
  -H "Authorization: Bearer $(cat "$TOKEN_FILE")" \
  -H "Content-Type: application/json" \
  --data-binary @explanation.json
```

Handle the response as the contract's Delivery table says:

- `201`: done. End with the success line, using `explanation_id` from the response.
- `422`: go to the next phase.
- `401`, `500`, `503`, or connection refused: end with the failure line. Name the status and the server's message (for `401`, the token file path), because each one needs a person to fix the server or its token file. Do not start a server.

## Phase: fix rejections

Read every entry in `reasons`, fix all of them in the draft, refill the anchors, and send the document again with the same command as in the deliver phase (validate in file mode, post in post mode). Validation and ingest return the same `422` envelope. Do not drop content to get past a reason you do not understand; read the contract section that the key path names. After the fifth rejected attempt, end with the failure line and the first reason.

## Final line

Before the final line, write at most three short lines for a person who reads the transcript: the structure you chose, and the marked entry points and key functions. In file mode, one of the lines says how the document was written: "Updated from the explanation for `<old head, 12 characters>`.", or "Written from scratch: <reason>." when update mode was requested but could not be used. Then write the success, written, or failure line from "Progress and the final line" as the last line. If the PR's head changes later, the explanation shows as stale and needs a new run.
