---
name: review-dead-code
description: Run the review:dead-code procedure from the shared skill collection.
---

# review-dead-code

Read and follow [the full procedure](../../plugins/review/skills/dead-code/SKILL.md). Resolve its resources relative to that procedure's actual directory. In a standalone installation, map logical worker identifiers such as `review:dead-code` through `profile.installation.commands`. These aliases change the invocation name only: preserve protocol skill identifiers, output shapes and model-policy keys. Prepared workers retain the input packet's access limits.
