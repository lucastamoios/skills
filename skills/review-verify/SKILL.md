---
name: review-verify
description: Run the review:verify procedure from the shared skill collection.
---

# review-verify

Read and follow [the full procedure](../../plugins/review/skills/verify/SKILL.md). Resolve its resources relative to that procedure's actual directory. In a standalone installation, map logical worker identifiers such as `review:verify` through `profile.installation.commands`. These aliases change the invocation name only: preserve protocol skill identifiers, output shapes and model-policy keys. Prepared workers retain the input packet's access limits.
