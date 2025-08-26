
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from api.conversation import router as conversation_router
from api.voice_recording import router as voice_recording_router
from services.voice_to_text_service import generate_conversation_summary, generate_soap_note

# Load environment variables from backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


print(f"🔑 GROQ_API_KEY loaded: {'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")
if os.getenv('GROQ_API_KEY'):
    print(f"🔑 API Key starts with: {os.getenv('GROQ_API_KEY')[:10]}...")


app = FastAPI(title="Medical Voice Assistant API", version="2.0.0")

# Pydantic model for summary request
class GenerateSummaryRequest(BaseModel):
    doctor_conversation: str
    patient_conversation: str
    full_transcript: str

# Pydantic model for SOAP request
class GenerateSOAPRequest(BaseModel):
    doctor_conversation: str
    patient_conversation: str
    full_transcript: str
    timeline: list | None = None

# Allow CORS for local Streamlit frontend

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount static files for downloads and HTML pages
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/recordings", StaticFiles(directory="recordings"), name="recordings")

# Root endpoint for summary generation (called directly by frontend)
@app.post("/generate_summary")
async def generate_summary_endpoint(request: GenerateSummaryRequest):
    """Generate summary from doctor and patient conversations"""
    try:
        # Combine conversations for summary
        combined_text = f"""
        Doctor Conversation: {request.doctor_conversation}

        Patient Conversation: {request.patient_conversation}

        Full Transcript: {request.full_transcript}
        """

        # Use existing summary service (expects 'transcript' or 'timeline')
        summary_data = {"transcript": combined_text}
        result = await generate_conversation_summary(summary_data)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e), "summary": "Error generating summary"}, status_code=500)

# New endpoint for SOAP note generation
@app.post("/generate_soap")
async def generate_soap_endpoint(request: GenerateSOAPRequest):
    try:
        combined_text = f"Doctor: {request.doctor_conversation}\nPatient: {request.patient_conversation}\n{request.full_transcript}"
        data = {"transcript": combined_text, "timeline": request.timeline or []}
        result = await generate_soap_note(data)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"soap_html": "", "soap_json": {}, "error": str(e)}, status_code=500)

# Include routers
app.include_router(conversation_router, prefix="/api/v1/conversation")
app.include_router(voice_recording_router, prefix="/api/v1/voice-recording")

if __name__ == "__main__":
    import uvicorn
    print("[STARTUP] Starting FastAPI server on 0.0.0.0:8000")
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"[STARTUP] Failed to start server: {e}")
