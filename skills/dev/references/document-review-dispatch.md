# Select and dispatch a document reviewer

Apply this procedure only to requirements and design-spec in `review` mode.
Run one review per draft. A preferred-provider failure can cause a replacement
attempt, not an additional required opinion.

## Select the route

Read `document_review` in models.json. Identify the initiating client from the
active runner, rather than guessing from which skill directory was loaded.
Record the document author's model and provider when known as separate facts;
client routing alone does not prove the author and reviewer used different
providers.

- In Codex, prefer an installed Claude CLI using its configured default model
  and medium effort. This default selection is authorized for this review route.
- In Claude, prefer an installed Codex CLI using GPT-6.1 Sol and medium effort.
- If the initiating client is unknown or the preferred backend is unavailable,
  use GPT-6.1 Sol with medium effort through an available approved Codex backend.

Check executable availability and version, then inspect its current help before
building the command. Installation does not prove authentication or model access.
Record a missing executable, authentication failure, unavailable model, unsupported
capability, or execution failure as evidence for fallback. Do not install clients,
change credentials, switch accounts, or bypass permissions to enable the review.
A permission denial does not authorize using the fallback to perform the denied
action. If fallback also cannot run, report the review blocked.

Use an exact Claude model from applicable user configuration when safely
available; otherwise omit the model flag and record requested selection as
`cli-configured-default`. Read only model settings, never dump configuration or
credentials. Record the actual model from backend metadata when exposed. Keep
that resolved selection for correction rechecks when the CLI can enforce it;
otherwise record the limitation and any observed version change.

## Dispatch with a fresh context

Supply the skill, development/v1 packet, pinned source artifacts, and report
contract. Keep the author's private reasoning out of the packet. Start from the
exclusive job directory. Do not resume or continue an existing conversation.
Use argument arrays and stdin for prompts; do not interpolate source text into
shell commands. Preserve applicable host permissions, repository rules, and hooks.

For Claude CLI, use print mode, JSON output, no session persistence, and medium
effort. Restrict built-in tools to `Read,Glob,Grep` and restrict allowed tools to
that same set. Use strict MCP configuration with an empty MCP server map so
connected external tools are unavailable to this review. Use `dontAsk` permission mode so a background review cannot hang
on an interactive approval. Grant read access only to declared sources. Do not
enable permission bypass, add a write tool, or use an automatic fallback-model
flag. If the installed CLI cannot enforce these limits, use the approved fallback.

For Codex CLI, use `exec`, GPT-6.1 Sol, medium effort, ephemeral execution, a
read-only sandbox, and the job's exclusive final-response output path. Preserve
normal rules and hook trust. Do not grant writable source directories for this
review. A native Codex worker is also valid for fallback when its fresh context,
model, effort, and declared read-only source scope can be enforced.

Use `captured-final-response` delivery for a read-only CLI review. The reviewer
returns the full report. Capture Claude's final result from the JSON envelope,
checking the result/error status; keep backend metadata separately. For Codex,
capture its final response and dispatch metadata. A process exit alone is not a
valid review: require the report, expected identity, coverage, source digests,
and status before accepting it. Publish the report verbatim with an atomic rename
to the exclusive output path. Never overwrite an earlier attempt.

If a preferred attempt fails, terminate it and preserve its evidence before
starting a fresh fallback attempt. The fallback reads the original packet and
drafts, not the failed review's conclusions. Report the route and fallback reason.
Continue author corrections and affected-section rechecks under document-review.md.
