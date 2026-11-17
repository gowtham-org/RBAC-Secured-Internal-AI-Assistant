"""
main.py
--------
FastAPI backend for a RAG-based role-based access chatbot at FinSolve Technologies.

Now uses:
- Google AI Studio (Gemini) for LLM responses
- Google embeddings (text-embedding-004) for semantic search
"""

import logging
import os
import time

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv

from google import genai
from langchain_chroma import Chroma
from prometheus_client import start_http_server
from prometheus_fastapi_instrumentator import Instrumentator

from app import metrics as m
from app.google_embeddings import GoogleAIStudioEmbeddings
from app.users_loader import verify_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# Env + Google Client Setup
# -----------------------------
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY in environment (.env).")

client = genai.Client(api_key=GOOGLE_API_KEY)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# -----------------------------
# Initialize FastAPI app
# -----------------------------
app = FastAPI()
security = HTTPBasic()

# Auto metrics: request count, latency, status codes per endpoint.
# We don't call .expose() on purpose. Metrics are served on a separate
# port below so they never go through the public Cloudflare Tunnel.
Instrumentator(excluded_handlers=["/healthz", "/metrics"]).instrument(app)


@app.on_event("startup")
def start_metrics_server():
    port = os.getenv("METRICS_PORT")
    if not port:  # only when set, so tests don't try to bind a port
        return
    try:
        start_http_server(int(port))
        logger.info("metrics server listening on :%s", port)
    except OSError:
        # e.g. port already in use under --reload. Never take the API down for metrics.
        logger.exception("could not start metrics server on :%s", port)


def count_gemini_tokens(result) -> None:
    """Record token usage. Must never break a chat request."""
    try:
        usage = getattr(result, "usage_metadata", None)
        if not usage:
            return
        for direction, attr in (
            ("input", "prompt_token_count"),
            ("output", "candidates_token_count"),
        ):
            n = getattr(usage, attr, None)
            if isinstance(n, int):
                m.GEMINI_TOKENS.labels(direction=direction).inc(n)
    except Exception:
        logger.exception("token accounting failed")


# -----------------------------
# Load Vector Database
# -----------------------------
embedding_function = GoogleAIStudioEmbeddings(model="models/gemini-embedding-001")

vectordb = Chroma(
    persist_directory=os.getenv("CHROMA_DIR", "chroma_db"),
    embedding_function=embedding_function,
    collection_name="company_docs",
)


# -----------------------------
# Helper: Authentication
# -----------------------------
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    username = (credentials.username or "").strip()
    password = (credentials.password or "").strip()
    role = verify_user(username, password)
    if not role:
        m.ACCESS_DENIED.inc()
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"username": username, "role": role}


# -----------------------------
# Endpoints
# -----------------------------
@app.get("/login")
def login(user=Depends(authenticate)):
    return {"message": f"Welcome {user['username']}!", "role": user["role"]}


@app.get("/test")
def test(user=Depends(authenticate)):
    return {"message": f"Hello {user['username']}! You can now chat.", "role": user["role"]}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/chat")
async def chat(request: Request, user=Depends(authenticate)):
    """
    Main chat endpoint:
    - Role comes from the authenticated session, never from the request body
    - Retrieves relevant documents from ChromaDB based on that role
    - Uses Gemini to generate the final answer
    """
    start = time.perf_counter()
    try:
        data = await request.json()
        message = data.get("message", "").strip()
        if not message:
            raise HTTPException(status_code=400, detail="Missing 'message' in request body")

        user_role = user["role"].lower()
        m.CHAT_REQUESTS_BY_ROLE.labels(role=user["role"]).inc()

        # -----------------------------
        # Role-based retrieval
        # -----------------------------
        with m.RETRIEVAL_SECONDS.time():
            if "c-levelexecutives" in user_role:
                docs = vectordb.similarity_search(message, k=3)
                if not docs:
                    docs = vectordb.similarity_search(
                        message,
                        k=5,
                        filter={"role": {"$in": ["engineering", "hr", "finance", "marketing", "general"]}},
                    )

            elif "employee" in user_role:
                docs = vectordb.similarity_search(message, k=3, filter={"category": "general"})

            else:
                docs = vectordb.similarity_search(message, k=3, filter={"role": user["role"]})

        logger.info(
            "chat request | user=%s role=%s docs_returned=%d",
            user["username"], user["role"], len(docs),
        )

        if not docs:
            m.EMPTY_RETRIEVAL.labels(role=user["role"]).inc()
            return {"response": f"No relevant data found for your role: {user['role']}"}

        # -----------------------------
        # Build prompt
        # -----------------------------
        context = "\n\n".join([doc.page_content for doc in docs])

        prompt = f"""
You are an AI assistant at FinSolve Technologies.

The user has the role: {user['role']}

Use the context below to answer the user's question in a friendly, clear, conversational style.
Summarize naturally; do not just dump bullet points.
If the context is insufficient, say what's missing and ask 1-2 clarifying questions.

Context:
{context}

Question:
{message}

Answer:
""".strip()

        # -----------------------------
        # Gemini response
        # -----------------------------
        try:
            with m.LLM_SECONDS.time():
                result = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        except Exception as exc:
            m.GEMINI_ERRORS.labels(
                stage="generation", error_type=m.classify_gemini_error(exc)
            ).inc()
            raise

        count_gemini_tokens(result)
        llm_answer = (result.text or "").strip()

        return {
            "username": user["username"],
            "role": user["role"],
            "query": message,
            "response": llm_answer if llm_answer else "Empty response from Gemini.",
        }

    except HTTPException:
        raise
    except Exception:
        logger.exception("chat failed for user=%s", user["username"])
        raise HTTPException(status_code=500, detail="Internal error while processing chat request")
    finally:
        m.CHAT_SECONDS.observe(time.perf_counter() - start)