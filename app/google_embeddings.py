# app/google_embeddings.py
import os
import random
import time
from typing import List

from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from langchain_core.embeddings import Embeddings

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY in environment (.env).")

genai.configure(api_key=GOOGLE_API_KEY)


class GoogleAIStudioEmbeddings(Embeddings):
    """
    Gemini embeddings with batching + retry/backoff to avoid free-tier rate limits.
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
                return genai.embed_content(
                    model=self.model,
                    content=content,
                    task_type=task_type,
                )
            except ResourceExhausted as e:
                # exponential backoff + jitter
                sleep_s = self.base_sleep * (2 ** attempt) + random.uniform(0, 1.0)
                time.sleep(min(sleep_s, 60))
            except Exception:
                # small delay for transient errors
                time.sleep(1.0)
        # last try (raise if still failing)
        return genai.embed_content(model=self.model, content=content, task_type=task_type)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        # Batch multiple texts into one request (reduces request count a lot)
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            res = self._embed_with_retry(batch, task_type="retrieval_document")
            # When content is a list, response returns a list of embeddings
            batch_embeddings = res["embedding"] if isinstance(res["embedding"][0], float) else res["embedding"]
            vectors.extend(batch_embeddings)
        return vectors

    def embed_query(self, text: str) -> List[float]:
        res = self._embed_with_retry(text, task_type="retrieval_query")
        return res["embedding"]