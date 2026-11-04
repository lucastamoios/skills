---
name: transcript-clean
description: Run the transcript:clean procedure from the shared skill collection.
---

# transcript-clean

Read and follow [the full procedure](../../skills/transcript/skills/clean/SKILL.md). Resolve its resources relative to that procedure's actual directory. In a standalone installation, map logical worker identifiers such as `transcript:clean` through `profile.installation.commands`. These aliases change the invocation name only: preserve protocol skill identifiers, output shapes and model-policy keys. Prepared workers retain the input packet's access limits.
