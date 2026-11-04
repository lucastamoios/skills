---
name: meeting-distill
description: Extract long-term knowledge from a meeting transcript and persist it into docs/. Filters out ephemeral content and focuses on durable architectural, product, domain, and team knowledge. In the brain, also records the meeting (date, type, what was shared) in the meetings ledger so planning has a reliable timeline.
user_invocable: true
allowed-tools: Read, Grep, Glob, Edit, Write, Agent, Bash(git log *), Bash(git diff *)
argument-hint: "[paste transcript or path to transcript file]"
---

# Meeting Distill

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Extract long-term relevant knowledge from a meeting transcript and persist it into the project's knowledge folder. That folder is `vault/` in the brain (`profile.paths.brain`) and `docs/` in a code repo (for example the configured organization repo, whose docs are shared with the team) - use whichever the current repo actually has. Mentions of `docs/` below mean this folder. This skill is designed for recurring team syncs, all-hands, and planning meetings.

Argument: `$ARGUMENTS`

## Step 1: Obtain the transcript

- If `$ARGUMENTS` contains a file path, read it.
- If `$ARGUMENTS` is empty or short, the transcript was likely pasted directly in the conversation. Use the conversation context.
- If no transcript is available, ask the user to paste one or provide a file path.

## Step 2: Identify participants and meeting type

Scan the transcript and note:
- **Who attended** (names and roles, if discernible)
- **Meeting type** (weekly sync, all-hands, planning, 1:1, etc.)
- **Date** (from the transcript header or context)

## Step 3: Extract long-term knowledge

Read the transcript and extract **only durable knowledge** - information that will still be relevant months from now. For each item, classify it:

### What to extract

| Category | What to look for |
|----------|-----------------|
| **Product direction** | New product ideas, feature visions, strategic pivots, market positioning signals |
| **Architecture/tooling** | New tools, systems, or architectural patterns being built or adopted (how they work, why they were chosen) |
| **Domain knowledge** | Regulatory, scientific, or industry context that helps understand the business |
| **Team/org changes** | New hires, role changes, team restructuring, new responsibilities |
| **Process changes** | New workflows, changed policies, new vendor relationships that affect how work gets done |
| **Client/market signals** | Patterns in client needs or market dynamics (not individual deal details) |

### What to ignore

| Category | Why |
|----------|-----|
| Status updates on in-flight work | Ephemeral - will be outdated in days |
| Deadlines and timelines | Ephemeral - stale immediately after the date passes |
| HR/benefits/admin announcements | Not relevant to project context |
| Small talk, introductions of existing team members | No knowledge value |
| Bug reports or incident details | Belong in issue trackers, not docs |
| Specific customer names and deal values | Business-sensitive, not engineering context (unless the client relationship reveals a product pattern) |
| Action items and to-dos | Belong in task trackers |

## Step 4: Reconcile with existing docs

Read `docs/index.md` to understand existing documentation structure.

For each knowledge atom:

1. **Find the right file** - check if an existing doc covers the topic
2. **If a doc exists** - read it, update the relevant section. Merge new information naturally into existing prose. Do not create duplicate sections.
3. **If no doc exists** - only create a new file if the knowledge does not fit into any existing doc.
4. **If content contradicts existing docs** - update the doc with the newer information. Add the meeting date as source context (e.g., "as of April 2026 weekly sync").

### Writing conventions

- **No em-dashes or connector dashes** in any text; use commas, colons, periods, or parentheses (compound-word hyphens are fine)
- **Full sentences** with pronouns and normal punctuation
- **No fluff** - write for an AI assistant that needs facts, not prose
- **Lead with the what, then the why**
- **Attribute ideas to people** when it helps understand the organizational context (e.g., "Matt identified the need for..." or "Samantha proposed...")

## Step 5: Update docs/index.md

If any new files were created, add them to `docs/index.md` under the appropriate section.

## Step 6: Record in the meetings ledger (brain only)

When running in the brain (`profile.paths.brain`), append a dated entry to `profile.work.meeting_log`, newest first, right under the `<!-- meeting-distill appends entries below this line -->` marker. This is separate from the durable knowledge above. The ledger is a reliable timeline of prior standups and weeklies.

Classify the meeting from the event and the configured private cadence. Do not infer an organization's schedule from this package. Then add:

```
## <YYYY-MM-DD> - <Standup | Weekly | other>

- Shared: <one or two lines on what the user reported or what was decided>
- Direction: <only if something shifted priorities or focus; otherwise omit>
```

Keep it short. The full knowledge lives in the project docs; this is only the timeline. Skip this step entirely when running in a code repo rather than the brain.

## Step 7: Report

Output a concise summary of what was extracted and where it was written:

```
Meeting: [type] - [date]
Participants: [names]

Changes:
- Updated docs/<area>/engineering.md: [what was added]
- Updated docs/<area>/overview.md: [what was added]
- Created docs/<area>/new-topic.md: [why a new file was needed]

Skipped (ephemeral):
- [1-2 sentence summary of what was intentionally left out]
```

## Key principles

- **Err on the side of excluding.** If you are unsure whether something is long-term relevant, leave it out. The user can always ask you to add more.
- **Never add deadlines or dates as actionable items.** Dates are only useful as temporal context for when a decision was made.
- **Merge, don't duplicate.** Always check existing docs first. The goal is to enrich existing documentation, not create parallel files.
- **Preserve existing structure.** When updating a file, respect its current organization. Add new sections where they naturally fit.
- **No em-dashes or connector dashes.** Use the punctuation that means the same thing: commas, colons, periods, or parentheses. Hyphens inside compound words are fine.
