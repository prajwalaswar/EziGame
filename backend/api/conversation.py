# conversation.py
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from backend.services.voice_to_text_service import (
    transcribe_simple_audio,
    process_conversation_audio,
    generate_conversation_summary
)
import os

router = APIRouter()

class SummaryRequest(BaseModel):
    conversation: str

@router.post("/transcribe/")
async def transcribe(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        result = await transcribe_simple_audio(temp_path)
        os.remove(temp_path)
        if "error" in result:
            return JSONResponse(result, status_code=500)
        return JSONResponse(result)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return JSONResponse({"error": str(e), "transcript": ""}, status_code=500)

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
        return JSONResponse(result)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return JSONResponse({"error": str(e), "transcript": "", "doctor_transcript": "", "patient_transcript": "", "full_conversation": []}, status_code=500)

@router.post("/generate-summary/")
async def generate_summary(request: SummaryRequest):
    return await generate_conversation_summary(request.dict())

@router.post("/summarize-conversation/")
async def summarize_conversation(data: dict):
    return await generate_conversation_summary(data)
