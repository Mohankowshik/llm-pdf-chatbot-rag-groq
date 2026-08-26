
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
try:
    from backend.database.db import engine, Base
    from backend.routes import auth, upload, chat
except ImportError:
    from database.db import engine, Base
    from routes import auth, upload, chat



def initialize_database():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        print(f"Database initialization failed: {exc}")
        raise


initialize_database()

app = FastAPI(title="PDF Chatbot API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/")
def root():
    return {"message": "PDF Chatbot API is running!"}
