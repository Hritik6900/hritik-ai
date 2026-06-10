"""
Voice handler - processes Vapi webhook events.
Logs call lifecycle events and transcripts.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

VOICE_LOG_FILE = "voice_calls.log"


def log_event(event_type: str, data: Dict) -> None:
    """
    Log a voice call event to file.
    
    Args:
        event_type (str): Type of event (call-started, call-ended, transcript, etc)
        data (dict): Event data
    """
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "event_type": event_type,
        "data": data
    }
    
    # Append to log file
    with open(VOICE_LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    # Also print to console for debugging
    print(f"[{timestamp}] {event_type}: {json.dumps(data, indent=2)}")


def handle_call_started(event: Dict) -> None:
    """
    Handle call-started webhook event.
    
    Args:
        event (dict): Event payload from Vapi
    """
    call_id = event.get("call", {}).get("id")
    phone_number = event.get("call", {}).get("phoneNumber", "unknown")
    
    log_data = {
        "call_id": call_id,
        "phone_number": phone_number,
        "start_time": datetime.now().isoformat()
    }
    
    log_event("call-started", log_data)


def handle_call_ended(event: Dict) -> None:
    """
    Handle call-ended webhook event.
    
    Args:
        event (dict): Event payload from Vapi
    """
    call_id = event.get("call", {}).get("id")
    duration_seconds = event.get("call", {}).get("duration", 0)
    
    log_data = {
        "call_id": call_id,
        "duration_seconds": duration_seconds,
        "end_time": datetime.now().isoformat()
    }
    
    log_event("call-ended", log_data)


def handle_transcript(event: Dict) -> None:
    """
    Handle transcript webhook event.
    
    Args:
        event (dict): Event payload from Vapi
    """
    call_id = event.get("call", {}).get("id")
    messages = event.get("messages", [])
    
    # Extract user and assistant messages
    conversation = []
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")
        conversation.append({
            "role": role,
            "content": content
        })
    
    log_data = {
        "call_id": call_id,
        "messages_count": len(messages),
        "conversation": conversation
    }
    
    log_event("transcript", log_data)


def handle_webhook(payload: Dict) -> dict:
    """
    Main webhook handler - routes events to appropriate handlers.
    
    Args:
        payload (dict): Webhook payload from Vapi
    
    Returns:
        dict: Response acknowledgment
    """
    message_type = payload.get("message", {}).get("type", "unknown")
    
    if message_type == "call-started":
        handle_call_started(payload.get("message", {}))
    elif message_type == "call-ended":
        handle_call_ended(payload.get("message", {}))
    elif message_type == "transcript":
        handle_transcript(payload.get("message", {}))
    else:
        # Log any other events
        log_event(message_type, payload.get("message", {}))
    
    return {"status": "received"}


def get_call_history(call_id: str = None) -> list:
    """
    Get call history from log file.
    
    Args:
        call_id (str, optional): Filter by specific call_id
    
    Returns:
        list[dict]: List of call events
    """
    if not os.path.exists(VOICE_LOG_FILE):
        return []
    
    events = []
    with open(VOICE_LOG_FILE, "r") as f:
        for line in f:
            try:
                event = json.loads(line)
                if call_id is None or event.get("data", {}).get("call_id") == call_id:
                    events.append(event)
            except json.JSONDecodeError:
                continue
    
    return events


if __name__ == "__main__":
    # Test event logging
    test_event = {
        "call_id": "test_123",
        "phone_number": "+1234567890",
        "start_time": datetime.now().isoformat()
    }
    
    log_event("call-started", test_event)
    
    # Test call history
    history = get_call_history()
    print(f"\nCall history: {len(history)} events")
