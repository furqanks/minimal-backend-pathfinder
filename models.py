from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
import datetime
import json

from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="owner")
    programs = relationship("Program", back_populates="user")
    emails = relationship("Email", back_populates="user")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    file_path = Column(String)
    content_type = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    owner = relationship("User", back_populates="documents")
    analyses = relationship("DocumentAnalysis", back_populates="document")

class DocumentAnalysis(Base):
    __tablename__ = "document_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    summary = Column(Text)
    # Changed from ARRAY(String) to Text to store JSON string for SQLite compatibility
    key_points = Column(Text)  # Will store JSON string representation of list
    sentiment = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="analyses")
    
    # Helper methods for key_points JSON conversion
    @property
    def key_points_list(self):
        """Convert stored JSON string to Python list"""
        if self.key_points:
            return json.loads(self.key_points)
        return []
    
    @key_points_list.setter
    def key_points_list(self, points_list):
        """Convert Python list to JSON string for storage"""
        if points_list is not None:
            self.key_points = json.dumps(points_list)
        else:
            self.key_points = json.dumps([])

class Program(Base):
    __tablename__ = "programs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    university = Column(String, index=True)
    description = Column(Text)
    deadline = Column(DateTime)
    is_shortlisted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", back_populates="programs")

class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, index=True)
    sender = Column(String)
    recipient = Column(String)
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    user = relationship("User", back_populates="emails")
