"""Prometheus metrics for the RAG backend. Keep every label low-cardinality."""
from prometheus_client import Counter, Histogram

# Gemini calls can take a while, so buckets go up to 60s.
# 5s is in there on purpose: it's the p95 SLO line.
BUCKETS = (0.1, 0.25, 0.5, 1, 2, 3, 4, 5, 7.5, 10, 20, 30, 60)

CHAT_SECONDS = Histogram(
    "rag_chat_seconds", "Total time for a /chat request", buckets=BUCKETS
)
RETRIEVAL_SECONDS = Histogram(
    "rag_retrieval_seconds", "Retrieval time (embed query + Chroma search)", buckets=BUCKETS
)
EMBEDDING_SECONDS = Histogram(
    "rag_embedding_seconds", "Gemini embed_query call (part of retrieval)", buckets=BUCKETS
)
LLM_SECONDS = Histogram(
    "rag_llm_seconds", "Gemini generate_content call", buckets=BUCKETS
)

CHAT_REQUESTS_BY_ROLE = Counter(
    "rag_chat_requests_by_role_total", "Chat requests per role", ["role"]
)
EMPTY_RETRIEVAL = Counter(
    "rag_empty_retrieval_total", "Chat requests where no docs matched the role", ["role"]
)
ACCESS_DENIED = Counter(
    "rag_access_denied_total", "Failed logins (bad username or password)"
)
GEMINI_ERRORS = Counter(
    "rag_gemini_errors_total",
    "Errors from Gemini calls",
    ["stage", "error_type"],  # stage: embedding|generation, type: rate_limited|server_error|other
)
GEMINI_TOKENS = Counter(
    "rag_gemini_tokens_total", "Gemini tokens used", ["direction"]  # input|output
)


def classify_gemini_error(exc: Exception) -> str:
    code = getattr(exc, "code", None)
    text = str(exc)
    if code == 429 or "429" in text or "RESOURCE_EXHAUSTED" in text:
        return "rate_limited"
    if isinstance(code, int) and code >= 500:
        return "server_error"
    return "other"