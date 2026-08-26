from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
try:
    from backend.database.db import get_db
    from backend.database.models import User, ChatHistory
    from backend.routes.auth import get_current_user
    from backend.services.rag import run_full_rag_pipeline
except ImportError:
    from database.db import get_db
    from database.models import User, ChatHistory
    from routes.auth import get_current_user
    from services.rag import run_full_rag_pipeline
import json


router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    response, sources = run_full_rag_pipeline(request.question, current_user.id)

    try:
        chat_history = ChatHistory(
            user_id=current_user.id,
            user_question=request.question,
            bot_response=response,
            sources=json.dumps(sources)
        )
        db.add(chat_history)
        db.commit()
        db.refresh(chat_history)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save chat history: {str(exc)}") from exc

    return {"answer": response, "sources": sources}


@router.get("/history")
def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    history = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).order_by(ChatHistory.response_time.desc()).all()
    return {"history": [
        {
            "question": h.user_question,
            "answer": h.bot_response,
            "sources": json.loads(h.sources) if h.sources else [],
            "time": h.response_time
        }
        for h in history
    ]}
