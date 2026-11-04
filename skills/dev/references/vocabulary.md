# Reconcile vocabulary

Use this method while drafting requirements and design. The goal is a consistent
meaning for each concept across the request, domain documentation, requirements,
design, and code.

Read the relevant existing glossary or domain notes before naming concepts.
Check the terms used in accepted decisions, user-facing language, and code.
Reuse an established term when its meaning fits. Preserve legal and regulatory
terms and distinguish their meanings from application-specific usage.

For terms material to the scope, establish their meaning with a concrete example
and, when the boundary is unclear, a contrasting case. Check whether two names
are synonyms, whether one name hides different concepts, and whether a concept
has different meanings in different contexts. Do not merge those contexts just
to make the names uniform. Code establishes current behavior, not necessarily
the intended domain model.

When evidence leaves a meaning, boundary, or preferred term uncertain, return a
stable question ID to the coordinator with the competing meanings, examples,
source references, a recommendation when supported, and the dependent work.
The coordinator asks the user and records his answer. Continue independent work,
but keep affected terms provisional until answered. Do not invent a meaning to
complete the document or repeatedly ask about a settled definition.

Introduce a new term cautiously. First show the concept that existing vocabulary
cannot express and why established terms do not fit. Prefer familiar domain
language to invented jargon or new compound labels. Propose the term and its
plain-language definition to the user before treating a new or renamed domain term
as canonical. Routine implementation identifiers may follow established naming
patterns when their meaning is already settled.

Record accepted meanings in the existing canonical glossary or domain note when
that file is assigned for editing. Otherwise, put the proposed update in the
worker output for the coordinator. Create a glossary only when useful knowledge
has no existing home and the write is authorized. Keep one definition source;
reference it from requirements, scenarios, and design rather than maintaining
competing glossaries. Record deliberate mappings to legacy code names without
silently renaming code or changing product scope.

Before completing the stage, check that its artifacts use accepted terms
consistently. Return the vocabulary sources, resolved mappings, any proposed
canonical updates, and unanswered questions with their affected requirement or
decision IDs.
