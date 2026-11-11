---
name: run
description: Single entry point for short-video work. Read what the user wants (analyze a reference, get questions, write, critique, or revise a script, or the whole flow), build the inputs from the Marketing vault, dispatch the right marketing workers in order, loop script and critique, and save the results back to the vault. Use whenever the user asks for anything about his videos without naming a worker.
---

# Run

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Turn a plain request into the right sequence of marketing workers. The workers (`culto`, `reference`, `ask`, `angle`, `script`, `critique`) stay self-contained; this skill is the caller that reads the vault, builds their JSON inputs, chains their outputs, and talks to the user. It does not do the workers' analysis itself.

Read [the contract](../../protocol/contract.md) before dispatching. Every worker input and output follows it.

## 1. Choose the route

Infer the route from the request. Ask one short question only when two routes are equally likely.

| The user says or gives | Route |
| --- | --- |
| "culto", "história de origem", a new creator, or no `<creator>-culto.md` | `culto` conversation |
| A video link, transcript, or "por que esse vídeo deu certo" | `reference` |
| "me pergunta", "não sei sobre o que falar", or no usable case in the vault | `ask` conversation, mode `discover`: no `topic` |
| A topic or a half-told story, without a whole case | `ask` conversation, mode `complete`: the user's words as `topic` |
| A case, an answer, "faz um roteiro", or "pega um fato da história" | Pick one fact (section 1b), then `angle` → `script` → critique loop |
| "oferta", "produto", "CTA fraco", or the creator has no `<creator>-oferta.md` | `offer`, then save the result as `<creator>-oferta.md` |
| A script and "critica", "o the configured editor aprovaria?" | `critique` |
| A script plus feedback (from the configured editor or anyone) | `critique` with the feedback as `criteria` or `expert_notes`, then `script` revise |
| "do zero", "faz tudo", or a vague request for a new video | Full flow below |

Full flow: `offer` (only if `<creator>-oferta.md` is missing), `reference` (when a reference is given) and `ask` (when the vault has no usable case) in parallel; wait for the user's answers; `angle`; `script`; critique loop.

A script needs a reference. When the request gives none and `inspiracao-para-roteiros.md` has none that fits the format, ask the user for one before `script`, and do not write the script without a model unless he says to go ahead.

A usable case is a fact in `<creator>-historia.md`, backed by its dated entry in `<creator>-dados.md`, that says what happened, what changed, and a number or proof. An opinion or thesis is not a case.

## 1b. One fact per script

`<creator>-dados.md` keeps everything the user said, verbatim and dated. `<creator>-culto.md` keeps who he is. `<creator>-historia.md` keeps the rest as isolated facts, one per item, grouped by episode, each pointing to its `dados` entry. A script tells one fact, or a small group of facts from the same episode, never the whole episode: a script that tries to fit everything reads as confused.

- Read the `Índice de roteiros` table at the top of `<creator>-roteiros.md` first. It lists every script already made, including archived ones, with its fact, thesis and status. It is the one place that says what was already done.
- Use the fact the user names. Otherwise pick one item from `historia` that is not marked "usado" and whose episode does not already carry a script with the same thesis in the index. Prefer one with a number or a scene, and say which one you picked and why in one line.
- Give the workers that fact and its full original `dados` entry as `material`. Other facts of the same episode go in only when the script needs them as context, marked as context.
- When the script is saved, mark the fact in `historia` with "(Usado no Roteiro N.)" and add its row to the index (title, fact, thesis, status). Update the status after the user's verdict.

## 2. Build inputs from the vault

Read `profile.marketing.root` and `profile.marketing.default_creator`. Each creator has a folder `<Creator>/` with notes prefixed `<creator>-`; shared notes sit at the configured root. Use the creator named in the request before the configured default. If no creator is configured, ask. Read the expert criteria from `profile.marketing.expert_notes`. Workers receive the selected content as explicit input and do not read the vault.

| Input field | Source |
| --- | --- |
| `creator.handle`, `niche`, `audience`, `brand`, `voice_samples`, `constraints`, `assets` | `<creator>-culto.md` |
| `creator.theme` | The `Tema` section of `<creator>-culto.md`, verbatim. Every script request carries it. If the culto has no theme, ask the creator for it in the `culto` conversation before `angle`. |
| `creator.authority` | `<creator>-culto.md` and `<creator>-historia.md`, only verifiable items |
| `ask.goal` | `<creator>-objetivos.md`, when present. When the file is missing, leave `goal` out; `ask` works without it. Do not write a goal yourself. |
| `material` | The chosen fact from `<creator>-historia.md` and its original entry in `<creator>-dados.md`, verbatim, with date and source (section 1b) |
| `product` | `<creator>-produto.md` |
| `offer.product_notes` | `<creator>-produto.md` and any linked product note |
| `script.offer`, `critique.offer` | `<creator>-oferta.md` (the saved `offer` result); if absent and a script is requested, run `offer` first |
| `reference.video`, `reference.notes` | The user's link or transcript, plus the matching row in `inspiracao-para-roteiros.md` |
| `critique.material` | The same `material` entries given to `script`, verbatim |
| `expert_notes`, `critique.criteria` | `profile.marketing.expert_notes` and any new feedback in the request |
| `script.format_preference`, `reference.notes` (format name) | `formatos.md`: the format the user names, or the one that best shows the case's proof, using `case.format_evidence` from `ask` |
| `ask.previous_questions` | Questions already in `<creator>-dados.md` |
| `ask.used_topics` | Titles of the scripts in the index of `<creator>-roteiros.md` |
| `angle.previous_scripts` | Every row of the index in `<creator>-roteiros.md`: title, fact, thesis, status |
| `script.voice_samples` | Add the user's literal sentences from this conversation to `creator.voice_samples` |

Use the language named in the current request, otherwise `profile.user.language`. Ask when neither supplies a language. Prefer the case the user names; otherwise the most recent usable case. Never fill a field with a guess; leave it out and let the worker report `needs_input`.

## 2b. Keep the user's voice

- Put the user's own words for this request (corrections, preferences, feedback from the expert) in `expert_notes` verbatim, in his language. Do not summarize or translate them.
- Never add constraints the user did not give: no length target, no "leave out X", no cuts. If you think a constraint helps, ask him.
- The user's verdict on a script overrides the critique. When he approves or rejects a script, record it with the reason in `<creator>-roteiros.md`, and add it to the calibration examples in `skills/critique/references/criteria.md` when it teaches something new.

## 3. Dispatch

Create a run directory `~/.local/state/marketing/runs/<YYYY-MM-DD-HHMM>-<slug>/`. For each step write `<nn>-<skill>.input.json`, run the worker, and expect `<nn>-<skill>.output.json`.

- Prefer a fresh subagent per worker with no inherited conversation. Give it only: the worker's `SKILL.md` path, the input path, the output path, and "follow the contract, write only the output file". Run independent workers (`reference` and `ask`) in parallel.
- If subagents are not available, run the worker inline by following its `SKILL.md`, and still write the files.
- Validate every input and output: `uv run --with jsonschema python3 <plugin>/scripts/validate.py <skill>.output <file>` (plain `python3` works only when `jsonschema` is installed). On failure, rerun that worker once with the validation error appended to the prompt; if it fails again, stop and report.

Handle each status:

- `ok`: continue.
- `needs_input`: show the user the `missing_inputs[].question` items, all at once, and stop. Resume the same run from that step after he answers.
- `blocked`: show `warnings` and stop.

## 4. Chain the steps

- **ask ↔ user, as a conversation.** Show the questions numbered, in the user's language. When he answers, append each answer verbatim to `<creator>-dados.md` with today's date and the question, and add each new fact that does not belong in the culto to `<creator>-historia.md` as an isolated item pointing to that entry. Then call `ask` again with every turn of this case in `conversation`, verbatim. Repeat until `result.case.done` is true, showing only the new follow-up questions each time. Confirm the `uncertain_terms` with him in the same message. Go to `angle` only when the case is done, or when he says to go ahead anyway; then pass every turn as `material`.
- **Any worker → ask.** When `angle`, `script` or `critique` returns `needs_input`, add its `missing_inputs[].question` items to the `ask` conversation and stop for the user's answer. Do not write or revise a script without the fact.
- **angle → premise check → script.** Use `result.recommended` unless the user picked another angle. Before calling `script`, validate the premises with the user. The user asks for a script once and expects the questions at that moment, never after a script is written.
  - Collect every premise the script would rest on that the creator did not say: a `thesis_basis` or bridge to `creator.theme` marked `inference:`, each `risks` item phrased as a question, each `proof` claim with `status: "needs_source"`, a missing `outcome`, and any scene, time, place or feeling the hook or the demonstration would need that `material` does not hold.
  - Show the chosen fact, the angle in one line (the other angles in one line each, so he can switch) and those questions, numbered, all in one message, and stop. Ask in plain words that quote what he already said, for example "o que esse momento diz sobre usar IA no seu ofício?".
  - Append his answers verbatim to `<creator>-dados.md`, then rerun `angle` with them in `material` if they change the thesis, and only then call `script`.
  - Skip the stop only when there is no open premise, or when he says to go ahead without answering; then the unanswered premises stay out of the script or become `needs_source` placeholders.
- **The user's feedback on a script.** Put his words verbatim in `script.expert_notes`, split into `critique.criteria` (one criterion per point, his words as the `question`), and run `script` in `revise` mode, then the critique loop. Fix any stale fact in the vault first, with his words.
- **script → critique loop.** Round 1: `script` in `generate` mode, then `critique` with `round: 1, max_rounds: 3`. While the verdict is `revise` and rounds remain, run `script` in `revise` mode with `previous_script` and `critique`, then `critique` again. On `approve`, show the script to the user and ask for his verdict before calling it done. On `rethink`, go back to the step named in `rethink_reason` (usually `ask` for a better case) and tell the user why. After 3 rounds without approval, stop and show the last critique. If the only issues left are claims with `status: "needs_source"` or lines that put words in the creator's mouth, do not spend another round: stop and ask him those questions, and record in the training notes which premise the premise check missed.

- **culto ↔ user, as a conversation.** Show `result.question`, one at a time. Append every item of `data_to_save` to `<creator>-dados.md`, verbatim, even when no script uses it. Rewrite `<creator>-culto.md` from `sections`, `creator` and `format`. When `angle`, `script` or `critique` needs a fact that belongs in the culto, ask it here, and record in the training notes why the interview did not ask for it.

## 5. Report and save

Reply in the user's language with:

1. The final script as he would read it aloud, with the visual for each beat.
2. The critique verdict and any open `issues`.
3. Every claim with `status: "needs_source"`, as a question he must confirm before recording.
4. The run directory path.

Append the final script to `<creator>-roteiros.md` as a new dated version with its reference, angle, verdict, and run path, and add or update its row in the index at the top. Do not edit earlier versions. Do not send anything to the configured editor or post anything; the user does that.
