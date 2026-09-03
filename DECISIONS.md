# Design Decisions & Trade-offs

A running log of choices made in this project, what was given up,
and what would change in production.

---

## Deployment

**Minikube on a local machine, not a managed cluster.**
Chosen to avoid cloud costs. Trade-off: the whole stack depends on one
laptop being powered on and a specific process running. Not a security
control — just downtime. In production this would be EKS with the app
reachable independent of any workstation.

**Cloudflare Tunnel as the public entry point.**
Gives a stable HTTPS endpoint with no inbound firewall rule and no
exposed home IP, since the tunnel dials out. Trade-off: hard dependency
on Cloudflare and on the local cluster. On AWS this would be replaced by
Route53 → ALB (via the AWS Load Balancer Controller) → nginx ingress →
Service → pods.

**ChromaDB on a ReadWriteOnce PVC.**
Chroma persists its index to local disk; without a volume, a pod restart
loses it and the embed job has to re-run. The limitation: RWO means one
replica only — the deployment cannot scale horizontally as written.
Scaling would require running Chroma as a StatefulSet server or moving
to a managed vector store (pgvector, OpenSearch).

**Deploys via `kubectl set image` from a self-hosted runner.**
Works, but leaves no declared desired state, no audit trail, and no
clean rollback. The image tag in `backend-deploy.yaml` and the tag CI
sets can drift apart. Being replaced with ArgoCD.

---

## Security

**Passwords hashed with bcrypt, not encrypted.**
The app must *verify* passwords, not read them. Encryption would require
the app to hold a decryption key at runtime, so anyone with pod access
would get every password in plaintext. Hashing leaves nothing to steal.

**SOPS + age for the source passwords.**
Separate problem from verification: occasionally a human needs to read a
password back. `secrets.enc.yaml` holds them encrypted; the age private
key never enters the repo. Committed encrypted so the file is safe to
publish.

**Demo credentials removed from the README.**
They were published alongside a live endpoint, including the c-level
account with unrestricted document access — a documented bypass of the
exact control this project exists to demonstrate. Old passwords remain
in git history, which is why they were rotated rather than just deleted:
the hashes make the historical plaintext worthless.

**Free tier, no billing account attached.**
So the exposure was never a runaway bill — it was quota exhaustion
(anyone could burn the daily request limit) plus full document read
access. A budget must be set before billing is ever enabled.

---

## Bugs found and fixed

**Authentication bypass on `/chat`.**
The endpoint took the user's role from the JSON request body and never
verified it:

```python
user = data["user"]              # client-supplied
user_role = user["role"].lower() # trusted
```

An unauthenticated POST claiming `c-levelexecutives` returned HR salary
data. The Streamlit UI concealed this because it only sent roles obtained
from a real login — but the frontend is one client among many, and any
control living in the client is not a control. Fixed by adding
`Depends(authenticate)` to `/chat` so the role comes from the verified
session.

Notably, hardening the login with bcrypt did nothing for this. The
password was never the control that was failing.

**Error messages pointing at the wrong cause.**
Three separate times, a misleading message slowed down diagnosis:

- "Check your quota" — actually a stray comma in the API key
- "Invalid credentials" — actually the backend being unreachable
- A broad `except Exception` returning HTTP 200 with an error string,
  hiding real failures from both the client and the logs

Fixed by separating connection errors from auth errors in the frontend,
and by logging tracebacks and returning proper status codes in the
backend. Contrast: `KeyError: 'password'` took four seconds to diagnose
because it failed loudly at a specific line. Loud failures beat silent
wrong answers.

**Key naming as a safety net.**
Renaming `password` → `password_hash` in the config map was deliberate.
Keeping the old name would have let stale comparison code run and
silently return False for every login. The rename turned that into an
immediate `KeyError` with a file and line number.

---

## Known gaps

- No automated tests covering auth or RBAC. The suite currently asserts
  `1 + 1 == 2` while CI reports green — worse than no tests, because it
  looks like coverage.
- No rate limiting. Free-tier quota can be exhausted by anyone with
  valid credentials.
- HTTP Basic auth rather than short-lived tokens. No expiry, no
  revocation short of rotating the hash.
- No prompt-injection defense. A malicious document in `resources/data/`
  could attempt to override the system prompt.
- No metrics or tracing. No visibility into latency, retrieval quality,
  or token spend per user.
- No image scanning or pinned base image digest in CI.