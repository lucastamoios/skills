---
name: meeting
description: Prepare concise, Slack-ready briefs for standups, weekly updates, one-on-ones, project reviews, and other work meetings. Use when the user asks what to report, wants an update for teammates, company owners, or his manager, needs recent accomplishments or blockers, or wants context and questions for an upcoming meeting. Reconcile Calendar, the brain vault, Obsidian tasks, Codex and Claude sessions, Git and GitHub, Linear, Slack, and daily logs.
---

# Meeting

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. For shell examples, set `SKILL_CONFIG` to the installed `skill-config/scripts/config.py` absolute path. The examples query the private profile at runtime; verify required fields before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Prepare a concise brief from the real work record. This skill owns meeting reporting and preparation. The `priorities` skill owns day planning, and `meeting-distill` owns durable knowledge after a meeting.

## 1. Resolve the meeting

Use the connected Google Calendar meeting-prep workflow to find the named or next relevant event. Read the event, recurrence, attendees, description, attachments, and nearby calendar context.

If there is no calendar event, use the meeting named by the user and find its most recent matching entry in `profile.work.meeting_log`.

Classify the meeting:

- **Standup**: a short verbal update about completed work, current work, and blockers.
- **Weekly or one-on-one**: progress, decisions, risks, next outcomes, and asks.
- **Project or decision meeting**: focused context, open decisions, evidence, and questions.

## 2. Set the evidence window

Use the previous occurrence of the same recurring event as the start of the window. If it cannot be found, use the latest matching meeting-ledger entry. If neither exists, use the previous seven calendar days.

Use the meeting start as the end of the window. For a meeting happening now, use the current time. Use the window to guide research, but show it in the brief only when it helps the audience understand the update or the user asks for it. Do not substitute a global last-run timestamp for the meeting-specific window.

## 3. Gather every source

Read [references/sources.md](references/sources.md), then attempt every source below. Gather independent sources concurrently where possible.

### Delegate evidence collection

Before gathering evidence, spawn parallel read-only subagents for independent
source groups. In Codex, use `gpt-5.6-luna` for these subagents. In Claude Code,
use `haiku`. If the requested model or subagent interface is unavailable, gather
that scope directly. Do not silently substitute a different model.

The main agent must read this skill and its required references, resolve the
meeting, set the evidence window, assign bounded source scopes, reconcile the
returned evidence, make all brief decisions, and perform all writes. Use no more
subagents than useful. Prefer these groups, and adapt them to the available
sources and the request:

1. Vault, tasks, logs, repositories, and sessions.
2. GitHub and Linear.
3. Calendar and Slack.

Do not delegate one file per subagent. Give each subagent the evidence window,
the exact files or apps to inspect, and a strict output contract. Each subagent
must return only brief-relevant evidence: the concrete outcome or ask, impact,
current state, decision, blocker or resume condition, source identifier and
timestamp, and any material coverage gap. It must omit raw file contents,
transcripts, tool output, routine implementation details, duplicate
notifications, speculative conclusions, and its own narrative or ranking. A
subagent that owns live sources must verify drift-prone claims in those sources.

Wait for all useful subagents. Deduplicate their findings and resolve conflicts
against the freshest authoritative source. Keep final synthesis, audience
filtering, the Slack-ready brief, and all external mutations in the main agent.

1. Google Calendar, including recurrence, attendees, descriptions, and attachments.
2. The brain vault, beginning with `profile.paths.vault/index.md`, the relevant organization notes, and `profile.work.meeting_log`.
3. Recent Codex and Claude sessions within the evidence window.
4. Git commits and current GitHub pull request, review, and check state.
5. Linear issues, descriptions, and recent comments.
6. Slack direct messages, mentions, relevant channels, and full threads.
7. Obsidian tasks, including Today, In Progress, Review, Blocked, and To Do.
8. Daily logs, as supplementary evidence only.

Run the session collector:

```bash
python3 "$(python3 "$SKILL_CONFIG" get paths.skills --path)/meeting/scripts/recent_sessions.py" \
  --since "<window-start-ISO>" \
  --until "<window-end-ISO>" \
  --scope "$(python3 "$SKILL_CONFIG" get paths.brain --path)"
```

Inspect each relevant root session returned by the collector. Extract concrete outcomes, decisions, blockers, handoffs, issue identifiers, pull requests, branches, and changed files. Inspect child or sidechain sessions only when the root session does not contain the outcome.

If any source is unavailable, continue with the others. Mention the gap only when it materially limits the brief's accuracy. Never imply that an unavailable source was checked.

## 4. Reconcile the evidence

Create one deduplicated work record. Deduplicate by Linear issue, pull request, branch, or concrete outcome.

Apply these rules:

- Live GitHub, Linear, Slack, Calendar, and Obsidian task state determines what is current.
- Session transcripts show what the user and his agents attempted, decided, completed locally, or left blocked. They do not prove that a pull request merged, CI passed, a deploy completed, or another person responded.
- Git commits and diffs verify local implementation. GitHub verifies remote and review state.
- Daily logs and vault notes provide context, but they do not override newer live evidence.
- Distinguish `Done`, `In progress`, `Blocked or waiting`, `Decision`, and `Ask`.
- Exclude tool mechanics, repeated notifications, speculative plans, and abandoned approaches.
- For the configured organization meetings, exclude personal projects and unrelated side projects unless the user asks for them.
- Do not read or surface `profile.paths.vault/personal/journal/` for work meetings.

When a session-derived claim cannot be verified live, label it as local or session-derived instead of presenting it as confirmed current.

## 5. Apply the audience and relevance filter

Write for the user's teammates, company owners, and manager. They care about outcomes, user or business impact, current direction, risks, decisions, and help needed.

Include an item only when it answers at least one of these questions:

- What meaningful outcome changed?
- Why does it matter to the company, product, customer, or team?
- What is currently moving toward an outcome?
- What risk, dependency, decision, or ask needs the audience's attention?

Omit routine implementation proof and researcher metadata:

- Test counts, passing test suites, test names, and validation commands.
- Commit SHAs, branch names, CI status, and deployment mechanics.
- Seed-data details, tool activity, source inventories, and evidence-collection gaps.
- Low-level implementation detail that does not change impact, risk, timing, or a decision.
- PR and issue identifiers unless someone needs the link to review, decide, or follow up.

Mention testing, CI, deployment, or technical detail only when it reveals a material risk, explains a delay, establishes that something reached users, or supports a decision the audience must make.

Prefer the impact statement over the activity statement. For example, say "State Hub now supports product-specific and organization-wide fee defaults in UAT" instead of listing migrations, test counts, commits, and deployment commands.

## 6. Scale detail to the size of the outcome

Give substantial outcomes more space than routine delivery activity. Judge the
size by the result and its impact, not by whether the work happened through a
pull request.

- Aggregate small results such as routine pull request reviews, replies, merges,
  rebases, and follow-ups into one topic for each relevant status. Do not give
  each small result its own bullet.
- Lead with the count and the aggregate result. Add a short description beside
  an identifier only when it helps the audience recognize the work.
- For completed work, prefer a compact form such as: `Reviewed 5 PRs; 2 merged
  (#123: export fix, #456: settings search).`
- For current pull request work, prefer a compact form such as: `Working on
  merging 3 PRs (#123: export fix, #456: settings search, #789: review gate).`
- Omit identifiers and descriptions when the count alone is enough. Do not turn
  the compact summary into a hidden list of status details.
- Give a larger outcome its own bullet and enough space to state what changed,
  why it matters, and the next decision, risk, or handoff. A large feature must
  not be compressed merely because its implementation is a pull request.

## 7. Write the brief

Return only a ready-to-paste Slack message, not a research report or an explanation of the message. Keep it verbal-friendly and compact. Omit empty sections. Include a source identifier or link only when the audience needs to act on it.

Use Slack mrkdwn:

- Use one asterisk for bold, for example `*Done:*`.
- Use simple bullets with `•`.
- Do not use Markdown headings, tables, double-asterisk bold, or `>` blockquotes.
- Do not wrap the message in a code fence.
- Do not add a preamble, evidence section, or closing commentary outside the message.

If the user explicitly names another destination or format, adapt to it instead.

### Standup

```text
*Standup*

• *Done:* <completed outcome and why it matters>
• *In progress:* <current outcome and its direction>
• *Blocked, decision, or ask:* <only when the audience needs to know or act>
```

### Weekly or one-on-one

```text
*Weekly update*

*Progress*
• <completed and materially advanced outcome>

*Decisions and changes*
• <decision, changed assumption, or important feedback>

*Risks and blockers*
• <current risk, dependency, owner, and next signal>

*Next*
• <already committed or clearly implied next outcome>

*Asks*
• <decision, review, or help needed>
```

### Project or decision meeting

```text
*Meeting brief*

• *Purpose:* <what the meeting must accomplish>
• *Relevant context:* <facts and recent work>
• *Decisions needed:* <specific choices>
• *Questions and asks:* <what the user should ask or request>
• *Preparation:* <documents, pull requests, issues, or data to open>
• *Attendees:* <people and relevant roles>
```

If the user asks only what he did recently, report completed and in-progress outcomes without adding an action plan. Keep source coverage and verification details internal unless he asks for them or a gap materially changes confidence. Do not write to external systems unless he explicitly asks.
