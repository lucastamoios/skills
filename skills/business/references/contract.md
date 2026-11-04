# Shared operating contract

This contract applies to all five business skills. Read it once per continuous
session and reuse it across transitions. Specialist skills depend on this shared
folder; install and preserve the five folders together.

## Evidence and decisions

Distinguish observed behavior, a person's statement, a hypothesis, a proposal, and
an accepted decision. Record the source and date for claims that influence a choice.
Keep negative and conflicting evidence visible. A missing answer is unknown, not
zero or failure. A simulated customer or AI critique is a rehearsal, not field evidence.

Assess evidence against the exact hypothesis. A signup may show interest; it does
not demonstrate payment, retention, delivery cost, or authority to buy. Interviews
can explain past behavior and constraints; hypothetical praise cannot establish
future purchasing behavior. Do not impose a universal ladder that ranks all usage
above every purchase or all interviews below every signup.

Use the user's current correction to update their stated context. Distinguish it
from an independently verified external rule. Dates, regulations, prices, platform
requirements, and market claims need current sources when they affect the advice.

## Delegate context retrieval

For this suite, delegate every web research task and every retrieval of additional
project context to a subagent. This includes Brain searches, competitor research,
reading interview archives, and checking project documents. Reading these skill
instructions, processing material already supplied in the conversation, and checking
a specific returned excerpt for a discrepancy can stay with the main agent.

The main agent should frame the question and send the researcher only the context
needed to answer it. Do not send personal journals, credentials, unrelated files,
or the full conversation by default. Respect the user's project and privacy boundaries.

Give each researcher a bounded brief:

- State the decision that the research informs and the exact question to answer.
- Supply relevant known facts, source paths or links, and the freshness needed.
- Set the scope, allowed tools, and read-only boundary. Ask for evidence that could
  disconfirm the idea as well as support it.
- Request a concise answer with source URLs or file locations, source dates,
  observations, interpretations, disagreements, unknowns, and a stopping condition.

Parallelize independent questions only when useful. Do not create several agents
for the same lookup or recursively delegate by default. Use the session's available
subagent tools; an ordinary browser search is not itself a subagent. If the calling
agent cannot spawn children, send the research need back to its orchestrator. If
no delegation capability exists, disclose that limitation and continue with supplied
context. If direct research tools are available, ask whether direct research is
acceptable before replacing the agreed delegation behavior. If those tools are also
unavailable, explain the missing evidence without asking permission for an impossible
action. Do not invent a research result or silently skip necessary evidence.

The manager checks whether returned sources actually answer the question. It
reconciles disagreements and presents only what changes the decision, with citations
near the relevant claims. It asks for a targeted follow-up when evidence is missing.
The specialist uses this same contract when invoked without the manager.

## Respect the business and the user's authority

Account for the model actually being considered: service, product, partnership,
or public procurement. For public-sector work, distinguish the beneficiary, operator,
budget holder, decision maker, contracting process, and supplier economics. Do not
replace formal acceptance or procurement conditions with a generic startup funnel.
Delegate verification of legal or platform requirements instead of declaring them
from memory. Do not provide a legal conclusion based on a business framework.

Recommend a next move; do not promise that it is objectively the right one. Explain
tradeoffs once and respect the user's judgment. Do not transfer a source author's
personality, portfolio, audience, geography, or business preferences to the user.

Drafting a test does not authorize contacting prospects, publishing pages, taking
payments, buying ads, scheduling automation, or changing a production system.
Carry out those actions only within the user's actual authorization. Follow the
workspace's separate messaging, SSH, commit, and vault rules.

## Preserve continuity

Keep the project state available to the next specialist. Do not make the user repeat
the context or choose the skill for you. Preserve partial progress when interrupted.
For durable notes, follow [working-note.md](working-note.md). Read only the relevant
foundation and source sections; do not load the whole library on every transition.
