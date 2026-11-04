---
name: message
description: Tailor a message to post in a company Slack channel - natural, relaxed, professional, confident. Gathers context (Slack via codex, Linear and GitHub directly), suggests any actions to take first, then produces three distinct copy-paste variants for the user to pick from. Use for "draft a slack message", "help me post in #channel", "write a slack update for the team", "tailor this for slack". Do not use for reading or summarizing a channel (summarize-channel), or standups (standup).
user_invocable: true
allowed-tools: Bash(codex exec *), Bash(gh *), Read, Grep, Glob, mcp__linear-server__list_issues, mcp__linear-server__get_issue, mcp__linear-server__list_comments, mcp__linear-server__get_project
argument-hint: "[what you want to say + which channel/thread]"
---

# Message

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Turn a rough intent into a Slack message that sounds like the user: relaxed, human, confident, professional. Check the real context first, flag anything worth doing before posting, then hand over three distinct variants. **Never post.** the user posts himself.

Argument: `$ARGUMENTS` (the gist of what he wants to say, ideally with the target channel or thread).

## Step 1: Pin down the ask

From `$ARGUMENTS` and the conversation, establish:

- **What** he wants to communicate (the core point, in one line).
- **Where** it goes: which channel, or a reply inside an existing thread. If he did not say where, do not ask: assume Slack and format for it (see Formatting below), skipping the channel-specific context gathering.
- **Type**: announcement / heads-up / FYI / question to the team / status update / celebration / reply. This drives register and length.
- **Audience**: the whole company, engineering, a specific group. Who reads it changes how much context to include.

If any of these is genuinely unclear and you cannot infer it, ask. If it is reasonably inferable, infer it and say what you assumed.

## Step 2: Gather context

Pull from the sources that are clearly relevant. The goal is twofold: match the channel's tone, and **never claim something is done or true when it is not**.

- **Slack** (channel norms, thread history, what was already said, who is present). The Slack MCP is not authenticated in this environment, so read via codex:

  ```bash
  codex exec "Read the last N messages in the #<channel> Slack channel and summarize the tone and what has been discussed. If there is a thread at <link>, include its full contents."
  ```

  If codex returns nothing useful or cannot reach Slack, say so plainly and ask the user to paste the relevant thread.

- **Linear** (via the linear-server MCP): if the message references an issue (<PREFIX>-<number>), read it to confirm status, title, and scope before describing it.
- **GitHub** (via `gh`): if the message references a PR or deploy, confirm the real state (merged? checks green?) with `gh pr view` before saying it shipped.
- **The brain**: if the message is about the user's own recent work, check `profile.paths.logs/` or the vault so the description is accurate.

When something material is ambiguous and not cheaply verifiable, ask the user rather than guessing.

## Step 3: Suggest actions before posting

Surface anything worth doing first, as a short list. Do not perform outbound actions; just flag them. Typical items:

- **Verify a claim**: "You say the deploy is live. `gh` shows the PR merged but I can't confirm the deploy ran. Worth checking before you post."
- **Link something**: "This references <PREFIX>-<number> but has no link. Add it so people can click through."
- **Right place**: "This reads like #engineering, not #general."
- **Thread vs top-level**: "There's already a thread on this. A reply there keeps it in one place instead of a new top-level message."
- **Tag someone**: "You probably want to @ the person who owns this so they see it."
- **Timing**: "It's late for most of the team. `@here` now will ping people off-hours; consider dropping the `@here` or waiting."

If there's nothing worth flagging, say so in one line and move on. Keep this proportional; do not invent concerns.

## Step 4: Write three variants

Produce **three genuinely distinct** options, not three paraphrases. Vary them along a real axis, for example:

1. **Tight**: shortest version that still lands. Good default for a busy channel.
2. **Warm**: a touch more personable, a little context or a thank-you where it fits.
3. **Fuller**: more detail or reasoning, for when the audience needs the why.

Pick the axis that fits the message type. For a quick heads-up, three lengths. For an announcement, three framings. Label each so the user can choose fast.

### Voice

Sound like a real person who is relaxed and sure of themselves, not a corporate account.

- **Succinct, direct, relaxed.** That is his baseline register: he says what he means in few words without sounding stiff. Cut ideas until only the ones that matter remain, then let those flow.
- **Confident, not sheepish**; humble, not self-deprecating. State things plainly. No "sorry to bother", no "just wanted to quickly".
- **No dashes as connectors.** No em-dashes and no spaced hyphens joining clauses. Use commas, colons, periods, or parentheses. (Hyphens inside words like "end-to-end" are fine.)
- **Full sentences with pronouns.** No telegraphic fragments.
- **Written by a Brazilian for a US audience.** Avoid US-native idioms and slang; they read as AI-generated to the team. Plain, direct English.
- **Informal by default**, the way a colleague talks rather than the way a company writes. He should never have to ask for this.
- **Vocabulary depends on the language.** In English he is not a native: use words and expressions a non-native knows well, plain and common, never clever or idiomatic. In Portuguese he is fluent and well-read, so a richer, more natural vocabulary is fine.
- **Flowing sentences, not clipped ones.** Prefer longer sentences whose clauses connect with commas and conjunctions over short standalone ones: "we will rock you, then smash" instead of "we will rock you. Smash you." Keep the message short by cutting ideas, never by chopping sentences into fragments. See the counter-example below.
- **Cut corporate filler and hedging**: "circle back", "touch base", "just", "I think maybe", "wanted to reach out". Say the thing.
- **Emoji sparingly**, only where the channel already uses them and it adds warmth, not decoration.

### Formatting

**Deliver every variant already in Slack formatting, ready to paste with no conversion step.** Handing over plain markdown and leaving the user to translate it is a failure of this skill.

The syntax he uses:

- Bold is a *single* asterisk: `*bold*`, never `**bold**`.
- Italic is underscores: `_italic_`.
- Links use the markdown form: `[text](url)`. This is deliberate and replaces the older mrkdwn `<url|text>` style.
- There are no headings. Structure with short paragraphs instead.

Keep line breaks readable, and use a short bulleted list only when it genuinely helps scanning. Apply bold sparingly, to the two or three nouns a reader scans for (a tab name, a feature name), not for emphasis throughout. If in doubt about anything else, load the `slack-by-salesforce:slack-messaging` skill.

### Voice anchor (examples)

Real examples of the user's well-tailored messages, embedded here, are the strongest voice anchor. Until they are added, the rules above are the anchor.

**Counter-example, rejected by the user as "too AI" (2026-08-01):**

> Same state, two tabs, two numbers.

The staccato triad reads as generated even though it is compact and technically accurate. The pattern to avoid is any punchy fragment written for rhythm rather than to say something: three nouns in a row, a sentence with no verb, a line that exists to set up the next one. Say the thing in a full sentence instead: "Someone can update a Cost on one tab and see the old value on the other." This is the same rule as "full sentences with pronouns" above, and it is the one most likely to slip, because the fragment feels tighter while writing.

<!--
the user: paste 1-3 messages you consider well-tailored below, ideally a mix of types
(an announcement, a thread reply, a question). Note which landed well, and add one
counter-example (too stiff or too casual) to steer away from. Then this section
becomes the primary reference for Step 4.
-->

## Step 5: Hand off

Deliver the three variants as **bare text**: no blockquote wrapping, no "here is the message" preamble, no trailing commentary beyond the short labels. Each variant should be directly copyable.

Then, in a separate line outside the drafts, remind the user that nothing was posted and offer to tighten whichever one he leans toward. Do not post, and do not save a draft, unless he later explicitly asks and the Slack connector is authorized.

If the user asks for only one variant or says to send only the message, return exactly that message. Omit the variant label, the other versions, the posting reminder, and every sentence outside the copy-paste text.
