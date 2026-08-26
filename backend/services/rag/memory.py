
from typing import List, Dict, Any, Optional
from collections import deque


class ConversationMemory:
    """
    Manages conversation history for follow-up question understanding.
    Uses a sliding window to keep the last N interactions.
    """
    
    def __init__(self, max_history_size: int = 5):
        self.max_history_size = max_history_size
        self.history = deque(maxlen=max_history_size)
    
    def add_interaction(self, question: str, answer: str):
        """Add a question-answer pair to the conversation history."""
        self.history.append({
            "question": question,
            "answer": answer
        })
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get the conversation history as a list of dicts."""
        return list(self.history)
    
    def get_formatted_history(self) -> str:
        """Get conversation history formatted as a string for prompts."""
        if not self.history:
            return ""
        
        history_str = "Previous conversation:\n"
        for interaction in self.history:
            history_str += f"User: {interaction['question']}\n"
            history_str += f"Assistant: {interaction['answer']}\n"
        
        return history_str
    
    def clear(self):
        """Clear the conversation history."""
        self.history.clear()


# Global per-user memory store (in production, use Redis or similar)
_user_memories: Dict[int, ConversationMemory] = {}


def get_user_memory(user_id: int) -> ConversationMemory:
    """Get or create conversation memory for a user."""
    if user_id not in _user_memories:
        _user_memories[user_id] = ConversationMemory()
    return _user_memories[user_id]

