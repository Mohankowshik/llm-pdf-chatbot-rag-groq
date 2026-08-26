
from typing import List, Dict, Any


def build_system_prompt() -> str:
    """Build the production-grade system prompt for RAG answers."""
    return """You are an expert document assistant tasked with answering questions strictly and only from the provided retrieved context. Follow these rules meticulously:

1. **No Hallucinations**: If the answer is not explicitly present in the context, reply EXACTLY: "I could not find this information in the uploaded documents." Do NOT make up any information even if you think you know it.
2. **Read Carefully**: Read every single retrieved chunk carefully, including tables, bullet points, and contact information. Tables are just as important as paragraphs.
3. **Exact Values**: Extract exact numbers, contact information, and text from the context without modification or summarization unless asked.
4. **All Matches**: If multiple relevant values or answers exist in the context, return ALL of them, not just one.
5. **Cite Page Numbers**: ALWAYS cite the page number(s) where the information was found using the format [Page X]. If information spans multiple pages, cite all relevant pages.
6. **Ground Everything**: Every part of your answer must be directly supported by the provided context. Do not use external knowledge.
7. **Tables**: For tables, present the information in a clear, readable format, and cite the page number.
8. **Follow-Up Questions**: If there is conversation history, understand the context of follow-up questions and maintain consistency with previous answers.
"""


def build_context_from_chunks(chunks: List[Dict[str, Any]]) -> str:
    """Format retrieved and reranked chunks into a clean context string."""
    if not chunks:
        return "No relevant context found."
    
    context_parts = []
    for i, chunk in enumerate(chunks):
        metadata = chunk["metadata"]
        context_parts.append(f"--- Chunk {i+1} (Page {metadata['page']}, {metadata['filename']}) ---\n")
        context_parts.append(chunk["text"])
        context_parts.append("\n\n")
    
    return "\n".join(context_parts)


def build_full_prompt(
    query: str,
    chunks: List[Dict[str, Any]],
    conversation_history: str = ""
) -> str:
    """Build the complete prompt including system prompt, context, and query."""
    system_prompt = build_system_prompt()
    context_str = build_context_from_chunks(chunks)
    
    full_prompt = f"""{system_prompt}

{conversation_history}

Retrieved Context:
{context_str}

Current User Question: {query}

Answer:"""
    
    return full_prompt

