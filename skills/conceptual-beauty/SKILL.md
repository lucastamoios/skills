---
name: conceptual-beauty
description: Analyze or redesign the conceptual beauty of software, code, or domain models through integritas, consonantia, and claritas. Use for explicit conceptual-beauty requests or when the user asks whether a system's concepts form a coherent, proportionate, intelligible whole. Do not use for ordinary code review that does not examine the conceptual model.
---

# Conceptual Beauty Orchestrator

## Role

Coordinate conceptual analysis without carrying the full theory inside the orchestration layer. Use the six sibling specialist skills as separate analytical units. Read each selected specialist's `SKILL.md` completely before applying it.

## Inputs

- Current concept or system node.
- Known parent context.
- Optional existing child concepts.
- Current goal: understand, critique, redesign, or compare.

## Invariants

- Never expand the entire concept DAG before analyzing the upper levels.
- Prefer one level of expansion; allow two when the relation is obvious and low-risk.
- Treat the DAG as conceptual containment/meaning structure, not a call graph.
- Do not force integritas, consonantia, and claritas into isolated phases. Cycle among them.
- Spend most analytical effort on Core Domain concepts, less on Supporting, and avoid reinventing Generic concepts unless their boundary with the core is the problem.

## Procedure

1. State the current node and its conceptual level.
2. Read and apply [Domain Classification](../conceptual-beauty-domain/SKILL.md) for the relevant subdomain.
3. Read and apply [Concept DAG Mapping](../conceptual-beauty-dag/SKILL.md) to expose only the next one or two levels.
4. Decide which lens has the highest expected value first:
   - Read and apply [Integritas](../conceptual-beauty-integritas/SKILL.md) when the division itself is uncertain.
   - Read and apply [Consonantia](../conceptual-beauty-consonantia/SKILL.md) when parts exist but boundaries, weight, or interfaces feel wrong.
   - Read and apply [Claritas](../conceptual-beauty-claritas/SKILL.md) when the model is hard to name, explain, or hold in working memory.
5. Read and apply other lens skills as tensions appear. Do not flatten their distinct criteria into a generic checklist.
6. Read and apply [Synthesis](../conceptual-beauty-synthesis/SKILL.md).
7. Choose one action: revise current division, stabilize current level, descend one level, or stop.

## Output contract

Return:

- Current node and level.
- Domain classification.
- Immediate children currently under consideration.
- Main findings by lens.
- Open tensions.
- Next action and permitted depth of expansion.

The orchestrator should remain small. If it starts containing detailed rules from a lens, move those rules back into the relevant skill.
