
from typing import Dict, Any, List, Tuple
try:
    from backend.config import settings
    from backend.services.rag.loader import load_pdf
    from backend.services.rag.cleaner import clean_document
    from backend.services.rag.chunker import create_chunks
    from backend.services.rag.query_rewriter import generate_multi_queries
    from backend.services.rag.retriever import hybrid_retrieve, add_chunks_to_index
    from backend.services.rag.reranker import rerank_chunks
    from backend.services.rag.prompt import build_full_prompt
    from backend.services.groq_client import generate_response
    from backend.services.rag.memory import get_user_memory
except ImportError:
    from config import settings
    from services.rag.loader import load_pdf
    from services.rag.cleaner import clean_document
    from services.rag.chunker import create_chunks
    from services.rag.query_rewriter import generate_multi_queries
    from services.rag.retriever import hybrid_retrieve, add_chunks_to_index
    from services.rag.reranker import rerank_chunks
    from services.rag.prompt import build_full_prompt
    from services.groq_client import generate_response
    from services.rag.memory import get_user_memory


def process_pdf_for_rag(file_path: str, user_id: int) -> List[Dict[str, Any]]:
    """Full pipeline to process a PDF and add to RAG indexes."""
    # Step 1: Load PDF
    pdf_data = load_pdf(file_path)
    
    # Step 2: Clean document
    cleaned_data = clean_document(pdf_data)
    
    # Step 3: Chunk document
    chunks = create_chunks(cleaned_data)
    
    # Step 4: Add to indexes (ChromaDB and BM25)
    add_chunks_to_index(chunks, user_id)
    
    return chunks


def run_full_rag_pipeline(query: str, user_id: int) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Run the complete RAG pipeline for a user query:
    
    1. Generate multi-queries
    2. Hybrid retrieve (dense + BM25)
    3. Rerank with cross-encoder
    4. Build prompt with conversation history
    5. Generate answer with Groq
    6. Update conversation memory
    
    Returns:
        (answer, sources) where sources is list of source dict with filename, page, snippet
    """
    # Get user conversation memory
    memory = get_user_memory(user_id)
    conversation_history = memory.get_formatted_history()
    
    # 1. Generate multi-queries
    multi_queries = generate_multi_queries(query)
    
    # 2. Hybrid retrieve
    retrieved_chunks = hybrid_retrieve(query, user_id, multi_queries)
    
    if not retrieved_chunks:
        # No chunks found
        answer = "I could not find this information in the uploaded documents."
        sources = []
        # Add to memory even if no answer
        memory.add_interaction(query, answer)
        return answer, sources
    
    # 3. Rerank chunks
    reranked_chunks = rerank_chunks(query, retrieved_chunks, top_k=settings.TOP_K)
    
    # 4. Build prompt
    prompt = build_full_prompt(query, reranked_chunks, conversation_history)
    
    # 5. Generate answer
    answer = generate_response(prompt)
    
    # 6. Prepare sources and update memory
    sources = []
    for chunk in reranked_chunks:
        meta = chunk["metadata"]
        snippet = chunk["text"][:150] + "..." if len(chunk["text"]) > 150 else chunk["text"]
        sources.append({
            "filename": meta["filename"],
            "page": meta["page"],
            "section_heading": meta["section_heading"],
            "snippet": snippet
        })
    
    # Update conversation memory
    memory.add_interaction(query, answer)
    
    return answer, sources

