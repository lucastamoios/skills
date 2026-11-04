---
name: mini-plan
description: Plan a small, bounded change through a short clarification round and one document combining requirements, concrete design decisions, execution steps, and verification. Use for lightweight planning of a small feature, fix, script, configuration change, or new skill. Stop at the plan unless the user explicitly requests execution.
---

# Mini-plan

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Turn a small request into one actionable plan. Keep enough detail that another
agent can execute it without inventing product behavior or material design
choices. Match the user's language.

## Clarify briefly

Offer mini-plan by default only when a new task has meaningful scope or design
choices. Execute simple, well-defined tasks directly without offering or applying
mini-plan, unless the user explicitly asks for planning. Examples include updating
a branch with main, straightforward renames, and small mechanical edits with clear
scope. A task being small is not, by itself, a reason to require a plan.

When offered as the default planning choice for a new task, ask once:
“Quer usar o mini-plan antes de executar esta tarefa?” Offer “Sim, planejar
primeiro” and “Não, executar direto”, then wait for the answer before execution.
Keep the choice for that task across follow-ups and corrections. An explicit
request to use mini-plan, skip planning, or use another workflow already answers
the question. Ordinary conversation and informational questions do not trigger it.
If the user chooses mini-plan, prepare the plan and stop there; the original
execution request does not bypass this deliberate planning pause. Resume execution
when the user subsequently asks. If the user declines, continue the original task.

Read relevant project instructions and the minimum existing context needed to
identify affected files, conventions, and constraints. Reuse information already
provided. Do not launch the requirements, design-spec, or plan pipeline.

Before closing the plan, ask a short batch of questions about material gaps.
Aim for one round of one to three questions, with a recommended option where
useful. Ask about behavior, scope, implementation choices, and success criteria
together when they matter. Do not ask the user to supply facts you can inspect.
If the request already settles those choices, skip redundant questions.

Wait for answers to material questions. Continue independent inspection while
waiting. Ask a follow-up only if an answer exposes a new material gap. State
minor assumptions instead of turning routine choices into approval gates.

If the work contains independent initiatives or unresolved architectural risks,
explain the concrete reason and recommend narrowing the slice or using the full
planning workflow. Do not silently expand this skill into that workflow.

## Write one plan

Use the project's established planning documentation location, including a
component tree where applicable. Otherwise use `profile.paths.docs/<project>/plans/`.
Resolve the project from its repository, not its worktree name. Record a new
fallback documentation root in its `AGENTS.md`. Reuse an existing plan for the
same scope and update an existing index when the project has one. Do not create
separate requirements, design, BDD, or traceability documents for this flow.
Follow an explicit user request for a chat-only plan instead of writing a file.

Use this compact structure, adapting headings to the user's language:

1. **Goal and boundaries.** State the outcome and only the exclusions needed to
   prevent likely scope confusion.
2. **Requirements and decisions.** Use a short table with observable requirements,
   concrete implementation decisions, and verification. Put each requirement's
   definition beside it. Explain trade-offs only where a real choice matters.
3. **Execution.** Give a short ordered checklist, usually three to six steps.
   Name the exact affected files or artifacts, what changes, and the expected
   result. Include commands or small snippets when they remove ambiguity.
4. **Done when.** State the observable acceptance criteria and any unresolved
   blocker. Label a blocked plan as a draft instead of inventing a decision.

Aim for a document that can be read in a few minutes. Do not require full code
listings, separate decision IDs, or a fixed number of requirements. Verification
may be a focused existing test, a manual example, or artifact inspection,
depending on the change. Do not add tests that only mirror file contents.

Review once for missing behavior, contradictory decisions, unverified paths,
and steps that leave material choices to the implementer. Ensure every
requirement has both an implementation step and a way to verify it.

## Finish at the plan

Return the plan's location and a short account of the settled decisions.
Do not implement, commit, create tickets, or invoke an implementation skill
merely because the plan is ready. Execute only when the user explicitly asks;
an existing request to plan and implement is sufficient. A request for a plan
about creating something, by itself, is not execution authorization.

When execution is requested, use this same document as its specification and
update its checklist with verified results. Do not recreate the larger planning
pipeline. Keep any required execution permissions in force.
