# Skill catalog

The installer registers 80 commands. Use `$name` in Codex or `/name` in Claude Code. Start with the main entrypoint for a workflow; worker procedures may require a prepared input packet, connected tools or a model policy.

Standalone plugin aliases keep their original protocol identifiers. See [command-map.json](command-map.json) for the mapping.

## Engineering

| Command | What it helps with |
| --- | --- |
| [dev](skills/dev/SKILL.md) | Coordinate the selected development stages as separate agents with explicit file inputs, exclusive outputs, configured models, and serial dependencies. |
| [take](skills/take/SKILL.md) | Pick up a specified ticket or piece of work by understanding its context, explaining what should change and why, and preparing Product clarification before requirements. |
| [requirements](skills/requirements/SKILL.md) | Capture testable user requirements and BDD scenarios for a feature area. |
| [design-spec](skills/design-spec/SKILL.md) | Capture technical design decisions traced to user requirements. |
| [plan](skills/plan/SKILL.md) | Create an implementation plan with tasks and verification traced to requirements and design decisions. |
| [mini-plan](skills/mini-plan/SKILL.md) | Plan a small, bounded change through a short clarification round and one document combining requirements, concrete design decisions, execution steps, and verification. |
| [create-issues](skills/create-issues/SKILL.md) | Split requirements, design specs, and plans into self-contained issues organized as independently verifiable outcomes. |
| [next-issue](skills/next-issue/SKILL.md) | Pick the next unblocked issue assigned to the configured user, prepare its branch and worktree, and load the context needed to start. |
| [code-tdd](skills/code-tdd/SKILL.md) | Implement an assigned development milestone with outside-in test-driven development from a prepared input and output contract. |
| [fix](skills/fix/SKILL.md) | Use when a bug is reported from any source - Sentry alert, Linear issue, pasted stacktrace, or plain description. |
| [implement-review](skills/implement-review/SKILL.md) | Evaluate explicit review findings and implement authorized corrections from a prepared development input and output contract. |
| [create-pr](skills/create-pr/SKILL.md) | Create or update a GitHub PR for the current branch. |
| [record-pr](skills/record-pr/SKILL.md) | Record reviewer-facing media for a PR using Playwright. |
| [explain](skills/explain/SKILL.md) | Explain a pull request, branch, commit range, or current diff as an interactive top-down walkthrough, a short overview and part map first, then one part at a time, pausing for questions. |
| [explain-pr](skills/explain-pr/SKILL.md) | Write or update a structured pull request explanation for a configured local reader service, following its contract and current PR head. |
| [business-rules](skills/business-rules/SKILL.md) | Extract the business rules behind an issue, pull request or code change, using concrete examples from the target project before explaining the general rule. |
| [tech-debt](skills/tech-debt/SKILL.md) | Scan a codebase for technical debt - outdated deps, test gaps, code churn hotspots, TODO/HACK markers, recurring Sentry errors, and missing Linear tickets. |
| [nuke-review](skills/nuke-review/SKILL.md) | Run an extremely strict maintainability review for abstraction quality, giant files, and spaghetti-condition growth. |
| [context7-mcp](skills/context7-mcp/SKILL.md) | This skill should be used when the user asks about libraries, frameworks, API references, or needs code examples. |

## Concepts and design

| Command | What it helps with |
| --- | --- |
| [concept-review](skills/concept-review/SKILL.md) | Review code abstractions for conceptual correctness, completeness, and simplicity. |
| [concept-review-docs](skills/concept-review-docs/SKILL.md) | Review requirements and design specs for conceptual correctness. |
| [conceptual-beauty](skills/conceptual-beauty/SKILL.md) | Analyze or redesign the conceptual beauty of software, code, or domain models through integritas, consonantia, and claritas. |
| [conceptual-beauty-claritas](skills/conceptual-beauty-claritas/SKILL.md) | Test whether a software or domain concept manifests its form through precise names, honest boundaries, coherent cuts, and manageable cognitive load. |
| [conceptual-beauty-consonantia](skills/conceptual-beauty-consonantia/SKILL.md) | Test whether parts, boundaries, interfaces, and conceptual weight stand in due proportion within a software or domain model. |
| [conceptual-beauty-dag](skills/conceptual-beauty-dag/SKILL.md) | Map a software or domain model as a progressively expanded DAG of conceptual containment, specialization, and dependence of meaning. |
| [conceptual-beauty-domain](skills/conceptual-beauty-domain/SKILL.md) | Classify a problem-space subdomain as Core, Supporting, or Generic to set the depth of a conceptual-beauty analysis. |
| [conceptual-beauty-integritas](skills/conceptual-beauty-integritas/SKILL.md) | Test a software or domain concept for wholeness and a coherent fundamentum divisionis. |
| [conceptual-beauty-synthesis](skills/conceptual-beauty-synthesis/SKILL.md) | Synthesize domain classification, a partial concept DAG, and integritas, consonantia, and claritas findings into the next structural decision. |

## Knowledge, notes and attention

| Command | What it helps with |
| --- | --- |
| [brainstorm](skills/brainstorm/SKILL.md) | Explore rough ideas, hunches, and open questions, then use selective structured reasoning when a concrete decision emerges. |
| [conversation](skills/conversation/SKILL.md) | Turn a pasted conversation or noisy multi-speaker transcript into proposed actions on the current work, future tasks, and knowledge updates, plus a list of the specialized, non-trivial. |
| [counsel](skills/counsel/SKILL.md) | Answer a question or think something through using the brain, including personal and professional vault notes, Obsidian tasks, pending.yml, and agent memory. |
| [docs-update](skills/docs-update/SKILL.md) | Refresh the project's docs in three places, all keyed on per-folder SHAs that record what was last reconciled. |
| [gardener](skills/gardener/SKILL.md) | Tend the brain's knowledge as the orchestrator for the gardener family. |
| [gardener-audit](skills/gardener-audit/SKILL.md) | Audit a documentation folder for inconsistencies and produce a report with suggested fixes - never edits the docs. |
| [gardener-board](skills/gardener-board/SKILL.md) | Reconcile the configured task board with shipped outcomes, using pull requests, issue state and recent sessions. |
| [gardener-inbox](skills/gardener-inbox/SKILL.md) | Process the configured capture inbox into private notes, tasks and proposed follow-ups. |
| [gardener-prune](skills/gardener-prune/SKILL.md) | Reduce a documentation folder to the minimum tokens a future agent needs, without losing knowledge, and leave it better connected and convention-clean. |
| [gardener-transcripts](skills/gardener-transcripts/SKILL.md) | Mine the raw Claude Code session transcripts for meta-signals the in-session capture misses - repeated corrections, recurring worries, orphaned knowledge, recurring questions, friction,. |
| [meeting](skills/meeting/SKILL.md) | Prepare concise, Slack-ready briefs for standups, weekly updates, one-on-ones, project reviews, and other work meetings. |
| [meeting-distill](skills/meeting-distill/SKILL.md) | Extract long-term knowledge from a meeting transcript and persist it into docs/. |
| [priorities](skills/priorities/SKILL.md) | Choose the user's highest-value work from configured work, review, personal and task sources. |
| [retro](skills/retro/SKILL.md) | Review a requested session for durable project knowledge and evidence-backed improvements to skills, tools, checks, and agent instructions. |
| [session-log](skills/session-log/SKILL.md) | Capture completed session activity into the configured private daily log, using the user’s timezone. |
| [start](skills/start/SKILL.md) | Start or reconcile a focused work session using configured private task notes. |
| [stop](skills/stop/SKILL.md) | Stop and reconcile the active Obsidian task note. |
| [study](skills/study/SKILL.md) | Guide interactive learning by discovering what the user already understands and connecting new ideas to it, one small step at a time. |
| [sync](skills/sync/SKILL.md) | Synchronize the configured context repository with its upstream and run its optional setup integration. |

## Business

| Command | What it helps with |
| --- | --- |
| [business](skills/business/SKILL.md) | Guide a continuous conversation about a business idea or product, recommend the next useful step, and coordinate exploration, offer design, experiments, and evidence review. |
| [business-explore](skills/business-explore/SKILL.md) | Explore a business idea, customer problem, or possible direction and identify the most consequential uncertainty. |
| [business-offer](skills/business-offer/SKILL.md) | Shape a testable business offer by clarifying the customer, outcome, alternatives, differentiation, delivery scope, buying process, channel, and price hypothesis. |
| [business-experiment](skills/business-experiment/SKILL.md) | Turn a consequential business uncertainty into a practical experiment with observable evidence, a predeclared decision criterion, and bounded effort. |
| [business-review](skills/business-review/SKILL.md) | Interpret business evidence from interviews, sales attempts, pilots, experiments, or product use and recommend whether to continue, adjust, investigate, or stop a hypothesis. |

## Review workers

| Command | What it helps with |
| --- | --- |
| [review-code](skills/review-code/SKILL.md) | Find high-confidence correctness, security, contract, concurrency, and error-path defects in a declared change. |
| [review-consolidate](skills/review-consolidate/SKILL.md) | Consolidate completed review evidence or prepare editable PR comments from it. |
| [review-dead-code](skills/review-dead-code/SKILL.md) | Assess dead-code candidates using runtime reachability and concrete planned consumers. |
| [review-intent](skills/review-intent/SKILL.md) | Compare a change with explicit product requirements and acceptance criteria. |
| [review-map](skills/review-map/SKILL.md) | Build an interactive architecture map for a PR, branch or local diff. |
| [review-paths](skills/review-paths/SKILL.md) | Map changed production entrypoints, state, decisions, and basis scenarios into an independent evidence file for later review and QA. |
| [review-qa](skills/review-qa/SKILL.md) | Prepare an isolated Docker environment, exercise changed UI with Playwright, and execute mapped and exploratory QA scenarios. |
| [review-risk](skills/review-risk/SKILL.md) | Trace changed production boundaries to real consumers, deployment failure modes, monitoring signals, and rollback limits. |
| [review-run](skills/review-run/SKILL.md) | Coordinate review lenses as independent agents with explicit file contracts and models. |
| [review-tests](skills/review-tests/SKILL.md) | Assess whether tests protect changed business behavior, detect plausible regressions, and remain reliable. |
| [review-verify](skills/review-verify/SKILL.md) | Independently check review findings against the declared code snapshot and primary sources. |
| [review-walkthrough](skills/review-walkthrough/SKILL.md) | Explain a reviewed change by connecting its explicit requirements to implementation evidence, then trace one concrete case through the code interactively. |

## Marketing workers

| Command | What it helps with |
| --- | --- |
| [marketing-angle](skills/marketing-angle/SKILL.md) | Turn a creator's concrete case into video angles that say why the viewer should care, as structured JSON. |
| [marketing-ask](skills/marketing-ask/SKILL.md) | Generate questions that pull a concrete, filmable case out of a creator (scene, numbers, before and after, mistake, decision) instead of opinions, as structured JSON. |
| [marketing-critique](skills/marketing-critique/SKILL.md) | Judge a short-video script the way the content expert does and return a structured verdict (approve, revise, rethink), per-criterion scores, beat-level issues with concrete fixes, what. |
| [marketing-culto](skills/marketing-culto/SKILL.md) | Interview a creator one question at a time to build the personal brand document (culto), the data every other marketing skill needs, and a graded format profile, as structured JSON. |
| [marketing-offer](skills/marketing-offer/SKILL.md) | Build a creator's offer as structured JSON with a One Belief and answers to the 10 offer questions (difference, why care, how true, problem mechanism, enemy, why now, why trust, solution. |
| [marketing-reference](skills/marketing-reference/SKILL.md) | Explain why a short video that performed well worked, as structured JSON. |
| [marketing-run](skills/marketing-run/SKILL.md) | Single entry point for short-video work. |
| [marketing-script](skills/marketing-script/SKILL.md) | Write or revise a short-video script (Reels, Shorts, TikTok) beat by beat as structured JSON, with exact lines, visuals, timing, CTA, sourced claims, and preparation. |

## Other tools

| Command | What it helps with |
| --- | --- |
| [skill-config](skills/skill-config/SKILL.md) | Configure a private user profile for shared skills, or resolve the profile, project context and optional integrations used by an installed skill. |
| [auto-rename](skills/auto-rename/SKILL.md) | Rename the current Codex task with an emoji-prefixed work status and a concise outcome title. |
| [brand](skills/brand/SKILL.md) | Find canonical company, product, or personal-site marks and prepare them as transparent, consistently sized PNG icons for 1Password or similar icon collections. |
| [escriva](skills/escriva/SKILL.md) | Responde a uma pergunta ou desabafo espiritual no tom de São Josemaría Escrivá, baseado nos seus próprios escritos via RAG local. |
| [folha-ponto](skills/folha-ponto/SKILL.md) | Busca registros de acesso no BRCondos, interpreta eventos ControlId, calcula horas extras de empregada domestica e gera resumo para WhatsApp e folha de ponto em PDF. |
| [meme](skills/meme/SKILL.md) | Brainstorm meme ideas and render a chosen template with captions using memegen.link. |
| [message](skills/message/SKILL.md) | Tailor a message to post in a company Slack channel - natural, relaxed, professional, confident. |
| [transcript-clean](skills/transcript-clean/SKILL.md) | Clean and reconstruct noisy meeting transcripts into publication-ready conversational prose while preserving every substantive turn, the speaker's voice, and the source chronology. |

## Configuration and dependencies

`skill-config` handles personal defaults, paths and optional integrations. Development and independent review require model assignments supplied by the user. Account integrations require the user’s own access. `auto-rename` needs supported chat-management tools; `escriva` needs a configured RAG service; `folha-ponto` uses the configured access-history provider. Installing the collection does not grant access to those resources.
