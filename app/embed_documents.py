"""
embed_documents.py
-------------------
Loads documents from department folders, splits into chunks,
generates embeddings using Google (Gemini) embeddings,
and saves them in a Chroma vector database with role metadata.
"""

import os
import shutil
from dotenv import load_dotenv

from langchain_community.document_loaders import UnstructuredFileLoader, CSVLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from app.google_embeddings import GoogleAIStudioEmbeddings

# -------------------------------
# Configuration
# -------------------------------
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "resources", "data")
BASE_DIR = os.path.abspath(BASE_DIR)
CHROMA_DIR = "chroma_db"

load_dotenv()

embedding_model = GoogleAIStudioEmbeddings(model="models/gemini-embedding-001")

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
            print(f"⚠️ No documents found for department: {department}")
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

# -------------------------------
# Build or refresh Chroma DB
# -------------------------------
shutil.rmtree(CHROMA_DIR, ignore_errors=True)

db = Chroma.from_documents(
    documents=all_split_docs,
    embedding=embedding_model,
    persist_directory=CHROMA_DIR,
    collection_name="company_docs",
)
db.persist()

print(f"\n✅ Successfully stored {len(all_split_docs)} documents in Chroma.")
sample_meta = db._collection.get()["metadatas"][:5]
print(f"Sample metadata: {sample_meta}")