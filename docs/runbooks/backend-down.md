# Runbook: RoleChatBackendDown

**Alert:** `RoleChatBackendDown` (critical)

## What it means
Prometheus cannot scrape the backend's metrics endpoint (port 9100) for 3 minutes, or the target has disappeared. Most of the time that means the backend is down or not ready, so users cannot chat.

## First 5 minutes
```bash
kubectl get pods -n rolechat
kubectl get application rolechat -n argocd
```

| What you see | Meaning | Next step |
|---|---|---|
| Backend pod `0/1 Running` | Readiness probe failing (`/healthz`) | `kubectl logs -n rolechat deploy/rolechat-backend --tail=50` |
| `CrashLoopBackOff` / `Error` | App crashing on start | Read logs. Common: missing `GOOGLE_API_KEY`, bad users file, Chroma path problem |
| `OOMKilled` in `kubectl describe pod` | Hit the 1Gi memory limit | Raise the limit in `k8s/base/backend-deploy.yaml` (via git) |
| `Pending` | No room or PVC problem | `kubectl describe pod -n rolechat <pod>`, look at Events. Check `docker stats --no-stream minikube` |
| Pod is `1/1 Running` and users can chat | Only the **metrics** scrape is broken | See "Pod is fine but target is down" |
| No pods at all | ArgoCD app out of sync or deleted | `kubectl get application rolechat -n argocd`, check sync status |

## Pod is fine but target is down
```bash
kubectl get servicemonitor -n rolechat
kubectl port-forward -n rolechat deploy/rolechat-backend 9100:9100
curl -s localhost:9100/metrics | head
```
- If `curl` works, the app is fine. Check the Service has a port named `metrics` and the label `app: rolechat-backend`.
- If `curl` fails, the metrics server did not start. Look for `could not start metrics server` in the logs, and check `METRICS_PORT=9100` is set on the deployment.

## If the whole cluster is down
After a laptop reboot or sleep: `minikube start`, then `kubectl get pods -A` and wait for everything to come back. If you changed Minikube's memory with `docker update`, re-check it, because it may reset on restart:
```bash
docker inspect minikube --format 'mem={{.HostConfig.Memory}}'
```

## Limitation
If Prometheus itself is down, this alert cannot fire. An outside check on the public `/healthz` (a free uptime monitor) would cover that gap.

## Confirm it is fixed
`up{job="rolechat-backend"}` returns 1 in Prometheus, and a test chat works.