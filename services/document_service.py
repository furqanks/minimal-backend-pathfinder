import os
import shutil
from typing import Dict, List, Any
import json

def process_document(file_path: str, content_type: str) -> None:
    """
    Process a document after upload.
    
    This function handles initial document processing like:
    - Extracting text content
    - Generating metadata
    - Creating thumbnails (for images)
    
    Args:
        file_path: Path to the uploaded file
        content_type: MIME type of the file
    """
    # Create a metadata file for the document
    metadata = {
        "file_path": file_path,
        "content_type": content_type,
        "size_bytes": os.path.getsize(file_path),
        "created_at": os.path.getctime(file_path),
        "modified_at": os.path.getmtime(file_path),
    }
    
    # Extract text based on content type
    if content_type == "application/pdf":
        # For PDFs, use poppler-utils to extract text
        try:
            import subprocess
            output = subprocess.check_output(["pdftotext", file_path, "-"])
            metadata["extracted_text"] = output.decode("utf-8", errors="replace")
        except Exception as e:
            metadata["extraction_error"] = str(e)
    
    elif content_type.startswith("text/"):
        # For text files, read directly
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                metadata["extracted_text"] = f.read()
        except Exception as e:
            metadata["extraction_error"] = str(e)
    
    # Save metadata to a JSON file alongside the original
    metadata_path = f"{file_path}.metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

def analyze_document(file_path: str, content_type: str) -> Dict[str, Any]:
    """
    Analyze a document to extract insights.
    
    Args:
        file_path: Path to the document file
        content_type: MIME type of the file
        
    Returns:
        Dictionary containing analysis results
    """
    # Check if metadata exists
    metadata_path = f"{file_path}.metadata.json"
    extracted_text = ""
    
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
            extracted_text = metadata.get("extracted_text", "")
    
    # If no extracted text in metadata, try to extract it now
    if not extracted_text and content_type == "application/pdf":
        try:
            import subprocess
            output = subprocess.check_output(["pdftotext", file_path, "-"])
            extracted_text = output.decode("utf-8", errors="replace")
        except Exception:
            pass
    
    elif not extracted_text and content_type.startswith("text/"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                extracted_text = f.read()
        except Exception:
            pass
    
    # Perform basic analysis
    word_count = len(extracted_text.split())
    
    # Extract key points (simple implementation)
    sentences = [s.strip() for s in extracted_text.replace("\n", " ").split(".") if s.strip()]
    key_points = []
    
    # Get sentences that might be important (longer sentences)
    for sentence in sentences:
        if len(sentence.split()) > 10:  # Arbitrary threshold
            key_points.append(sentence)
    
    # Limit to top 5 key points
    key_points = key_points[:5]
    
    # Generate a simple summary
    summary = ""
    if sentences:
        summary = sentences[0]  # First sentence as summary
        if len(sentences) > 1:
            summary += " " + sentences[-1]  # Add last sentence
    
    # Simple sentiment analysis
    positive_words = ["good", "great", "excellent", "positive", "success", "benefit", "advantage"]
    negative_words = ["bad", "poor", "negative", "failure", "problem", "disadvantage", "issue"]
    
    positive_count = sum(1 for word in extracted_text.lower().split() if word in positive_words)
    negative_count = sum(1 for word in extracted_text.lower().split() if word in negative_words)
    
    sentiment = "neutral"
    if positive_count > negative_count * 2:
        sentiment = "positive"
    elif negative_count > positive_count * 2:
        sentiment = "negative"
    
    return {
        "summary": summary,
        "key_points": key_points,
        "word_count": word_count,
        "sentiment": sentiment
    }
