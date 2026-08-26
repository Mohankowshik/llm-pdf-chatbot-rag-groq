from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
try:
    from backend.database.db import get_db
    from backend.database.models import User, PDFUpload
    from backend.routes.auth import get_current_user
    from backend.services.rag import process_pdf_for_rag
    from backend.config import settings
except ImportError:
    from database.db import get_db
    from database.models import User, PDFUpload
    from routes.auth import get_current_user
    from services.rag import process_pdf_for_rag
    from config import settings

router = APIRouter()


@router.post("/upload")
def upload_pdfs(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", settings.UPLOAD_DIR))
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)

    results = []

    for file in files:
        safe_filename = os.path.basename(file.filename)
        if not safe_filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"File {safe_filename} is not a PDF")

        # Save file
        file_path = os.path.join(upload_dir, safe_filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        # Save to database
        pdf_upload = PDFUpload(filename=safe_filename, file_path=file_path, user_id=current_user.id)
        db.add(pdf_upload)
        db.commit()
        db.refresh(pdf_upload)

        # Process PDF with new RAG pipeline
        try:
            process_pdf_for_rag(file_path, current_user.id)
            results.append({"filename": safe_filename, "status": "success"})
        except Exception as e:
            results.append({"filename": safe_filename, "status": "failed", "error": str(e)})

    return {"results": results}

