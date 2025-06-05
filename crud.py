from sqlalchemy.orm import Session
import models, schemas, security
from fastapi import HTTPException, status
import os
import json

def get_user(db: Session, user_id: int):
    """Get a user by ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Get a user by email."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get a list of users."""
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    """Create a new user."""
    # Check if user already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    hashed_password = security.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password
    )
    
    # Add to database and commit
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# Document CRUD operations
def get_document(db: Session, document_id: int):
    """Get a document by ID."""
    return db.query(models.Document).filter(models.Document.id == document_id).first()

def get_documents(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get documents for a user."""
    return db.query(models.Document).filter(
        models.Document.user_id == user_id
    ).offset(skip).limit(limit).all()

def create_document(db: Session, document: schemas.DocumentCreate, user_id: int, file_path: str):
    """Create a new document for a user."""
    db_document = models.Document(
        **document.dict(),
        file_path=file_path,
        user_id=user_id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def delete_document(db: Session, document_id: int):
    """Delete a document."""
    db_document = get_document(db, document_id=document_id)
    if db_document:
        db.delete(db_document)
        db.commit()
    return db_document

def create_document_analysis(db: Session, analysis: schemas.DocumentAnalysisCreate):
    """Create a document analysis."""
    db_analysis = models.DocumentAnalysis(
        document_id=analysis.document_id,
        summary=analysis.summary,
        # Store key_points as JSON string
        key_points=json.dumps(analysis.key_points),
        sentiment=analysis.sentiment
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis

def get_document_analysis(db: Session, document_id: int):
    """Get analysis for a document."""
    return db.query(models.DocumentAnalysis).filter(
        models.DocumentAnalysis.document_id == document_id
    ).first()

# Program CRUD operations
def get_programs(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get programs for a user."""
    return db.query(models.Program).filter(
        models.Program.user_id == user_id
    ).offset(skip).limit(limit).all()

def create_program(db: Session, program: schemas.ProgramCreate, user_id: int):
    """Create a new program for a user."""
    db_program = models.Program(
        **program.dict(),
        user_id=user_id
    )
    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program

# Email CRUD operations
def get_emails(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get emails for a user."""
    return db.query(models.Email).filter(
        models.Email.user_id == user_id
    ).offset(skip).limit(limit).all()

def create_email(db: Session, email: schemas.EmailCreate, user_id: int):
    """Create a new email for a user."""
    db_email = models.Email(
        **email.dict(),
        user_id=user_id
    )
    db.add(db_email)
    db.commit()
    db.refresh(db_email)
    return db_email
