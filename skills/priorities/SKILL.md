---
name: priorities
description: Choose the user's highest-value work from configured work, review, personal and task sources. Use for daily prioritization, blocked work, review queues and task-board reconciliation.
---

# Priorities

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. For shell examples, set `SKILL_CONFIG` to the installed `skill-config/scripts/config.py` absolute path. The examples query the private profile at runtime; verify required fields before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Return first the blocked tasks that need the user's attention now, then one
finishable primary outcome, two valuable wins, every meaningful tiny task,
actionable side quests, blocked-work watches, and the complete review queue
that still needs the user. Rank actionable work by impact divided by total
effort within the current leadership direction, using everything the user has
shared as part of impact.

### Requester precedence

Read `profile.work.requester_order`, `profile.work.requester_aliases` and the relevant private context. Resolve aliases before ranking. Apply precedence to the person setting the outcome, not merely a review commenter. Preserve outstanding commitments until completed or explicitly superseded. Urgent incidents and explicit delivery obligations retain their priority. Without a configured policy, use current explicit commitments and ask about consequential conflicts.

## 1. Set the evidence window

Run:

```bash
python3 "$(python3 "$SKILL_CONFIG" get paths.skills --path)/priorities/scripts/last_run.py" window
```

Use the returned `since` timestamp for recent work and Slack. It includes one
week of overlap before the last successful Slack cutoff.

Immediately before returning the final answer, run `last_run.py mark` only when
Slack was queried successfully. If marking fails, report it under `Missing`.

## 2. Gather fresh evidence

Gather independent sources concurrently where possible. Treat unavailable
sources as coverage gaps, not reasons to stop.

### Delegate evidence collection

Before gathering evidence, use read-only subagents for independent source groups when the configured evidence-collection policy permits them. Read model choices from `profile.execution.evidence_collection`. If no choice or backend is available, gather that scope directly. Do not silently substitute a model.

The main agent must read this skill and its required references, set the evidence
window, assign bounded source scopes, reconcile the returned evidence, make all
priority decisions, and perform all writes. Use no more subagents than useful.
Prefer these groups, and adapt them to the available sources and the request:

1. Vault, tasks, logs, repositories, and sessions.
2. GitHub and Linear.
3. Slack.

Do not delegate one file per subagent. Give each subagent the evidence window,
the exact files or apps to inspect, and a strict output contract. Each subagent
must return only decision-relevant evidence: the concrete outcome or ask, current
state, the user-controlled next action, requester or audience, blocker or resume
condition, source identifier and timestamp, and any material coverage gap. It
must omit raw file contents, transcripts, tool output, routine implementation
details, duplicate notifications, speculative conclusions, and priority
rankings. A subagent that owns live sources must verify drift-prone claims in
those sources.

Wait for all useful subagents. Deduplicate their findings and resolve conflicts
against the freshest authoritative source. Keep ranking, final synthesis, task
reconciliation, cutoff updates, and all external mutations in the main agent.

### Direction

Read the configured vault index and the relevant documents in `profile.work.direction_notes`. Resolve requester aliases and precedence from the profile and private context. Follow only recent decisions into directly relevant linked notes.

### Work state

Check:

- Obsidian task lanes from `profile.paths.scripts/tasks.py list`: Today, In Progress, Review, Blocked, and To Do; read every open task's current state and recent notes, and read every Blocked task's body for its blocker, its resume condition, and any `Needs from the user` note;
- recent commits and dirty state across relevant repos and active worktrees;
- every open GitHub PR authored by the user, requesting the user, or authored by
  configured automation accounts, plus other PRs where the user controls an action; include
  issue comments, inline review threads, reviews, new commits after the user's
  review, checks, conflicts, and merge decisions;
- Linear issues assigned to the user, the configured automation, or a configured automation component and recently updated
  issues connected to his work;
- Slack DMs, group DMs, mentions, thread replies, review requests, blockers,
  and recent messages from configured leadership and outstanding handoffs;
- recent Codex and Claude root sessions; flag every idle session whose last
  message asks the user a question or waits on his decision;
- recent daily logs as supplementary evidence.

Start GitHub and Linear with the bundled collectors:

```bash
python3 "$(python3 "$SKILL_CONFIG" get paths.skills --path)/priorities/scripts/collect_github_prs.py" \
  --repo "$(python3 "$SKILL_CONFIG" get work.github_repository)" \
  --output /tmp/priorities-github.json
python3 "$(python3 "$SKILL_CONFIG" get paths.skills --path)/priorities/scripts/collect_linear_issues.py" \
  --output /tmp/priorities-linear.json
python3 "$(python3 "$SKILL_CONFIG" get paths.skills --path)/priorities/scripts/build_review_inventory.py" \
  --github /tmp/priorities-github.json \
  --linear /tmp/priorities-linear.json
```

The Linear collector reads `LINEAR_API_KEY` from the injected environment. When it is missing or unresolved, use `profile.integrations.environment.check_command` if configured, or report the missing environment setup. Never request the secret in chat or resolve it again through an unrelated credential flow.

The GitHub collector must inspect every open PR. Do not replace it with a
review-request search.

For Slack, resolve the user and configured requesters by user ID; search
direct and group conversations, mentions, and participated threads; then read full promising
DMs and threads. Ignore casual conversation and duplicate notifications.

Collect sessions with:

```bash
python3 "$(python3 "$SKILL_CONFIG" get paths.skills --path)/meeting/scripts/recent_sessions.py" \
  --since "<since-ISO>" \
  --until "<now-ISO>" \
  --scope "$(python3 "$SKILL_CONFIG" get paths.brain --path)"
```

Also inspect current open desktop tasks. Brain-scoped session collection alone
misses tasks running in Codex-managed worktrees outside `profile.paths.brain`. Read the
latest user instructions and substantive assistant result, combine rollout
fragments by session ID, and separate completed work, remaining work, and
unanswered decisions. A question already answered in a later turn is resolved.

For each In Progress card, match the live session and worktree. Base remaining
effort on what is already implemented and verified. Do not treat an old lane
or an uncommitted diff alone as proof that the work is currently active.
Preserve useful continuity when selecting today's outcome, but do not label
a foundation or partial API as user-visible completion.

Inspect every relevant root session. Sessions prove local work and decisions,
not current PR, CI, deploy, merge, or external-response state. Verify those
claims live.

## 3. Build one candidate ledger

Deduplicate work by outcome, originating request, Linear issue, PR stack, or
branch. For each candidate record:

- outcome and why it matters;
- exact next action the user controls;
- requester and people or deliveries unblocked;
- live state: actionable, partially actionable, waiting, or done;
- impact, total effort, and leverage;
- observable `Done means` condition;
- source identifiers.

Apply these state rules:

- **Actionable**: the user can finish the outcome today.
- **Partially actionable**: the user can finish a valuable independent slice.
- **Waiting**: another person, data, deploy, access, CI, or decision is required.
- **Done or superseded**: remove it from ranking.

Only actionable work and independent slices may enter the top three. Put
waiting work under `Watches` with one signal and one resume condition.

For a multiday initiative, do not select the initiative itself as the one
thing. Define a vertical, independently useful slice that the user can complete
today. The slice must have its own outcome, external value, and `Done means`
condition. Do not use a preparatory subtask unless completing it creates a
meaningful decision, handoff, or delivery by itself.

Do not list mechanical preconditions as work. Unlocking credentials, signing
in, opening an application, rerunning a command, or checking a notification
belongs inside the blocked outcome or under `Missing`.

## 4. Reconcile review ownership

Classify GitHub work as:

- **Needs the user**: the user controls a review, fix, reply, reconciliation, merge
  decision, conflict resolution, or failing check.
- **Waiting**: the user completed his action and another person must respond,
  approve, merge, deploy, or provide data.
- **Excluded**: draft, stale, duplicate, superseded with evidence, or noise.
- **Origin unresolved**: a bot PR whose originating human request is unknown.

Treat configured requester-originated the configured automation work as the user-owned through
review, validation, handoff, and merge readiness, regardless of PR author or GitHub
review-request state.

For every open configured automation accounts PR:

1. Find its Linear issue and parent chain.
2. Identify the originating human request from Slack or Linear when possible.
3. Group PRs serving the same request and preserve stack order.
4. Assign exactly one of the four states above.

Reconcile the count as:

`open bot PRs = Needs the user + Waiting + Excluded + Origin unresolved`

Do not infer supersession from similar titles or intent. Compare base, ancestry,
diff, rules, tests, and deployment target, and seek an explicit disposition.
If the user has already explained the overlap to the person who controls the
choice and asked for a decision, classify it as `Waiting`; do not recommend
reviewing or implementing either path until that person responds.

Build the `Needs the user` review queue at request level. Exclude PRs already
reviewed by the user at the current head and PRs waiting on someone else. For each
remaining outcome record review depth, risk, total effort, merge readiness,
blocked people, and delivered value.

Treat collector `pending_action_signals` as triage, not a verdict. For every PR
in the user's scope, compare the current head and the latest substantive activity
with the user's last review, comment, commit, or handoff. Read issue comments and
inline review threads, including replies and resolution state. Mark `Needs
the user` when any of these remains:

- a new question, request, blocker, or substantive reply directed to the user;
- requested changes or an unresolved thread on the user's PR;
- a renewed review request or material new commits after the user's review;
- a failing check, conflict, or merge decision the user owns.

Do not count bot status messages, acknowledgements, emoji-only replies,
duplicate notifications, or comments that require no decision or response.

Use these review tiers:

- **Critical**: active production/security incident or explicit same-day commitment.
- **High**: current configured leadership request, strategic the configured automation outcome, or
  merge-near delivery with meaningful unblock value.
- **Medium**: useful team unblock with modest delay cost.
- **Low**: maintenance or stale work with limited current value.

A review request is evidence of ownership, not automatic priority. A review
already approved by another required reviewer usually loses leverage unless
the user still owns a distinct decision or the review-calibration value is
explicitly worth the effort.

## 5. Rank by leverage

Estimate every actionable candidate:

- **Impact**: 1 maintenance, 2 minor, 4 significant, 8 major, 16 transformative.
- **Effort**: total responsible effort, including investigation, review depth,
  implementation, verification, communication, and handoff.
- **Leverage**: `impact / effort_hours`.

Impact is the overall value of completing the outcome today. Incorporate all
known context once: company goals and metrics, customer/product value, current
the configured leadership direction, outstanding leadership handoffs, the configured automation ownership,
people unblocked, commitments, strategic learning, cost of delay, and the user's
stated preferences. Do not add
requester or strategy bonuses again after scoring impact.

Rank in this order:

1. Put active production/security incidents, committed client deadlines, and
   explicit same-day obligations first. A defect found in an unmerged PR is a
   required pre-merge fix, not evidence of an active production incident.
2. Remove work the user cannot advance independently.
3. Apply current requester precedence: the configured requester order. Use the
   actual outcome and direction, not reviewer identity, to assign precedence.
4. Within that direction, order candidates by leverage using remaining total
   responsible effort. Prefer finishing an independently useful slice already
   in progress when it serves the same priority and avoids unnecessary switching.
5. Break close ties by higher impact, greater unblock value, then fresher
   human demand. Explain when fresh direction or verified session progress
   changes the previous daily plan.

Use conservative estimates when uncertain. Do not expose scores unless they
materially explain a close decision.

## 6. Choose the day

Select exactly:

1. **Blocked, needs your attention now**: every blocked or waiting outcome
   whose next action is the user's own decision, reply, or dispatch. Source it
   from Blocked-lane tasks whose note names the user as the unblock and from idle
   agent sessions waiting on his answer. Blocked work waiting on someone else
   stays under Watches.
2. **The one thing**: one independently finishable, high-impact result that
   justifies approximately half a day of focused work (normally 3 to 4 hours
   of total responsible effort). It can be somewhat shorter when the value is
   unusually high, but it must be substantial enough that, if the user delivers
   only this result, he can reasonably call the day complete. It must not
   require more than one workday. If the best leverage is multiday work,
   select its valuable vertical slice instead.
3. **Two valuable wins**: distinct actionable outcomes or valuable slices.
4. **Tiny tasks**: every meaningful outcome requiring about 15 minutes or less.
5. **Side quests**: lower-priority actionable work or bounded delegation.
6. **Watches**: blocked or waiting outcomes.

Tiny tasks must create an externally meaningful result such as a decision,
reply, handoff, correction, or small fix. Exclude setup chores and tasks already
contained in the top three or review queue. Label urgency by delay cost:

- **Now**: blocks today's work, another person, release, client, production, or
  security outcome.
- **Today**: delaying until tomorrow has a concrete cost.
- **Soon**: useful, but delay beyond today has little immediate cost.

Side quests must be actionable now. Watches must name what to check and the
exact condition for resuming. Write `None found.` for an empty section.

When review work wins, define a finite review delivery. Completion is the user's
decision or handoff, never the PR merging.

## 7. Reconcile the Obsidian task board

Before returning, reconcile the board through `profile.paths.scripts/tasks.py`. Use
fresh evidence to reflect what changed since the previous board reconciliation.
Apply proven workflow state before daily priority placement.

1. Read every open lane and match work by Linear ID, pull request URL or number,
   normalized title, then an unambiguous distinctive title. Never move an
   uncertain match.
2. Reconcile every clear state change first:
   - Move a task to In Progress only when current session, worktree, or repository
     evidence proves that the user is actively working on it.
   - Move a task to Review when the user's remaining action is a bounded review,
     validation, reply, or merge-readiness decision.
   - Move a task to Blocked when the outcome cannot advance until a named external
     signal or dependency changes. Add the blocker and exact resume condition.
   - Move a Blocked task out when its recorded resume condition has occurred. Place
     it using the current action and priority rules below.
   - Move a task to Done when a merged pull request, completed Linear issue, or
     another checked artifact conclusively proves the stated outcome. Add the
     evidence before moving it.
   - Move stale In Progress or Review work to its current truthful lane only when
     fresh evidence proves that the prior state no longer applies.
3. Place the remaining actionable work by daily priority:
   - Put **The one thing** in Today, unless it is already genuinely In Progress.
   - Put every item under **Blocked, needs your attention now** in Today, because
     the user controls the next unblocking action. Do not leave it in Blocked merely
     because the larger outcome is waiting after the user acts.
   - Put the **Two valuable wins** in To Do, unless a proven workflow state above
     requires In Progress, Review, Blocked, or Done.
   - Put meaningful side quests and other actionable surfaced outcomes in To Do
     when they deserve a card but are neither today's commitment nor a valuable
     win. Do not move Scheduled, Maybe, or Delegated work merely to tidy the board.
4. Create a missing card only for the one thing, a the user-controlled unblocker, a
   valuable win, or another meaningful actionable outcome that clearly deserves
   tracking. Include realm, type, identifiers, why it matters, `Done means`,
   impact, effort, and work type.
5. Do not create cards for **Watches** or **Tiny tasks**. If one already matches an
   existing card, move it only when fresh evidence proves a real workflow-state
   change. Do not move or create a card merely because the item appears in the
   daily output. Do not create a card for every review-queue item either; reconcile
   an existing card when present, and create one only when the outcome independently
   deserves tracking.
6. Retain tasks already in the correct lane. Report every created or moved task
   with its evidence, report the selected tasks retained in place, and summarize
   deliberately untouched matches.

If the task files or command are unavailable, retry once only when the failure may be transient.
Do not infer board state from sessions or claim synchronization without proof.

## 8. Output

Use this exact structure:

```markdown
## Blocked, needs your attention now

- **<blocked outcome>**: <exact unblocking action the user controls>. Unblocks: <what resumes once he acts>. Source: <task, session, or PR>.

## The one thing

<Outcome>

Why this wins today: <impact, leverage, requester/direction, and live state>

Done means: <condition the user controls>

## Two valuable wins

1. <Outcome>. Done means: <condition>.
2. <Outcome>. Done means: <condition>.

## Tiny tasks

- **<Now|Today|Soon> · <estimate>**: <meaningful action>. Why now: <delay cost>.

## Side quests

- <actionable lower-priority outcome or delegation>

## Watches

- Watch: <waiting outcome>. Check <one signal>. Resume only when <condition>.

## Review queue

1. **<Critical|High|Medium|Low> — <request-level outcome>**: <PRs>. Why: <value and why it outranks the next item>. the user action: <controlled action>. Estimate: <total responsible effort>.

## Coverage

- Checked: <successful sources; list Codex and Claude separately>
- Review load: <Needs the user PR count and effort; highest-value unblockers; "X open bot PRs = Needs the user A + Waiting B + Excluded C + Origin unresolved D">
- Tasks: <created, moved, or retained filename slugs>
- Missing: <unavailable sources and failed cutoff update, or "none">
```

When GitHub succeeded, include every request-level `Needs the user` outcome in the
review queue, even when already selected above. Omit Waiting, Excluded, and
Origin unresolved items from the ordered queue while retaining their counts in
Coverage. Write `None.` when the queue is empty.

Keep the answer decisive and compact. Do not dump the backlog or invent work to
fill a section.
