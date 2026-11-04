# Installation and private configuration

This package contains reusable skills, supporting scripts and the Marketing, Review and Transcript procedures. It contains no personal profile, Brain vault, session logs or Git history.

## Install

Use Python 3.10 or newer. Setup needs no network connection.

```sh
python3 install.py --client codex
python3 install.py --client claude
python3 install.py --client both
```

Setup asks which optional modules you want, then asks for your preferred name, language, IANA timezone and private context directory. It asks additional questions only for selected modules. Press Enter to keep an existing answer or skip an optional field. Arrays and alias maps use JSON notation when requested.

The installer copies this release into `~/.local/share/agent-skills/packages/` and links its skills into the selected clients. Keep the installed copy; the downloaded package can be moved or removed after installation. Existing unrelated skills are preserved. A conflict stops the installation before writing links or answers. Reinstallation retains answers and accepts explicit changes.

Private answers live in `~/.config/agent-skills/config.json` with owner-only file permissions. They stay outside this package. Never enter a password or token into setup. Credentials belong in an environment or a vault. Configure optional services later through `skill-config`, using paths and credential references.

Start a new client session after installation. Invoke `skill-config` to update your private settings. If you select another profile path with `--config`, provide that path through `SKILLS_CONFIG` when starting the client. `SKILL_CONFIG`, used in shell examples, is the path to the installed `skills/skill-config/scripts/config.py` helper.

## Modules and commands

All skill entrypoints are installed. Optional modules select setup questions, not permission to read your accounts or private notes.

Shared skills keep their names. Standalone plugin commands use names such as `marketing-run`, `marketing-offer`, `review-run` and `transcript-clean`. `command-map.json` maps the original logical names to these installed aliases. Protocol identifiers and model-policy keys retain their original names. The original plugin layouts and manifests are also retained for native plugin packaging.

Task management uses the bundled helper and the configured private task directory. No personal task notes are shipped. GitHub, Linear, Slack, Calendar, local RAG services, model policies and screenshot services require your own accounts or resources. Setup does not install those services or access them. A skill asks for a missing required field when it is needed.

Some modules require additional tools, such as `gh`, Playwright, ffmpeg or jq. The relevant procedure describes those requirements. Marketing schema validation uses jsonschema; timesheet PDF generation uses reportlab. These tools are not downloaded by the installer.

## Validate

```sh
python3 check_package.py
python3 -m unittest discover -s tests -v
```

The tests install into temporary directories, answer the real questionnaire through standard input, and exercise configured helpers. They do not install into your real clients or read the author's Brain.

`check_package.py` checks file hashes, forbidden package content and known credential formats. It is a release check, not a proof that every possible secret has been detected. Run a separate secret scanner when preparing the final GitHub release.

## License and private data

The collection is currently marked `UNLICENSED`; see the README for the current license status. Private profiles, notes and account settings remain outside the repository and installed release.
