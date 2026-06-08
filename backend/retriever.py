"""
Retriever - Pure ChromaDB + sentence-transformers
"""

import os
import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
collection = chroma_client.get_or_create_collection("hritik_knowledge")

def retrieve(query: str, top_k: int = 8) -> list[dict]:
    query_embedding = embed_model.encode(query).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "source": results["metadatas"][0][i]["source"],
            "score": results["distances"][0][i]
        })
    
    return chunks

if __name__ == "__main__":
    results = retrieve("Tell me about Hritik's projects")
    for r in results:
        print(f"Source: {r['source']}")
        print(f"Score: {r['score']:.4f}")
        print(f"Text: {r['text'][:200]}")
        print("---")