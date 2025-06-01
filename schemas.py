from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# User schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        orm_mode = True

# Document schemas
class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    file_path: str
    created_at: datetime
    user_id: int
    
    class Config:
        orm_mode = True

# Program schemas
class ProgramBase(BaseModel):
    name: str
    university: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    is_shortlisted: bool = False

class ProgramCreate(ProgramBase):
    pass

class Program(ProgramBase):
    id: int
    created_at: datetime
    user_id: int
    
    class Config:
        orm_mode = True

# Email schemas
class EmailBase(BaseModel):
    subject: str
    sender: str
    recipient: str
    content: str
    is_read: bool = False

class EmailCreate(EmailBase):
    pass

class Email(EmailBase):
    id: int
    created_at: datetime
    user_id: int
    
    class Config:
        orm_mode = True
