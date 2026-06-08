# """
# Ingestion script - No LlamaIndex, pure ChromaDB + sentence-transformers
# """

# import os
# import chromadb
# from pathlib import Path
# from dotenv import load_dotenv
# from sentence_transformers import SentenceTransformer
# import pypdf

# load_dotenv()

# CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
# KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", "./knowledge")

# # Load embedding model locally
# print("🔄 Loading embedding model...")
# embed_model = SentenceTransformer("all-MiniLM-L6-v2")
# print("✅ Embedding model loaded!")

# def chunk_text(text, chunk_size=512, overlap=64):
#     words = text.split()
#     chunks = []
#     i = 0
#     while i < len(words):
#         chunk = " ".join(words[i:i+chunk_size])
#         chunks.append(chunk)
#         i += chunk_size - overlap
#     return chunks

# def load_pdf(filepath):
#     text = ""
#     reader = pypdf.PdfReader(filepath)
#     for page in reader.pages:
#         text += page.extract_text() or ""
#     return text

# def load_md(filepath):
#     with open(filepath, "r", encoding="utf-8") as f:
#         return f.read()

# def ingest_documents():
#     print(f"📂 Loading documents from: {KNOWLEDGE_DIR}")

#     chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
#     collection = chroma_client.get_or_create_collection("hritik_knowledge")

#     all_chunks = []
#     all_ids = []
#     all_metadatas = []
#     chunk_id = 0

#     knowledge_path = Path(KNOWLEDGE_DIR)

#     # Load PDFs
#     for pdf_file in knowledge_path.rglob("*.pdf"):
#         print(f"📄 Loading: {pdf_file.name}")
#         text = load_pdf(str(pdf_file))
#         chunks = chunk_text(text)
#         for chunk in chunks:
#             if chunk.strip():
#                 all_chunks.append(chunk)
#                 all_ids.append(f"chunk_{chunk_id}")
#                 all_metadatas.append({"source": pdf_file.name})
#                 chunk_id += 1

#     # Load Markdown files
#     for md_file in knowledge_path.rglob("*.md"):
#         print(f"📝 Loading: {md_file.name}")
#         text = load_md(str(md_file))
#         chunks = chunk_text(text)
#         for chunk in chunks:
#             if chunk.strip():
#                 all_chunks.append(chunk)
#                 all_ids.append(f"chunk_{chunk_id}")
#                 all_metadatas.append({"source": md_file.name})
#                 chunk_id += 1

#     print(f"✅ Total chunks created: {len(all_chunks)}")
#     print("🔗 Embedding chunks...")

#     embeddings = embed_model.encode(all_chunks, show_progress_bar=True).tolist()

#     print("🗄️ Storing in ChromaDB...")
#     collection.add(
#         documents=all_chunks,
#         embeddings=embeddings,
#         ids=all_ids,
#         metadatas=all_metadatas
#     )

#     print("\n" + "="*60)
#     print(f"✅ SUCCESS: Ingested {len(all_chunks)} chunks")
#     print(f"📍 Stored in: {os.path.abspath(CHROMA_PERSIST_DIR)}")
#     print("="*60)

# if __name__ == "__main__":
#     ingest_documents()


"""
Ingestion script - No LlamaIndex, pure ChromaDB + sentence-transformers
"""

import os
import chromadb
from pathlib import Path
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import pypdf

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", "./knowledge")

print("🔄 Loading embedding model...")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Embedding model loaded!")

def chunk_text(text, chunk_size=256, overlap=32):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def load_pdf(filepath):
    text = ""
    reader = pypdf.PdfReader(filepath)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def load_md(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def ingest_documents():
    print(f"📂 Loading documents from: {KNOWLEDGE_DIR}")

    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = chroma_client.get_or_create_collection("hritik_knowledge")

    all_chunks = []
    all_ids = []
    all_metadatas = []
    chunk_id = 0

    knowledge_path = Path(KNOWLEDGE_DIR)

    for pdf_file in knowledge_path.rglob("*.pdf"):
        print(f"📄 Loading: {pdf_file.name}")
        text = load_pdf(str(pdf_file))
        chunks = chunk_text(text)
        for chunk in chunks:
            if chunk.strip():
                all_chunks.append(chunk)
                all_ids.append(f"chunk_{chunk_id}")
                all_metadatas.append({"source": pdf_file.name})
                chunk_id += 1

    for md_file in knowledge_path.rglob("*.md"):
        print(f"📝 Loading: {md_file.name}")
        text = load_md(str(md_file))
        chunks = chunk_text(text)
        for chunk in chunks:
            if chunk.strip():
                all_chunks.append(chunk)
                all_ids.append(f"chunk_{chunk_id}")
                all_metadatas.append({"source": md_file.name})
                chunk_id += 1

    print(f"✅ Total chunks created: {len(all_chunks)}")
    print("🔗 Embedding chunks...")

    embeddings = embed_model.encode(all_chunks, show_progress_bar=True).tolist()

    print("🗄️ Storing in ChromaDB...")
    collection.add(
        documents=all_chunks,
        embeddings=embeddings,
        ids=all_ids,
        metadatas=all_metadatas
    )

    print("\n" + "="*60)
    print(f"✅ SUCCESS: Ingested {len(all_chunks)} chunks")
    print(f"📍 Stored in: {os.path.abspath(CHROMA_PERSIST_DIR)}")
    print("="*60)

if __name__ == "__main__":
    ingest_documents()