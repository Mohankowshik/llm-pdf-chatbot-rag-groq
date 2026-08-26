from typing import Dict, Any
try:
    from backend.services.vector_store import query_vector_store
    from backend.services.groq_client import generate_response
except ImportError:
    from services.vector_store import query_vector_store
    from services.groq_client import generate_response



def build_prompt(query: str, results: Dict[str, Any]):
    """Build prompt with retrieved chunks."""
    context = ""
    sources = []

    if results and "documents" in results and len(results["documents"][0]) > 0:
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i]
            context += f"\n{doc}\n"
            sources.append({
                "filename": metadata["filename"],
                "page": metadata["page"],
                "snippet": doc[:100] + "..." if len(doc) > 100 else doc
            })
    else:
        context = "No relevant information found."

    prompt = f"""You are an intelligent document assistant. Answer ONLY using the provided context. If the answer is not present in the context, reply: 'I could not find this information in the uploaded documents.'

Context:
{context}

Question: {query}

Provide a concise and accurate answer."""

    return prompt, sources


def run_rag_pipeline(query: str, user_id: int):
    """Run full RAG pipeline."""
    results = query_vector_store(query, user_id)
    prompt, sources = build_prompt(query, results)
    response = generate_response(prompt)
    return response, sources
