"""
Global pytest fixtures.

app.main talks to Google's API and a real Chroma DB the moment it's
imported. Everything below runs at collection time -- before any test
file imports app.main -- so tests never make network calls, never need
a real GOOGLE_API_KEY, and never touch a real vector index.
"""
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

# Needed before app.users_loader / app.main import, since USERS_FILE
# is read into a module-level constant at import time, not per-call.
os.environ.setdefault("GOOGLE_API_KEY", "test-key-not-real")
os.environ.setdefault("GEMINI_MODEL", "gemini-2.5-flash")
os.environ["USERS_FILE"] = str(Path(__file__).parent / "fixtures" / "test_users.json")
os.environ.setdefault("CHROMA_DIR", "/tmp/test_chroma_db")

# app.main constructs a real genai.Client, a real GoogleAIStudioEmbeddings,
# and a real Chroma instance unconditionally at import time. Patch all
# three before that import happens.
_patchers = [
    patch("google.genai.Client", MagicMock()),
    patch("app.google_embeddings.GoogleAIStudioEmbeddings", MagicMock()),
    patch("langchain_chroma.Chroma", MagicMock()),
]
for _p in _patchers:
    _p.start()
