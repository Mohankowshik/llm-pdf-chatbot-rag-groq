# LLM-Based PDF Chatbot using RAG and Groq (Llama 3 8B)

A production-ready web application that allows users to upload PDF documents and ask natural language questions about their content using Retrieval-Augmented Generation (RAG) powered by Groq's Llama 3 8B model.

## Features

- User Authentication (Register/Login with JWT)
- Upload multiple PDF files
- Extract text from PDFs with page numbers
- Text chunking with configurable size/overlap
- Embedding generation using sentence-transformers
- Vector storage with ChromaDB
- Semantic search with cosine similarity
- RAG pipeline for accurate, context-aware answers
- Source citation (filename, page number, snippet)
- ChatGPT-style UI
- Conversation history
- Error handling
- Admin logging to SQLite database
- Docker support

## Tech Stack

### Frontend
- React.js
- Tailwind CSS
- Axios
- React Router
- React Markdown

### Backend
- Python
- FastAPI
- Uvicorn
- PyMuPDF (fitz)
- sentence-transformers
- ChromaDB
- SQLAlchemy
- python-jose[cryptography]
- passlib[bcrypt]
- python-dotenv
- groq

### Database
- SQLite

### Deployment
- Docker
- Docker Compose

## Project Structure

```
.
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── routes/
│   │   ├── auth.py
│   │   ├── upload.py
│   │   └── chat.py
│   ├── services/
│   │   ├── pdf_loader.py
│   │   ├── chunker.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── groq_client.py
│   │   └── rag_pipeline.py
│   ├── database/
│   │   ├── db.py
│   │   └── models.py
│   ├── uploads/
│   └── chroma_db/
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   ├── Dockerfile
│   └── src/
│       ├── main.jsx
│       ├── index.css
│       ├── App.jsx
│       └── pages/
│           ├── Login.jsx
│           ├── Register.jsx
│           └── Chat.jsx
├── docker-compose.yml
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker and Docker Compose (optional, for containerized deployment)
- Groq API Key (get one from [groq.com](https://console.groq.com))

### 1. Clone the repository

```bash
cd "LLM-based PDF Chatbot (RAG)"
```

### 2. Backend Setup (without Docker)

a. Navigate to the backend directory
```bash
cd backend
```

b. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

c. Install dependencies
```bash
pip install -r requirements.txt
```

d. Configure environment variables
```bash
cp .env.example .env
# Edit .env and set your GROQ_API_KEY and other variables
```

e. Run the backend server
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API docs will be available at `http://localhost:8000/docs`

### 3. Frontend Setup (without Docker)

a. Navigate to the frontend directory (from project root)
```bash
cd frontend
```

b. Install dependencies
```bash
npm install
```

c. Run the dev server
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 4. Docker Deployment

a. Create a .env file in project root
```bash
cp .env.example .env
# Edit .env and set your GROQ_API_KEY
```

b. Build and run with Docker Compose
```bash
docker-compose up --build
```

The backend will be at `http://localhost:8000`
The frontend will be at `http://localhost:3000`

## Usage

1. Register a new account or login with an existing one
2. Upload PDF documents using the sidebar
3. Ask questions about the content of the uploaded PDFs in the chat interface
4. View answers along with source citations
5. Logout when done

## Configuration

You can configure the following settings in `backend/.env` or `docker-compose.yml`:
- `SECRET_KEY`: Secret key for JWT token generation
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `GROQ_API_KEY`: Your Groq API key
- `CHUNK_SIZE`: Size of text chunks for embedding (default: 1000)
- `CHUNK_OVERLAP`: Overlap between consecutive chunks (default: 200)
- `TOP_K`: Number of relevant chunks to retrieve (default: 3)
- `DATABASE_URL`: SQLite database URL

## License

MIT
