# app/google_embeddings.py
import os
from typing import List

from dotenv import load_dotenv
import google.generativeai as genai
from langchain_core.embeddings import Embeddings

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY in environment (.env).")

genai.configure(api_key=GOOGLE_API_KEY)


class GoogleAIStudioEmbeddings(Embeddings):
    """
    Uses Gemini embedding model via google-generativeai embed_content.
    Use: models/gemini-embedding-001
    """

    def __init__(self, model: str = "models/gemini-embedding-001"):
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        vectors: List[List[float]] = []
        for t in texts:
            res = genai.embed_content(
                model=self.model,
                content=t,
                task_type="retrieval_document",
            )
            vectors.append(res["embedding"])
        return vectors

    def embed_query(self, text: str) -> List[float]:
        res = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_query",
        )
        return res["embedding"]