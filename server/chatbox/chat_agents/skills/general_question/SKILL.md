---
name: general-question
description: Provides fallback prompts when no topic is available in agent state.
---

# General Question Prompts

## Prompts

- `prompts/generate_prompt.txt`: used by the `generate` node when topic is empty.
- `prompts/transform_question_prompt.txt`: used by the `transform_question` node when topic is empty.

Keep placeholders unchanged:
- `{summary}`
- `{context}`
- `{question}`
