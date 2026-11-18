# System One decision run 20261117-231604

vLLM v0.34.0 · DiffusionGemma-26B-A4B NVFP4 · NVIDIA GB10 (DGX Spark)

**Expectations met: 77/78** across 32 requests. Latency median 0.13 s.

| # | Folder | Request | Latency | Answers (p / confidence) | Misses |
|---|---|---|---|---|---|
| 1 | Text decisions | Support ticket triage | 0.13 s | `urgent` = True (1.00)<br>`team` = infra (1.00)<br>`severity` = critical (1.00) |  |
| 2 | Text decisions | Spam filter | 0.10 s | `spam` = True (1.00) |  |
| 3 | Text decisions | Not spam (control) | 0.10 s | `spam` = False (0.00) |  |
| 4 | Text decisions | Product review sentiment (1-5 stars) | 0.11 s | `stars` = one (0.99)<br>`refund` = True (1.00) |  |
| 5 | Text decisions | Content moderation (multi-label) | 0.12 s | `insult` = True (1.00)<br>`threat` = True (0.98)<br>`spam` = False (0.00)<br>`action` = remove (1.00) |  |
| 6 | Text decisions | Chatbot intent routing | 0.10 s | `intent` = status (1.00) |  |
| 7 | Text decisions | Prompt-injection guard | 0.12 s | `injection` = True (1.00)<br>`risk` = critical (0.93) |  |
| 8 | Text decisions | Card transaction fraud check | 0.13 s | `fraud` = True (1.00)<br>`risk` = critical (1.00)<br>`action` = block (1.00) |  |
| 9 | Text decisions | Agent tool router | 0.11 s | `first_tool` = calculator (1.00)<br>`needs_calendar` = True (1.00) |  |
| 10 | Text decisions | Code review gate | 0.13 s | `security` = True (1.00)<br>`kind` = injection (0.29)<br>`merge` = changes (0.98) |  |
| 11 | Text decisions | PII detector | 0.12 s | `pii` = True (1.00)<br>`ssn` = True (1.00)<br>`redact` = redact (0.97) |  |
| 12 | Text decisions | Language detection | 0.09 s | `language` = spanish (1.00) |  |
| 13 | Text decisions | Refund policy with instructions | 0.10 s | `eligible` = False (0.00) |  |
| 14 | Text decisions | Joint read (all questions on one canvas) | 0.09 s | `urgent` = False (0.09)<br>`team` = billing (0.99)<br>`severity` = medium (0.62) |  |
| 15 | Document decisions | Contract clause review | 0.20 s | `auto_renews` = True (1.00)<br>`liability_cap` = True (1.00)<br>`exit` = False (0.00)<br>`law` = delaware (1.00)<br>`risk` = high (0.80) |  |
| 16 | Document decisions | Privacy policy compliance (GDPR-style) | 0.21 s | `retention_limit` = False (0.00)<br>`easy_deletion` = False (0.00)<br>`portability` = False (0.00)<br>`shares_ads` = True (1.00)<br>`compliance` = poor (1.00) |  |
| 17 | Document decisions | Research paper triage | 0.11 s | `field` = speech (1.00)<br>`empirical` = True (1.00)<br>`open_source` = True (1.00)<br>`relevance` = high (1.00) |  |
| 18 | Document decisions | Email thread: action items | 0.10 s | `action_required` = True (1.00)<br>`deadline` = True (1.00)<br>`open_question` = True (1.00)<br>`priority` = high (0.61) |  |
| 19 | Document decisions | Incident postmortem classification | 0.13 s | `root_cause` = deploy (1.00)<br>`detected_by_alert` = False (0.00)<br>`customer_impact` = True (1.00)<br>`severity` = sev1 (0.91) |  |
| 20 | Image decisions | Invoice image - accounts payable | 0.37 s | `is_invoice` = True (1.00)<br>`over_1000` = True (1.00)<br>`currency` = usd (0.99)<br>`paid` = False (0.00) |  |
| 21 | Image decisions | Invoice image vs purchase order (image + JSON) | 0.14 s | `vendor_match` = True (0.99)<br>`over_po` = False (0.00)<br>`action` = hold (0.63) | `over_po` expected True |
| 22 | Image decisions | Receipt - expense categorization | 0.35 s | `category` = meals (1.00)<br>`reimbursable` = True (0.99) |  |
| 23 | Image decisions | Error screenshot - incident severity | 0.36 s | `is_error` = True (1.00)<br>`component` = database (0.93)<br>`severity` = critical (1.00) |  |
| 24 | Image decisions | Chart reading - trend | 0.34 s | `trend` = up (1.00)<br>`q4_above_q1` = True (1.00) |  |
| 25 | Image decisions | Two images - compare charts | 0.29 s | `declining` = west (0.29) |  |
| 26 | Image decisions | Road scene - driving action | 0.34 s | `sign` = stop (1.00)<br>`action` = stop (1.00) |  |
| 27 | Image decisions | Signed form - KYC / onboarding check | 0.36 s | `signed` = True (0.99)<br>`tos` = True (1.00)<br>`marketing` = False (0.00)<br>`complete` = False (0.01) |  |
| 28 | Image decisions | Confidential stamp - DLP gate | 0.30 s | `confidential` = True (1.00)<br>`action` = block (1.00) |  |
| 29 | Image decisions | Monitoring dashboard - page on-call? | 0.29 s | `page` = True (1.00)<br>`health` = failing (0.91) |  |
| 30 | Image decisions | Phishing page screenshot | 0.35 s | `phishing` = True (1.00)<br>`asks_card` = True (1.00)<br>`urgency` = True (1.00) |  |
| 31 | OpenAI-style /v1/decisions (text only) | Decisions API - predicate + choice + score | 0.12 s | `refund` = True (1.00)<br>`reason` = damaged (1.00)<br>`anger` = angry (0.99) |  |
| 32 | OpenAI-style /v1/decisions (text only) | Decisions API - chat-style input messages | 0.11 s | `domain` = restaurant (1.00)<br>`has_time` = True (0.99) |  |

p = probability of the chosen label (yes-probability for yes/no, label softmax for choice/score).
Full responses, including `diagnostics.label_mass`, are in the matching run-*.json.
