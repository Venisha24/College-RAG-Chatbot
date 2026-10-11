import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from rag_engine import CollegeRAGEngine

app = FastAPI(
    title="GLS University RAG Chatbot REST API",
    description="Backend API service for student query processing over GLS University PDF Database",
    version="1.0.0"
)

# Initialize RAG Engine
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
rag_engine = CollegeRAGEngine(DATA_DIR)

class QueryRequest(BaseModel):
    query: str
    api_key: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    context_used: str

@app.get("/")
def home():
    return {
        "status": "online",
        "university": "GLS University, Ahmedabad",
        "service": "College RAG Chatbot API",
        "indexed_chunks": len(rag_engine.chunks)
    }

@app.get("/api/documents")
def get_documents():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.pdf')]
    return {"documents": files, "total_chunks": len(rag_engine.chunks)}

@app.post("/api/chat", response_model=QueryResponse)
def process_chat(req: QueryRequest):
    if not req.query or not req.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty")
    
    api_key = req.api_key or os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=401, detail="API key is required. Pass api_key in payload or set GEMINI_API_KEY env var.")

    result = rag_engine.generate_response(req.query, api_key)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
