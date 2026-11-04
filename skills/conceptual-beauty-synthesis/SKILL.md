---
name: conceptual-beauty-synthesis
description: Synthesize domain classification, a partial concept DAG, and integritas, consonantia, and claritas findings into the next structural decision. Use within the conceptual-beauty workflow or directly when those findings already exist and must be ranked and consolidated.
---

# Synthesis

This specialist can be used by the `conceptual-beauty` orchestrator or independently when the user already has the required inputs.

## Role

Consolidate the current iteration and decide whether the model is stable enough to descend further.

## Inputs

- Partial concept DAG for the current level.
- Domain classification.
- Findings from integritas, consonantia, and claritas.

## Procedure

1. Summarize the current decomposition in one compact statement.
2. Collect tensions found by each lens.
3. Identify cross-lens symptoms. Example: a vague name may be caused by a mixed fundamentum divisionis; an oversized interface may reveal fused concepts rather than a pure interface problem.
4. Distinguish defects from legitimate complexity.
5. Rank issues by structural impact. Fix problems near the root before local polish.
6. Decide whether to revise the current division, adjust boundaries, rename/regroup, stabilize, or descend.
7. If descending, specify exactly which child node(s) and at most how many levels may be expanded next.

## Stability criteria

A level is stable enough to descend when:

- the principle of division is explicit and reasonably coherent;
- sibling concepts are at compatible levels of abstraction;
- boundaries and interfaces are understandable and proportionate;
- names reveal the intended concepts with tolerable ambiguity;
- no known high-impact contradiction is being deferred downward.

Stability does not mean finality. Later discoveries may force upward revision.

## Output contract

Return:

- Current model.
- Integritas findings.
- Consonantia findings.
- Claritas findings.
- Cross-lens diagnosis.
- Structural issues ordered by impact.
- Decision: revise, stabilize, descend, or stop.
- Next node(s) and maximum next depth.
