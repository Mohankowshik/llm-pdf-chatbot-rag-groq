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
- Relational logging to MySQL database
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
- PyMySQL
- python-jose[cryptography]
- passlib[bcrypt]
- python-dotenv
- groq

### Database
- MySQL (Relational DB)
- ChromaDB (Vector DB)

### Deployment
- Vercel (frontend, static Vite build)
- Render (backend, Docker)
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
│   │   ├── groq_client.py
│   │   └── rag/
│   │       ├── loader.py
│   │       ├── cleaner.py
│   │       ├── chunker.py
│   │       ├── embeddings.py
│   │       ├── retriever.py
│   │       ├── query_rewriter.py
│   │       ├── reranker.py
│   │       ├── prompt.py
│   │       ├── memory.py
│   │       ├── generator.py
│   │       └── pipeline.py
│   ├── database/
│   │   ├── db.py
│   │   └── models.py
│   ├── uploads/
│   └── chroma_db/
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── vercel.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   ├── Dockerfile
│   ├── .env.example
│   └── src/
│       ├── main.jsx
│       ├── index.css
│       ├── App.jsx
│       └── pages/
│           ├── Login.jsx
│           ├── Register.jsx
│           └── Chat.jsx
├── render.yaml
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

c. Configure the API URL (optional — defaults to `http://localhost:8000`)
```bash
cp .env.example .env
# Edit .env and set VITE_API_URL if the backend runs elsewhere
```

d. Run the dev server
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

### 5. Production Deployment (Vercel + Render)

The backend cannot run on Vercel: it keeps state on disk (uploaded PDFs and the
ChromaDB store), needs a raw MySQL connection, and loads PyTorch plus two
transformer models — well past Vercel's 250 MB serverless bundle limit with no
persistent filesystem. So the frontend is served by Vercel and the backend runs
on Render using its native Python runtime (no Docker required).

**a. Deploy the backend to Render**

1. Create a MySQL instance and note its connection URL. Render does not offer
   managed MySQL, so use a provider such as Aiven, Railway or PlanetScale.
2. In Render, choose **New → Blueprint** and point it at this repository. It reads
   [render.yaml](render.yaml).
3. When prompted, set the two secret variables:
   - `GROQ_API_KEY` — your Groq API key
   - `DATABASE_URL` — e.g. `mysql+pymysql://user:pass@host:3306/dbname`
4. Deploy and confirm `https://<your-service>.onrender.com/` returns
   `{"message":"PDF Chatbot API is running!"}`.

The blueprint pins `plan: starter` because the embedding and reranker models
exceed a 512 MB free instance. Change that line to `free` to try it at no cost,
but expect possible out-of-memory crashes on the first request.

**b. Deploy the frontend to Vercel**

1. In Vercel, choose **Add New → Project** and import this repository.
2. Set **Root Directory** to `frontend`. Vercel detects Vite automatically and
   uses [vercel.json](frontend/vercel.json) for the SPA rewrite.
3. Add an environment variable for the Production (and Preview) environment:
   - `VITE_API_URL` = your Render backend URL, e.g. `https://pdf-chatbot-api.onrender.com`
   - No trailing slash.
4. Deploy. `VITE_API_URL` is inlined at build time, so **redeploy whenever the
   backend URL changes**.

**Persistence note:** Render's filesystem is wiped on every restart, which clears
the uploaded PDFs and the vector store (chat history in MySQL is unaffected).
Attaching a persistent disk mounted at `/data` keeps them — on `starter` and above
you can then set `UPLOAD_DIR=/data/uploads`, `CHROMA_DIR=/data/chroma_db` and
`HF_HOME=/data/hf_cache` so the models are cached across restarts too.

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
- `DATABASE_URL`: MySQL database connection URL (e.g. `mysql+pymysql://root:password@localhost:3306/pdf_chatbot`)
- `UPLOAD_DIR`: Where uploaded PDFs are stored (default: `uploads`)
- `CHROMA_DIR`: Where the ChromaDB vector store is persisted (default: `chroma_db`)

Frontend settings live in `frontend/.env`:
- `VITE_API_URL`: Base URL of the backend API (default: `http://localhost:8000`)

## License

MIT
