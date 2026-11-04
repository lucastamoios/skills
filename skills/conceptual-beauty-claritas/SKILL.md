---
name: conceptual-beauty-claritas
description: Test whether a software or domain concept manifests its form through precise names, honest boundaries, coherent cuts, and manageable cognitive load. Use within the conceptual-beauty workflow or directly when the requested lens is claritas or conceptual intelligibility.
---

# Claritas

This specialist can be used by the `conceptual-beauty` orchestrator or independently when the user requests this specific lens.

## Role

Test whether the form of a concept is intelligibly manifested: whether one can see what the thing is, where its boundaries lie, and why its name fits.

## Central idea

Claritas is not mere brevity or superficial simplicity. It is the intelligible manifestation of form. A concept may be deep and still be clear.

Names matter because a good name reveals the concept rather than merely describing an implementation accident. Decomposition matters because names become precise only when the things being named have real conceptual unity.

## Questions

- Can the concept be named precisely without a sentence full of qualifications?
- Does the name say what the thing is, or merely what its current implementation does?
- Does the division correspond to real units of meaning, or merely convenient code sizes?
- How many hidden facts must be held in working memory to understand this unit?
- Does the public surface reveal intention, or require archaeology through implementation details?
- Is apparent simplicity honest, or is complexity merely hidden behind vague names?
- Are two different concepts sharing one name, or one concept fragmented across several names?

## Naming

Prefer names grounded in the ubiquitous language of the domain. Rename only after understanding the concept. A bad name is often a symptom of a bad cut, not merely a vocabulary problem.

## Size and decomposition

Smaller functions or modules can improve clarity, but smallness is not a goal in itself. Divide when a smaller unit corresponds to a coherent unit of meaning. Fragmentation can reduce claritas by making the reader reconstruct the whole from scattered pieces.

## Cognitive load

A useful proxy for claritas is the amount of state, context, or hidden convention that must be mentally loaded at once. Reduce accidental cognitive load while preserving the real complexity of the domain.

## Failure modes

- Vague names such as Manager, Helper, Processor, Utils, Data, or Service where a domain name exists.
- Names that encode implementation rather than meaning.
- Functions split mechanically without conceptual boundaries.
- Hidden temporal coupling or implicit state that makes local code deceptive.
- Abstractions whose names promise more or less than they actually guarantee.

## Output contract

Return:

- concept/name pairs that are clear;
- ambiguous or misleading names;
- questionable conceptual cuts;
- hidden cognitive load;
- suggested renames or regroupings;
- places where clarification requires revisiting integritas or consonantia.
