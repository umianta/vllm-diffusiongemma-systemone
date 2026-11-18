# Lesson 1: Deploy DiffusionGemma on vLLM

**Goal:** a running vLLM server on Kubernetes that answers `POST /v1/systemone`.
**Time:** about 20 minutes, plus the model download.

## What you're deploying

DiffusionGemma-26B-A4B is a *diffusion* language model. A normal LLM writes one token at a time. DiffusionGemma fills a fixed-width "canvas" of tokens in parallel and refines it over a few denoising steps. For decisions, that means the model can read the probability of every allowed answer (yes/no, one of N options, a level on a scale) in a single short pass. That's why decisions come back in roughly 0.1–0.4 s.

vLLM (v0.31.0 and later) ships the decision API natively. `vllm serve` exposes:

| Route | Purpose |
|------|------|
| `POST /v1/systemone` | Jev-style structured decisions: text, JSON, documents, images |
| `POST /v1/decisions` | OpenAI-style decisions: text only |
| `POST /v1/chat/completions` | ordinary generation |

Only one container is needed: no sidecar and no front-end service.

## Prerequisites

| Need | Notes |
|------|------|
| Kubernetes with an NVIDIA GPU | written for k3s on an NVIDIA GB10 (DGX Spark); see "Other clusters" below |
| About 60 GiB of GPU memory | 18 GiB of weights plus KV cache |
| An NVFP4-capable (Blackwell) GPU | the checkpoint is NVFP4 |
| About 19 GB of disk on the GPU node | for the model |
| `kubectl`, and `hf` (huggingface_hub CLI) on the node | |

## Step 1: Download the model onto the GPU node

```bash
pip install -U "huggingface_hub[cli]"
hf download nvidia/diffusiongemma-26B-A4B-it-NVFP4 \
  --revision ec4ff3df205028f4e81c954c2227f9312b3ec2ea
ls ~/.cache/huggingface/hub/models--nvidia--diffusiongemma-26B-A4B-it-NVFP4/snapshots/
# ec4ff3df205028f4e81c954c2227f9312b3ec2ea
```

The model is mounted read-only from this cache, so the pod never downloads anything and works with no internet access.

## Step 2: Point the PV at your cache

Edit `k8s/10-hf-cache.yaml` and set `hostPath.path` to **your** cache directory, for example `/home/<you>/.cache/huggingface`. The line is marked `CHANGE ME`.

## Step 3: Pre-pull the image

The image is about 11 GB. Pull it before you deploy, so the startup probe isn't spent waiting on the download.

```bash
sudo k3s crictl pull docker.io/vllm/vllm-openai:v0.34.0     # k3s
# docker pull vllm/vllm-openai:v0.34.0                      # plain Docker / kind
```

`v0.34.0` is a multi-arch tag, so it covers both arm64 (GB10) and amd64.

## Step 4: Free the GPU

On a single shared GPU, stop anything else that holds GPU memory, then drop the page cache. On unified-memory systems such as the GB10, the page cache counts as "used".

```bash
kubectl get pods -A | grep -iE "vllm|kserve"     # find other GPU servers and scale them to 0
sudo sysctl vm.drop_caches=1
```

## Step 5: Apply

```bash
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml     # k3s
kubectl apply -k .
kubectl -n systemone rollout status deploy/diffusiongemma --timeout=30m
```

Startup takes about 2–3 minutes. Follow it with `kubectl -n systemone logs -f deploy/diffusiongemma`:

```
Loading weights took 17.21 seconds
Model loading took 18.16 GiB memory and 20.04 seconds
...
Application startup complete.
```

## Step 6: Verify

```bash
export SYSONE_URL=http://<node-ip>:30810      # NodePort; use http://localhost:30810 on the node
curl -s $SYSONE_URL/health -o /dev/null -w "%{http_code}\n"     # 200
curl -s $SYSONE_URL/v1/models | jq -r '.data[].id'               # diffusiongemma
```

## Reading the manifest

Here are the important lines in `k8s/20-vllm-diffusiongemma.yaml` and why each one is there:

| Setting | Why |
|------|------|
| `runtimeClassName: nvidia`, **no** `nvidia.com/gpu` request | The GB10 device plugin advertises 0 GPUs, so a request would stay Pending forever. The NVIDIA runtime injects the GPU directly. |
| `--diffusion-config={"canvas_length": 64}` | width of the diffusion canvas that decisions are read from |
| `--max-logprobs=32` | decision reads score every label, so they need logprobs |
| `--attention-backend=TRITON_ATTN` | FlashInfer can't serve this model |
| `--gpu-memory-utilization=0.5` | about 60 GiB of the 121 GiB unified memory |
| `--enable-prefix-caching` | questions that share the same input reuse its KV cache |
| `strategy: Recreate` | a rolling update would run two copies on one GPU and OOM |
| `HF_HUB_OFFLINE=1` | never call out to Hugging Face at runtime |

### Other clusters

On a normal discrete-GPU cluster:

1. Delete `runtimeClassName` and the `NVIDIA_*` env vars.
2. Add `resources.limits: {nvidia.com/gpu: 1}`.
3. Raise `--gpu-memory-utilization` to about 0.9 if the GPU is dedicated.
4. Replace the hostPath PV with a normal PVC that you fill once with a download Job.

## Undeploy

```bash
kubectl delete -k .        # the model cache on the node is untouched
```

## Exercises

1. Find the line in the startup logs that reports how much KV-cache memory vLLM allocated. How many concurrent 16k-token requests would fit?
2. Lower `--gpu-memory-utilization` to 0.35 and redeploy. Does the server still start? What did the KV-cache size change to?

Next: [Lesson 2: Your first decision](02-first-decision.md)
