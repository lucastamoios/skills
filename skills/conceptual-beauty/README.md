# Conceptual Beauty Skills

A small skill set for analyzing the beauty of concepts and code through the classical triad integritas, consonantia, claritas.

## Core idea

Treat a software system as a DAG of concepts ordered from more general to more specific. The DAG describes conceptual containment and dependence of meaning, not merely function calls or runtime dependencies.

Do not expand the whole DAG up front. Work by progressive conceptual expansion: start from the current node, expose one or two levels, analyze them, revise the division if needed, then descend again. A bad division near the root contaminates everything below it.

The three lenses are distinct but not independent. Expect to cycle among them repeatedly.

## Skills

- `conceptual-beauty`: controls depth, ordering, and which lens to invoke.
- `conceptual-beauty-domain`: distinguishes Core, Supporting, and Generic subdomains before deep analysis.
- `conceptual-beauty-dag`: maps conceptual levels and containment without over-expanding.
- `conceptual-beauty-integritas`: tests wholeness and, especially, the fundamentum divisionis.
- `conceptual-beauty-consonantia`: tests due proportion, separability, boundaries, and interface size.
- `conceptual-beauty-claritas`: tests names, conceptual cuts, cognitive load, and manifestation of form.
- `conceptual-beauty-synthesis`: consolidates findings and decides whether to revise, stabilize, or descend.

## Operating sequence

1. Identify the current conceptual node and its level.
2. Classify the relevant subdomain.
3. Expand only one or two levels below the current node.
4. Apply integritas, consonantia, and claritas as needed, cycling between them.
5. Synthesize findings and repair the current level before descending.
6. Repeat.

## Important distinction

Subdomain belongs to the problem space. Bounded Context belongs to the solution/model space. They may align, but do not assume a one-to-one mapping.
