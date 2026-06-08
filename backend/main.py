# """
# FastAPI backend for Hritik AI chat application.
# Provides REST endpoints for chat and voice transcription.
# """

# import os
# from dotenv import load_dotenv
# from fastapi import FastAPI, HTTPException, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import logging
# import time

# # Import backend modules
# from chat import chat
# from transcribe import transcribe
# from retriever import index

# # Load environment variables
# load_dotenv()

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# if not GEMINI_API_KEY:
#     raise ValueError("GEMINI_API_KEY not set in .env file")

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Initialize FastAPI app
# app = FastAPI(
#     title="Hritik AI Backend",
#     description="RAG-powered chat interface for Hritik Kumar",
#     version="1.0.0"
# )

# # Add CORS middleware (allow all origins for development)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# # Request/Response models
# class ChatRequest(BaseModel):
#     message: str
#     session_id: str = None


# class ChatResponse(BaseModel):
#     response: str
#     sources: list[str]
#     latency: float


# class TranscribeResponse(BaseModel):
#     transcript: str
#     latency: float


# class HealthResponse(BaseModel):
#     status: str
#     chunks_loaded: int
#     timestamp: str


# # Middleware for request logging
# @app.middleware("http")
# async def log_requests(request, call_next):
#     """Log incoming requests and response time."""
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     logger.info(f"{request.method} {request.url.path} - {response.status_code} ({process_time:.2f}s)")
#     return response


# # Routes

# @app.get("/health", response_model=HealthResponse)
# async def health():
#     """
#     Health check endpoint.
#     Returns status and number of chunks loaded in ChromaDB.
#     """
#     try:
#         # Try to count documents in the collection
#         collection = index._vector_store._collection
#         chunks_count = collection.count() if hasattr(collection, 'count') else 0
        
#         logger.info(f"✅ Health check: {chunks_count} chunks loaded")
        
#         return HealthResponse(
#             status="ok",
#             chunks_loaded=chunks_count,
#             timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
#         )
#     except Exception as e:
#         logger.error(f"❌ Health check failed: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/chat", response_model=ChatResponse)
# async def chat_endpoint(request: ChatRequest):
#     """
#     Chat endpoint.
#     Accepts a message and returns a RAG-grounded response with sources.
    
#     Request body:
#     {
#         "message": "Tell me about your experience",
#         "session_id": "optional-session-id"
#     }
#     """
    
#     if not request.message or request.message.strip() == "":
#         raise HTTPException(status_code=400, detail="Message cannot be empty")
    
#     logger.info(f"📬 Chat request: {request.message[:50]}...")
    
#     try:
#         result = await chat(request.message, request.session_id)
        
#         return ChatResponse(
#             response=result["response"],
#             sources=result["sources"],
#             latency=result["latency"]
#         )
        
#     except Exception as e:
#         logger.error(f"❌ Chat error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/transcribe", response_model=TranscribeResponse)
# async def transcribe_endpoint(file: UploadFile = File(...)):
#     """
#     Transcribe endpoint.
#     Accepts an audio file and returns the transcribed text.
    
#     Supported formats: webm, wav, mp3, m4a, ogg, flac, aac
#     """
    
#     if not file:
#         raise HTTPException(status_code=400, detail="No audio file provided")
    
#     # Validate audio file
#     allowed_types = [
#         "audio/webm", "audio/wav", "audio/mpeg", "audio/mp4",
#         "audio/x-m4a", "audio/ogg", "audio/flac", "audio/aac"
#     ]
    
#     if file.content_type not in allowed_types:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Invalid audio format. Allowed: {', '.join(allowed_types)}"
#         )
    
#     logger.info(f"🎙️  Transcribe request: {file.filename} ({file.content_type})")
    
#     try:
#         # Read audio bytes
#         audio_bytes = await file.read()
        
#         # Transcribe
#         result = await transcribe(audio_bytes, file.content_type)
        
#         if "error" in result:
#             raise HTTPException(status_code=500, detail=result["error"])
        
#         return TranscribeResponse(
#             transcript=result["transcript"],
#             latency=result["latency"]
#         )
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"❌ Transcription error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/")
# async def root():
#     """Root endpoint - API info."""
#     return {
#         "name": "Hritik AI Backend",
#         "version": "1.0.0",
#         "docs": "/docs",
#         "endpoints": {
#             "health": "GET /health",
#             "chat": "POST /chat",
#             "transcribe": "POST /transcribe"
#         }
#     }


# if __name__ == "__main__":
#     import uvicorn
    
#     # Run with: uvicorn main:app --reload
#     uvicorn.run(
#         app,
#         host="0.0.0.0",
#         port=8000,
#         log_level="info"
#     )


"""
FastAPI backend - Hritik AI
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from chat import chat

load_dotenv()

app = FastAPI(title="Hritik AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    sources: list[str]

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        result = chat(request.message, request.session_id)
        return ChatResponse(
            response=result["response"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))