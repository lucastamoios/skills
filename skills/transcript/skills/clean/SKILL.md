---
name: clean
description: >-
  Clean and reconstruct noisy meeting transcripts into publication-ready conversational prose while preserving every substantive turn, the speaker's voice, and the source chronology. Use for transcripts with overlapping speech, split turns, filler words, repetitions, slang, profanity used as filler, diarization or speaker-name errors, broken punctuation, and likely transcription mistakes. Produce readable prose suitable for a book without summarizing or regrouping by topic, correct speaker names only from unambiguous evidence, mark uncertain passages inline, and validate word, turn, and timestamp fidelity against the raw source before delivery.
---

# Clean Meeting Transcripts

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Turn a raw transcript into faithful, publication-ready conversational prose. Preserve the source and the speaker's recognizable voice. Do not summarize the meeting, silently resolve uncertainty, or require a separate review pass.

## Prepare

1. Read the complete transcript before editing. Use later introductions, repeated terminology, and later corrections to interpret earlier passages.
2. Preserve the original file unchanged. For a file input, write the result beside it as `<stem>-cleaned.md` unless the user specifies another path. For pasted text, return the cleaned transcript in the response.
3. Read [references/unclear-resolutions.md](references/unclear-resolutions.md). Apply a confirmed resolution only when its stated context matches the meeting.
4. Read [references/editorial-style.md](references/editorial-style.md). Apply its publication-quality rules to every turn.
5. Read [references/difficult-words.md](references/difficult-words.md). Load only the sections that match the meeting context.
6. If the meeting clearly belongs to a known context but the glossary is insufficient, search the relevant non-sensitive local notes. Start with `profile.paths.vault/index.md`. Never inspect `profile.paths.vault/personal/journal/`. Do not load archived notes unless a current note links to one as necessary evidence.
7. Preserve the transcript's original language. Do not translate unless the user asks.

Treat glossary entries and local notes as spelling and interpretation candidates. They are not evidence that a speaker said a term.

## Identify speakers

Build a participant map from the complete transcript before rewriting turns.

Correct an anonymous or incorrect speaker label automatically when the transcript gives unambiguous evidence, such as:

- the speaker explicitly identifies themselves;
- the host introduces the person before giving them the floor;
- a named label elsewhere is connected to the same anonymous label by stable transcript structure;
- the transcript explicitly corrects a participant's name.

Apply a matching user-confirmed identity from the resolution map before using a generic label. Do not infer that a speaker is the person they address. If a mapping remains uncertain, replace the speaker label with a neutral numbered label: `Pessoa 1`, `Pessoa 2`, and so on. Number uncertain speakers independently within each transcript. Keep the same number for the same diarized speaker throughout the file. Do not include a guessed name or role by default. If the user explicitly asks to retain a supported probable identity, use `Provavelmente <Nome>` as the stable speaker label. Reserve `⟦unclear; probably: ...⟧` for uncertain spoken content, not speaker identity. Report each automatic label mapping once in the correction summary.

## Reconstruct the conversation

1. Use timestamps as the primary chronology when they exist.
2. Work in small adjacent conversation windows. Join fragments when grammar, topic, timing, and speaker identity show that they form one thought.
3. Reorder adjacent fragments from overlapping speech only when one ordering is strongly supported. Preserve meaningful interjections in their actual position.
4. Merge consecutive fragments from the same speaker when the split is only a transcription artifact.
5. Keep different speakers separate. Never combine their statements into one turn.
6. If more than one ordering is plausible, preserve the observed order and add `⟦unclear; probably: original order preserved⟧` at the affected boundary.
7. Mark unrecoverable audio as `[INAUDIBLE]`, `[OVERLAP]`, or `[MISSING]`. Never invent missing speech.

Do not regroup non-adjacent turns under thematic headings. Add a heading only at an existing boundary between adjacent turns. Do not move a turn to make a section read better. Do not split one source turn and place its parts in different sections.

## Account for every source turn

Maintain a turn ledger while cleaning. For every source turn, record exactly one outcome:

- retained as its own cleaned turn;
- merged with an immediately adjacent fragment from the same speaker;
- removed because it contains only filler, duplicate recognition, or non-speech noise.

Never mark a substantive turn as removed. Never replace several turns with a synthesized explanation. Keep the earliest source timestamp on an adjacent merged turn. Within each source, cleaned timestamps must remain monotonically nondecreasing.

## Remove noise without removing meaning

Remove:

- empty fillers such as isolated `um`, `uh`, `hmm`, `é...`, `tipo`, and `assim`;
- meaningless repeated words caused by recognition or overlap;
- abandoned sentence starts that contribute no information;
- duplicated passages created by overlapping transcript segments;
- empty acknowledgements that do not affect the exchange.

Preserve:

- agreement, refusal, uncertainty, hesitation, emphasis, and changes of position;
- a short response such as `yes`, `yeah`, `sim`, or `não` when it answers a question or confirms a decision;
- discourse markers when they change tone or logic;
- disagreement, qualifications, conditions, and unanswered questions;
- names, numbers, dates, negations, commitments, responsibilities, and technical terms.

Add punctuation, capitalization, paragraph breaks, and consistent turn formatting. Keep timestamps when present, reducing redundant timestamps only when several belong to one reconstructed turn.

Rewrite the surface form inside each turn when the meaning is clear. You may:

- remove stutters, false starts, and repeated discourse fillers;
- fix agreement, verb form, obvious transcription spelling, and sentence boundaries;
- normalize an obvious colloquial or technical form, such as `prode` to `produção` in a software-deployment context;
- remove or soften an isolated vulgar interjection when it contributes emotion but no factual meaning;
- turn clearly reported speech into a quotation;
- join or split sentences inside the same turn so that the thought reads naturally.

Preserve every proposition, actor, negation, qualification, condition, commitment, causal connection, emotion, and change of position. Preserve a recognizable conversational voice, not every verbal tic. Do not compress several clauses into a general statement, add an interpretation, or flatten the speaker into formal institutional prose. A cleaned transcript is not a summary or meeting minutes. It is a light editorial reconstruction of the original speech.

## Handle difficult words

Apply an obvious spelling or capitalization normalization when the spoken term is clearly identifiable from the transcript, a matching confirmed resolution, or the glossary. A matching confirmed resolution does not need an uncertainty marker. List each proper-name or acronym normalization in the correction summary.

Do not silently replace a word that is nonsensical, contextually surprising, phonetically ambiguous, or meaning-bearing. Replace only the smallest uncertain span with `⟦unclear; probably: <best-supported interpretation>⟧`. Keep the complete surrounding sentence and adjacent turns in the transcript so the reader can understand the context without opening another file.

Use one marker per semantic uncertainty. Put the most likely interpretation after `probably:`. Use `⟦unclear; probably: unknown⟧` when the transcript does not support a useful hypothesis. Use these corner brackets and a semicolon exactly. They have no link, table, task, or property meaning in standard Obsidian Markdown. Do not use square brackets or a pipe for uncertainty markers. Do not include issue IDs, confidence labels, decision fields, or a separate review list. Do not use external fact checking to manufacture speech that is absent from the transcript.

## Deliver the result

Produce the cleaned transcript directly. For file input, write `<stem>-cleaned.md`. Do not create `<stem>-cleaned-draft.md` or `<stem>-cleaning-review.md`, and do not pause for the user to resolve uncertainty.

In the response, include:

1. the cleaned transcript or a link to the cleaned file;
2. `Automatic corrections`, listing speaker-label mappings and proper-name or acronym normalizations, without listing routine filler removal or punctuation edits;
3. `Fidelity validation`, reporting word retention, turn retention, timestamp order, and the result of the turn-ledger check;
4. `Limits`, listing inaudible, missing, unrecoverable, or inline unclear passages.

If the user later confirms an inline interpretation, replace that marker with the confirmed text in the cleaned file. This later correction is optional and is not part of the default cleaning workflow.

## Validate fidelity

Before delivery, compare the raw and cleaned versions. Run:

```bash
python3 scripts/validate_fidelity.py --raw <source.md> --cleaned <source-cleaned.md>
```

Repeat `--raw` for each source of a consolidated transcript. The script is a tripwire, not proof of semantic fidelity. `critical` means that the output probably became a summary. `review` means that the reduction is large enough to require a complete turn-ledger comparison. A non-pass result blocks delivery. Do not lower the thresholds to make an output pass. Rewrite the transcript or prove from the ledger that every removed turn was empty noise, then report that evidence explicitly.

Confirm that:

- every substantive claim, decision, objection, condition, and open question remains;
- every proposition in a rewritten source turn still maps to an explicit clause in the cleaned turn;
- every name, number, date, negation, responsibility, and commitment is preserved or explicitly marked inline;
- no statement moved to another speaker without strong evidence;
- every source turn is accounted for in the turn ledger;
- headings occur only at chronological boundaries and never cause topical regrouping;
- timestamps never move backward within one source;
- every unresolved speaker uses a stable `Pessoa N` label or an explicitly requested `Provavelmente <Nome>` label, with no uncertainty marker in the speaker label;
- every uncertainty marker contains a concrete best-supported interpretation or `unknown`;
- no obvious transcription artifact, repeated filler, isolated coarse interjection, or broken sentence remains when it can be repaired without guessing;
- the cleaned transcript reads continuously and could appear in a professionally edited interview or book without becoming a summary or meeting minutes.
