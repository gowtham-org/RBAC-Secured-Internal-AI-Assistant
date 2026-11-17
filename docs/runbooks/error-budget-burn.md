# Runbook: RoleChatErrorBudgetFastBurn / RoleChatErrorBudgetSlowBurn

**Alerts:** `RoleChatErrorBudgetFastBurn` (critical), `RoleChatErrorBudgetSlowBurn` (warning)
**SLO:** 99% of `/chat` requests must not return a 5xx.

## What it means
Users are getting server errors on `/chat`. Wrong passwords (401) do **not** count, only 5xx.
- **FastBurn:** over 14.4% of requests are failing right now. The monthly budget is gone in about 2 days at this rate. Act now.
- **SlowBurn:** over 6% have failed over the last 6 hours. Not an emergency, but fix it this week.

Both alerts are ignored when there are fewer than 10 `/chat` requests in the last hour.

## First 5 minutes
1. Open the **RoleChat / Overview** dashboard. Check "/chat requests by status" and "Gemini errors".
2. Read the backend logs for the real error:
   ```bash
   kubectl logs -n rolechat deploy/rolechat-backend --tail=100 | grep -i -E "error|failed|exception"
   ```
   The app logs `chat failed for user=...` with the full traceback for every 500.
3. Check the pod is healthy: `kubectl get pods -n rolechat`

## Likely causes
| What you see | Cause | Fix |
|---|---|---|
| Gemini errors panel is non-zero, `rate_limited` | Free-tier quota exhausted | Follow [gemini-429.md](gemini-429.md) |
| Traceback from `generate_content` with 5xx from Google | Gemini outage on Google's side | Check https://status.cloud.google.com, wait, nothing to fix on our side |
| `RuntimeError: Embedding failed after 8 retries` | Embedding quota or outage | Same as above, see [gemini-429.md](gemini-429.md) |
| Chroma or SQLite errors, "database is locked" | The embed job and the backend are both using `chroma-pvc` | Check no embed Job is running: `kubectl get jobs -n rolechat`. If one is, wait for it to finish |
| Errors started right after a deploy | Bad release | Roll back (below) |
| `users.json` / file not found errors | The `chatbot-users` secret did not mount | `kubectl describe pod -n rolechat -l app=rolechat-backend` |

## Rolling back a bad release
The deployed image tag lives in `k8s/base/kustomization.yaml`. Revert the CI commit that bumped it:
```bash
git log --oneline -5 -- k8s/base/kustomization.yaml
git revert <sha-of-the-bump-commit>
git push
```
ArgoCD syncs it automatically. **Do not use `kubectl rollout undo`.** ArgoCD has `selfHeal` on and will undo your rollback within seconds.

## Confirm it is fixed
- The `Server error ratio (5xx)` panel returns to about 0%.
- The alert clears on its own after the error rate stays low for a while. FastBurn clears first (5m window), SlowBurn can take up to a few hours (6h window).