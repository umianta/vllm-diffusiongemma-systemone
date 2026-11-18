# Lesson 2: Your first decision

**Goal:** send a `/v1/systemone` request, read every field of the response, and learn the three question types.
**Files:** `scenarios/01-support-ticket-triage/`

```bash
export SYSONE_URL=http://<node-ip>:30810
```

## The request

`scenarios/01-support-ticket-triage/request.json`:

```json
{
  "model": "diffusiongemma",
  "state": { "ticket": "Everything is down and we have a demo at noon." },
  "questions": {
    "urgent":   { "type": "noul",   "instructions": "Does the customer need a reply within the hour?" },
    "team":     { "type": "choice", "instructions": "Which team owns this?",
                  "criteria": { "infra": "outages, servers", "billing": "invoices, payments", "product": "features, bugs" } },
    "severity": { "type": "score",  "instructions": "How severe is the impact?",
                  "criteria": ["low", "medium", "high", "critical"] }
  }
}
```

Each part does one job:

- **`state`** is *what the questions are about*. It can be a string or any JSON.
- **`questions`** is a map from an id you choose to a question. They are answered independently, in order.
- **`criteria`** depends on the question type (see the table below).

Send it:

```bash
curl -s $SYSONE_URL/v1/systemone -H 'content-type: application/json' \
  -d @scenarios/01-support-ticket-triage/request.json | jq
```

## The three question types

| `type` | Asks | `criteria` | Answer field |
|------|------|------|------|
| `noul` | yes / no | optional `{"true": "...", "false": "..."}` describing each side | `noul` = P(yes) |
| `choice` | pick one of N | `{"label": "description or null", ...}` | `choice` = winning label |
| `score` | a level on an ordered scale | `["low", "medium", "high", ...]` | `score` = expected level index |

## The response

This is the real response, from `scenarios/01-support-ticket-triage/response.json`, trimmed:

```json
"answers": {
  "urgent":   { "type": "noul", "noul": 0.9987,
                "probabilities": { "yes": 0.9987, "no": 0.0013 }, "confidence": 0.983 },
  "team":     { "type": "choice", "choice": "infra",
                "probabilities": { "infra": 0.99968, "billing": 0.00012, "product": 0.00020 }, "confidence": 0.9995 },
  "severity": { "type": "score", "score": 2.9976,
                "legend": { "0": "low", "1": "medium", "2": "high", "3": "critical" },
                "probabilities": { "0": 0.00001, "1": 0.00015, "2": 0.0021, "3": 0.9978 }, "confidence": 0.9975 }
},
"usage": { "input_tokens": 189, "output_tokens": 6 },
"diagnostics": {
  "urgent":   { "label_mass": 0.984, "argmax_is_label": true },
  "team":     { "label_mass": 0.9998, "argmax_is_label": true },
  "severity": { "label_mass": 0.9998, "argmax_is_label": true }
}
```

How to read the fields:

| Field | Meaning | How to use it |
|------|------|------|
| `probabilities` | a softmax over **your labels only** | the distribution for thresholds and ranking |
| `score` | Σ index × p, the *expected* level; 2.9976 means almost certainly "critical" | sort or threshold on a continuous value |
| `label_mass` | how much of the model's *total* probability went to your labels | **a quality signal:** low means the model wanted some other word |
| `argmax_is_label` | whether the model's single top token was one of your labels | `false` means be suspicious |
| `confidence` | top label probability × `label_mass` | one number to threshold on |

> **Rule of thumb:** act automatically only when `confidence` is high (for example above 0.9). Otherwise send the case to a human, or to a slower "System 2" LLM.

## Why it's fast

There are 6 output tokens for 3 questions. No text is generated: the model reads the probability of each label at its answer position on the diffusion canvas. Questions that share a `state` reuse its KV cache (prefix caching), so adding a question costs very little.

## Label rules

- **Prefer short, single-word labels:** `yes`, `infra`, `critical`, `spanish`. The native vLLM server also accepts multi-token labels such as `customer-success`, but single common words give the cleanest, best-calibrated probabilities.
- **At most 64 questions per request.** The 65th returns `400 questions: at most 64 for this model`.
- **Use descriptions instead of long labels.** Put the meaning in the description and keep the label short: `"refund": "money back"`.

## Exercises

1. Change the ticket to `"Can you add dark mode next quarter?"`. Predict `urgent`, `team` and `severity` before you send it.
2. Add a fourth question, `"sentiment"`, as a `score` with `["angry", "neutral", "happy"]`.
3. Replace `infra` with the multi-word label `"customer-success"` and send the ticket again. Compare `label_mass` and `confidence` with the original.
4. Remove the descriptions from `team` (set each to `null`). Does `label_mass` change?

Next: [Lesson 3: Text decisions](03-text-decisions.md)
