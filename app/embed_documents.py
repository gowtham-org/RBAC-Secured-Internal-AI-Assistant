"""
embed_documents.py
-------------------
Loads documents from department folders, splits into chunks,
generates embeddings using Google (Gemini) embeddings,
and saves them in a Chroma vector database with role metadata.

Fixes applied:
  - Fix 1: Retry with exponential backoff on 429 / RESOURCE_EXHAUSTED errors
  - Fix 2: Embed in small batches with sleep between batches to stay under free-tier rate limits
"""

import os
import time
import random
import shutil
from dotenv import load_dotenv

from langchain_community.document_loaders import UnstructuredFileLoader, CSVLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from google import genai

from app.google_embeddings import GoogleAIStudioEmbeddings

# -------------------------------
# Configuration
# -------------------------------
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "resources", "data")
BASE_DIR = os.path.abspath(BASE_DIR)
CHROMA_DIR = "chroma_db"

BATCH_SIZE = 50        # Number of chunks to embed per API call batch
SLEEP_BETWEEN = 15     # Seconds to sleep between batches (keeps RPM under free-tier limit of 15)
MAX_RETRIES = 6        # Max retry attempts per batch on 429 errors

load_dotenv()

# -------------------------------
# Fix 1: Embedding wrapper with retry + exponential backoff
# -------------------------------
class RateLimitedEmbeddings(GoogleAIStudioEmbeddings):
    """
    Wraps GoogleAIStudioEmbeddings to add retry logic with
    exponential backoff on 429 / RESOURCE_EXHAUSTED quota errors.
    """

    def _embed_with_retry(self, content, task_type):
        for attempt in range(MAX_RETRIES):
            try:
                return genai.embed_content(
                    model=self.model,
                    content=content,
                    task_type=task_type,
                )
            except Exception as e:
                error_str = str(e)
                is_quota_error = (
                    "429" in error_str
                    or "RESOURCE_EXHAUSTED" in error_str
                    or "quota" in error_str.lower()
                )
                if is_quota_error:
                    wait = (2 ** attempt) + random.uniform(1, 3)
                    print(
                        f"⚠️  Rate limited (attempt {attempt + 1}/{MAX_RETRIES}). "
                        f"Retrying in {wait:.1f}s..."
                    )
                    time.sleep(wait)
                else:
                    # Non-quota errors (auth, network, etc.) — fail fast
                    raise
        raise RuntimeError(
            f"Embedding failed after {MAX_RETRIES} retries due to quota limits. "
            "Wait for daily quota reset or upgrade your Google AI Studio plan."
        )


embedding_model = RateLimitedEmbeddings(model="models/gemini-embedding-001")

# -------------------------------
# Aggregate all split documents
# -------------------------------
all_split_docs = []

for department in os.listdir(BASE_DIR):
    dept_path = os.path.join(BASE_DIR, department)
    if os.path.isdir(dept_path):
        print(f"\n📁 Processing department: {department}")
        all_docs = []

        for file in os.listdir(dept_path):
            file_path = os.path.join(dept_path, file)
            try:
                if file.endswith(".md"):
                    try:
                        loader = UnstructuredFileLoader(file_path)
                        docs = loader.load()
                    except Exception:
                        loader = TextLoader(file_path)
                        docs = loader.load()

                elif file.endswith(".csv"):
                    loader = CSVLoader(file_path)
                    docs = loader.load()
                else:
                    continue

                all_docs.extend(docs)

            except Exception as e:
                print(f"❌ Failed to load {file}: {e}")

        if not all_docs:
            print(f"⚠️  No documents found for department: {department}")
            continue

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = splitter.split_documents(all_docs)

        for doc in split_docs:
            doc.metadata = {
                "role": department.lower(),
                "category": "general" if department.lower() == "general" else department.lower(),
            }

        all_split_docs.extend(split_docs)
        print(f"✅ Loaded & split {len(split_docs)} documents for {department}")

print(f"\n📊 Total documents to embed: {len(all_split_docs)}")

# -------------------------------
# Fix 2: Build Chroma DB in batches with throttling
# -------------------------------
shutil.rmtree(CHROMA_DIR, ignore_errors=True)

total_batches = (len(all_split_docs) + BATCH_SIZE - 1) // BATCH_SIZE
print(f"⏳ Embedding in {total_batches} batches of {BATCH_SIZE} chunks each...\n")

db = None
for i in range(0, len(all_split_docs), BATCH_SIZE):
    batch = all_split_docs[i : i + BATCH_SIZE]
    batch_num = i // BATCH_SIZE + 1

    print(f"📦 Batch {batch_num}/{total_batches} — chunks {i + 1} to {i + len(batch)}")

    if db is None:
        # First batch: create the Chroma collection
        db = Chroma.from_documents(
            documents=batch,
            embedding=embedding_model,
            persist_directory=CHROMA_DIR,
            collection_name="company_docs",
        )
    else:
        # Subsequent batches: add to existing collection
        db.add_documents(batch)

    db.persist()
    print(f"   ✅ Batch {batch_num} stored successfully.")

    # Throttle between batches to respect free-tier RPM limit
    if i + BATCH_SIZE < len(all_split_docs):
        print(f"   ⏸️  Sleeping {SLEEP_BETWEEN}s to respect rate limits...")
        time.sleep(SLEEP_BETWEEN)

# -------------------------------
# Summary
# -------------------------------
print(f"\n✅ Successfully stored {len(all_split_docs)} documents in Chroma.")
sample_meta = db._collection.get()["metadatas"][:5]
print(f"Sample metadata: {sample_meta}")