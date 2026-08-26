from groq import Groq
try:
    from backend.config import settings
except ImportError:
    from config import settings


def generate_response(prompt: str):
    """Generate response using Groq API (Llama 3.1 8B)."""
    api_key = settings.GROQ_API_KEY
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment variables.")

    client = Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama-3.1-8b-instant",
        temperature=0.1,
    )
    return chat_completion.choices[0].message.content

