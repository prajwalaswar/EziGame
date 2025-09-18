import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from api.conversation import router as conversation_router
from api.voice_recording import router as voice_recording_router
from api.summary import router as summary_router
from api.ai_edit import router as ai_edit_router
from api.streaming import router as streaming_router
# from api.voice_detection import router as voice_detection_router
from api.legacy import router as legacy_router

# Load environment variables from backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

print(f"🔑 GEMINI_API_KEY loaded: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")
if os.getenv('GEMINI_API_KEY'):
    print(f"🔑 API Key starts with: {os.getenv('GEMINI_API_KEY')[:10]}...")

app = FastAPI(title="Medical Voice Assistant API", version="2.0.0")

# Allow CORS for local Streamlit frontend

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/recordings", StaticFiles(directory="recordings"), name="recordings")
app.include_router(summary_router, prefix="/api/v1/summary", tags=["Summary"])

# Legacy root endpoints for backwards compatibility (e.g., /generate_soap)
app.include_router(legacy_router, prefix="", tags=["Legacy"])

app.include_router(ai_edit_router, prefix="/api/v1/ai-edit", tags=["AIEdit"])

# Include routers
app.include_router(conversation_router, prefix="/api/v1/conversation", tags=["Conversation"])
app.include_router(voice_recording_router, prefix="/api/v1/voice-recording", tags=["VoiceRecording"])
app.include_router(streaming_router, prefix="/api/v1/streaming", tags=["Streaming"])
# app.include_router(voice_detection_router, prefix="/api/v1/voice-detection", tags=["VoiceDetection"])

if __name__ == "__main__":
    import uvicorn
    print("[STARTUP] Starting FastAPI server on 0.0.0.0:8000")
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"[STARTUP] Failed to start server: {e}")
