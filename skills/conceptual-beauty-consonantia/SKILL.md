---
name: conceptual-beauty-consonantia
description: Test whether parts, boundaries, interfaces, and conceptual weight stand in due proportion within a software or domain model. Use within the conceptual-beauty workflow or directly when the requested lens is consonantia, proportionality, fusion, or fragmentation.
---

# Consonantia

This specialist can be used by the `conceptual-beauty` orchestrator or independently when the user requests this specific lens.

## Role

Test whether the parts of a concept or system stand in due proportion to one another and to the whole.

## Central idea

Consonantia is not mere symmetry. It is debita proportio: the right proportion according to the nature and purpose of the whole.

Harmony presupposes distinction. Parts must be sufficiently separable to stand in intelligible relation. But excessive isolation destroys organic unity. The aim is distinctness without fragmentation.

## Questions

- What relations between the parts matter here?
- Is any part carrying too much conceptual weight?
- Is any part underdeveloped relative to its importance?
- Are boundaries clear enough that the parts can be compared and related?
- Are responsibilities proportional to the concept represented?
- Does internal complexity leak across the boundary?
- Is the interface smaller and simpler than the implementation it hides?
- If an interface grows large, is that because the concept is genuinely broad or because several concepts have been fused together?

## Conceptual weight

Weight means structural burden, not mere size. A concept has high weight when removing or changing it causes much of the model to collapse or when many other concepts depend on it for meaning.

A useful diagnostic:

- How much conceptual work should this part carry?
- How much does it actually carry?

A mismatch indicates disproportion.

## Interfaces

A complex module may legitimately have rich internals, but its surface should remain as small, stable, and expressive as the concept permits. Complexity should be absorbed, not exported by default.

## Failure modes

- God concepts that become the semantic center of everything.
- Interfaces whose complexity mirrors internal implementation complexity.
- Artificially tiny modules whose boundaries create more coupling than clarity.
- Concepts so entangled that they cannot be named or reasoned about independently.
- Excessive fragmentation where every minor distinction becomes a separate abstraction.

## Output contract

Return:

- parts and their relative conceptual weight;
- boundary quality;
- interface proportionality;
- overgrown or underdeveloped concepts;
- signs of fusion or fragmentation;
- recommended rebalancing.
