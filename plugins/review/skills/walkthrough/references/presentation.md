# Present the prepared walkthrough

These instructions are for the user-facing coordinator after the background worker has written its artifact. Use the prepared evidence; do not create findings or require another agent to wait for user interaction.

## Open with the requested outcomes and their implementation

First show the reviewed checkout's absolute folder as a clickable link and its current Git branch. Verify both from the reviewed checkout; if detached, state `detached HEAD` and the short commit. Give this location preface before preparation if the user requests it first. Then give a brief business case:

Explain:

- What was done and for whom, using a concrete case.
- Why the behavior exists and why this change was needed, grounded in the ticket and its relevant discussion.
- The business rules and important exceptions, with links to the ticket and applicable primary regulatory sources.
- The before/after outcome in terms the user can observe.

Distinguish regulatory obligations from product requirements and modeling choices. If no relevant regulatory basis was established, do not invent one. State any missing rationale briefly without making the user wait for a technical inventory.

Follow the case with the prepared requirement sections. Use each requirement's ID and requested outcome as its heading. In short paragraphs, explain what was requested and cite its source, show the exact code locations and their roles, summarize the available implementation and verification evidence or uncertainty, and name the walkthrough part that explains it. Use sections rather than a table. This opening answers both what the ticket asked for and where the code addresses it.

Keep each section compact. If the overview is long, split it across turns before beginning the detailed code trail. Keep every requirement visible in the overview, including partial implementation and unresolved evidence. Distinguish implementation found, checks actually executed, and behavior explained. Do not claim satisfaction from a source link alone. If explicit requirements are unavailable, state that gap and use the prepared observable behaviors without presenting inferred intent as ticket requirements.

Defer framework mechanics and the full code trace until the relevant part. Explain unfamiliar terms as they appear, then give the small connected glossary before the first detailed code explanation. Respect a reader who already knows the business context or asks to jump directly to a requirement or code part.

## Connect the words to the running case

Define each term in this feature's context, including ordinary words with specialized meanings. Explain its relationship to other terms, rather than giving isolated dictionary definitions. Use compact definitions in prose rather than a table. Bold the relevant terms and related terms in the glossary and subsequent prose. Use consistent names and clarify ambiguous words such as rule rather than silently switching meanings.

Tie the terms to what the reader can recognize in the interface: inputs, buttons, displayed values and results. Use the same concrete entity throughout. For a backend-only change, use the corresponding caller, event or stored result. Introduce additional vocabulary only when the next topic needs it. Do not require a diagram, recording or new tool to establish these connections.

## Transition to code

Start with the prepared part that explains the main requested workflow, or the part the reader selects. Name the requirements it addresses. Choose the entrypoint, central function or orchestration function that gives the reader a useful connection between the case's inputs, decisions and outputs. Show its exact clickable file and line. Briefly state the question reading it will answer and connect it to the relevant user action. Defer secondary entrypoints and summarize framework wiring. Explain what input arrives and follow the actual execution sequence through checks, calls, mutations and response. Keep the same case throughout. Finish this flow before switching to another entrypoint, unless the reader asks to jump. Bring in a prior finding only when the execution reaches the behavior it concerns.

Keep the requirement sections as the navigation guide. Use the related behavior questions to track what remains to explain or verify, including affected existing flows. Group related requirements to preserve a connected execution trail, and refer back to shared logic instead of explaining it again. When the reader jumps, retain the skipped requirements and questions so they can be resumed.

## Explain one topic at a time

After the requirement overview, each response covers one topic and stays below approximately 350 words. Prefer less. Use short sections and paragraphs, with a focused code excerpt when it materially improves understanding. Do not use tables or repeat the complete glossary or requirement overview in every turn.

Explain in this order:

1. **Requirement and business meaning:** Name the requirements this part addresses and what it accomplishes for the actor in the running case. Identify supporting behavior explicitly when it has no sourced requirement.
2. **Terms and starting function:** Define any new contextual terms, relate them to known terms, and show the exact clickable `file:line`. Connect its input to the running case and the interface or caller.
3. **Logic:** Trace three to five important steps in execution order, including relevant parameter and state changes.
4. **Output:** Explain what the function returns and where that data goes. Connect meaningful fields to interface values, downstream decisions or stored effects. Distinguish in-memory changes from database writes and explain hidden metadata only when it matters here.
5. **Business rule:** Explain the rule the code enforces, its source, and important exceptions.
6. **Review context:** Connect any canonical finding or passed lens that applies here and explain why that lens revealed it.

Carry the same concrete case through the topics. Translate framework mechanics into explicit familiar operations. Explain only syntax or framework behavior needed for the current topic.

End with a brief statement of which requirements are now explained and what remains uncertain, then give the next reading purpose as a concrete question and name its function and related requirement. Understanding code and verifying that it implements the intended behavior are separate claims. Do not imply PR approval or mark a behavior verified merely because it was explained.

Ask a focused question that lets the reader continue, go deeper, jump or stop. Let the reader's doubts choose the next investigation; use the requirement mapping and behavior questions to retain coverage when the trail branches. Track unresolved questions about correctness, readability or performance against the relevant requirement or supporting behavior, without turning every question into an immediate detour or losing it. Do not equate staged files or remaining diff lines with behavioral verification.

## Narrow on demand

When the reader asks for more detail, narrow one level at a time:

1. Expand the business rule, exception, or state transition.
2. Trace the relevant branch and its input or internal-state conditions.
3. Explain the exact lines, types, query behavior, framework mechanism, or test assertion.

Do not repeat higher-level material unless the new detail changes it. If research corrects an earlier explanation, lead with the correction.

If the user asks for everything at once, provide the remaining topics in order, but keep each topic as a separate short chunk.
