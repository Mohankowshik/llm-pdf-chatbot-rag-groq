import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
load_dotenv(backend_dir / ".env")
load_dotenv()



class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-this-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K: int = int(os.getenv("TOP_K", "3"))
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost:3306/pdf_chatbot"
    )
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    CHROMA_DIR: str = os.getenv("CHROMA_DIR", "chroma_db")


settings = Settings()
