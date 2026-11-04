---
name: conceptual-beauty-dag
description: Map a software or domain model as a progressively expanded DAG of conceptual containment, specialization, and dependence of meaning. Use within the conceptual-beauty workflow or directly for a partial concept DAG. Do not substitute code calls, imports, or runtime dependencies for conceptual edges.
---

# Concept DAG Mapping

This specialist can be used by the `conceptual-beauty` orchestrator or independently when the user requests this specific mapping.

## Role

Map the conceptual structure of a system without prematurely expanding it to maximum depth.

## Model

Represent concepts as a directed acyclic graph from more general to more specific. Edges express conceptual containment, specialization, or dependence of meaning. They do not merely mirror code calls, package imports, or runtime dependencies.

A concept may participate in more than one higher-level concept, so the structure is not necessarily a tree. Cycles are a warning that levels or meanings may be confused.

## Progressive expansion rule

- Start from the current node.
- Expose one level below it by default.
- Expose a second level only when doing so clarifies the first without committing to deep design.
- Analyze and revise before descending further.
- Never treat the first decomposition as final.

## Procedure

1. Name the current node in business/conceptual language.
2. State what the node includes and excludes.
3. Propose immediate child concepts.
4. For each edge, state why the child belongs under or depends conceptually on the parent.
5. Check whether children sit at comparable abstraction levels.
6. Flag cross-cutting/shared concepts rather than forcing them into one branch.
7. Stop expansion and invoke the beauty lenses before going deeper.

## Questions

- Are these children really children, or are some examples, implementation details, actors, operations, or qualities?
- Are we mixing levels of abstraction?
- Would another fundamentum divisionis produce a cleaner set of children?
- Does a node appear in multiple places because it is genuinely shared, or because the decomposition is confused?
- Is any apparent cycle conceptual, or merely a runtime collaboration that should not appear in this DAG?

## Output contract

Return a compact partial DAG containing:

- current node;
- parent context, if known;
- immediate children;
- optional grandchildren only when justified;
- edge rationale;
- unresolved alternative decompositions;
- explicit stop point for this iteration.
