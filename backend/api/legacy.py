from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from .schemas import GenerateSOAPRequest
from services.voice_to_text_service import generate_soap_note
from services.logger import logger

router = APIRouter()

@router.post("/generate_soap", response_model=None)
async def legacy_generate_soap(request: GenerateSOAPRequest):
    """Legacy root-level endpoint for backward compatibility.

    This forwards to the same generator used by `/api/v1/summary/generate_soap`.
    """
    logger.info("Legacy endpoint '/generate_soap' hit: Generating SOAP note (legacy).")
    try:
        combined_text = (
            f"Doctor: {request.doctor_conversation}\n"
            f"Patient: {request.patient_conversation}\n"
            f"Full Transcript: {request.full_transcript}"
        )
        data = {
            "transcript": combined_text,
            "timeline": jsonable_encoder(request.timeline or [])
        }
        result = await generate_soap_note(data)
        logger.info("Legacy SOAP note generated successfully.")
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        logger.error(f"Error generating SOAP note (legacy): {e}")
        raise HTTPException(status_code=500, detail="Failed to generate SOAP note")
