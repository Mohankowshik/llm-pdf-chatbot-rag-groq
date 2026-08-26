
from groq import Groq
from typing import Optional
try:
    from backend.config import settings
except ImportError:
    from config import settings


_client = None


def get_groq_client():
    """Get singleton Groq client instance."""
    global _client
    if _client is None:
        api_key = settings.GROQ_API_KEY
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in environment variables.")
        _client = Groq(api_key=api_key)
    return _client


def generate_response(
    prompt: str,
    model: str = "llama-3.1-8b-instant",
    temperature: float = 0.1
) -> str:
    """Generate a response using Groq API with streaming support (optional)."""
    client = get_groq_client()
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
        temperature=temperature,
    )
    
    return chat_completion.choices[0].message.content

