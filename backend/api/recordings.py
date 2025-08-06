# recordings.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from backend.services.voice_recording_service import (
    get_recording_info,
    list_all_recordings,
    delete_recording,
    cleanup_old_recordings
)

router = APIRouter()

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join("recordings", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=filename, media_type='audio/mpeg')

@router.get("/recordings")
async def list_recordings():
    return list_all_recordings()

@router.get("/recordings/{filename}")
async def get_recording_details(filename: str):
    return get_recording_info(filename)

@router.delete("/recordings/{filename}")
async def delete_recording_file(filename: str):
    return delete_recording(filename)

@router.post("/cleanup-recordings/")
async def cleanup_old_recordings_endpoint(days_old: int = 30):
    return cleanup_old_recordings(days_old)
