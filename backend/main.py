
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from backend.api.health import router as health_router
from backend.api.voice import router as voice_router
from backend.api.conversation import router as conversation_router
from backend.api.recordings import router as recordings_router
from backend.api.voice_recording import router as voice_recording_router

load_dotenv()


app = FastAPI(title="Medical Voice Assistant API", version="2.0.0")

# Allow CORS for local Streamlit frontend

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount static files for downloads
app.mount("/static", StaticFiles(directory="recordings"), name="static")

# Include routers
app.include_router(health_router)
app.include_router(voice_router)
app.include_router(conversation_router)
app.include_router(recordings_router)
app.include_router(voice_recording_router)
