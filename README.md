![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red)
![Google%20Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-black)

# 🤖 RBAC-Secured Internal AI Assistant (Role-Based RAG Chatbot)

A secure, production-ready internal AI chatbot powered by **Google Gemini + Vector Search (RAG)** — with **Role-Based Access Control (RBAC)** for Finance, HR, Engineering, Marketing, Employees, and C-Level Executives.

---

## 🌐 Live Demo

🔗 **Frontend (Streamlit UI):** https://gowthamchowdam.streamlit.app/  
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

---

## 🛠 Tech Stack

| Layer        | Technology                         |
|-------------|-------------------------------------|
| Frontend    | Streamlit (Streamlit Cloud)         |
| Backend     | FastAPI + Uvicorn                   |
| Embeddings  | Google Gemini Embeddings            |
| LLM         | Google Gemini                       |
| Vector DB   | ChromaDB                            |
| Deployment  | Minikube (Backend) + Streamlit Cloud (Frontend) |
| Public URL  | Cloudflare Tunnel                   |
| Language    | Python 3.11                         |

---


## 🏗 Project Structure

```text
RBAC-Secured-Internal-AI-Assistant/
├── app/
│   ├── __init__.py
│   ├── embed_documents.py
│   ├── frontend.py
│   ├── google_embeddings.py
│   ├── main.py
│   └── users_loader.py
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


---

## 🔐 Security Notes

```md
## 🔐 Security Notes

This system is designed to reduce internal data leakage in RAG by enforcing **role-based retrieval**.

### What’s protected
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
- Cloudflare Tunnel credentials are stored in Kubernetes secrets (`cloudflared-creds`, `cloudflared-config`)

### Recommended hardening (next steps)
- Enforce HTTPS-only traffic end-to-end
- Add rate limiting (FastAPI middleware / API gateway)
- Add audit logs for user queries and document access decisions
- Use short-lived tokens instead of basic auth (JWT/OAuth)


✅ Quickstart (Local Development)
1) Clone the repository
    ```bash
    git clone https://github.com/gowtham-org/RBAC-Secured-Internal-AI-Assistant.git
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

Frontend: http://localhost:8501

Backend docs: http://localhost:8000/docs

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
    cloudflared tunnel route dns rolechat api.gowthamchowdam23.online
    ```
C) Deploy cloudflared inside Minikube

Create K8s secrets (replace <TUNNEL_ID>):
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
    curl -u "Gowtham:ceopass" https://api.gowthamchowdam23.online/login
    ```
8) Streamlit Cloud Setup (Public Frontend)

Connect the GitHub repo in Streamlit Cloud

Set Python version = 3.11

App entry point = app/frontend.py

Add Secrets:

API_URL="https://api.gowthamchowdam23.online"
🧪 Sample Users & Roles

Users are managed from Kubernetes ConfigMap.

## 🧪 Sample Users & Roles

| Username | Password     | Role              |
|----------|--------------|-------------------|
| Gowtham    | ceopass      | c-levelexecutives |
| Kiran      | employeepass | employee          |
| Aakanksha     | password123  | engineering       |
| Sahithi    | securepass   | marketing         |
| Yasasvi      | financepass  | finance           |
| Shiva  | hrpass123    | hr                |
| Sid  | sidpass123    | marketing                |
| Peter  | pete123    | engineering                |

---

🔧 Update / Revoke Users (No code change required)
kubectl edit configmap chatbot-users -n rolechat

Changes apply immediately on next login.

🔧 Extending & Customizing

✅ Add new roles

Create folder: resources/data/<role>/

Add .md or .csv files

Add users for the role in k8s/users-configmap.yaml

Re-run embed job:
    ```bash
    kubectl delete job embed-docs -n rolechat
    kubectl apply -n rolechat -f k8s/embed-job.yaml
    ```
✅ Add more document types

Extend loaders in app/embed_documents.py (PDF, DOCX, etc.)

✅ Change Gemini model

Set GEMINI_MODEL env var in backend deployment:

gemini-2.5-flash (fast)

gemini-1.5-pro (higher quality)