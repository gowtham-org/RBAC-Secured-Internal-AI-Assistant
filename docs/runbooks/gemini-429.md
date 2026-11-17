# Runbook: RoleChatGeminiRateLimited

**Alert:** `RoleChatGeminiRateLimited` (warning)

## What it means
Google's API returned "rate limited" (HTTP 429) more than 5 times in 15 minutes. The free tier has a low per-minute and per-day request limit. **Every chat uses two Gemini calls** (one to embed the question, one to write the answer), so you hit the limit twice as fast as the user count suggests.

## What users experience
- Slow answers: the embedding code retries up to 8 times with growing waits (up to 60 seconds each).
- Failed answers (500) if the retries run out. That feeds the error-budget alerts too.

## First 5 minutes
1. On **RoleChat / Overview**, look at **"Gemini errors (per min)"**. The label tells you which call is limited:
   - `embedding / rate_limited`: the question-embedding call
   - `generation / rate_limited`: the answer call
2. Check your quota in Google AI Studio: https://ai.dev/rate-limit
3. Check who is sending traffic: "Requests by role (per min)". A spike from one role, or lots of failed logins, may be a script or someone testing.

## Fixes (cheapest first)
| Option | How | Trade-off |
|---|---|---|
| **Wait** | Per-minute limits reset within a minute. The daily limit resets once a day (Pacific time) | Free, but users wait |
| **Slow down** | Stop any load test or loop you are running | Free |
| **Different model** | Change `GEMINI_MODEL` in `k8s/base/backend-deploy.yaml` to a model with a higher free quota, then push (ArgoCD applies it) | Answer quality may change |
| **Enable billing** | In Google AI Studio, attach billing to the project | Costs money |

If you change code or config, remember the deployed pod only changes through git. A manual `kubectl edit` will be reverted by ArgoCD.

## Confirm it is fixed
"Gemini errors (per min)" returns to zero and answer times drop back. The alert clears 15 minutes after the last 429.