![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red)
![Google%20Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-black)

# 🤖 FinSolve Role-Based RAG Chatbot

A secure, production-ready internal AI chatbot powered by **Google Gemini + Vector Search (RAG)** — with **Role-Based Access Control (RBAC)** for Finance, HR, Engineering, Marketing, Employees, and C-Level Executives.

---

## 🌐 Live Demo

🔗 **Frontend (Streamlit UI):** https://gowthamchowdam.streamlit.app/  
🔗 **Backend (Stable URL via Cloudflare Tunnel):** https://api.gowthamchowdam23.online  
🔗 **Backend API Docs (Swagger):** https://api.gowthamchowdam23.online/docs

---

## 🖥 Application UI

<img width="1920" height="1080" alt="FinSolve RAG Chatbot UI" src="https://github.com/user-attachments/assets/500fab48-c69f-4661-86d2-38c594a44363" />

---

## 🧩 Problem Background

**FinSolve Technologies**, a leading FinTech company, faced:

- Fragmented document access across departments
- Communication delays
- Security risks when sharing internal documents
- No centralized knowledge retrieval system

Teams needed a secure AI assistant that:

- Understands context
- Respects role-based access
- Retrieves department-specific knowledge
- Responds conversationally

---

## 🧠 Solution Overview

This chatbot implements a **Retrieval-Augmented Generation (RAG)** pipeline with **Role-Based Filtering**:

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

## 🏗 Project Architecture

```mermaid
flowchart TD
    ST[Streamlit Cloud Frontend]
    CF[Cloudflare Tunnel]
    API[FastAPI Backend (Minikube)]
    CH[ChromaDB (PVC)]
    GEM[Gemini API]
    DATA[Department Documents]
    USERS[Users ConfigMap]

    ST -->|API_URL| CF --> API
    API --> CH
    API --> GEM
    DATA --> CH
    USERS --> API

📁 Project Structure

Role_based_aichatbot/
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


✅ Quickstart (Local Development)
1) Clone the repository
git clone https://github.com/gowtham-org/Role_based_aichatbot.git
cd Role_based_aichatbot
2) Create virtual environment (Python 3.11)
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
3) Create .env
GOOGLE_API_KEY=your_google_ai_studio_api_key
GEMINI_MODEL=gemini-2.5-flash
4) Build embeddings + ChromaDB (Run once)
python -m app.embed_documents
5) Run backend (FastAPI)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
6) Run frontend (Streamlit)
streamlit run app/frontend.py

Open:

Frontend: http://localhost:8501

Backend docs: http://localhost:8000/docs

2) Start Minikube + Namespace
minikube start
kubectl create namespace rolechat || true
3) Create Secret for Gemini API Key
kubectl delete secret google-api -n rolechat 2>/dev/null || true
kubectl create secret generic google-api -n rolechat \
  --from-literal=GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
4) Apply PVC + Users ConfigMap
kubectl apply -n rolechat -f k8s/chroma-pvc.yaml
kubectl apply -n rolechat -f k8s/users-configmap.yaml
5) Deploy Backend
kubectl apply -n rolechat -f k8s/backend-deploy.yaml
kubectl get pods -n rolechat
6) Build Vector DB (Embed Job)
kubectl delete job embed-docs -n rolechat 2>/dev/null || true
kubectl apply -n rolechat -f k8s/embed-job.yaml
kubectl logs -n rolechat job/embed-docs -f
7) Cloudflare Tunnel (Stable Backend URL)
A) Login + Create tunnel
cloudflared tunnel login
cloudflared tunnel create rolechat
B) Route DNS
cloudflared tunnel route dns rolechat api.gowthamchowdam23.online
C) Deploy cloudflared inside Minikube

Create K8s secrets (replace <TUNNEL_ID>):

kubectl create secret generic cloudflared-creds -n rolechat \
  --from-file=<TUNNEL_ID>.json=$HOME/.cloudflared/<TUNNEL_ID>.json

kubectl create secret generic cloudflared-config -n rolechat \
  --from-file=config.yml=$HOME/.cloudflared/config.yml

Deploy:

kubectl apply -n rolechat -f k8s/cloudflared-deploy.yaml
kubectl logs -n rolechat deploy/cloudflared -f

Test:

curl -u "Gowtham:ceopass" https://api.gowthamchowdam23.online/login
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

kubectl delete job embed-docs -n rolechat
kubectl apply -n rolechat -f k8s/embed-job.yaml

✅ Add more document types

Extend loaders in app/embed_documents.py (PDF, DOCX, etc.)

✅ Change Gemini model

Set GEMINI_MODEL env var in backend deployment:

gemini-2.5-flash (fast)

gemini-1.5-pro (higher quality)