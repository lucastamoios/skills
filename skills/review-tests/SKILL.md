---
name: review-tests
description: Run the review:tests procedure from the shared skill collection.
---

# review-tests

Read and follow [the full procedure](../../plugins/review/skills/tests/SKILL.md). Resolve its resources relative to that procedure's actual directory. In a standalone installation, map logical worker identifiers such as `review:tests` through `profile.installation.commands`. These aliases change the invocation name only: preserve protocol skill identifiers, output shapes and model-policy keys. Prepared workers retain the input packet's access limits.
