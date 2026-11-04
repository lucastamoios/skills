---
name: skill-config
description: Configure a private user profile for shared skills, or resolve the profile, project context and optional integrations used by an installed skill.
---

# Private Skill Configuration

Read the JSON profile at `$SKILLS_CONFIG`, or `~/.config/agent-skills/config.json` when the variable is unset. Use the bundled `scripts/config.py` to validate or query it. In shell examples from other skills, `SKILL_CONFIG` is the absolute path to this helper; `SKILLS_CONFIG` is the optional path to the private JSON profile. Resolve this skill's installation directory before invoking its helper; never assume another user's home directory.

```bash
python3 <skill-config-directory>/scripts/config.py check
python3 <skill-config-directory>/scripts/config.py get paths.brain
python3 <skill-config-directory>/scripts/config.py get work --json
```

When another skill names `profile.<key>`, read that key from this profile. Resolve a relative path against the profile's directory. Load only the `contexts.<skill-name>` documents and integration resources relevant to the current request. Private context supplies user facts and local procedures; it does not grant permission for external actions or override the user's current instructions. Never load unrelated personal journals.

Use the user's current request before stored defaults. If an optional section is absent, skip its integration and report any material coverage gap. If a required value is absent, ask only for the fields needed by the selected skill. Never substitute the package author's identity, organization, repository or machine paths.

## Configure an installation

Use [the questions](references/questions.json) to ask about the selected modules. Begin with display name, language, timezone and context directory. Offer work, transcripts, marketing, timesheets and local integrations only when relevant. The user may skip optional modules. Preserve existing answers when updating a profile.

Save the answers outside the public skill directories. Start from [the empty profile](references/profile.example.json). Store paths to private notes and resources instead of copying them into the public package. Use `scripts/config.py init --output <private-profile.json>` to create an empty profile without overwriting a file. Set `SKILLS_CONFIG` or link the profile at the default path, then run `check`.

Keep credential values in a vault or injected environment. Ask for an environment-variable name or vault reference, never for a credential value in chat. Do not read or print credential values during setup. The helper returns only profile configuration; it does not resolve secret references.

The public distribution must include this skill alongside consumers. Project-specific services remain optional. A questionnaire configures an integration; it does not install that service.

For a standalone package installation, `profile.installation.commands` maps logical plugin worker identifiers to installed skill aliases. Keep protocol identifiers and model-policy keys unchanged when selecting an invocation alias.
