![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red)
![Google%20Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-black)
![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Hub-2496ED?logo=docker&logoColor=white)

# 🤖 RBAC-Secured Internal AI Assistant (Role-Based RAG Chatbot)

A secure, production-ready internal AI chatbot powered by **Google Gemini + Vector Search (RAG)** — with **Role-Based Access Control (RBAC)** for Finance, HR, Engineering, Marketing, Employees, and C-Level Executives.

---

## ⚠️ Important Note — Local Deployment

> **This project runs locally on a Linux machine using Minikube.**
>
> The live demo URLs below (`gowthamchowdamm.streamlit.app` and `api.gowthamchowdam23.online`) are only accessible when the local Minikube cluster is running. If the machine is off or Minikube is stopped, the backend will be unreachable and the Streamlit frontend will fail to connect.
>
> **To bring the system online:**
> ```bash
> ~/start-rolechat.sh
> ```
> Once Minikube is running and all pods are healthy, the dashboard and APIs become accessible via the URLs listed below.

---

## 🌐 Live Demo

🔗 **Frontend (Streamlit UI):** https://gowthamchowdamm.streamlit.app/
🔗 **Backend (Stable URL via Cloudflare Tunnel):** https://api.gowthamchowdam23.online
🔗 **Backend API Docs (Swagger):** https://api.gowthamchowdam23.online/docs

---

## 🖼 Screenshots

### 🖥 Streamlit UI (Chat + Login)
<img width="1920" height="1080" alt="RBAC RAG Chatbot UI" src="https://github.com/user-attachments/assets/500fab48-c69f-4661-86d2-38c594a44363" />

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

---

## 🔄 How It Works (Flow)

1. **Login** → user authenticated + role identified
2. **Query** → user asks a question
3. **Retrieve** → ChromaDB returns top-k relevant chunks *filtered by role*
4. **Generate** → Gemini generates answer using retrieved context

---

## 👥 Role-Based Access Control (RBAC)

| Role               | Permissions                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| C-Level Executives | Full unrestricted access to all documents                                   |
| Finance Team       | Financial reports, expenses, reimbursements                                 |
| Marketing Team     | Campaign performance, customer insights, sales data                         |
| HR Team            | Employee handbook, attendance, leave, payroll                               |
| Engineering Dept.  | System architecture, deployment, CI/CD                                      |
| Employees          | General information (FAQs, company policies, events)                        |

---

## 🚀 Features

### 🔐 Secure Retrieval
- Metadata-based **role filtering**
- Prevents cross-department data leakage

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

### ⚙️ CI/CD Pipeline
- Automated testing on every PR and push
- Docker image build and push to Docker Hub on merge to main
- Automated rolling deployment to Minikube via self-hosted runner

---

## 🛠 Tech Stack

| Layer        | Technology                                      |
|-------------|--------------------------------------------------|
| Frontend    | Streamlit (Streamlit Cloud)                      |
| Backend     | FastAPI + Uvicorn                                |
| Embeddings  | Google Gemini Embeddings                         |
| LLM         | Google Gemini                                    |
| Vector DB   | ChromaDB                                         |
| Deployment  | Minikube (Backend) + Streamlit Cloud (Frontend)  |
| Public URL  | Cloudflare Tunnel                                |
| CI/CD       | GitHub Actions + Docker Hub                      |
| Language    | Python 3.11                                      |

---

## 🏗 Project Structure

```text
RBAC-Secured-Internal-AI-Assistant/
├── .github/
│   └── workflows/
│       └── cicd.yml          # GitHub Actions CI/CD pipeline
├── app/
│   ├── __init__.py
│   ├── embed_documents.py
│   ├── frontend.py
│   ├── google_embeddings.py
│   ├── main.py
│   └── users_loader.py
├── tests/
│   └── test_api.py           # Pytest smoke tests
├── resources/
│   └── data/
│       ├── engineering/
│       ├── finance/
│       ├── general/
│       ├── hr/
│       └── marketing/
├── k8s/
│   ├── backend-deploy.yaml
│   ├── chroma-pvc.yaml
│   ├── cloudflared-deploy.yaml
│   ├── embed-job.yaml
│   └── users-configmap.yaml
├── Dockerfile
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚙️ CI/CD Pipeline (GitHub Actions)

This project uses a fully automated CI/CD pipeline triggered on pushes and pull requests to `main`.

### Pipeline Flow

```
Feature branch push
        ↓
PR opened → CI runs (tests + build validation)
        ↓
PR merged to main → Full pipeline runs
        ↓
  ✅ Tests pass
  ✅ Docker image built + pushed to Docker Hub
  ✅ Rolling deploy to Minikube (self-hosted runner)
        ↓
Streamlit Cloud auto-redeploys frontend
```

### Jobs

| Job | Runs On | Trigger | What it does |
|-----|---------|---------|--------------|
| 🧪 Test + Build | GitHub servers | Every PR + push to main | Runs pytest, builds Docker image |
| 🐳 Push to Docker Hub | GitHub servers | Push to main only | Pushes `latest` + `git-sha` tags |
| 🚀 Deploy to Minikube | Self-hosted runner (your machine) | Push to main only | Rolling update via `kubectl set image` |

### Docker Image Tags

Every merge to `main` produces two tags on Docker Hub:

```
<your-dockerhub-username>/role-chatbot-api:latest       # always points to latest
<your-dockerhub-username>/role-chatbot-api:<git-sha>    # unique per commit (for rollbacks)
```

### Rollback to a Previous Version

```bash
kubectl set image deployment/rolechat-backend \
  backend=<your-dockerhub-username>/role-chatbot-api:<previous-sha> \
  -n rolechat
```

### Setting Up CI/CD (for contributors / new machines)

#### 1. Add GitHub Secrets

Go to repo → **Settings** → **Secrets and variables** → **Actions**:

```
DOCKER_USERNAME  →  your Docker Hub username
DOCKER_PASSWORD  →  your Docker Hub password
DOCKER_IMAGE     →  your-dockerhub-username/role-chatbot-api
```

#### 2. Install Self-Hosted Runner (on your Linux/WSL machine)

```bash
# Create runner folder inside your project directory
cd /path/to/your/project
mkdir actions-runner && cd actions-runner

# Download runner
# Get the exact URL from: GitHub → repo → Settings → Actions → Runners → New runner
curl -o actions-runner-linux-x64-2.x.x.tar.gz -L <URL from GitHub>
tar xzf ./actions-runner-linux-x64-2.x.x.tar.gz

# Configure (token is shown on the GitHub runner setup page)
./config.sh --url https://github.com/<your-org>/<your-repo> --token <TOKEN from GitHub>

# DO NOT install as a background service
# Instead use the start/stop scripts below
```

#### 3. Create Start & Stop Scripts

The runner should **only run when Minikube is active**. Create these two scripts in your home directory.

> **Important:** Replace `/path/to/your/project/actions-runner` with the actual path
> where you cloned the repo and set up the runner on your machine.

**`~/start-rolechat.sh`** — run this when you want to work:
```bash
#!/bin/bash
echo "🚀 Starting RoleChat stack..."

echo "⏳ Starting Minikube..."
minikube start

echo "🔍 Checking pods..."
kubectl get pods -n rolechat

echo "⚡ Starting GitHub Actions runner..."
cd /path/to/your/project/actions-runner
./run.sh &
echo $! > ~/runner.pid
echo "✅ Runner started (PID: $(cat ~/runner.pid))"

echo ""
echo "✅ RoleChat stack is fully online!"
echo "   Frontend : https://gowthamchowdamm.streamlit.app"
echo "   Backend  : https://api.gowthamchowdam23.online"
echo "   Runner   : Online on GitHub"
```

**`~/stop-rolechat.sh`** — run this when you're done:
```bash
#!/bin/bash
echo "🛑 Stopping RoleChat stack..."

if [ -f ~/runner.pid ]; then
    kill $(cat ~/runner.pid) 2>/dev/null
    rm ~/runner.pid
fi
pkill -f "Runner.Listener" 2>/dev/null
echo "⚡ Runner stopped"

minikube stop
echo "✅ Everything stopped. Safe to close WSL."
```

Make them executable:
```bash
chmod +x ~/start-rolechat.sh ~/stop-rolechat.sh
```

#### 4. Daily Usage

```bash
# Start everything (Minikube + runner)
~/start-rolechat.sh

# Stop everything when done
~/stop-rolechat.sh
```

#### 5. Service Behavior by Machine State

| Scenario | Runner | Minikube | Stack |
|---|---|---|---|
| Machine OFF | ❌ Off | ❌ Off | ❌ Offline |
| WSL ON, scripts not run | ❌ Off | ❌ Off | ❌ Offline |
| `start-rolechat.sh` run | ✅ On | ✅ On | ✅ Fully live |
| `stop-rolechat.sh` run | ❌ Off | ❌ Off | ❌ Clean shutdown |

> **Note:** The CI job (tests + Docker build) always runs on GitHub's servers regardless
> of your machine state. Only the CD (deploy to Minikube) job requires your machine
> and runner to be online.

#### 6. Verify Runner is Online

Go to repo → **Settings** → **Actions** → **Runners** — should show:
```
✅ Online  |  self-hosted  Linux  X64
```

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
# 5. Once CI passes and PR is approved → merge
# 6. Full CI/CD pipeline deploys automatically
```

> **Note for forks:** The CD (deploy) job only runs on the original repository.
> Forks will run CI (tests + build) but will not trigger deployment to Minikube.

---

## 🔐 Security Notes

This system is designed to reduce internal data leakage in RAG by enforcing **role-based retrieval**.

### What's protected
- Department-specific documents are stored with metadata (role/department tags).
- Retrieval queries are filtered by the authenticated user's role before sending context to the LLM.
- Secrets (API keys) are injected via Kubernetes Secrets and should never be committed to the repo.

### Data access rules
- **C-Level**: unrestricted access
- **Departments**: access only to their own folder/chunks
- **Employees**: limited to general policies/FAQ

### Secrets handling
- `GOOGLE_API_KEY` is stored in:
  - Local: `.env` (ignored by git)
  - Kubernetes: `Secret` (`google-api`)
  - CI/CD: GitHub Actions Secrets (`DOCKER_USERNAME`, `DOCKER_PASSWORD`, `DOCKER_IMAGE`)
- Cloudflare Tunnel credentials are stored in Kubernetes secrets (`cloudflared-creds`, `cloudflared-config`)
- `actions-runner/` folder is added to `.gitignore` — never committed to the repo

### Recommended hardening (next steps)
- Enforce HTTPS-only traffic end-to-end
- Add rate limiting (FastAPI middleware / API gateway)
- Add audit logs for user queries and document access decisions
- Use short-lived tokens instead of basic auth (JWT/OAuth)

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
3) Create .env
    ```bash
    GOOGLE_API_KEY=your_google_ai_studio_api_key
    GEMINI_MODEL=gemini-2.5-flash
    ```
4) Build embeddings + ChromaDB (Run once)
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

## ☸️ Kubernetes Deployment (Minikube)

2) Start Minikube + Namespace
    ```bash
    minikube start
    kubectl create namespace rolechat || true
    ```
3) Create Secret for Gemini API Key
    ```bash
    kubectl delete secret google-api -n rolechat 2>/dev/null || true
    kubectl create secret generic google-api -n rolechat \
      --from-literal=GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
    ```
4) Apply PVC + Users ConfigMap
    ```bash
    kubectl apply -n rolechat -f k8s/chroma-pvc.yaml
    kubectl apply -n rolechat -f k8s/users-configmap.yaml
    ```
5) Deploy Backend
    ```bash
    kubectl apply -n rolechat -f k8s/backend-deploy.yaml
    kubectl get pods -n rolechat
    ```
6) Build Vector DB (Embed Job)
    ```bash
    kubectl delete job embed-docs -n rolechat 2>/dev/null || true
    kubectl apply -n rolechat -f k8s/embed-job.yaml
    kubectl logs -n rolechat job/embed-docs -f
    ```
7) Cloudflare Tunnel (Stable Backend URL)

A) Login + Create tunnel
    ```bash
    cloudflared tunnel login
    cloudflared tunnel create rolechat
    ```
B) Route DNS
    ```bash
    cloudflared tunnel route dns rolechat <your-backend-domain>
    ```
C) Deploy cloudflared inside Minikube

Create K8s secrets (replace `<TUNNEL_ID>` with your actual tunnel ID):
    ```bash
    kubectl create secret generic cloudflared-creds -n rolechat \
      --from-file=<TUNNEL_ID>.json=$HOME/.cloudflared/<TUNNEL_ID>.json

    kubectl create secret generic cloudflared-config -n rolechat \
      --from-file=config.yml=$HOME/.cloudflared/config.yml
    ```
Deploy:
    ```bash
    kubectl apply -n rolechat -f k8s/cloudflared-deploy.yaml
    kubectl logs -n rolechat deploy/cloudflared -f
    ```
Test:
    ```bash
    curl -u "<username>:<password>" https://<your-backend-domain>/login
    ```
8) Streamlit Cloud Setup (Public Frontend)

- Connect the GitHub repo in Streamlit Cloud
- Set Python version = 3.11
- App entry point = `app/frontend.py`
- Add Secrets:
```toml
API_URL = "https://<your-backend-domain>"
```

---

## 🧪 Sample Users & Roles

Users are managed from Kubernetes ConfigMap (`k8s/users-configmap.yaml`).

| Username   | Role              |
|------------|-------------------|
| Gowtham    | c-levelexecutives |
| Kiran      | employee          |
| Aakanksha  | engineering       |
| Sahithi    | marketing         |
| Yasasvi    | finance           |
| Shiva      | hr                |
| Sid        | marketing         |
| Peter      | engineering       |

> **Note:** Passwords are managed in `k8s/users-configmap.yaml` and should never be committed in plain text to public repos. Rotate them regularly.

---

## 🔧 Update / Revoke Users (No code change required)
```bash
kubectl edit configmap chatbot-users -n rolechat
```
Changes apply immediately on next login.

---

## 🔧 Extending & Customizing

✅ **Add new roles**

- Create folder: `resources/data/<role>/`
- Add `.md` or `.csv` files
- Add users for the role in `k8s/users-configmap.yaml`
- Re-run embed job:
    ```bash
    kubectl delete job embed-docs -n rolechat
    kubectl apply -n rolechat -f k8s/embed-job.yaml
    ```

✅ **Add more document types**

- Extend loaders in `app/embed_documents.py` (PDF, DOCX, etc.)

✅ **Change Gemini model**

Set `GEMINI_MODEL` env var in backend deployment:
- `gemini-2.5-flash` (fast)
- `gemini-1.5-pro` (higher quality)