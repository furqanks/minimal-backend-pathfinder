from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Import database, models, and routers using absolute imports
import models
import database
from routers import auth

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Program Pal Pathfinder API",
    description="API for managing university program applications, documents, and insights.",
    version="0.1.0",
)

# CORS Middleware
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "*"  # Allow all for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Program Pal Pathfinder API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/db-test")
def test_db(db: Session = Depends(database.get_db)):
    """Test database connection"""
    try:
        # Just query something simple to test connection
        db.execute("SELECT 1")
        return {"message": "Database connection successful"}
    except Exception as e:
        return {"error": f"Database connection failed: {str(e)}"}
