
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from backend.services.rag.loader import load_pdf
from backend.services.rag.cleaner import clean_document
from backend.services.rag.chunker import create_chunks
from backend.services.rag.retriever import add_chunks_to_index, hybrid_retrieve
from backend.services.rag.query_rewriter import generate_multi_queries

def debug():
    print("=== Debugging RAG Pipeline ===")
    
    # Step 1: Load PDF
    pdf_path = os.path.join(os.path.dirname(__file__), "backend", "uploads", "AI_Chatbot_Test_Document.pdf")
    print(f"\nLoading PDF from {pdf_path}")
    pdf_data = load_pdf(pdf_path)
    print(f"Loaded PDF with {len(pdf_data['pages'])} pages")
    
    # Step 2: Clean
    cleaned = clean_document(pdf_data)
    print(f"Cleaned document has {len(cleaned['pages'])} elements")
    
    # Step 3: Chunk
    chunks = create_chunks(cleaned)
    print(f"Created {len(chunks)} chunks")
    print(f"First chunk: {chunks[0]['text'][:100]}...")
    print(f"First chunk metadata: {chunks[0]['metadata']}")
    
    # Step 4: Add to index
    user_id = 1
    print(f"\nAdding chunks to index for user {user_id}")
    add_chunks_to_index(chunks, user_id)
    
    # Step 5: Query
    query = "What is this document about?"
    print(f"\nTesting query: {query}")
    multi_queries = generate_multi_queries(query)
    print(f"Generated queries: {multi_queries}")
    retrieved = hybrid_retrieve(query, user_id, multi_queries)
    print(f"\nRetrieved {len(retrieved)} chunks!")
    for i, chunk in enumerate(retrieved):
        print(f"\nChunk {i}:")
        print(f"  Text: {chunk['text'][:80]}...")
        print(f"  Metadata: {chunk['metadata']}")

if __name__ == "__main__":
    debug()
