---
name: gardener-transcripts
description: Mine the raw Claude Code session transcripts for meta-signals the in-session capture misses - repeated corrections, recurring worries, orphaned knowledge, recurring questions, friction, and violations of already-documented norms - then file the approved harvest into guardrails, memory, or the vault. Trigger on explicit transcript-mining intent ("mine the transcripts", "harvest the transcripts", "what am I always correcting", "run the transcript miner"), or as the transcripts arm of a full gardener pass. Do not trigger for ordinary session distillation (/retro) or vault tending (gardener-prune/audit).
user_invocable: true
---

# Gardener: Transcripts

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. For shell examples, set `SKILL_CONFIG` to the installed `skill-config/scripts/config.py` absolute path. The examples query the private profile at runtime; verify required fields before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Per-session capture (/retro, ad hoc memory writes) is done by the same agent doing the work, in the moment, only when it notices. The signals that matter most are cross-session patterns it structurally cannot see: one correction is noise, the same correction in five sessions is a rule. This skill runs the offline pass: extract the user's side of every transcript since the last run, mine it with parallel subagents, dedup against what is already documented, and file the approved delta.

It has a second mandate, equally important: find **documented-but-violated norms**. A memory that exists but keeps getting violated is a recall failure, and the fix is rewriting its trigger or promoting it to the global guardrails, not writing more memories.

## Step 1: Watermark

Read `profile.paths.brain/.transcripts-watermark` (a single ISO-8601 timestamp: the newest message mined by the previous run). If it does not exist, default to 21 days ago. Do not mine the same window twice.

## Step 2: Extract

Run the versioned extractor into the session scratchpad:

```bash
"$(python3 "$SKILL_CONFIG" get paths.scripts --path)/extract-user-messages.sh" --out <scratchpad>/user-messages --since <watermark>
```

It produces one markdown file per project dir containing only the user-typed messages (sidechain subagent prompts, harness noise, automated hook prompts filtered; long pastes truncated). Files that are pure noise are dropped automatically. Note the total size before fanning out.

**Early exit:** if the total extracted material is under roughly 30KB, there is not enough signal for pattern mining. Report that briefly (or silently skip when running under the gardener orchestrator), leave the watermark untouched so the material accumulates, and stop.

## Step 3: Mine with parallel subagents

Group the output files into chunks of roughly 250KB and spawn one **Sonnet** subagent per chunk, all in a single message so they run concurrently. Each agent must read its files fully (chunked reads) and report on six categories, every finding with short verbatim quotes (max 15 words), timestamps, and an occurrence count:

1. **Corrections**: the user correcting behavior, style, scope, or facts; repeats across sessions are the prize.
2. **Recurring worries**: themes he keeps returning to, risks he keeps probing.
3. **Orphaned knowledge**: valuable facts or rationale stated in passing that likely never got persisted to code, docs, skills, or memory.
4. **Recurring questions**: questions asked more than once, meaning the answer never landed anywhere durable.
5. **Friction patterns**: retries, re-explaining context, permission-gate loops, "again" moments.
6. **Violated documented norms**: paste into each agent's prompt the current `MEMORY.md` index and the relevant configured rules from `profile.integrations.guidance.rules`, and ask it to flag any place where the user had to re-state a norm those already document.

Tell each agent that patterns (2+ occurrences) outrank one-offs, that high-value one-offs go in a separate list, that pure task instructions carry no signal, and that its final message is the deliverable.

## Step 4: Merge and dedup

Combine the reports and check every candidate against the current MEMORY.md index, the configured guidance rule files, and the vault index. Discard anything already adequately documented (a re-found existing memory is not a finding unless it was violated, which makes it a category-6 finding instead).

## Step 5: Propose a filing plan

Present a numbered plan, one line per candidate, each with its evidence count and a proposed destination:

- **Command-tied norm**: propose a client hook only when the relevant hook configuration and a permitted destination are declared in `profile.integrations.guidance`. Follow that client's current hook contract. Without that integration, propose a private note and leave hook setup pending.
- **Hard cross-project rule**: propose the configured rules destination in `profile.integrations.guidance.rules`. If no writable destination is configured, ask where it belongs. Do not invent a dotfiles layout or change another client's settings.
- **Preference or gotcha**: new or updated memory file plus MEMORY.md index line.
- **Violated norm**: rewrite that memory's description and index line to be trigger-first ("BEFORE doing X: ..."). If the same norm shows up violated in a second run, promote it up the ladder (guardrails, or a hook when command-tied).
- **Durable work knowledge**: the right note under `profile.work.knowledge_root/`, following vault conventions.
- **Personal content**: the right note under `vault/personal/`. Anything journal-grade (emotional, spiritual, family) is flagged for the user to place himself, never auto-written.
- **Recurring worry that wants a runbook or script** (not a memory): propose it as a follow-up task; do not write docs for it here.

In an interactive session, apply the plan only after the user approves it (he can strike items by number). In a non-interactive run, write the full candidate list to `profile.paths.brain/pending.yml` with reasoning and evidence, apply nothing else, and proceed to Step 6: staging counts as processing the window, so the watermark must still advance or the next headless run would duplicate every candidate.

## Step 6: Advance the watermark and commit

Write the newest message timestamp seen during extraction to `profile.paths.brain/.transcripts-watermark`. Interactively, stage the brain changes and hand the user the signed commit command (conventional `feat(gardener):` or `docs:` prefix). In unattended runs, commit directly (signed, no Co-Authored-By, no connector dashes), matching gardener-inbox.

## Notes

- Expect most worktree project dirs to contribute nothing: they are dominated by automated review hooks, and the extractor already drops them.
- Keep the miner honest about coverage: if a chunk was skipped or an agent failed, say so rather than presenting a partial pass as complete.
- The related arms are [[gardener]] (orchestrator), [[gardener-inbox]], [[gardener-board]], [[gardener-audit]], [[gardener-prune]].
