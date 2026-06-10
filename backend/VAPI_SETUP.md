# Vapi Voice Agent Integration Guide

## Setup Instructions

### 1. Environment Configuration

Update your `.env` file in `backend/` with:

```bash
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
CHROMA_PERSIST_DIR=./chroma_db
KNOWLEDGE_DIR=./knowledge
VAPI_API_KEY=your_vapi_api_key  # Get from Vapi dashboard
```

### 2. Backend Startup

```bash
cd backend

# Activate environment
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Install any new dependencies (if needed)
pip install -r requirements.txt

# Run the backend
uvicorn main:app --reload --port 8000
```

The backend will now run with all endpoints:
- Text chat: `POST /chat`
- Voice chat: `POST /voice/chat` (Vapi)
- Voice webhook: `POST /voice/webhook` (Vapi events)
- Calendar availability: `GET /calendar/availability`
- Calendar booking: `POST /calendar/book`

### 3. Vapi Configuration

#### Step 1: Update vapi_config.json

Replace these placeholders in `backend/vapi_config.json`:
- `YOUR_BACKEND_URL` → Your backend URL (e.g., `http://localhost:8000` for local, or `https://your-domain.com` for production)
- `YOUR_VAPI_API_KEY` → Your Vapi API key (from Vapi dashboard)

#### Step 2: Create Assistant in Vapi Dashboard

1. Go to [Vapi Dashboard](https://dashboard.vapi.ai)
2. Click "Create Assistant"
3. Copy the entire `vapi_config.json` content
4. Paste into the Vapi editor
5. Click "Save"

#### Step 3: Get Phone Number

1. In Vapi dashboard, go to "Phone Numbers"
2. Purchase or link a phone number
3. Assign the assistant to that number
4. Test by calling the number

### 4. System Prompt

The voice system prompt is in `backend/vapi_system_prompt.txt`. Key features:
- **Short responses** - max 3-4 sentences per turn
- **Natural speech** - no bullets, markdown, or robotic language
- **Calendar integration** - offers to check availability
- **Booking flow** - confirms name, email, and slot
- **Graceful fallback** - redirects unknown topics to scheduling

To use a custom system prompt in Vapi, paste the contents of `vapi_system_prompt.txt` into the `systemPrompt` field in the Vapi config.

## File Structure

```
backend/
├── main.py                          # Updated with voice/calendar endpoints
├── chat.py                          # Existing RAG + LLM (reused by voice)
├── retriever.py                     # Existing ChromaDB (reused by voice)
├── calendar.py                      # NEW: Calendar availability + booking
├── voice_handler.py                 # NEW: Webhook event processing
├── vapi_config.json                 # NEW: Vapi assistant configuration
├── vapi_system_prompt.txt           # NEW: Voice-specific system prompt
├── bookings.json                    # NEW: Local booking storage
├── chroma_db/                       # Existing persisted vector store
└── knowledge/                       # Existing knowledge base
    ├── personal/
    │   ├── CV.pdf
    │   └── hritik_facts.md
    └── github/
        ├── DualCast.md
        ├── NavDrishti-Server.md
        ├── terra_vision.md
        └── voteRakshak.md
```

## Architecture

```
Phone Call (Recruiter)
        ↓
    [Vapi Agent]
        ↓
    /voice/chat endpoint (main.py)
        ↓
    chat() function (chat.py)
        ↓
    retrieve() + Groq LLM (retriever.py + Groq API)
        ↓
    Response to Vapi
        ↓
    Voice Output (11labs TTS)
```

Calendar Flow:
```
Recruiter asks: "Can I schedule an interview?"
        ↓
    check_availability tool
        ↓
    /calendar/availability endpoint
        ↓
    Returns: ["Monday 10 AM - 11 AM IST", ...]
        ↓
Recruiter selects slot
        ↓
    book_slot tool
        ↓
    /calendar/book endpoint
        ↓
    Saves to bookings.json + returns confirmation
```

## Endpoints Reference

### Text Chat
```
POST /chat
Content-Type: application/json

{
  "message": "Tell me about your projects",
  "session_id": "default"
}

Response:
{
  "response": "I have experience in...",
  "sources": ["DualCast.md", "CV.pdf"]
}
```

### Voice Chat (Vapi)
```
POST /voice/chat
Content-Type: application/json

{
  "message": {
    "type": "assistant-request",
    "call": {
      "id": "call_123",
      "phoneNumber": "+1234567890"
    },
    "messages": [
      {"role": "user", "content": "Tell me about NavDrishti"}
    ]
  }
}

Response:
{
  "response": "NavDrishti is a navigation project..."
}
```

### Voice Webhook
```
POST /voice/webhook
Content-Type: application/json

{
  "message": {
    "type": "call-started" | "call-ended" | "transcript",
    "call": {"id": "call_123"},
    "messages": [...],
    "duration": 120  // seconds (for call-ended)
  }
}

Response:
{
  "status": "received"
}
```

### Calendar Availability
```
GET /calendar/availability

Response:
{
  "success": true,
  "slots": [
    "Monday 10 AM - 11 AM IST",
    "Tuesday 2 PM - 3 PM IST",
    ...
  ],
  "timezone": "IST",
  "count": 5
}
```

### Calendar Booking
```
POST /calendar/book
Content-Type: application/json

{
  "name": "John Recruiter",
  "email": "john@company.com",
  "slot": "Monday 10 AM - 11 AM IST",
  "purpose": "Technical Interview"
}

Response (Success):
{
  "success": true,
  "booking_id": "BK_20240609_101523_1234",
  "message": "Booking confirmed! Hritik will see your interview..."
}

Response (Error):
{
  "success": false,
  "error": "Invalid slot..."
}
```

### Admin Endpoints
```
# Get all bookings
GET /admin/bookings

# Clear all bookings (testing only)
DELETE /admin/bookings/clear
```

## Testing Guide

See `TESTING.md` for complete curl-based testing procedures.

Quick test:
```bash
# Test health
curl http://localhost:8000/health

# Test text chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about NavDrishti"}'

# Test calendar availability
curl http://localhost:8000/calendar/availability

# Test calendar booking
curl -X POST http://localhost:8000/calendar/book \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Recruiter",
    "email": "test@example.com",
    "slot": "Monday 10 AM - 11 AM IST"
  }'
```

## Key Design Decisions

### 1. Reusing Existing Chat Logic
- Voice agent uses the **exact same** `chat()` function from `chat.py`
- No separate AI brain or duplicate retrieval logic
- All voice responses are grounded in the same RAG pipeline
- Same system prompt (with voice-specific modifications)

### 2. Voice-Specific Prompt Engineering
- Shorter sentences (3-4 per turn vs. longer text responses)
- No markdown or bullet points (not spoken naturally)
- Conversational tone vs. formal
- Focus on calendar/booking flow

### 3. Calendar Integration
- Hardcoded slots (easy to customize in `calendar.py`)
- Local JSON storage for bookings (can upgrade to database)
- Booking IDs for tracking and confirmation
- Confirmation emails (implement via Vapi or separate service)

### 4. Webhook Logging
- All Vapi events logged to `voice_calls.log`
- Call start/end with duration
- Full transcript stored
- Easy debugging of voice interactions

## Troubleshooting

### Voice agent sounds robotic
- Update `vapi_system_prompt.txt` with more natural phrasing
- Use Vapi's backchannel settings to sound more conversational
- Test with different voice IDs in `vapi_config.json`

### Calendar not working
- Check that slots are being returned from `/calendar/availability`
- Verify `bookings.json` exists in backend directory
- Check logs for booking errors

### Webhook not receiving events
- Verify webhook URL in `vapi_config.json` is correct
- Check CORS headers (they're set to allow all)
- Monitor `voice_calls.log` for events
- Test with manual POST to `/voice/webhook`

### Missing responses
- Check that ChromaDB is initialized (run `python ingest.py`)
- Verify GROQ_API_KEY and GEMINI_API_KEY in `.env`
- Test `/chat` endpoint directly to debug RAG pipeline
- Check FastAPI logs for errors

## Production Deployment

When deploying to production:

1. **Update URLs**: Replace `YOUR_BACKEND_URL` in `vapi_config.json` with your production domain
2. **API Security**: Add authentication to sensitive endpoints (`/admin/*`)
3. **Database**: Replace `bookings.json` with a real database (PostgreSQL, MongoDB, etc.)
4. **Monitoring**: Set up logging aggregation for `voice_calls.log`
5. **SSL/TLS**: Ensure HTTPS for all webhook endpoints
6. **Rate Limiting**: Add rate limiting to prevent abuse
7. **Backup**: Regularly backup `bookings.json` and `chroma_db/`

## Next Steps

1. ✅ Backend endpoints are ready
2. ✅ Calendar logic is ready
3. ✅ Voice handler is ready
4. 📋 Configure Vapi (see Step 3 above)
5. 📋 Get Vapi phone number
6. 📋 Test voice interactions
7. 📋 Deploy to production

---

**Questions?** Review the TESTING.md file for detailed test cases and curl commands.
