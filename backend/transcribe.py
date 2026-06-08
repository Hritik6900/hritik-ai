"""
Audio transcription module for Hritik AI.
Handles voice input using Gemini's native audio understanding.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set in .env file")

genai.configure(api_key=GEMINI_API_KEY)


async def transcribe(audio_bytes: bytes, audio_format: str = "audio/webm") -> dict:
    """
    Transcribe audio using Gemini 1.5 Flash's native audio understanding.
    
    Args:
        audio_bytes (bytes): Raw audio data
        audio_format (str): MIME type of audio (audio/webm, audio/wav, audio/mp3, etc.)
    
    Returns:
        dict: {
            "transcript": str,  # The transcribed text
            "latency": float   # Processing time in seconds
        }
    """
    
    start_time = time.time()
    
    print(f"🎤 Transcribing audio ({audio_format}, {len(audio_bytes)} bytes)...")
    
    try:
        # Create audio part for Gemini
        audio_part = {
            "mime_type": audio_format,
            "data": audio_bytes
        }
        
        # Call Gemini with audio
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        response = model.generate_content([
            audio_part,
            "Transcribe this audio exactly as spoken. Return only the transcript, nothing else."
        ])
        
        transcript = response.text.strip()
        latency = time.time() - start_time
        
        print(f"✅ Transcription complete in {latency:.2f}s")
        print(f"📝 Transcript: '{transcript}'")
        
        return {
            "transcript": transcript,
            "latency": latency
        }
        
    except Exception as e:
        latency = time.time() - start_time
        error_msg = f"Error transcribing audio: {str(e)}"
        print(f"❌ Error: {e}")
        
        return {
            "transcript": "",
            "error": error_msg,
            "latency": latency
        }


if __name__ == "__main__":
    print("Transcribe module loaded. Use with FastAPI for voice input processing.")
