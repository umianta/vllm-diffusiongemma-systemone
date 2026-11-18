# Lesson 4: Document decisions

**Goal:** ask many questions about one long document (a contract, policy, paper, email thread or postmortem) in a single fast request.
**Files:** `scenarios/15` to `scenarios/19`

## How it works

Put the document in `state` (as a string, or as `{"document": "..."}`) and ask as many questions as you need, up to 64. The document is encoded **once**. With `--enable-prefix-caching`, every question reuses that KV cache, so five questions about a contract cost barely more than one. Scenario 15 answers 5 questions about a contract in **0.21 s**.

```json
{
  "model": "diffusiongemma",
  "instructions": "You review vendor contracts for a procurement team.",
  "state": {"document": "MASTER SERVICES AGREEMENT (excerpt)\n4.2 Term. ... renews automatically ...\n9.3 Limitation of Liability ...\n14.1 Governing Law. ... Delaware ..."},
  "questions": {
    "auto_renews":   {"type": "noul", "instructions": "Does the contract renew automatically?"},
    "liability_cap": {"type": "noul", "instructions": "Is there a cap on liability?"},
    "exit":          {"type": "noul", "instructions": "Can the customer terminate for convenience?"},
    "law":           {"type": "choice", "instructions": "Which law governs the agreement?",
                      "criteria": {"delaware": null, "california": null, "england": null, "texas": null}},
    "risk":          {"type": "score", "instructions": "Overall commercial risk to the customer",
                      "criteria": ["low", "medium", "high", "critical"]}
  }
}
```

## The scenarios

| # | Document | Questions | Recorded result |
|---|---|---|---|
| 15 | Contract excerpt | auto-renew? · cap? · exit? · governing law · risk | yes · yes · no · `delaware` · high |
| 16 | Privacy notice | retention limit? · easy deletion? · portability? · ads sharing? · GDPR score | no · no · no · yes · `poor` |
| 17 | Research abstract | field · empirical? · code released? · relevance | `speech` · yes · yes · high |
| 18 | Email thread | action required? · deadline? · open question? · priority | yes · yes · yes · high |
| 19 | Incident postmortem | root cause · caught by alert? · customer impact? · severity | `deploy` · no · yes · `sev1` |

## Patterns

- **Turn a checklist into questions.** A compliance checklist (scenario 16) maps one-to-one onto `noul` questions. You get a calibrated probability per item instead of a free-text summary you'd have to parse.
- **Fit the scale to the domain.** Scenario 16 uses `["poor", "weak", "fair", "good"]` and scenario 19 uses `["sev4", "sev3", "sev2", "sev1"]`. Order levels from least to most, because `score` is the expected index.
- **Ask about what's missing.** "Is there an unanswered question in the thread?" (scenario 18) and "Was it detected by an alert?" (scenario 19) require reasoning about absence. Both were answered correctly.
- **Use `instructions` for the reader's role.** "You review vendor contracts for a procurement team" frames what "risk" means.

## Long documents

The server runs with `--max-model-len=16384` tokens. For longer documents:

1. Split the document into sections and ask the same questions per section. Take the max for "does any clause...?" questions.
2. Or raise `--max-model-len` (lesson 1) if you have memory for the KV cache.

## Exercises

1. **Scenario 15:** add `"Does the provider have the right to raise prices?"` (the excerpt says up to 12% at renewal).
2. **Scenario 16:** rewrite the privacy notice to be compliant, adding a 2-year retention period and an online "delete my account" button. Re-run it. Does `compliance` move to `good`?
3. **Scenario 19:** add a `choice` for "which team should own the follow-up", with `payments`, `sre` and `qa`.
4. Take a real document from your own work, such as an RFC, a runbook or a design doc, and write 5–10 checklist questions for it.

Next: [Lesson 5: Image decisions](05-image-decisions.md)
