
import os
import uuid
import chromadb
from typing import List, Dict, Any
try:
    from backend.config import settings
    from backend.services.rag.embeddings import (
        generate_embeddings,
        generate_embedding,
        get_query_prefix,
        get_document_prefix
    )
except ImportError:
    from config import settings
    from services.rag.embeddings import (
        generate_embeddings,
        generate_embedding,
        get_query_prefix,
        get_document_prefix
    )

# ChromaDB setup
chroma_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../..", settings.CHROMA_DIR))
chroma_client = chromadb.PersistentClient(path=chroma_path)


def get_or_create_collection(user_id: int):
    """Get or create ChromaDB collection for a user."""
    collection_name = f"user_{user_id}"
    return chroma_client.get_or_create_collection(name=collection_name)


def add_chunks_to_index(chunks: List[Dict[str, Any]], user_id: int):
    """Add chunks to ChromaDB index."""
    if not chunks:
        return
    
    collection = get_or_create_collection(user_id)
    
    ids = [f"chunk_{user_id}_{uuid.uuid4().hex}" for _ in range(len(chunks))]
    texts = [chunk["text"] for chunk in chunks]
    # Add bge document prefix
    prefixed_texts = [get_document_prefix() + text for text in texts]
    metadatas = [chunk["metadata"] for chunk in chunks]
    embeddings = generate_embeddings(prefixed_texts)
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )


def retrieve_chunks(query: str, user_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
    """Retrieve relevant chunks from ChromaDB."""
    collection = get_or_create_collection(user_id)
    if collection.count() == 0:
        return []
    
    # Add query prefix
    prefixed_query = get_query_prefix() + query
    query_embedding = generate_embedding(prefixed_query)
    
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count())
        )
    except Exception as e:
        if "dimension" in str(e).lower():
            # Old collection had different embedding dimension -> reset collection
            collection_name = f"user_{user_id}"
            chroma_client.delete_collection(name=collection_name)
            chroma_client.get_or_create_collection(name=collection_name)
            return []
        raise e
    
    chunks = []
    if results and results.get("ids") and len(results["ids"]) > 0:
        for i in range(len(results["ids"][0])):
            chunks.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i]
            })
    
    return chunks


def hybrid_retrieve(
    query: str,
    user_id: int,
    multi_queries: List[str],
    top_k_initial: int = 8
) -> List[Dict[str, Any]]:
    """Retrieve chunks using dense retrieval with optimized candidate limit."""
    all_chunks = []
    seen_ids = set()
    
    # 1. First retrieve for the original query (priority)
    orig_retrieved = retrieve_chunks(query, user_id, top_k=min(top_k_initial, 6))
    for chunk in orig_retrieved:
        if chunk["id"] not in seen_ids:
            seen_ids.add(chunk["id"])
            all_chunks.append(chunk)
    
    # 2. Retrieve for expanded variations (top 3 each)
    for q in multi_queries[:3]:
        if q == query:
            continue
        retrieved = retrieve_chunks(q, user_id, top_k=3)
        for chunk in retrieved:
            if chunk["id"] not in seen_ids:
                seen_ids.add(chunk["id"])
                all_chunks.append(chunk)
        if len(all_chunks) >= top_k_initial:
            break
    
    return all_chunks[:top_k_initial]

