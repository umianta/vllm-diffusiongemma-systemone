# Lesson 8: Production tips and limits

**Goal:** know when to trust an answer, how to design questions that work well, and where System 1 stops and System 2 has to take over.

## 1. Threshold on `confidence`, and check `label_mass`

`confidence` = P(top label) × `label_mass`. A right answer can still have a low `label_mass`. These cases are from the recorded run:

| Scenario | Question | Answer | `label_mass` | Meaning |
|---|---|---|---|---|
| 10 | `security`: "Does the change introduce a security vulnerability?" | yes ✅ | 0.01 | the model wanted to answer with something other than yes/no |
| 21 | `vendor_match` | yes ✅ | 0.01 | same |
| 22 | `reimbursable` | yes ✅ | 0.16 | |
| 27 | `marketing` box ticked? | no ✅ | 0.10 | |
| 17 | `empirical` | yes ✅ | 0.52 | |
| 01 | `team` | `infra` ✅ | 1.00 | the ideal case |

Here's a routing policy that works well:

```text
confidence ≥ 0.90                         → act automatically
0.60 ≤ confidence < 0.90                  → act, but log for review
confidence < 0.60  or  label_mass < 0.5   → escalate: a human, or a System 2 LLM call with reasoning
```

## 2. Question design checklist

- **Make labels short, common, lower-case words** (`yes`, `block`, `infra`). Multi-word labels are accepted, but they score less cleanly.
- **Put the meaning in descriptions:** `"challenge": "ask for 3-D Secure / OTP"`.
- **Ask one thing per question.** "Is it urgent and from a VIP?" should be two questions.
- **Phrase yes/no questions so "yes" is natural.** If `label_mass` is low, rephrase. For example, "Is this code vulnerable to SQL injection?" works better than "Does the change introduce a security vulnerability?".
- **Order `score` levels from least to most,** because `score` is the expected index.
- **Test the negative case.** Every "is it spam?" needs a not-spam control (scenarios 02 and 03).

## 3. What System 1 is bad at

| Weak spot | Example | Do instead |
|---|---|---|
| Comparing numbers across inputs | scenario 21: $4,850 vs PO 4600, answered "not over" | compute in code, then pass the fact in `state` |
| Long multi-step reasoning | "Given these 12 rules, which applies?" | split into several questions, or use chat completions with thinking |
| Free-text extraction | "What is the invoice number?" | `/v1/chat/completions` (generation), not decisions |
| Audio and video | | not supported by this model |

The pattern is: **System 1 decides fast and cheaply; low confidence falls through to System 2** (a generating LLM, or a person).

## 4. Determinism

Async scheduling and batching mean borderline probabilities move a little between runs. In our runs, `kind=injection` in scenario 10 varied between confidence 0.03 and 0.99 while the label stayed the same. Clear-cut answers are stable. For regression tests, compare **labels**, not exact probabilities.

## 5. Performance

These numbers were measured on a single GB10 with `max-num-seqs=32`:

| Workload | Latency |
|---|---|
| text, 1–5 questions | 0.09–0.22 s |
| document, 4–5 questions | 0.15–0.22 s |
| image, 2–4 questions | 0.15–0.36 s |

- Questions about the same `state` share the prefix cache, so batch them into one request instead of sending one request per question.
- `cache_salt` isolates the prefix cache per tenant in multi-tenant setups.
- `priority` (an integer) lets urgent decisions jump the queue when scheduling by priority.

## 6. Security

- **No auth by default.** vLLM serves without auth. Put it behind an API gateway, or start vLLM with `--api-key` (clients then send `Authorization: Bearer ...`).
- **`state` is untrusted input.** Scenario 07 shows the model *flagging* prompt injection, but decisions read from a text that tries to manipulate them can still be skewed. Keep policy in `instructions` and never let `state` override it.
- **NodePort is for labs only.** Use an Ingress or Gateway with TLS for anything shared.

## 7. Where to go next

- vLLM docs: [structured diffusion](https://docs.vllm.ai/en/latest/examples/features/structured_diffusion/)
- Wire the routing policy from section 1 into a real service: System 1 here, with a fallback to `/v1/chat/completions`.
- Grow `tools/build_collection.py` into your team's decision test suite.

[Back to the course overview](../README.md)
