# Marketing plugin

Use `marketing:run` for everything: it reads the request, builds inputs from the Marketing vault, runs the workers below in order, and saves the script back to the vault.

Seven self-contained workers for short-video content. Each takes one JSON input and returns one JSON output under the [marketing/v1 contract](protocol/contract.md), so each can later become its own agent in the content-generation tool.

| Skill | Question it answers | Schemas |
| --- | --- | --- |
| `marketing:culto` | Who is this creator, and what can he say and show? | [in](protocol/schemas/culto.input.schema.json) / [out](protocol/schemas/culto.output.schema.json) |
| `marketing:reference` | Why did this video work? | [in](protocol/schemas/reference.input.schema.json) / [out](protocol/schemas/reference.output.schema.json) |
| `marketing:ask` | What should I ask to get a filmable case? | [in](protocol/schemas/ask.input.schema.json) / [out](protocol/schemas/ask.output.schema.json) |
| `marketing:angle` | Why should the viewer care about this case? | [in](protocol/schemas/angle.input.schema.json) / [out](protocol/schemas/angle.output.schema.json) |
| `marketing:offer` | What does the CTA sell, and why would the viewer take it? | [in](protocol/schemas/offer.input.schema.json) / [out](protocol/schemas/offer.output.schema.json) |
| `marketing:script` | What exactly is said and shown? | [in](protocol/schemas/script.input.schema.json) / [out](protocol/schemas/script.output.schema.json) |
| `marketing:critique` | Would the expert approve it, and what must change? | [in](protocol/schemas/critique.input.schema.json) / [out](protocol/schemas/critique.output.schema.json) |

Typical flow (what `marketing:run` does): `reference` and `ask` in parallel; `ask` keeps a conversation with the creator, interviewing him to find a topic when he has none (mode `discover`, with openers that join format, style and history) and then closing the case (mode `complete`) until it has what happened, the outcome and his thesis; then `angle` (thesis and outcome together), then `script` and `critique` in a loop (`script` in `revise` mode) until `approve`. Any worker that needs a fact only the creator has sends the question back to the `ask` conversation.

## Where the inputs come from

The skills never read the vault. The caller copies content into the input:

- `creator.brand`: `vault/projects/Marketing/<Creator>/<creator>-culto.md`, built by `marketing:culto`
- Everything the creator ever said: `<creator>-dados.md`, kept even when no script uses it
- `material`: one fact from `<creator>-historia.md` and its entry in `<creator>-dados.md`
- `product`: `<creator>-produto.md`
- `reference_analysis` sources and expert notes: `inspiracao-para-roteiros.md`
- extra `criteria` for critique: `profile.marketing.expert_notes` (the built-in list already covers it as of 2026-11-04)

## Validate

`uv run --with jsonschema python3 scripts/validate.py <schema-name> <file.json>` checks a file against a schema, e.g. `script.output`. Plain `python3` works when `jsonschema` is installed. The [examples](examples/) validate.
