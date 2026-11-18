# Lesson 6: The OpenAI-style `/v1/decisions` API

**Goal:** use the second decision endpoint, which runs the same engine through an OpenAI-shaped schema.
**Files:** `scenarios/31`, `scenarios/32`

## Comparing the two endpoints

| | `/v1/systemone` | `/v1/decisions` |
|---|---|---|
| Input | `state` (string or any JSON) | `input` (string or a list of `{"role":"user","content":...}` messages) |
| Questions | map `id → {type, instructions, criteria}` | **list** of `{type, name, instructions, ...}` |
| Yes/no type | `noul` | `predicate` |
| Choice options | `criteria: {"label": "desc"}` | `choices: [{"value", "description"}]` (2–255) |
| Score levels | `criteria: ["low", ...]` | `levels: [{"label", "description"}]` (2–10) |
| Images | yes (`images`) | **no**: text only |
| Extras | `instructions`, `joint` | `joint`, `safety_identifier` |
| Diagnostics | `label_mass` per question | no |

Use `/v1/systemone` for images, JSON state, and diagnostics. Use `/v1/decisions` when your client code already speaks the OpenAI style and needs a list-shaped, typed schema.

## Scenario 31: predicate + choice + score

```json
{
  "model": "diffusiongemma",
  "input": "My package arrived crushed and the glass inside is broken. I want my money back today.",
  "questions": [
    {"type": "predicate", "name": "refund", "instructions": "Is the customer asking for a refund?"},
    {"type": "choice", "name": "reason", "instructions": "Why are they unhappy?",
     "choices": [{"value": "damaged", "description": "item arrived broken"},
                 {"value": "late", "description": "delivery delay"},
                 {"value": "wrong", "description": "wrong item"}]},
    {"type": "score", "name": "anger", "instructions": "How upset is the customer?",
     "levels": [{"label": "calm"}, {"label": "annoyed"}, {"label": "angry"}]}
  ]
}
```

The response has `answers` as a **list**, in question order:

```json
"answers": [
  {"type": "predicate", "name": "refund", "probability": 0.9994},
  {"type": "choice", "name": "reason", "choice": "damaged",
   "probabilities": [{"value": "damaged", "probability": 0.99...}, ...], "confidence": 0.99...},
  {"type": "score", "name": "anger", ...}
]
```

Recorded result: refund 1.00 · `damaged` · `angry`.

## Scenario 32: message-list input

```json
{"model": "diffusiongemma",
 "input": [{"role": "user", "content": "Can you book me a table for two at 7pm tomorrow?"}],
 "questions": [
   {"type": "choice", "name": "domain", "instructions": "Which assistant skill handles this?",
    "choices": [{"value": "restaurant"}, {"value": "flight"}, {"value": "weather"}, {"value": "music"}]},
   {"type": "predicate", "name": "has_time", "instructions": "Did the user give a time?"}]}
```

Recorded result: `restaurant` · has_time 0.98.

## Exercises

1. Port scenario 05 (content moderation) to `/v1/decisions`. Compare the answers.
2. Send an `image_url` content part in `input`. What error comes back?
3. Write a three-turn conversation as `input` messages and ask whether the user's problem was resolved.

Next: [Lesson 7: Testing with Postman and the regression runner](07-testing.md)
