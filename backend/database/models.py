from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
try:
    from backend.database.db import Base
except ImportError:
    from database.db import Base



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    uploads = relationship("PDFUpload", back_populates="owner")
    chats = relationship("ChatHistory", back_populates="user")


class PDFUpload(Base):
    __tablename__ = "pdf_uploads"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    file_path = Column(String(500))
    upload_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="uploads")


class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user_question = Column(Text)
    bot_response = Column(Text)
    sources = Column(Text)
    response_time = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="chats")
