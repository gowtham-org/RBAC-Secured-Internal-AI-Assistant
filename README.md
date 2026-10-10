![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red)
![Google%20Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-black)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Minikube-326CE5?logo=kubernetes&logoColor=white)
![ArgoCD](https://img.shields.io/badge/GitOps-ArgoCD-EF7B4D?logo=argo&logoColor=white)
![SOPS](https://img.shields.io/badge/Secrets-SOPS%20%2B%20age-4B275F)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Hub-2496ED?logo=docker&logoColor=white)

# 🤖 RBAC-Secured Internal AI Assistant (Role-Based RAG Chatbot)

A secure, production-ready internal AI chatbot powered by **Google Gemini + Vector Search (RAG)** — with **Role-Based Access Control (RBAC)** for Finance, HR, Engineering, Marketing, Employees, and C-Level Executives.

Deployed with **GitOps**: GitHub Actions builds and writes to git, and **ArgoCD** running inside the cluster pulls and applies. All secrets live in git, encrypted with **SOPS + age**, and are decrypted in-cluster by **KSOPS**.

---

## ⚠️ Important Note — Local Deployment

> **The cluster runs on Minikube on a local machine.**
>
> The live demo URLs below (`gowthamchowdamm.streamlit.app` and `api.gowthamchowdam23.online`) are only reachable while that machine is running. If it's off, the backend is unreachable and the Streamlit frontend can't connect.
>
> **To bring the system online:**
> ```bash
> minikube start
> kubectl get application rolechat -n argocd   # Synced + Healthy = caught up with git
> ```
>
> **Deployment itself no longer depends on this machine.** CI runs on GitHub-hosted runners and only writes to git. Anything pushed while the laptop is off is applied automatically by ArgoCD the next time the cluster comes up.

---

## 🌐 Live Demo

🔗 **Frontend (Streamlit UI):** https://gowthamchowdamm.streamlit.app/
🔗 **Backend (Stable URL via Cloudflare Tunnel):** https://api.gowthamchowdam23.online
🔗 **Backend API Docs (Swagger):** https://api.gowthamchowdam23.online/docs

> The demo requires credentials. See Users & Roles below.

---

## 🖼 Screenshots

### 🖥 Streamlit UI (Chat + Login)
<img width="1920" height="1080" alt="RBAC RAG Chatbot UI" src="https://github.com/user-attachments/assets/500fab48-c69f-4661-86d2-38c594a44363" />

### 🔄 ArgoCD — GitOps Sync
<!-- Add a screenshot of the ArgoCD application tree (Synced + Healthy) here -->

### 📚 API Docs (FastAPI Swagger)
Open: https://api.gowthamchowdam23.online/docs

---

## 🧩 Problem Background

**Nexora Health Systems**, a fast-growing healthcare enterprise, faced:

- Fragmented internal documents across departments
- Slow resolution due to repetitive Q&A and manual lookups
- Security risks when sensitive documents were shared incorrectly
- No centralized, role-aware internal knowledge retrieval system

Teams needed an internal AI assistant that:

- Understands context and intent
- Enforces role-based access policies
- Retrieves department-specific knowledge only
- Responds conversationally with grounded answers

---

## 🧠 Solution Overview

This project implements a **Retrieval-Augmented Generation (RAG)** pipeline with **Role-Based Filtering**:

- User logs in (RBAC enforced)
- User asks a question
- System performs semantic search in **ChromaDB**
- Only **role-permitted documents** are retrieved
- Context is sent to **Google Gemini**
- Gemini generates the final grounded answer

Filtering happens **at retrieval time**, before anything reaches the LLM — so restricted content never enters the prompt in the first place.

---

## 🔄 How It Works (Flow)

1. **Login** → user authenticated + role identified
2. **Query** → user asks a question
3. **Retrieve** → ChromaDB returns top-k relevant chunks *filtered by role*
4. **Generate** → Gemini generates answer using retrieved context

---

## 🚀 Features

### 🔐 Secure Retrieval
- Metadata-based **role filtering**
- Prevents cross-department data leakage
- Role allow-list validation — a typo in the user store fails loudly instead of silently granting wrong access
- Per-user `disabled` flag to revoke access without deleting the record

### 🔎 Semantic Search (RAG)
- Gemini embeddings (`models/gemini-embedding-001`)
- Chroma vector database
- Fast similarity search

### 💬 Conversational AI
- Google Gemini LLM (default: `gemini-2.5-flash`)
- Context-aware responses
- Friendly, human-like tone

### 🖥 Interactive UI
- Streamlit frontend
- Login panel
- Session-based chat history
- Typing animation
- Feedback buttons (👍👎)

### ⚙️ GitOps Delivery
- Automated testing on every PR and push
- Docker image build and push to Docker Hub on merge to main
- Image tag committed to git — ArgoCD syncs it to the cluster
- `selfHeal` reverts any out-of-band `kubectl` change
- Rollback is a `git revert`

### 🔒 Encrypted Secrets in Git
- Every secret committed encrypted (SOPS + age)
- Decrypted in-cluster by the KSOPS kustomize plugin
- CI holds no cluster credentials and no decryption key

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit (Streamlit Cloud) |
| Backend | FastAPI + Uvicorn |
| Embeddings | Google Gemini Embeddings |
| LLM | Google Gemini |
| Vector DB | ChromaDB |
| Orchestration | Kubernetes (Minikube) |
| GitOps | ArgoCD + Kustomize + KSOPS |
| Secrets | SOPS + age |
| Public URL | Cloudflare Tunnel |
| CI | GitHub Actions + Docker Hub |
| Language | Python 3.11 |

---

## 🏗 Project Structure

```text
RBAC-Secured-Internal-AI-Assistant/
├── .github/workflows/
│   └── cicd.yml                      # CI: test, build, push, bump image tag in git
├── app/
│   ├── __init__.py
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
│   └── user-passwords.enc.yaml       # SOPS-encrypted record of demo user passwords
├── resources/data/                   # department document folders
│   ├── engineering/
│   ├── finance/
│   ├── general/
│   ├── hr/
│   └── marketing/
├── scripts/
│   └── hash_password.py              # generate a bcrypt hash for a new user
├── tests/
│   └── test_api.py
├── .sops.yaml                        # SOPS creation rules
├── Dockerfile
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ CI/CD — GitOps with ArgoCD

Deployment is **pull-based**. CI never talks to the cluster — it only writes to git. ArgoCD, running inside the cluster, notices the change and applies it.

### Pipeline flow

```
Feature branch push
        ↓
PR opened → CI runs (pytest + Docker build validation)
        ↓
PR merged to main
        ↓
[ CI — GitHub-hosted runner ]
  pytest → docker build → push to Docker Hub (latest + <git-sha>)
        ↓
[ CD — GitHub-hosted runner ]
  kustomize edit set image <repo>:<git-sha>
  commit "chore: bump image to <sha> [skip ci]" → push
        ↓
[ ArgoCD — in-cluster, polls every ~3 min ]
  kustomize build (KSOPS decrypts secrets in memory)
  → applies to the rolechat namespace → rolling update
        ↓
Streamlit Cloud auto-redeploys the frontend
```

### Jobs

| Job | Runs on | Trigger | What it does |
|---|---|---|---|
| 🧪 Test + Build | GitHub-hosted | Every PR + push to main | pytest, builds the Docker image |
| 🐳 Push to Docker Hub | GitHub-hosted | Push to main only | Pushes `latest` + `<git-sha>` tags |
| 📝 Bump image tag | GitHub-hosted | Push to main only | Commits the new tag to `k8s/base/kustomization.yaml` |
| 🚀 Deploy | **ArgoCD (in-cluster)** | Git change detected | Syncs the cluster to match git |

### Why pull-based

- **No laptop needed to deploy.** Everything in CI runs on GitHub's runners.
- **Git is the single source of truth.** What's in `k8s/` is what's running.
- **No cluster credentials in CI.** A compromised pipeline can't reach the cluster.
- **Drift is caught.** `selfHeal` reverts anything changed with `kubectl`.
- **Rollback is a git revert**, not a manual `kubectl set image`.

### Docker image tags

| Tag | Purpose |
|---|---|
| `latest` | convenience only — never deployed |
| `<git-sha>` | immutable, this is what gets deployed |

The deployed tag lives in `k8s/base/kustomization.yaml` under `images[].newTag`, so `git log -p k8s/base/kustomization.yaml` is a complete deployment history.

### Rollback

```bash
# find the commit that set the previous tag
git log --oneline -- k8s/base/kustomization.yaml

# revert it
git revert <commit-sha>
git push
```

ArgoCD syncs the previous image within ~3 minutes. Or use **History and Rollback** in the ArgoCD UI for an immediate revert.

### GitHub Secrets required

Repo → **Settings** → **Secrets and variables** → **Actions**:

```
DOCKER_USERNAME  →  Docker Hub username
DOCKER_PASSWORD  →  Docker Hub token
DOCKER_IMAGE     →  <dockerhub-username>/role-chatbot-api
```

The age private key is **not** a GitHub Secret. It never leaves the developer machine and the cluster, so CI has no way to decrypt any secret in this repo.

### PR Workflow for Contributors

```bash
# 1. Clone the repo
git clone https://github.com/<your-org>/RBAC-Secured-Internal-AI-Assistant.git
cd RBAC-Secured-Internal-AI-Assistant

# 2. Create a feature branch
git checkout -b feature/your-feature-name

# 3. Make your changes and commit
git add .
git commit -m "feat: describe your change"
git push origin feature/your-feature-name

# 4. Open a PR on GitHub → CI runs automatically
# 5. Once CI passes and the PR is approved → merge
# 6. CI bumps the image tag; ArgoCD deploys
```

> **Note for forks:** forks run CI (tests + build) but cannot push the image-tag commit to the upstream repo, so no deployment is triggered.

---

## 🔐 Security

This system is designed to reduce internal data leakage in RAG by enforcing **role-based retrieval**. Demo credentials are not published; accounts are provisioned on request.

### What's protected

- Department documents carry role/department metadata tags
- Retrieval is filtered by the authenticated user's role **before** context reaches the LLM
- Role values validated against an allow-list in `users_loader.py`
- Rate limiting on the API

### Data access rules

- **C-Level**: unrestricted access
- **Departments**: access only to their own folder/chunks
- **Employees**: limited to general policies/FAQ

### Secrets handling

All secrets live in git, encrypted with [SOPS](https://github.com/getsops/sops) and [age](https://github.com/FiloSottile/age). Nothing is ever committed in plaintext.

| Secret | File | Contents |
|---|---|---|
| `chatbot-users` | `k8s/secrets/users-secret.enc.yaml` | usernames, bcrypt hashes, roles |
| `google-api` | `k8s/secrets/google-api-secret.enc.yaml` | Gemini API key |
| `cloudflared-creds` | `k8s/secrets/cloudflared-creds.enc.yaml` | tunnel credentials |
| `cloudflared-config` | `k8s/secrets/cloudflared-config.enc.yaml` | tunnel config |

**Two independent layers:**

1. **SOPS/age** encrypts the file in git. Only `data` / `stringData` is encrypted, so `kind`, `name` and `namespace` stay readable and diffs remain reviewable.
2. **bcrypt** hashes the passwords themselves. Even someone with `kubectl get secret` access sees hashes, never usable passwords. (Kubernetes Secrets are base64-encoded, not encrypted — hashing is what makes them safe to read.)

**Decryption at deploy time:** the ArgoCD repo-server runs the [KSOPS](https://github.com/viaduct-ai/kustomize-sops) kustomize plugin, which decrypts in memory during `kustomize build`. Plaintext never touches disk, git, or CI.

**`.sops.yaml` rules** (order matters — SOPS uses the first match):

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

### Hardening status

**Done**

- [x] Secrets encrypted at rest in git (SOPS + age)
- [x] Passwords stored as bcrypt hashes, never plaintext
- [x] Role allow-list validation + per-user disable flag
- [x] Rate limiting on the API
- [x] GitOps deploys — no cluster credentials in CI
- [x] Immutable SHA-tagged images with git-tracked deploy history
- [x] HTTPS end-to-end via Cloudflare Tunnel

**Next**

- [ ] Replace HTTP Basic auth with short-lived JWTs
- [ ] Audit log of every query (user, role, documents retrieved, allow/deny)
- [ ] NetworkPolicies between the backend and the vector DB
- [ ] Prometheus / Grafana metrics and SLOs
- [ ] RAG evaluation (RAGAS) gating in CI

> Google AI Studio free tier only, no billing account attached — set a budget before ever enabling billing.

---

## 🧭 Architecture Decisions

**Why pull-based GitOps instead of CI pushing to the cluster**
CI holding cluster credentials means a compromised pipeline is a compromised cluster. With ArgoCD, CI only writes to git and the cluster pulls, so no kubeconfig or cluster token exists in CI at all. It also removes the self-hosted runner that previously had to be online for any deploy to happen.

**Why SOPS + age instead of Sealed Secrets**
SOPS encrypts per field, so `kind` and `name` stay readable in git and diffs are reviewable. The same encrypted file works locally (`sops -d`) and in the cluster (KSOPS), so there's no separate tool per environment.

**Why bcrypt hashes even though the Secret is encrypted**
Kubernetes Secrets are base64, not encryption. Anyone with `kubectl get secret` can read them. Hashing means even a cluster admin never sees a usable password.

**Why the embed job sits outside ArgoCD**
ArgoCD reconciles desired state; a Job is a one-time action. Jobs also have immutable auto-generated selectors, so they cannot be patched in place — `Replace` fails and `Force` would re-run the embedding on every sync, burning API calls. Planned improvement: name the Job after a content hash of `resources/data/` so ArgoCD creates a new one only when documents actually change.

**Why git-SHA image tags instead of semver**
A SHA maps to an exact commit, so `git show <sha>` reveals precisely what's running. Mutable tags like `latest` or `1.9` can be overwritten, leaving no way to know what's deployed.

---

## ✅ Quickstart (Local Development)

1) Clone the repository
    ```bash
    git clone https://github.com/<your-org>/RBAC-Secured-Internal-AI-Assistant.git
    cd RBAC-Secured-Internal-AI-Assistant
    ```
2) Create virtual environment (Python 3.11)
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
3) Create `.env`
    ```bash
    GOOGLE_API_KEY=your_google_ai_studio_api_key
    GEMINI_MODEL=gemini-2.5-flash
    ```
4) Build embeddings + ChromaDB (run once)
    ```bash
    python -m app.embed_documents
    ```
5) Run backend (FastAPI)
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
6) Run frontend (Streamlit)
    ```bash
    streamlit run app/frontend.py
    ```

Open:

- Frontend: http://localhost:8501
- Backend docs: http://localhost:8000/docs

---

## ☸️ Kubernetes Deployment (Minikube + ArgoCD)

### Prerequisites

```bash
minikube start --cpus=4 --memory=8g

# local tooling
sops --version
age --version
kustomize version        # standalone binary — kubectl's built-in kustomize cannot run exec plugins
```

Your age private key must be at `~/.config/sops/age/keys.txt`.

### 1. Install ArgoCD with KSOPS support

```bash
kubectl create namespace argocd

# Bootstrap the age key — the only manual secret, by necessity:
# the key that decrypts everything else cannot itself be stored encrypted.
kubectl create secret generic sops-age -n argocd \
  --from-file=keys.txt=$HOME/.config/sops/age/keys.txt

helm repo add argo https://argoproj.github.io/argo-helm && helm repo update
helm install argocd argo/argo-cd -n argocd -f argocd/values.yaml
```

`argocd/values.yaml` does three things:

- an init container copies the `ksops` binary into the repo-server
- `kustomize.buildOptions: --enable-alpha-plugins --enable-exec` allows the plugin to run
- mounts the age key and sets `SOPS_AGE_KEY_FILE`

Verify:

```bash
kubectl exec -n argocd deploy/argocd-repo-server -- which ksops kustomize
kubectl get cm argocd-cm -n argocd -o jsonpath='{.data.kustomize\.buildOptions}'
```

### 2. Create the Application

```bash
kubectl apply -f argocd/rolechat-app.yaml
```

ArgoCD then watches `k8s/` on `main` and syncs automatically, with `selfHeal` reverting any out-of-band change.

### 3. Build the vector DB (first time, and after document changes)

```bash
kubectl create -f k8s/jobs/embed-job.yaml
kubectl logs -f job/embed-docs -n rolechat
kubectl delete job embed-docs -n rolechat
```

### 4. Cloudflare Tunnel (stable backend URL)

Only needed when setting up a new tunnel — the existing credentials are already in `k8s/secrets/` and ArgoCD applies them.

```bash
cloudflared tunnel login
cloudflared tunnel create rolechat
cloudflared tunnel route dns rolechat <your-backend-domain>
```

Then encrypt the generated credentials into the repo:

```bash
kubectl create secret generic cloudflared-creds -n rolechat \
  --from-file=<TUNNEL_ID>.json=$HOME/.cloudflared/<TUNNEL_ID>.json \
  --dry-run=client -o yaml > k8s/secrets/cloudflared-creds.enc.yaml
sops -e -i k8s/secrets/cloudflared-creds.enc.yaml
```

### 5. Access the ArgoCD UI

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d; echo
kubectl port-forward svc/argocd-server -n argocd 8080:443
# https://localhost:8080 — user: admin
```

### 6. Streamlit Cloud (public frontend)

- Connect the GitHub repo in Streamlit Cloud
- Python version = 3.11
- App entry point = `app/frontend.py`
- Secrets:
    ```toml
    API_URL = "https://<your-backend-domain>"
    ```

### Verify manifests locally before pushing

```bash
export SOPS_AGE_KEY_FILE=$HOME/.config/sops/age/keys.txt
kustomize build --enable-alpha-plugins --enable-exec k8s/
```

Secrets should appear fully decrypted in the output, with no `ENC[` anywhere.

### Daily usage

```bash
minikube start
kubectl get application rolechat -n argocd   # Synced + Healthy = caught up with git
# ... work ...
minikube stop
```

---

## 👥 Role-Based Access Control (RBAC) 🧪 Sample Users & Roles

| Role | Permissions |
|---|---|
| C-Level Executives | Full unrestricted access to all documents |
| Finance Team | Financial reports, expenses, reimbursements |
| Marketing Team | Campaign performance, customer insights, sales data |
| HR Team | Employee handbook, attendance, leave, payroll |
| Engineering Dept. | System architecture, deployment, CI/CD |
| Employees | General information (FAQs, company policies, events) |

**Want to try it?** Open an issue or reach out and I'll provision a scoped demo account. Or clone the repo and define your own users locally.

---

## 🔧 Add / Update / Revoke Users

No redeploy and no code change. Users live in a SOPS-encrypted Secret that the backend re-reads on every login.

### Add a user

```bash
# 1. generate a bcrypt hash (the password is never echoed or stored)
python scripts/hash_password.py

# 2. open the encrypted file — SOPS decrypts it in your editor
#    and re-encrypts it on save
sops k8s/secrets/users-secret.enc.yaml

# 3. add the entry:
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

Add `"disabled": true` to their entry and push. Login is rejected while the record is kept for audit purposes.

### Valid roles

`c-levelexecutives`, `finance`, `marketing`, `hr`, `engineering`, `employee`

Anything else is rejected by `ALLOWED_ROLES` in `users_loader.py`, so a typo can never silently grant the wrong access.

---

## 🔧 Extending & Customizing

✅ **Add new roles**

- Create folder: `resources/data/<role>/`
- Add `.md` or `.csv` files
- Add the role to `ALLOWED_ROLES` in `app/users_loader.py`
- Add users via `sops k8s/secrets/users-secret.enc.yaml`
- Re-run the embed job:
    ```bash
    kubectl create -f k8s/jobs/embed-job.yaml
    ```

✅ **Add more document types**

- Extend loaders in `app/embed_documents.py` (PDF, DOCX, etc.)

✅ **Change the Gemini model**

Set `GEMINI_MODEL` in `k8s/base/backend-deploy.yaml` and push — ArgoCD applies it:
- `gemini-2.5-flash` (fast)
- `gemini-1.5-pro` (higher quality)

---

## 🗺 Roadmap

- [ ] JWT auth replacing HTTP Basic
- [ ] Query audit logging
- [ ] Content-hash-named embed job (re-index exactly when documents change)
- [ ] Prometheus + Grafana with SLOs and burn-rate alerts
- [ ] OpenTelemetry tracing across UI → API → Chroma → Gemini
- [ ] RAGAS evaluation gating in CI
- [ ] Hybrid search (BM25 + vector) with a re-ranker and source citations