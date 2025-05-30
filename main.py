from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
def read_root():
    return {"message": "Welcome to the Program Pal Pathfinder API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
