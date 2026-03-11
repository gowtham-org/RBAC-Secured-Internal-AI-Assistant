# app/google_embeddings.py
import os
import random
import time
from typing import List

from dotenv import load_dotenv
from google import genai
from langchain_core.embeddings import Embeddings

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY in environment (.env).")

# Single client instance — new SDK style
client = genai.Client(api_key=GOOGLE_API_KEY)


class GoogleAIStudioEmbeddings(Embeddings):
    """
    Gemini embeddings using google-genai SDK with batching + retry/backoff
    to avoid free-tier rate limits.
    """

    def __init__(
        self,
        model: str = "models/gemini-embedding-001",
        batch_size: int = 20,
        max_retries: int = 8,
        base_sleep: float = 2.0,
    ):
        self.model = model
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.base_sleep = base_sleep

    def _embed_with_retry(self, content, task_type: str):
        for attempt in range(self.max_retries):
            try:
                response = client.models.embed_content(
                    model=self.model,
                    contents=content,
                )
                return response
            except Exception as e:
                error_str = str(e)
                is_quota_error = (
                    "429" in error_str
                    or "RESOURCE_EXHAUSTED" in error_str
                    or "quota" in error_str.lower()
                )
                if is_quota_error:
                    sleep_s = self.base_sleep * (2 ** attempt) + random.uniform(0, 1.0)
                    sleep_s = min(sleep_s, 60)
                    print(
                        f"⚠️  Rate limited (attempt {attempt + 1}/{self.max_retries}). "
                        f"Retrying in {sleep_s:.1f}s..."
                    )
                    time.sleep(sleep_s)
                else:
                    # Non-quota error — small delay then retry
                    time.sleep(1.0)

        raise RuntimeError(
            f"Embedding failed after {self.max_retries} retries. "
            "Check your quota at https://ai.dev/rate-limit"
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            response = self._embed_with_retry(batch, task_type="retrieval_document")

            # New SDK returns response.embeddings — a list of ContentEmbedding objects
            for embedding_obj in response.embeddings:
                vectors.append(embedding_obj.values)

        return vectors

    def embed_query(self, text: str) -> List[float]:
        response = self._embed_with_retry(text, task_type="retrieval_query")
        # Single text returns one embedding
        return response.embeddings[0].values