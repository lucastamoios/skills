---
name: run
description: Single entry point for short-video work. Read what the user wants (analyze a reference, get questions, write, critique, or revise a script, or the whole flow), build the inputs from the Marketing vault, dispatch the right marketing workers in order, loop script and critique, and save the results back to the vault. Use whenever the user asks for anything about his videos without naming a worker.
---

# Run

## Private configuration

For an ordinary invocation that needs personal defaults or integrations, read the installed `skill-config` skill and resolve the `profile.<key>` fields below. Load only context relevant to the request. Command examples with these fields are templates; substitute configured values as quoted arguments before execution. Ask for required missing fields and skip unavailable optional integrations.

For a prepared worker packet, use only its declared access and supplied configuration. The coordinator resolves private defaults and passes the minimum required values or permitted resources. A worker must not load a machine-wide profile or unrelated context unless the packet explicitly permits it.

Turn a plain request into the right sequence of marketing workers. The workers (`reference`, `ask`, `angle`, `script`, `critique`) stay self-contained; this skill is the caller that reads the vault, builds their JSON inputs, chains their outputs, and talks to the user. It does not do the workers' analysis itself.

Read [the contract](../../protocol/contract.md) before dispatching. Every worker input and output follows it.

## 1. Choose the route

Infer the route from the request. Ask one short question only when two routes are equally likely.

| The user says or gives | Route |
| --- | --- |
| A video link, transcript, or "por que esse vídeo deu certo" | `reference` |
| "me pergunta", "não sei sobre o que falar", or no usable case in the vault | `ask`, then stop for answers |
| A case, an answer, or "faz um roteiro" | `angle` → `script` → critique loop |
| "oferta", "produto", "CTA fraco", or the creator has no `<creator>-oferta.md` | `offer`, then save the result as `<creator>-oferta.md` |
| A script and "critica", "o the configured editor aprovaria?" | `critique` |
| A script plus feedback (from the configured editor or anyone) | `critique` with the feedback as `criteria` or `expert_notes`, then `script` revise |
| "do zero", "faz tudo", or a vague request for a new video | Full flow below |

Full flow: `offer` (only if `<creator>-oferta.md` is missing), `reference` (when a reference is given) and `ask` (when the vault has no usable case) in parallel; wait for the user's answers; `angle`; `script`; critique loop.

A usable case is a dated entry in `<creator>-respostas.md` or `<creator>-fatos.md` that says what happened, what changed, and a number or proof. An opinion or thesis is not a case.

## 2. Build inputs from the vault

Read `profile.marketing.root` and `profile.marketing.default_creator`. Each creator has a folder `<Creator>/` with notes prefixed `<creator>-`; shared notes sit at the configured root. Use the creator named in the request before the configured default. If no creator is configured, ask. Read the expert criteria from `profile.marketing.expert_notes`. Workers receive the selected content as explicit input and do not read the vault.

| Input field | Source |
| --- | --- |
| `creator.handle`, `niche`, `audience`, `brand`, `voice_samples`, `constraints`, `assets` | `<creator>-culto.md` |
| `creator.authority` | `<creator>-culto.md` and `<creator>-fatos.md`, only verifiable items |
| `ask.goal` | `<creator>-objetivos.md`, when present |
| `material` | `<creator>-respostas.md` and `<creator>-fatos.md`, each entry with its date and source |
| `product` | `<creator>-produto.md` |
| `offer.product_notes` | `<creator>-produto.md` and any linked product note |
| `script.offer`, `critique.offer` | `<creator>-oferta.md` (the saved `offer` result); if absent and a script is requested, run `offer` first |
| `reference.video`, `reference.notes` | The user's link or transcript, plus the matching row in `inspiracao-para-roteiros.md` |
| `expert_notes`, `critique.criteria` | `profile.marketing.expert_notes` and any new feedback in the request |
| `script.format_preference`, `reference.notes` (format name) | `formatos.md`: the format the user names, or the one that best shows the case's proof |
| `ask.previous_questions` | Questions already in `<creator>-respostas.md` |

Use the language named in the current request, otherwise `profile.user.language`. Ask when neither supplies a language. Prefer the case the user names; otherwise the most recent usable case. Never fill a field with a guess; leave it out and let the worker report `needs_input`.

## 3. Dispatch

Create a run directory `~/.local/state/marketing/runs/<YYYY-MM-DD-HHMM>-<slug>/`. For each step write `<nn>-<skill>.input.json`, run the worker, and expect `<nn>-<skill>.output.json`.

- Prefer a fresh subagent per worker with no inherited conversation. Give it only: the worker's `SKILL.md` path, the input path, the output path, and "follow the contract, write only the output file". Run independent workers (`reference` and `ask`) in parallel.
- If subagents are not available, run the worker inline by following its `SKILL.md`, and still write the files.
- Validate every output: `python3 <plugin>/scripts/validate.py <skill>.output <file>`. On failure, rerun that worker once with the validation error appended to the prompt; if it fails again, stop and report.

Handle each status:

- `ok`: continue.
- `needs_input`: show the user the `missing_inputs[].question` items, all at once, and stop. Resume the same run from that step after he answers.
- `blocked`: show `warnings` and stop.

## 4. Chain the steps

- **ask → user.** Show the questions numbered, in the user's language. When he answers, append each answer to `<creator>-respostas.md` with today's date and the question, then continue to `angle` with the answer as `material`.
- **angle → script.** Use `result.recommended` unless the user picked another angle. Show the angles in one line each so he can switch later.
- **script → critique loop.** Round 1: `script` in `generate` mode, then `critique` with `round: 1, max_rounds: 3`. While the verdict is `revise` and rounds remain, run `script` in `revise` mode with `previous_script` and `critique`, then `critique` again. On `approve`, stop. On `rethink`, go back to the step named in `rethink_reason` (usually `ask` for a better case) and tell the user why. After 3 rounds without approval, stop and show the last critique.

## 5. Report and save

Reply in the user's language with:

1. The final script as he would read it aloud, with the visual for each beat.
2. The critique verdict and any open `issues`.
3. Every claim with `status: "needs_source"`, as a question he must confirm before recording.
4. The run directory path.

Append the final script to `<creator>-roteiros.md` as a new dated version with its reference, angle, verdict, and run path. Do not edit earlier versions. Do not send anything to the configured editor or post anything; the user does that.
