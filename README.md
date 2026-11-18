# Fast "System 1" decisions with DiffusionGemma on vLLM

A hands-on course: deploy **DiffusionGemma-26B-A4B** on Kubernetes with **vLLM v0.34.0**, then use its native decision API (`/v1/systemone`) to make calibrated yes/no, choice and score decisions. The inputs can be text, JSON records, long documents or images, and each decision takes about **0.1–0.4 s**.

```
                      ┌──────────────── vLLM v0.34.0 (one pod, one GPU) ────────────────┐
 text / JSON /  ───►  │  POST /v1/systemone   noul · choice · score   (+ images)         │ ──► {"urgent": 0.998,
 document / images    │  POST /v1/decisions   OpenAI-style, text only                    │      "team": "infra",
                      │  POST /v1/chat/completions  normal generation                    │      "severity": 2.99}
                      └──────────────────────────────────────────────────────────────────┘
```

Each answer is a probability over **your** labels. You get no free text to parse, and you can threshold on confidence.

> **Why "System 1"?** It's the fast, intuitive mode of thinking: snap judgements made in a fraction of a second. Use it for routing, triage, filtering and gating. Send the low-confidence cases on to a slower "System 2" LLM or a person (lesson 8).

## Course

| # | Lesson | You will |
|---|---|---|
| 1 | [Deploy DiffusionGemma on vLLM](course/01-deploy.md) | download the model, deploy one pod on k8s, and verify it |
| 2 | [Your first decision](course/02-first-decision.md) | learn `noul` / `choice` / `score` and read every response field |
| 3 | [Text decisions](course/03-text-decisions.md) | triage, spam, moderation, intent, prompt-injection, fraud, tool routing, code review, PII, policy, joint reads |
| 4 | [Document decisions](course/04-document-decisions.md) | contracts, privacy policies, papers, email threads, postmortems |
| 5 | [Image decisions](course/05-image-decisions.md) | invoices, receipts, screenshots, charts, road scenes, forms, DLP, dashboards, phishing |
| 6 | [The `/v1/decisions` API](course/06-decisions-api.md) | use the OpenAI-style schema |
| 7 | [Testing](course/07-testing.md) | Postman, shell loops, the regression runner, CI |
| 8 | [Production tips and limits](course/08-production-tips.md) | confidence thresholds, question design, what System 1 can't do |

## Quick start

Lesson 1 has the full deploy steps.

```bash
# 1. model onto the GPU node (~19 GB)
hf download nvidia/diffusiongemma-26B-A4B-it-NVFP4 --revision ec4ff3df205028f4e81c954c2227f9312b3ec2ea
# 2. set hostPath.path in k8s/10-hf-cache.yaml to that HF cache directory  (CHANGE ME)
# 3. deploy
kubectl apply -k .
kubectl -n systemone rollout status deploy/diffusiongemma --timeout=30m
# 4. first decision
export SYSONE_URL=http://<node-ip>:30810
curl -s $SYSONE_URL/v1/systemone -H 'content-type: application/json' \
  -d @scenarios/01-support-ticket-triage/request.json | jq '.answers | map_values(.choice // .noul // .score)'
```

## 32 test scenarios

Every scenario has its own folder with a ready-to-send request and the recorded response. All of them are also in the Postman collection, with the response saved as an example.

| Area | Scenarios |
|---|---|
| Text | 01 ticket triage · 02 spam · 03 not-spam control · 04 review stars · 05 moderation · 06 intent routing · 07 prompt-injection guard · 08 card fraud · 09 agent tool router · 10 code review gate · 11 PII · 12 language · 13 refund policy · 14 joint read |
| Documents | 15 contract · 16 privacy policy · 17 research paper · 18 email thread · 19 postmortem |
| Images | 20 invoice · 21 invoice vs PO · 22 receipt · 23 error screenshot · 24 chart · 25 two charts · 26 road sign · 27 signed form · 28 confidential stamp · 29 dashboard · 30 phishing page |
| `/v1/decisions` | 31 predicate + choice + score · 32 message input |

**Recorded baseline:** 77/78 expected answers matched, with a median latency of 0.17 s on one NVIDIA GB10. [TESTING.md](TESTING.md) has every request and response, and [results/latest.md](results/latest.md) has the summary.

## Repository layout

```
├── README.md                     this page
├── course/                       lessons 01–08
├── kustomization.yaml            kubectl apply -k .
├── k8s/
│   ├── 00-namespace.yaml         namespace systemone
│   ├── 10-hf-cache.yaml          read-only PV/PVC over the node's HF cache   ← CHANGE ME
│   └── 20-vllm-diffusiongemma.yaml  vLLM Deployment + NodePort 30810
├── scenarios/NN-name/            endpoint.txt · request.json · response.json  (32 folders)
├── TESTING.md                    all scenarios: expected vs actual, request + response
├── postman/
│   ├── diffusiongemma-systemone.postman_collection.json
│   └── images/                   10 synthetic test images
├── results/                      run history + latest.md
└── tools/
    ├── build_collection.py       source of truth for scenarios; --run = regression test
    └── gen_images.py             renders the test images
```

## Tested environment

| | |
|---|---|
| Hardware | NVIDIA GB10 (DGX Spark), 121 GiB unified memory, arm64 |
| Kubernetes | k3s, NVIDIA container runtime (`runtimeClassName: nvidia`) |
| Image | `vllm/vllm-openai:v0.34.0` (multi-arch) |
| Model | `nvidia/diffusiongemma-26B-A4B-it-NVFP4` @ `ec4ff3df` (18 GiB loaded) |

Lesson 1 explains how to adapt the manifest to a discrete-GPU cluster.

## Notes

- All test images and documents are **synthetic**. Brands, people and figures are fictional.
- Decision support in vLLM comes from [vllm-project/vllm#57250](https://github.com/vllm-project/vllm/pull/57250), included since v0.31.0. See also the vLLM docs for [structured diffusion](https://docs.vllm.ai/en/latest/examples/features/structured_diffusion/).

## License

Apache-2.0, see [LICENSE](LICENSE).
