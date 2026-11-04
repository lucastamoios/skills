---
name: meme
description: Brainstorm meme ideas and render a chosen template with captions using memegen.link. Use when the user asks for a meme, a reaction image, or a joke to share about work. Present ten text-only ideas first; render only after he chooses. Never post the result.
---

# Meme

## Private configuration

For ordinary use, read the installed `skill-config` skill and resolve the profile fields below. Set `SKILL_CONFIG` to its `scripts/config.py` absolute path before shell examples. For a prepared worker packet, use only its supplied values and explicitly permitted private resources. Ask for required missing fields; do not load unrelated private context.

Render a captioned meme to a local file. the user picks the template and the wording, you run the script.

`meme.py` lives next to this file. It uses only the Python standard library, so no venv and no install step.

## Which API and why

**memegen.link.** No account, no API key, 211 templates, and it escapes caption text server side, so `?`, `&`, `%`, `/` and quotes can be passed through verbatim.

Two alternatives were checked and rejected on 2026-09-10:

- **memegenerator.net is dead.** Both `api.memegenerator.net` and the homepage refuse connections outright. If the user asks for it by name, say it no longer resolves rather than pretending it works.
- **imgflip** works but `caption_image` needs a username and password on every call. Not worth an account for this.

One gotcha, already handled in the script: Cloudflare sits in front of memegen.link and answers 403 with `error code: 1010` to Python's default `Python-urllib/x.y` user agent. Any ordinary browser user agent gets through, which is why `meme.py` sets one on every request. If a rewrite drops that header, everything fails at once with a 403 that looks like a ban.

## Workflow

1. **Pitch ten ideas before rendering.** Give the user exactly ten distinct text-only concepts, each with a suggested template and the exact caption lines in reading order. Keep the jokes specific to his situation and vary the angle. Do not generate images or previews at this stage. If he asks for more ideas or rejects the batch, give ten fresh text-only ideas.
2. **Wait for his pick.** Render only after the user chooses an idea and wording, or directly instructs you to render a specific option. A request for caption changes is still ideation, not a rendering choice.
3. **Find the selected template id** if you do not already know it:
   ```bash
   "$(python3 "$SKILL_CONFIG" get paths.skills --path)/meme/meme.py" search drake
   ```
   Prints `id`, line count, and name. The line count is how many caption slots the template has.
4. **Render the selected idea.** Pass one argument per caption line, top to bottom:
   ```bash
   "$(python3 "$SKILL_CONFIG" get paths.skills --path)/meme/meme.py" make drake "Tasks with no subject" "A required subject picker" -o /tmp/meme.png
   ```
   It prints the public memegen.link URL and the local path. The URL is stable and embeds fine in GitHub and Slack, which is usually easier than uploading the file.
5. **Show him the result** with `SendUserFile` so he can see it before doing anything with it.

## Custom background

A template of `custom` plus a public image URL captions an arbitrary picture:

```bash
"$(python3 "$SKILL_CONFIG" get paths.skills --path)/meme/meme.py" make custom "top line" "bottom line" --background https://example.com/screenshot.png
```

The background has to be reachable from the public internet. A local screenshot will not work until it is hosted somewhere, so do not offer this for local files without saying that first.

## Rules

- **Never post the meme anywhere.** Generating the image is the whole job. Putting it in Slack, a PR, or a Linear comment is an outbound action that needs the user to approve that specific post, per the global guardrails.
- **Keep captions short.** Two to six words per line reads well. Long lines shrink to nothing.
- **Punch at the work, never at a person.** These go to colleagues. A meme about a bug, a queue, or a process is fine. One about a named teammate is not.
- Write the captions in plain English, avoiding US-native idioms and slang, since the audience reads the user as the author.

## Check

`profile.paths.skills/meme/meme.py --selftest` does one real round trip and asserts a PNG of a sane size comes back. Run it if rendering starts failing, to tell an API outage apart from a bad argument.
