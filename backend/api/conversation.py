# conversation.py
from fastapi import APIRouter, File, UploadFile, Depends
from fastapi.responses import JSONResponse
from services.voice_to_text_service import process_conversation_audio
from dependencies import get_logger, get_genai_client
import os

router = APIRouter()

@router.post("/analyze-conversation/")
async def analyze_conversation(
    audio: UploadFile = File(...),
    logger=Depends(get_logger),
    genai_client=Depends(get_genai_client),
):
    temp_path = f"temp_conversation_{audio.filename}"
    try:
        with open(temp_path, "wb") as f:
            f.write(await audio.read())
        result = await process_conversation_audio(temp_path, genai_client=genai_client)
        os.remove(temp_path)
        if "error" in result:
            return JSONResponse(result, status_code=500)

        result["success"] = True
        return JSONResponse(result)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        logger.error(f"analyze_conversation failed: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e),
            "transcript": "",
            "doctor_transcript": "",
            "patient_transcript": "",
            "full_conversation": []
        }, status_code=500)

