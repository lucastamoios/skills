---
name: conceptual-beauty-domain
description: Classify a problem-space subdomain as Core, Supporting, or Generic to set the depth of a conceptual-beauty analysis. Use within the conceptual-beauty workflow or directly when that classification is the requested result. Do not use to classify Bounded Contexts as if they were subdomains.
---

# Domain Classification

This specialist can be used by the `conceptual-beauty` orchestrator or independently when the user requests this specific classification.

## Role

Classify the problem-space subdomain before spending equal analytical effort everywhere.

## Categories

### Core Domain

The part that most expresses the distinctive business capability or competitive logic. Its concepts deserve the deepest work on language, division, invariants, and model shape.

### Supporting Subdomain

Necessary for the business but not itself the primary source of differentiation. Model it carefully enough to protect the core and keep boundaries clear, but do not over-invest by default.

### Generic Subdomain

A capability whose conceptual model is largely established outside this business, such as common authentication, commodity billing primitives, or standard file storage. Prefer adopting a known abstraction and encapsulating it rather than inventing a private ontology.

## Important caveat

Generic does not mean simple. It means the business usually does not gain much by inventing the concept anew.

## Procedure

1. Name the business capability represented by the current concept.
2. Ask whether the capability is a source of business-specific differentiation.
3. Ask whether a standard external model already captures most of it.
4. Classify as Core, Supporting, or Generic.
5. Record confidence and borderline cases.
6. State how classification changes analysis depth.

## Questions

- If this capability were outsourced or replaced by a standard product, would the business lose something distinctive?
- Does the business use ordinary industry language here, or does it require its own precise vocabulary?
- Are the hard decisions here business decisions or mainly technical/integration decisions?
- Is this concept generic in itself but critical at its boundary with the core?

## Output contract

- Subdomain name.
- Classification.
- Rationale.
- Confidence.
- Required analysis depth: deep, moderate, or boundary-focused.

## DDD distinction

Do not confuse subdomains with Bounded Contexts. Subdomain is problem space. Bounded Context is a boundary in the model/solution space. Map their relation explicitly later rather than assuming identity.
