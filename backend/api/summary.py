from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException
from .schemas import GenerateSummaryRequest, GenerateSOAPRequest
from services.voice_to_text_service import generate_conversation_summary, generate_soap_note
from dependencies import get_logger, get_genai_client, get_settings

router = APIRouter()

def _get_model_from_settings(settings: dict) -> str | None:
    # Return configured model name or None if not set. Do not provide a hardcoded default.
    return settings.get("GEMINI_LLM_MODEL")

@router.post("/generate_summary", response_model=None)
async def generate_summary_endpoint(
    request: GenerateSummaryRequest,
    logger=Depends(get_logger),
    genai_client=Depends(get_genai_client),
    settings: dict = Depends(get_settings),
):
    logger.info("Endpoint '/generate_summary' hit: Generating summary.")
    try:
        combined_text = f"""
        Doctor Conversation: {request.doctor_conversation}

        Patient Conversation: {request.patient_conversation}

        Full Transcript: {request.full_transcript}
        """
        summary_data = {"transcript": combined_text}
        result = await generate_conversation_summary(summary_data, genai_client=genai_client, model=_get_model_from_settings(settings))
        logger.info("Summary generated successfully.")
        return JSONResponse(result)
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return JSONResponse({"error": str(e), "summary": "Error generating summary"}, status_code=500)

@router.post("/generate_soap", response_model=None)
async def generate_soap_endpoint(
    request: GenerateSOAPRequest,
    logger=Depends(get_logger),
    genai_client=Depends(get_genai_client),
    settings: dict = Depends(get_settings),
):
    logger.info("Endpoint '/generate_soap' hit: Generating SOAP note.")
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
        result = await generate_soap_note(data, genai_client=genai_client, model=_get_model_from_settings(settings))
        logger.info("SOAP note generated successfully.")
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        logger.error(f"Error generating SOAP note: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate SOAP note")
    

# from fastapi import APIRouter, HTTPException
# from fastapi.responses import JSONResponse
# from fastapi.encoders import jsonable_encoder
# from .schemas import GenerateSummaryRequest, GenerateSOAPRequest
# from services.voice_to_text_service import generate_conversation_summary, generate_soap_note
# from services.logger import logger

# router = APIRouter()

# @router.post("/generate_summary")
# async def generate_summary_endpoint(request: GenerateSummaryRequest):
#     logger.info("Endpoint '/generate_summary' hit: Generating summary.")
#     try:
#         combined_text = "\n".join([
#             f"Doctor Conversation: {request.doctor_conversation}",
#             f"Patient Conversation: {request.patient_conversation}",
#             f"Full Transcript: {request.full_transcript}"
#         ])
        
#         summary_data = {"transcript": combined_text}
#         result = await generate_conversation_summary(summary_data)

#         logger.info("Summary generated successfully.")
#         return JSONResponse(content=jsonable_encoder(result))

#     except Exception as e:
#         logger.error(f"Error generating summary: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


# @router.post("/generate_soap")
# async def generate_soap_endpoint(request: GenerateSOAPRequest):
#     logger.info("Endpoint '/generate_soap' hit: Generating SOAP note.")
#     try:
#         combined_text = "\n".join([
#             f"Doctor: {request.doctor_conversation}",
#             f"Patient: {request.patient_conversation}",
#             f"Full Transcript: {request.full_transcript}"
#         ])

#         data = {
#             "transcript": combined_text,
#             "timeline": jsonable_encoder(request.timeline or [])
#         }
#         result = await generate_soap_note(data)

#         logger.info("SOAP note generated successfully.")
#         return JSONResponse(content=jsonable_encoder(result))

#     except Exception as e:
#         logger.error(f"Error generating SOAP note: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Failed to generate SOAP note: {str(e)}")
