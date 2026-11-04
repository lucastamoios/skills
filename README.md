# Skills

**The skills I use to build software, keep useful context and turn ideas into work.**

A collection of 79 reusable commands for Codex and Claude Code. They cover development, independent reviews, technical explanations, knowledge management, business experiments and short-form content.

Start with a problem you actually have. Pick a skill, give it the relevant context and keep steering. The workflows describe how to work; your private configuration tells them where your projects, notes and tools live.

[Get started](#get-started) · [Choose a skill](#choose-a-skill) · [Example workflows](#example-workflows) · [Full catalog](CATALOG.md) · [Installation details](INSTALL.md)

## Get started

You need Python 3.10 or newer and a filesystem that supports symbolic links. The installer has been tested on macOS and Linux-style directory layouts.

### 1. Download the collection

```bash
git clone https://github.com/lucastamoios/skills.git
cd skills
```

### 2. Install and answer the questions

For Codex:

```bash
python3 install.py --client codex
```

For Claude Code:

```bash
python3 install.py --client claude
```

Use `--client both` to install into both clients.

Setup asks for your preferred name, language, timezone and private context directory. Then it asks about the optional modules you select: work, transcripts, marketing, timesheets and local integrations. You can skip modules and fill missing fields later. Press Enter to keep an existing answer.

The installer creates a minimal private context and stores your answers in `~/.config/agent-skills/config.json`. Existing notes and unrelated skills are preserved. It does not ask for passwords or tokens.

### 3. Open a new agent session

In Codex, start with:

```text
$brainstorm I have three approaches to this feature. Help me examine the tradeoffs.
```

In Claude Code, use:

```text
/brainstorm I have three approaches to this feature. Help me examine the tradeoffs.
```

Then try `explain` on a change you are reading, or `mini-plan` on a small improvement. Use `skill-config` whenever you want to update your private settings.

## Choose a skill

| I want to… | Start here |
| --- | --- |
| Think through an idea before building it. | [brainstorm](skills/brainstorm/SKILL.md) |
| Understand the business rules behind a change. | [business-rules](skills/business-rules/SKILL.md) |
| Prepare a small, bounded change. | [mini-plan](skills/mini-plan/SKILL.md) |
| Coordinate a development task from clarification through review. | [dev](skills/dev/SKILL.md) |
| Find the cause of a reported bug. | [fix](skills/fix/SKILL.md) |
| Review correctness, requirements and runtime behavior independently. | [review-run](skills/review-run/SKILL.md) |
| Understand a diff one part at a time. | [explain](skills/explain/SKILL.md) |
| Examine the concepts and boundaries in a design. | [conceptual-beauty](skills/conceptual-beauty/SKILL.md) |
| Decide what deserves my attention today. | [priorities](skills/priorities/SKILL.md) |
| Keep my notes and tasks useful. | [gardener](skills/gardener/SKILL.md) |
| Test a business assumption. | [business](skills/business/SKILL.md) |
| Analyze a reference video or develop a script. | [marketing-run](skills/marketing-run/SKILL.md) |
| Clean a transcript while preserving what was said. | [transcript-clean](skills/transcript-clean/SKILL.md) |

The [full catalog](CATALOG.md) links every installed command to its procedure.

## Example workflows

### Build a feature

```text
$dev Add a CSV export for the filtered customer list.
Keep the existing permissions and include a review.
```

`dev` coordinates the stages the work needs: shared understanding, requirements, design, planning, implementation and review. It passes explicit inputs and outputs between workers. You can narrow the scope with requests such as “requirements only” or “only plan.”

For a small change, use `mini-plan` to keep the discussion and implementation plan together.

Development and review workers need a model policy or explicit model assignments. Setup leaves those choices empty. Ask `skill-config` to help configure `execution.model_policy` with models available in your client. The coordinator asks when a required assignment is missing.

### Investigate a bug

```text
$fix Submitting the form twice creates two invoices.
Trace the cause and verify the correction with a regression test.
```

The procedure connects the observed failure to its cause, then checks the changed behavior. It keeps the explanation tied to a reproducible case.

### Understand or review a change

```text
$explain Walk me through the current diff, starting with the user-visible behavior.
```

```text
$review-run Review this branch against main.
Focus on correctness, tenant boundaries and the changed UI.
```

`explain` teaches the change in short steps. `review-run` coordinates independent lenses and records their evidence. Review workers receive the declared project context; they do not inherit permission to read your whole private workspace.

### Explore a business idea

```text
$business I want to help small studios manage client feedback.
Help me identify the assumption I should test first.
```

The business family can explore the problem, shape an offer, design an experiment and interpret the resulting evidence.

### Turn a reference into content

```text
$marketing-run Analyze this reference and help me draft a short video
for the creator profile I configured.
```

The marketing procedures separate reference analysis, source material, angle, offer, script and critique. Claims need supplied evidence. Creator profiles, offers and expert feedback stay in your private context.

## How the collection fits together

The main entrypoints handle conversation and coordination. Focused workers handle bounded tasks with explicit inputs, outputs and access limits.

- **Engineering:** clarification, requirements, design, implementation, reviews and PR preparation.
- **Concepts:** vocabulary, domain boundaries, abstraction quality and design coherence.
- **Knowledge and attention:** private notes, tasks, session logs, meeting preparation and priorities.
- **Business:** exploration, offers, experiments and evidence review.
- **Content:** reference analysis, video scripts, critique and transcript editing.

Some procedures run directly in conversation. Others use scripts, connected tools or independent agents. Read a skill before using it on consequential work and adapt the workflow to your project.

## Your context stays private

The public repository contains reusable instructions, helpers and fictional examples. Your identity, repository defaults, glossary, creator profiles and organization-specific rules belong in your private profile and notes.

```text
This repository                   Your machine
skills and procedures             ~/.config/agent-skills/config.json
empty configuration templates     your private context directory
fictional examples                your own project notes and integrations
```

Credential values belong in a vault or an injected environment. The configuration can point to them, but setup never asks you to paste them into a conversation.

GitHub, Linear, Slack, calendars and local services require your own accounts and resources. Browser recording, PDF generation and schema validation have optional dependencies described in [the installation guide](INSTALL.md). Installing these skills does not install those services or grant access to them.

## Updating and validating

```bash
git pull
python3 install.py --client codex
```

Use the same client option you selected initially. Reinstallation preserves private answers and lets you change them. A conflicting existing skill or a modified installed release is reported before replacement. Installation copies the public files, so it does not require the clone to remain in place.

To check the repository and exercise the installation flow:

```bash
python3 check_package.py
python3 -m unittest discover -s tests -v
```

The installation tests use temporary directories and fictional profiles. They cover the questionnaire, both clients, updates, preserved settings, path boundaries and installed helpers. The wider package validation also exercises the configuration, recording helpers, schemas and snapshot tools.

After intentionally editing public files, run `python3 tools/refresh_manifest.py` before validation. Private files and generated state must stay outside the repository.

## Inspiration

The presentation of this collection was inspired by [Matt Pocock's skills repository](https://github.com/mattpocock/skills): make it easy to install, explain when each skill helps and give people a useful starting point. This repository documents its own workflows, installer and configuration contract.

## License

[MIT](LICENSE). Copyright © 2026 Lucas Almeida Aguiar.
