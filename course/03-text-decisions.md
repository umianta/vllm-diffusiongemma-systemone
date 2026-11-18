# Lesson 3: Text decisions

**Goal:** apply the three question types to real tasks such as routing, filtering, moderation, guarding and fraud. Learn the request features that make answers better: `criteria` descriptions, JSON `state`, top-level `instructions`, and `joint` reads.
**Files:** `scenarios/01` to `scenarios/14`

Run a scenario with:

```bash
s=scenarios/07-prompt-injection-guard
curl -s $SYSONE_URL/v1/systemone -H 'content-type: application/json' -d @$s/request.json \
  | jq '.answers | map_values(.choice // .noul // .score)'
```

## The scenarios

The results below come from the recorded run. The full responses are in each folder's `response.json`.

| # | Scenario | Pattern | Result |
|---|---|---|---|
| 01 | Support ticket triage | noul + choice + score on one input | urgent 1.00 · `infra` · critical |
| 02 | Spam filter | noul with `{"true","false"}` criteria | spam 1.00 |
| 03 | Not spam (control) | always test the negative case too | spam 0.00 |
| 04 | Review sentiment | 5-level `score` | `one` star (0.99) · refund 1.00 |
| 05 | Content moderation | several independent policy flags + action | insult, threat · `remove` |
| 06 | Chatbot intent routing | `choice` with descriptions | `status` |
| 07 | Prompt-injection guard | `instructions` sets the role | injection 1.00 · critical |
| 08 | Card fraud | JSON feature record as `state` | fraud 1.00 · `block` |
| 09 | Agent tool router | System 1 step in front of an LLM agent | `calculator` first · calendar later |
| 10 | Code review gate | a diff as `state` | security · `injection` · `changes` |
| 11 | PII detector | gate before logging | pii, ssn · `redact` |
| 12 | Language detection | labels with `null` descriptions | `spanish` |
| 13 | Refund policy | **rules** in `instructions`, facts in `state` | eligible 0.00 (gift cards excluded) |
| 14 | Joint read | `joint: true` | `billing` · medium |

## Patterns

### 1. Describe the labels, keep them short

From scenario 06:

```json
"intent": {"type": "choice", "instructions": "What does the customer want?",
  "criteria": {"status": "where is my order / tracking", "refund": "money back",
               "cancel": "cancel an order", "technical": "product not working", "human": "asks for a person"}}
```

The label (`status`) is what gets scored, and the description gives it meaning. Without descriptions, `status` vs `technical` is ambiguous.

### 2. Structured input works as-is

From scenario 08:

```json
"state": {"amount_usd": 4890, "merchant": "electronics, online", "card_country": "US", "ip_country": "RO",
          "account_age_days": 2, "txns_last_hour": 9, "shipping_matches_billing": false}
```

There's no need to turn the record into prose: send the JSON your system already has.

### 3. Put policy in `instructions` and facts in `state`

From scenario 13:

```json
"instructions": "Refund policy: full refund within 30 days of delivery if the item is unused. Opened software and gift cards are never refundable. ...",
"state": {"item": "gift card", "days_since_delivery": 5, "condition": "unused", "reason": "changed my mind"}
```

The model correctly answers *not eligible* (P(yes) = 0.00), even though every other fact (5 days, unused) points to "eligible". Keeping rules apart from data means you can change the policy without touching your data pipeline.

### 4. Pair a binary flag with an action

Scenarios 05, 08 and 11 ask both "is it X?" (`noul`) and "what should we do?" (`choice`). The flag gives you a calibrated probability for metrics. The action gives you something to execute.

### 5. Joint reads

From scenario 14:

```json
{"joint": true, "state": {...}, "questions": {...}}
```

By default each question is read on its own (sharing the input's KV cache). With `joint: true`, all answers are filled in on **one** diffusion canvas, so they can influence each other. The response then includes `joint.canvases` with each question's slot. Use joint reads when answers must be consistent with each other. Use independent reads when each answer should stand alone. Compare scenario 01 and scenario 14: with the joint read, the double-charge ticket came out `urgent` 0.11 and `severity` medium.

## Watch the diagnostics

Scenario 10 got all three answers right, but look at `diagnostics`:

```json
"security": {"label_mass": 0.01, "argmax_is_label": false},
"kind":     {"label_mass": 0.03, ...},
"merge":    {"label_mass": 1.00, ...}
```

Only 1–3% of the model's probability landed on the offered labels for `security` and `kind`. The label softmax still picked the right one, but the model "wanted" to say something else, so `confidence` is low. Don't automate on answers like that. Rephrase the question, for example "Is this code vulnerable to SQL injection?", or change the labels. Lesson 8 covers this in depth.

## Exercises

1. **Scenario 06:** add an `"address"` intent ("change shipping address") and test a message that needs it.
2. **Scenario 08:** set `account_age_days` to 900, `ip_country` to `"US"` and `txns_last_hour` to 1. How far does P(fraud) move?
3. **Scenario 13:** change the item to `"headphones"` with condition `"damaged on arrival"`. The answer should flip to eligible.
4. **Scenario 10:** reword `security` until `label_mass` is above 0.9.
5. Build your own: an "escalate to a manager?" `noul` for HR chat messages, with `true`/`false` criteria.

Next: [Lesson 4: Document decisions](04-document-decisions.md)
