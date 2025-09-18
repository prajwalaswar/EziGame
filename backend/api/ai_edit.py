from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from services.voice_to_text_service import generate_ai_edit
from dependencies import get_logger, get_genai_client

router = APIRouter()


class EditRequest(BaseModel):
    transcript: str


@router.post("/edit-transcript/")
async def edit_transcript(req: EditRequest, logger=Depends(get_logger), genai_client=Depends(get_genai_client)):
    logger.info("/edit-transcript called")
    if not req.transcript or not req.transcript.strip():
        raise HTTPException(status_code=400, detail="Empty transcript")

    try:
        result = await generate_ai_edit(req.transcript, genai_client=genai_client)
        return {"edited": result}
    except Exception as e:
        logger.error(f"AI edit failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
