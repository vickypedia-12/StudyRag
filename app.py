from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import shutil
import uvicorn
from pydantic import BaseModel
from study import StudyDocumentProcessor, StudyRAG

# Initialize FastAPI app
app = FastAPI(
    title="Study RAG API",
    description="API for the Study RAG application",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize the RAG components
processor = StudyDocumentProcessor()
rag = StudyRAG()

# Pydantic models for request/response
class QueryRequest(BaseModel):
    question: str
    max_sources: int = 3

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

class UploadResponse(BaseModel):
    filename: str
    status: str
    sections_processed: int = 0

# Routes
@app.get("/")
def read_root():
    return {"message": "Welcome to Study RAG API", "status": "active"}

@app.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """
    Query the RAG system with a question
    """
    try:
        result = rag.get_response_with_sources(request.question)
        
        # Limit the number of sources if requested
        if len(result["sources"]) > request.max_sources:
            result["sources"] = result["sources"][:request.max_sources]
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document to be processed by the RAG system
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs("study_materials", exist_ok=True)
        
        # Save the uploaded file
        file_path = os.path.join("study_materials", file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Check file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension not in ['.pdf', '.txt', '.json', '.ppt', '.pptx']:
            os.remove(file_path)
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Supported types: .pdf, .txt, .json, .ppt, .pptx"
            )
        
        # Process the document
        try:
            # Save the current count of documents in the vector store
            current_count = len(rag.vectorstore.get()["ids"]) if rag.vectorstore.get() else 0
            
            # Process the document
            processor.process_document(file_path)
            
            # Get the new count to calculate how many sections were processed
            new_count = len(rag.vectorstore.get()["ids"]) if rag.vectorstore.get() else 0
            sections_processed = new_count - current_count
            
            return {
                "filename": file.filename,
                "status": "success",
                "sections_processed": sections_processed
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@app.get("/documents")
async def list_documents():
    """
    List all documents available in the study materials
    """
    try:
        if not os.path.exists("study_materials"):
            return {"documents": []}
            
        documents = []
        for filename in os.listdir("study_materials"):
            if filename.endswith(('.pdf', '.txt', '.json', '.ppt', '.pptx')):
                file_path = os.path.join("study_materials", filename)
                file_size = os.path.getsize(file_path)
                file_modified = os.path.getmtime(file_path)
                
                documents.append({
                    "filename": filename,
                    "size_bytes": file_size,
                    "last_modified": file_modified
                })
                
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """
    Delete a document from the study materials
    """
    try:
        file_path = os.path.join("study_materials", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Document {filename} not found")
            
        os.remove(file_path)
        
        return {"filename": filename, "status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

@app.get("/search")
async def search_documents(query: str = Query(..., min_length=1), limit: int = Query(5, ge=1, le=20)):
    """
    Search for relevant documents without generating an answer
    """
    try:
        results = rag.search_documents(query, k=limit)
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)