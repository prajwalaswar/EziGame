# conversation.py

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from services.voice_to_text_service import process_conversation_audio
import os

router = APIRouter()

@router.post("/analyze-conversation/")
async def analyze_conversation(audio: UploadFile = File(...)):
    temp_path = f"temp_conversation_{audio.filename}"
    try:
        with open(temp_path, "wb") as f:
            f.write(await audio.read())
        result = await process_conversation_audio(temp_path)
        os.remove(temp_path)
        if "error" in result:
            return JSONResponse(result, status_code=500)

        # Add success flag for frontend
        result["success"] = True
        return JSONResponse(result)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return JSONResponse({
            "success": False,
            "error": str(e),
            "transcript": "",
            "doctor_transcript": "",
            "patient_transcript": "",
            "full_conversation": []
        }, status_code=500)

