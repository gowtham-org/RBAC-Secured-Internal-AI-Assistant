# README Update Guide — GitOps + SOPS Migration

What changed in the project, and exactly which README sections to edit.
Each block below is ready to paste.

---

## Summary of what we changed

| Area | Before | After |
|---|---|---|
| User store | `ConfigMap` with bcrypt hashes, plaintext in git | SOPS-encrypted `Secret` (`k8s/secrets/users-secret.enc.yaml`) |
| Gemini API key | Manually created Secret, not in git | SOPS-encrypted `Secret` in git |
| Cloudflared creds/config | Manually created, not in git | SOPS-encrypted Secrets in git |
| Manifest layout | Flat `k8s/*.yaml` | Kustomize: `k8s/base/`, `k8s/secrets/`, `k8s/jobs/` |
| Secret decryption | `sops -d \| kubectl apply` in CI on the laptop | KSOPS plugin inside the ArgoCD repo-server |
| Deployment | CI ran `kubectl set image` via self-hosted runner | GitOps — CI bumps the image tag in git, ArgoCD syncs |
| Deploy runner | Self-hosted runner on the laptop (required online) | GitHub-hosted runner; ArgoCD pulls from git |
| Image tag | Mutable `1.9` / `latest` in the manifest | Immutable git SHA, tracked in `k8s/base/kustomization.yaml` |
| Drift | Undetected | ArgoCD self-heal reverts out-of-band changes |
| Embed job | Applied with every deploy | Manual one-off in `k8s/jobs/` (hash-named automation planned) |
| Role validation | None | `ALLOWED_ROLES` + `disabled` flag in `users_loader.py` |

---

## 1. Section `## 🏗 Project Structure` (line ~134)

Replace the tree with:

```
RBAC-Secured-Internal-AI-Assistant/
├── .github/workflows/
│   └── cicd.yml                      # CI: test, build, push, bump image tag in git
├── app/
│   ├── embed_documents.py            # builds the Chroma vector DB
│   ├── frontend.py                   # Streamlit UI
│   ├── google_embeddings.py          # Gemini embeddings wrapper
│   ├── main.py                       # FastAPI backend
│   └── users_loader.py               # auth + role validation
├── argocd/
│   ├── values.yaml                   # ArgoCD Helm values (KSOPS init container, age key mount)
│   └── rolechat-app.yaml             # ArgoCD Application definition
├── k8s/
│   ├── kustomization.yaml            # root overlay — ArgoCD points here
│   ├── base/
│   │   ├── kustomization.yaml        # resource list + image tag (CI updates this)
│   │   ├── backend-deploy.yaml
│   │   ├── chroma-pvc.yaml
│   │   └── cloudflared-deploy.yaml
│   ├── secrets/
│   │   ├── kustomization.yaml
│   │   ├── secret-generator.yaml     # KSOPS generator
│   │   ├── users-secret.enc.yaml     # SOPS-encrypted
│   │   ├── google-api-secret.enc.yaml
│   │   ├── cloudflared-creds.enc.yaml
│   │   └── cloudflared-config.enc.yaml
│   └── jobs/
│       └── embed-job.yaml            # run manually when documents change
├── credentials/
│   └── user-passwords.enc.yaml       # SOPS-encrypted record of user passwords
├── resources/data/                   # department document folders
├── scripts/
│   └── hash_password.py              # generate a bcrypt hash for a new user
├── tests/
├── .sops.yaml                        # SOPS creation rules
├── Dockerfile
└── README.md
```

---

## 2. Section `## ⚙️ CI/CD Pipeline (GitHub Actions)` (line ~171)

Replace everything from this heading down to `### PR Workflow for Contributors`
(this removes the self-hosted runner setup, the start/stop scripts, and the
machine-state table, which no longer apply to deploys).

```markdown
## ⚙️ CI/CD Pipeline (GitOps with ArgoCD)

Deployment is **pull-based**. CI never talks to the cluster — it only updates
git. ArgoCD, running inside the cluster, notices the change and applies it.

### Pipeline flow

```
push to main
    │
    ▼
[ CI — GitHub-hosted runner ]
  pytest → docker build → push to Docker Hub (latest + <git-sha>)
    │
    ▼
[ CD — GitHub-hosted runner ]
  kustomize edit set image <repo>:<git-sha>
  commit "chore: bump image to <sha> [skip ci]" → push
    │
    ▼
[ ArgoCD — in-cluster ]
  detects the new commit → kustomize build (KSOPS decrypts secrets)
  → applies to the rolechat namespace → rolling update
```

### Why pull-based

- **No laptop needed to deploy.** CI runs entirely on GitHub's runners.
- **Git is the single source of truth.** What's in `k8s/` is what's running.
- **Drift is caught.** `selfHeal` reverts anything changed with `kubectl`.
- **Rollback is a git revert.** No manual `kubectl set image`.

### Image tags

| Tag | Purpose |
|---|---|
| `latest` | convenience only — never deployed |
| `<git-sha>` | immutable, this is what gets deployed |

The deployed tag lives in `k8s/base/kustomization.yaml` under `images[].newTag`,
so `git log -p k8s/base/kustomization.yaml` is a full deployment history.

### Rollback

```bash
# find the commit that set the previous tag
git log --oneline -- k8s/base/kustomization.yaml

# revert it
git revert <commit-sha>
git push
```

ArgoCD syncs the previous image within ~3 minutes. Or use
**History and Rollback** in the ArgoCD UI for an immediate revert.

### GitHub Secrets required

| Secret | Purpose |
|---|---|
| `DOCKER_USERNAME` | Docker Hub login |
| `DOCKER_PASSWORD` | Docker Hub token |
| `DOCKER_IMAGE` | full image name, e.g. `user/role-chatbot-api` |

The age private key is **not** a GitHub Secret. It never leaves the laptop and
the cluster — CI has no access to any encrypted secret.
```

---

## 3. Section `### Secrets handling` (line ~369)

Replace with:

```markdown
### Secrets handling

All secrets live in git, encrypted with [SOPS](https://github.com/getsops/sops)
and [age](https://github.com/FiloSottile/age). Nothing is ever committed in
plaintext.

| Secret | File | What it holds |
|---|---|---|
| `chatbot-users` | `k8s/secrets/users-secret.enc.yaml` | usernames, bcrypt hashes, roles |
| `google-api` | `k8s/secrets/google-api-secret.enc.yaml` | Gemini API key |
| `cloudflared-creds` | `k8s/secrets/cloudflared-creds.enc.yaml` | tunnel credentials |
| `cloudflared-config` | `k8s/secrets/cloudflared-config.enc.yaml` | tunnel config |

**Two layers of protection:**

1. **SOPS/age** encrypts the file in git. Only `data` / `stringData` is
   encrypted, so `kind`, `name` and `namespace` stay readable and diffs are
   reviewable.
2. **bcrypt** hashes the passwords themselves. Even someone with
   `kubectl get secret` access sees hashes, never usable passwords.

**Decryption at deploy time:** the ArgoCD repo-server runs the
[KSOPS](https://github.com/viaduct-ai/kustomize-sops) kustomize plugin. It
decrypts in memory during `kustomize build` — plaintext never touches disk and
never enters git or CI.

**.sops.yaml rules** (order matters — SOPS uses the first match):

```yaml
creation_rules:
  # K8s Secret manifests — encrypt only the data
  - path_regex: k8s/.*\.enc\.yaml$
    encrypted_regex: ^(data|stringData)$
    age: <your age public key>

  # Everything else — encrypt all values
  - path_regex: .*\.enc\.yaml$
    age: <your age public key>
```

**Role validation:** `users_loader.py` checks each role against `ALLOWED_ROLES`
and honours a `"disabled": true` flag, so a typo in the secret fails loudly
instead of silently granting the wrong access.
```

---

## 4. Section `### Recommended hardening (next steps)` (line ~377)

Replace the list with what's done vs. still open:

```markdown
### Hardening status

**Done**

- [x] Secrets encrypted at rest in git (SOPS + age)
- [x] Passwords stored as bcrypt hashes, never plaintext
- [x] Role allow-list validation + per-user disable flag
- [x] Rate limiting on the API
- [x] GitOps deploys — no cluster credentials in CI
- [x] Immutable SHA-tagged images with git-tracked deploy history

**Next**

- [ ] Replace HTTP Basic auth with short-lived JWTs
- [ ] Audit log of every query (user, role, documents retrieved, allow/deny)
- [ ] NetworkPolicies between the backend and the vector DB
- [ ] Prometheus / Grafana metrics and SLOs
- [ ] RAG evaluation (RAGAS) gating in CI
```

---

## 5. Section `## ☸️ Kubernetes Deployment (Minikube)` (line ~424)

Replace the manual `kubectl apply` sequence with:

```markdown
## ☸️ Kubernetes Deployment (Minikube + ArgoCD)

### Prerequisites

```bash
minikube start --cpus=4 --memory=8g
# sops, age and kustomize installed locally
# your age private key at ~/.config/sops/age/keys.txt
```

### 1. Install ArgoCD with KSOPS support

```bash
kubectl create namespace argocd

# bootstrap the age key — the only manual secret, by necessity:
# the key that decrypts everything else cannot itself be stored encrypted
kubectl create secret generic sops-age -n argocd \
  --from-file=keys.txt=$HOME/.config/sops/age/keys.txt

helm repo add argo https://argoproj.github.io/argo-helm && helm repo update
helm install argocd argo/argo-cd -n argocd -f argocd/values.yaml
```

`argocd/values.yaml` does three things:

- an init container copies the `ksops` binary into the repo-server
- `kustomize.buildOptions: --enable-alpha-plugins --enable-exec` allows the plugin to run
- mounts the age key and sets `SOPS_AGE_KEY_FILE`

### 2. Create the Application

```bash
kubectl apply -f argocd/rolechat-app.yaml
```

ArgoCD then watches `k8s/` on `main` and syncs automatically, with `selfHeal`
reverting any out-of-band `kubectl` change.

### 3. Build the vector DB (first time, and after document changes)

```bash
kubectl create -f k8s/jobs/embed-job.yaml
kubectl logs -f job/embed-docs -n rolechat
kubectl delete job embed-docs -n rolechat
```

The embed job is deliberately outside ArgoCD: it's a one-off action, not a
desired state, and Jobs are immutable so ArgoCD cannot reconcile them cleanly.

### 4. Access the ArgoCD UI

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d; echo
kubectl port-forward svc/argocd-server -n argocd 8080:443
# https://localhost:8080 — user: admin
```

### Verify locally before pushing

```bash
export SOPS_AGE_KEY_FILE=$HOME/.config/sops/age/keys.txt
kustomize build --enable-alpha-plugins --enable-exec k8s/
```
```

---

## 6. Section `## 🔧 Update / Revoke Users (No code change required)` (line ~511)

Replace with:

```markdown
## 🔧 Add / Update / Revoke Users

No redeploy and no code change. Users live in a SOPS-encrypted Secret that the
backend re-reads on every login.

### Add a user

```bash
# 1. generate a bcrypt hash (the password is never echoed or stored)
python scripts/hash_password.py

# 2. open the encrypted file — SOPS decrypts it in your editor and
#    re-encrypts it on save
sops k8s/secrets/users-secret.enc.yaml

# 3. add the entry
#    "NewUser": {"password_hash": "$2b$12$...", "role": "finance"}

# 4. commit and push — ArgoCD applies the Secret
git add k8s/secrets/users-secret.enc.yaml
git commit -m "chore: add user NewUser"
git push
```

The mounted Secret refreshes within 1–2 minutes. For an immediate update:

```bash
kubectl rollout restart deploy/rolechat-backend -n rolechat
```

### Disable a user

Add `"disabled": true` to their entry and push. Their login is rejected while
the record is kept for audit purposes.

### Valid roles

`c-levelexecutives`, `finance`, `marketing`, `hr`, `engineering`, `employee`

Anything else is rejected by `ALLOWED_ROLES` in `users_loader.py`, so a typo
can never silently grant the wrong access.
```

---

## 7. Section `## ⚠️ Important Note — Local Deployment` (line ~14)

Small edit — the demo is still laptop-bound, but deploys are not:

```markdown
## ⚠️ Important Note — Local Deployment

The cluster runs on Minikube on a local machine, so the **live demo URLs are
only reachable while that machine is running**. The backend becomes unreachable
when it's off.

Deployment itself no longer depends on that machine. CI runs on GitHub-hosted
runners and only writes to git; ArgoCD applies the change when the cluster is
up. Pushes made while the laptop is off are applied automatically the next time
it starts.
```

---

## 8. Section `## 🛠 Tech Stack` (line ~118)

Add a row or bullet:

```markdown
**GitOps & Secrets:** ArgoCD · Kustomize · KSOPS · SOPS + age · Helm
```

---

## 9. Optional: a new section after `## 🚀 Features`

```markdown
## 🧭 Architecture Decisions

**Why pull-based GitOps instead of CI pushing to the cluster**
CI with cluster credentials means a compromised pipeline is a compromised
cluster. With ArgoCD, CI only writes to git and the cluster pulls, so no
kubeconfig or cluster token exists in CI at all.

**Why SOPS + age instead of Sealed Secrets**
SOPS encrypts per field, so `kind` and `name` stay readable in git and diffs
are reviewable. The same encrypted file works locally (`sops -d`) and in the
cluster (KSOPS), so there's no separate tool for each environment.

**Why bcrypt hashes even though the Secret is encrypted**
Kubernetes Secrets are base64, not encryption. Anyone with
`kubectl get secret` can read them. Hashing means even cluster admins never see
a usable password.

**Why the embed job sits outside ArgoCD**
ArgoCD reconciles desired state; a Job is a one-time action. Jobs also have
immutable auto-generated selectors, so they cannot be patched in place. Planned
improvement: name the Job after a content hash of `resources/data/` so ArgoCD
creates a new one only when documents actually change.

**Why git-SHA image tags instead of semver**
A SHA maps to an exact commit, so `git show <sha>` reveals precisely what's
running. Mutable tags like `latest` or `1.9` can be overwritten, leaving no way
to know what's deployed.
```

---

## Quick checklist

- [ ] Project Structure tree updated
- [ ] CI/CD section rewritten (self-hosted runner setup removed)
- [ ] Secrets handling section rewritten
- [ ] Hardening list split into done / next
- [ ] Kubernetes Deployment section rewritten
- [ ] User management section rewritten
- [ ] Local Deployment note adjusted
- [ ] Tech Stack updated
- [ ] Architecture Decisions section added (optional)
- [ ] Screenshots refreshed — add the ArgoCD app tree, it's a strong visual