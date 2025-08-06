# voice_recording.py
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import os
from backend.services.voice_recording_service import process_voice_recording

router = APIRouter()

@router.post("/record-voice/")
async def record_voice(audio: UploadFile = File(...)):
    temp_path = f"temp_voice_{audio.filename}"
    try:
        with open(temp_path, "wb") as f:
            f.write(await audio.read())
        result = await process_voice_recording(temp_path, audio.filename)
        os.remove(temp_path)
        if not result.get("success"):
            return JSONResponse(result, status_code=500)
        return JSONResponse(result)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return JSONResponse({"error": str(e), "success": False}, status_code=500)
