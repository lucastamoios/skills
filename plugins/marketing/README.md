# Marketing plugin

Use `marketing:run` for everything: it reads the request, builds inputs from the Marketing vault, runs the workers below in order, and saves the script back to the vault.

Six self-contained workers for short-video content. Each takes one JSON input and returns one JSON output under the [marketing/v1 contract](protocol/contract.md), so each can later become its own agent in the content-generation tool.

| Skill | Question it answers | Schemas |
| --- | --- | --- |
| `marketing:reference` | Why did this video work? | [in](protocol/schemas/reference.input.schema.json) / [out](protocol/schemas/reference.output.schema.json) |
| `marketing:ask` | What should I ask to get a filmable case? | [in](protocol/schemas/ask.input.schema.json) / [out](protocol/schemas/ask.output.schema.json) |
| `marketing:angle` | Why should the viewer care about this case? | [in](protocol/schemas/angle.input.schema.json) / [out](protocol/schemas/angle.output.schema.json) |
| `marketing:offer` | What does the CTA sell, and why would the viewer take it? | [in](protocol/schemas/offer.input.schema.json) / [out](protocol/schemas/offer.output.schema.json) |
| `marketing:script` | What exactly is said and shown? | [in](protocol/schemas/script.input.schema.json) / [out](protocol/schemas/script.output.schema.json) |
| `marketing:critique` | Would the expert approve it, and what must change? | [in](protocol/schemas/critique.input.schema.json) / [out](protocol/schemas/critique.output.schema.json) |

Typical flow (what `marketing:run` does): `reference` and `ask` in parallel, then `angle`, then `script` and `critique` in a loop (`script` in `revise` mode) until `approve`.

## Where the inputs come from

The skills never read the vault. The caller copies content into the input:

- `creator.brand`: `vault/projects/Marketing/<Creator>/<creator>-culto.md`
- `material`: `<creator>-respostas.md` and `<creator>-fatos.md`
- `product`: `<creator>-produto.md`
- `reference_analysis` sources and expert notes: `inspiracao-para-roteiros.md`
- extra `criteria` for critique: `profile.marketing.expert_notes` (the built-in list already covers it as of 2026-11-04)

## Validate

`python3 scripts/validate.py <schema-name> <file.json>` checks a file against a schema, e.g. `script.output`. The [examples](examples/) validate.
