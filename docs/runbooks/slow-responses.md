# Runbook: RoleChatLatencySLOBurn

**Alert:** `RoleChatLatencySLOBurn` (warning)
**SLO:** 95% of `/chat` requests finish in under 10 seconds.

## What it means
More than 30% of requests have taken over 10s, for both the last 30 minutes and the last 6 hours. Answers still arrive, but users are waiting. Ignored when there are fewer than 10 `/chat` requests in the last hour.

## First 5 minutes: find which part is slow
Open **RoleChat / Overview** and read the panel **"Where the time goes: retrieval vs Gemini (p95)"**. It has three lines:

| Line | If this one is high |
|---|---|
| **Gemini answer** | Gemini itself is slow. Go to "Gemini is slow" below |
| **of which: embedding call** | The embedding call to Google is slow or retrying on 429s. See [gemini-429.md](gemini-429.md) |
| **retrieval (embed + Chroma)** is high but the embedding line is low | Chroma search is slow (the gap between the two lines is the Chroma time). Go to "Chroma is slow" below |

## Gemini is slow
- Check https://status.cloud.google.com for an incident.
- Large prompts are slower: the "Gemini tokens (per min)" panel shows input size. Very long retrieved context means slower answers.
- Nothing to fix on our side if Google is slow. If it keeps happening, consider a faster model by changing `GEMINI_MODEL` in `k8s/base/backend-deploy.yaml` (through git, so ArgoCD applies it).

## Chroma is slow
- The index lives on a PVC on your laptop's disk. Check the laptop is not under heavy load: `docker stats --no-stream minikube`.
- Check nobody is running the embed job at the same time: `kubectl get jobs -n rolechat`.

## The backend itself is starved
- CPU throttling: the pod is limited to 1 CPU. In Prometheus: `rate(container_cpu_cfs_throttled_seconds_total{namespace="rolechat"}[5m])`. (Per-container labels are missing on Minikube's docker driver, so filter by `pod` instead.)
- Minikube memory: it is capped at 5 GB. If it is near the cap, everything slows down. Check `docker stats --no-stream minikube`.
- Known caveat: `/chat` is `async` but makes blocking calls. A few slow requests at once can hold up others, including `/healthz`. If latency is bad **and** the pod shows readiness failures, this is the likely cause.

## Confirm it is fixed
The "Chat latency" panel drops back under the red 5s/10s lines. The alert clears after the 6-hour window recovers.