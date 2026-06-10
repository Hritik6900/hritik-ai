"""
FastAPI backend - Hritik AI
Includes text chat, voice agent integration, and calendar management.
"""

import os
import time
import json
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from chat import chat
from calendar import get_availability, book_slot
from voice_handler import handle_webhook

load_dotenv()

app = FastAPI(title="Hritik AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST/RESPONSE MODELS - TEXT CHAT
# ============================================================================

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    sources: list[str]

# ============================================================================
# REQUEST/RESPONSE MODELS - VOICE CHAT
# ============================================================================

class VapiMessage(BaseModel):
    role: str
    content: str

class VapiCall(BaseModel):
    id: str
    phoneNumber: Optional[str] = None

class VapiRequest(BaseModel):
    type: str
    call: VapiCall
    messages: list[VapiMessage]

class VapiChatRequest(BaseModel):
    message: VapiRequest

class VapiChatResponse(BaseModel):
    response: str

# ============================================================================
# REQUEST/RESPONSE MODELS - CALENDAR
# ============================================================================

class CalendarBookRequest(BaseModel):
    name: str
    email: str
    slot: str
    purpose: Optional[str] = "Interview"

class CalendarBookResponse(BaseModel):
    success: bool
    booking_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

# ============================================================================
# TEXT CHAT ENDPOINTS
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Text chat endpoint - standard chat interface.
    Retrieves context from knowledge base and generates grounded response.
    """
    try:
        start_time = time.time()
        result = chat(request.message, request.session_id)
        latency = time.time() - start_time
        
        return ChatResponse(
            response=result["response"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# VOICE CHAT ENDPOINTS
# ============================================================================

@app.post("/voice/chat", response_model=VapiChatResponse)
async def voice_chat_endpoint(request: VapiChatRequest):
    """
    Vapi voice chat endpoint - called on every conversation turn.
    
    Vapi sends:
    {
      "message": {
        "type": "assistant-request",
        "call": {"id": "call_123", "phoneNumber": "+1234567890"},
        "messages": [{"role": "user", "content": "Tell me about your projects"}]
      }
    }
    
    Returns:
    {
      "response": "Here's what I know about Hritik's projects..."
    }
    """
    try:
        call_id = request.message.call.id
        messages = request.message.messages
        
        # Extract the latest user message
        user_message = None
        for msg in reversed(messages):
            if msg.role == "user":
                user_message = msg.content
                break
        
        if not user_message:
            raise ValueError("No user message found in request")
        
        # Log the call for debugging
        print(f"[Voice Chat] Call ID: {call_id}, Message: {user_message[:100]}")
        
        # Call the existing chat function (reuses RAG pipeline)
        start_time = time.time()
        result = chat(user_message, session_id=call_id)
        latency = time.time() - start_time
        
        # For voice, we only return the response text (no sources in audio)
        response_text = result["response"]
        
        # Log latency for monitoring
        print(f"[Voice Chat] Call ID: {call_id}, Latency: {latency:.2f}s, Response: {response_text[:100]}")
        
        return VapiChatResponse(response=response_text)
        
    except Exception as e:
        print(f"[Voice Chat Error] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/webhook")
async def voice_webhook(payload: dict):
    """
    Vapi webhook endpoint - handles all call lifecycle events.
    
    Events received:
    - call-started: Call initiated
    - call-ended: Call finished (includes duration)
    - transcript: Full conversation transcript
    - message: User audio messages
    
    This endpoint logs all events to voice_calls.log for monitoring.
    """
    try:
        # Extract message type from nested structure
        message_data = payload.get("message", {})
        
        # Process webhook with voice_handler
        result = handle_webhook(payload)
        
        print(f"[Webhook] Processed event: {message_data.get('type', 'unknown')}")
        
        return {"status": "received", "message": "Webhook processed"}
        
    except Exception as e:
        print(f"[Webhook Error] {str(e)}")
        # Still return 200 to Vapi to acknowledge receipt
        return {"status": "error", "message": str(e)}

# ============================================================================
# CALENDAR ENDPOINTS
# ============================================================================

@app.get("/calendar/availability")
async def calendar_availability():
    """
    Get available time slots for interviews.
    
    Returns list of available slots in IST timezone.
    """
    try:
        slots = get_availability()
        return {
            "success": True,
            "slots": slots,
            "timezone": "IST",
            "count": len(slots)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calendar/book", response_model=CalendarBookResponse)
async def calendar_book(request: CalendarBookRequest):
    """
    Book an interview slot on Hritik's calendar.
    
    Request:
    {
      "name": "Recruiter Name",
      "email": "recruiter@company.com",
      "slot": "Monday 10 AM - 11 AM IST",
      "purpose": "Technical Interview"
    }
    
    Returns booking confirmation with unique booking ID.
    Saves to local bookings.json file.
    """
    try:
        result = book_slot(
            name=request.name,
            email=request.email,
            slot=request.slot,
            purpose=request.purpose
        )
        
        if result.get("success"):
            print(f"[Calendar] Booking confirmed: {result['booking_id']} - {request.email}")
            return CalendarBookResponse(
                success=True,
                booking_id=result["booking_id"],
                message=result["message"]
            )
        else:
            print(f"[Calendar] Booking failed: {result.get('error')}")
            return CalendarBookResponse(
                success=False,
                error=result.get("error", "Booking failed")
            )
    
    except Exception as e:
        print(f"[Calendar Error] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ADMIN ENDPOINTS (for testing/debugging)
# ============================================================================

@app.get("/admin/bookings")
async def admin_bookings():
    """
    Get all bookings (admin endpoint).
    Returns all recorded bookings from bookings.json.
    """
    try:
        with open("bookings.json", "r") as f:
            bookings = json.load(f)
        return {
            "total": len(bookings),
            "bookings": bookings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/admin/bookings/clear")
async def admin_clear_bookings():
    """
    Clear all bookings (admin endpoint - for testing only).
    """
    try:
        with open("bookings.json", "w") as f:
            json.dump([], f, indent=2)
        return {"status": "ok", "message": "All bookings cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))