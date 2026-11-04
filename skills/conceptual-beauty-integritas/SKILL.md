---
name: conceptual-beauty-integritas
description: Test a software or domain concept for wholeness and a coherent fundamentum divisionis. Use within the conceptual-beauty workflow or directly when the requested lens is integritas, conceptual completeness, or the principle of division.
---

# Integritas

This specialist can be used by the `conceptual-beauty` orchestrator or independently when the user requests this specific lens.

## Role

Test whether a concept is whole and whether its parts arise from a coherent principle of division.

## Central idea

Integritas is not merely "nothing important is missing." It also asks whether the decomposition has formal unity. The strongest diagnostic is the fundamentum divisionis: the principle according to which the whole is divided into parts.

## Questions

- What is the principle of division here?
- Is there one principle, or are several unrelated criteria mixed together?
- Do all proposed parts genuinely arise from that principle?
- Are sibling concepts at comparable logical levels?
- Is anything essential missing under the chosen principle?
- Is anything included that belongs to another division entirely?
- Could the same whole be divided differently under a different valid principle? If so, which division is useful for the present purpose?

## Failure modes

### Mixed fundamentum divisionis

Example pattern: one child is a component, another is an actor, another is a workflow, another is an implementation detail. The list may be useful operationally but lacks formal unity.

### Accidental completeness

The list feels comprehensive because it is long or familiar, not because the division closes under a known principle.

### Premature ontology

A convenient implementation split is mistaken for the nature of the domain.

### Missing essential part

Given the chosen division principle, one sibling required to complete the division is absent.

## Code application

At code level, inspect modules, services, functions, types, and packages according to the conceptual level currently under analysis. Ask whether a module contains one coherent concept or a bag of responsibilities collected by convenience.

## Output contract

Return:

- proposed fundamentum divisionis;
- whether it is single, mixed, or unclear;
- missing parts;
- alien/extraneous parts;
- alternative division principles worth considering;
- recommended revision of the current node.
