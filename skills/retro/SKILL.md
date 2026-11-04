---
name: retro
description: Review a requested session for durable project knowledge and evidence-backed improvements to skills, tools, checks, and agent instructions. Use only when the user explicitly asks for a retrospective or session distillation.
disable-model-invocation: true
---

# Retro

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Review the current session, or the session the user selects, and propose what should improve the next run. Combine durable project knowledge capture with improvements to the agent environment. Run only on explicit request. A suggestion, session ending, compaction, or invocation of another skill does not authorize a retro.

## Read the evidence

Use the current conversation by default. For a named past session, read its Codex or Claude transcript, including relevant tool results and corrections. Locate a specific session before reading logs; do not scan unrelated history. State when evidence is incomplete and do not reconstruct missing events as facts.

Look for durable decisions, architecture, component responsibilities, operational gotchas, outdated documentation, repeated corrections, missed instructions, excessive discovery, failed tools, and review omissions. Each candidate must cite a concrete turn, tool result, transcript location, or verified file span. A smooth session may yield knowledge without workflow findings. Return no candidates when neither is supported; do not fill categories with generic advice.

Keep verified facts, decisions, hypotheses, and unverified outcomes distinct. Do not turn one incident into a universal rule. Exclude credentials, transient runtime state, obvious code details, and abandoned debugging paths unless they reveal a reusable cause. Do not load personal journals for work retrospectives.

## Find the smallest useful change

Read the relevant knowledge index and existing instructions before proposing changes. Verify whether the guidance or check already exists and whether the agent could discover or execute it. If it exists, repair the connection or execution gap rather than duplicating it.

| Evidence | Preferred destination |
|---|---|
| Durable architecture, decision and rationale, component contract, or operational gotcha | Update the existing project knowledge note, or create one focused note. |
| An existing note is contradicted by verified session work | Correct or remove the outdated statement. |
| A skill's workflow, trigger, reference, or tool choice caused friction | Update that skill's canonical source. |
| A mechanical violation could have been detected | Connect an existing check, or propose a deterministic check with a concrete failure case. |
| A contextual judgment was missed | Add concise guidance to the skill or standards the responsible agent reads. |
| Discovery was unnecessarily expensive | Add a navigation pointer at the relevant entry point. |
| A tool lacked useful output or access | Propose a scoped tool improvement or access change. |
| Instructions duplicate, conflict with, or no longer serve the workflow | Propose consolidation, correction, or removal with evidence of their purpose. |

Choose guidance for the agent that needs it, whether implementer, reviewer, or coordinator. Do not force all standards into review or add every lesson to `AGENTS.md`. Preserve authorization boundaries. A permission denial alone does not justify broader access.

In Brain, shared skills live in `profile.paths.skills/`; edit their canonical source rather than installed copies. Plugin skills may have a different canonical source. Verify it before editing.

For project knowledge, use the established documentation home. In Brain, read `vault/index.md` and the relevant note; follow `vault/AGENTS.md` before editing the vault. A code repository may use `docs/` or a documented Brain destination. Respect that destination and its local instructions. Keep working plans separate from durable knowledge; do not graduate or delete planning artifacts without authorization.

## Present the candidates

Present one decision table with stable candidate IDs, type (knowledge or environment), evidence, impact, exact target file, and proposed change. Order by likely recurrence and consequence, and disclose uncertainty. For each environment change, explain how to verify that it improves the observed failure without obstructing valid work. Identify actionable knowledge even when the environment needs no changes.

Wait for the user to select candidates before writing. If his request already selects specific changes and authorizes applying them, apply only those changes without asking again. A request to run retro alone authorizes analysis and proposals. It does not authorize edits, external messages, access changes, commits, or memory writes.

Keep memory separate from project documentation. Write agent memory only when the user explicitly requests a memory update, following the active memory instructions.

## Apply the selected changes

Apply the smallest coherent change to each selected target. Preserve unrelated edits. For knowledge notes, record what is true and why the decision was made, use one focused topic per note, and update the relevant index or hub using its existing conventions. Do not rebuild the whole vault index or rewrite unrelated notes. Use Mermaid when a diagram is useful.

For skills, use the available skill-creator guidance and validate each changed skill. Synchronize only the affected installed skills where needed. For a new check, verify that it catches the demonstrated failure and accepts representative valid behavior before enabling it. Do not install hooks or modify CI beyond the selected scope.

Verify the changed links and references, remove duplicate guidance within the selected scope, and report the files changed and validation results. Preserve any remaining blockers or uncertain claims. Do not claim the next session improved until subsequent use demonstrates it.
