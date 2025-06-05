from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import shutil
from datetime import datetime
import json

import models
import schemas
import crud
import security
from database import get_db
from services.document_service import process_document, analyze_document

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={401: {"description": "Unauthorized"}},
)

# Create upload directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=schemas.Document)
def create_document(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a new document."""
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{current_user.id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
    
    # Process document (extract text, metadata, etc.)
    content_type = file.content_type
    process_document(file_path, content_type)
    
    # Create document in database
    document_data = schemas.DocumentCreate(
        title=title,
        description=description,
        content_type=content_type
    )
    
    return crud.create_document(db=db, document=document_data, user_id=current_user.id, file_path=file_path)

@router.get("/", response_model=List[schemas.Document])
def read_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all documents for the current user."""
    documents = crud.get_documents(db, user_id=current_user.id, skip=skip, limit=limit)
    return documents

@router.get("/{document_id}", response_model=schemas.Document)
def read_document(
    document_id: int,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific document by ID."""
    document = crud.get_document(db, document_id=document_id)
    if document is None or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.get("/{document_id}/download")
def download_document(
    document_id: int,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download a document."""
    document = crud.get_document(db, document_id=document_id)
    if document is None or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=document.file_path,
        filename=os.path.basename(document.file_path),
        media_type=document.content_type
    )

@router.post("/{document_id}/analyze", response_model=schemas.DocumentAnalysis)
def analyze_document_endpoint(
    document_id: int,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Analyze a document for insights."""
    document = crud.get_document(db, document_id=document_id)
    if document is None or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Analyze document
    analysis_result = analyze_document(document.file_path, document.content_type)
    
    # Create analysis record in database
    analysis_data = schemas.DocumentAnalysisCreate(
        document_id=document_id,
        summary=analysis_result.get("summary", ""),
        key_points=analysis_result.get("key_points", []),
        sentiment=analysis_result.get("sentiment", "neutral")
    )
    
    return crud.create_document_analysis(db=db, analysis=analysis_data)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a document."""
    document = crud.get_document(db, document_id=document_id)
    if document is None or document.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete file if it exists
    if os.path.exists(document.file_path):
        try:
            os.remove(document.file_path)
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Error deleting file: {str(e)}")
    
    # Delete from database
    crud.delete_document(db=db, document_id=document_id)
    
    return None
