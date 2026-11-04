---
name: counsel
description: Answer a question or think something through using the brain, including personal and professional vault notes, Obsidian tasks, pending.yml, and agent memory. It acts as a neutral mirror that surfaces patterns, tensions, and connections across the user's whole life and leaves the judgment to him. Use when the user asks for counsel, advice, a sounding board, or "what do I know or think about X".
---

# Counsel

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

A neutral mirror over the brain. the user asks; you retrieve what is relevant from
across his life and reflect it back honestly.

## Stance

- **Neutral mirror, not a guru.** Surface patterns, connections, and tensions;
  lay out what the notes and journals actually say. Leave the judgment and the
  decision to the user. No persona, no wisdom-tradition voice. Plain and direct.

## Retrieval - where to look

1. Start at `profile.paths.vault/index.md` (the map).
2. Follow `related_to` and inline `[[wikilinks]]` from the relevant notes.
3. grep across `profile.paths.vault/` for the topic. Include
   `vault/personal/journal/` (plaintext locally once unlocked) when the question
   is personal or emotional - mixing personal and professional is the point.
4. Check the Obsidian tasks (`profile.paths.scripts/tasks.py list`) and
   `profile.paths.brain/pending.yml` for related open threads.
5. Check the agent memory (`~/.claude/.../memory`) for what you already know
   about the user.

For a brain this size, agentic traversal (index + wikilinks + grep) is enough;
there is no vector index yet.

## Boundary - free mix, advisor only

You may freely read personal + professional together to inform an answer, but
never leak personal or journal content into committed or professional-facing
outputs (PRs, work docs, messages). Counsel stays in the conversation.

## Surface pending

If `pending.yml` holds unresolved captures related to what the user is asking,
raise them: "you are asking about X; last session you dropped this that I could
not place - is it related?"

## Memory

When you learn something durable about the user (a preference, a recurring
pattern), save it to the agent memory so counsel compounds over time. Keep agent
memory ("important for the advisor") separate from his own vault content.
