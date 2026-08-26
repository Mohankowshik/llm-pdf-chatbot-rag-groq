import os
import uuid
import chromadb
from typing import List, Dict, Any
try:
    from backend.config import settings
    from backend.services.embeddings import generate_embeddings, generate_embedding
except ImportError:
    from config import settings
    from services.embeddings import generate_embeddings, generate_embedding

# Absolute path for ChromaDB
chroma_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", settings.CHROMA_DIR))
chroma_client = chromadb.PersistentClient(path=chroma_path)


def get_or_create_collection(user_id: int):
    """Get or create a ChromaDB collection for a user."""
    collection_name = f"user_{user_id}"
    return chroma_client.get_or_create_collection(name=collection_name)


def add_chunks_to_vector_store(chunks: List[Dict[str, Any]], user_id: int):
    """Add chunks to ChromaDB."""
    if not chunks:
        return

    collection = get_or_create_collection(user_id)

    ids = [f"chunk_{user_id}_{uuid.uuid4().hex}" for _ in range(len(chunks))]
    texts = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    embeddings = generate_embeddings(texts)

    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=metadatas
    )


def query_vector_store(query: str, user_id: int):
    """Query ChromaDB for relevant chunks."""
    collection = get_or_create_collection(user_id)
    if collection.count() == 0:
        return {"documents": [[]], "metadatas": [[]]}

    query_embedding = generate_embedding(query)
    n_results = min(settings.TOP_K, collection.count())

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results
    )

    return results

