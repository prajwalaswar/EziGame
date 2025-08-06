# voice.py
from fastapi import APIRouter
from backend.services.voice_recording_service import record_voice
from backend.services.voice_to_text_service import convert_voice_to_text

router = APIRouter()

@router.post("/record")
def record():
    return record_voice()

@router.post("/voice-to-text")
def voice_to_text():
    return convert_voice_to_text()
