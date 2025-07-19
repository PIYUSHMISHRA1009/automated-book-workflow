# ai/embeddings.py

import chromadb
from sentence_transformers import SentenceTransformer
import os

# Initialize
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "chapters"
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(COLLECTION_NAME)

def store_chapter_embedding(chapter_num, title, content, feedback_score):
    embedding = model.encode(content)
    doc_id = f"chapter{chapter_num}"

    collection.upsert(
        documents=[content],
        embeddings=[embedding],
        ids=[doc_id],
        metadatas=[{
            "chapter": chapter_num,
            "title": title,
            "score": feedback_score
        }]
    )
    print(f"📦 Embedded chapter {chapter_num} into ChromaDB.")

def search_similar_chapters(query, top_k=3):
    embedding = model.encode(query)
    results = collection.query(query_embeddings=[embedding], n_results=top_k)
    return results
