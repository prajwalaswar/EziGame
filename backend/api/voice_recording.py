# voice_recording.py
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import os
import uuid
from datetime import datetime

from services.voice_to_text_service import process_conversation_audio
from services.logger import logger
import os
router = APIRouter() 

# Ensure recordings directory exists
RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)

@router.post("/record/")
async def record_voice(audio: UploadFile = File(...)):
    logger.info("Endpoint '/record/' hit: Saving uploaded audio file.")
    try:
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"recording_{timestamp}_{unique_id}.wav"
        file_path = os.path.join(RECORDINGS_DIR, filename)
        # Save the uploaded file
        with open(file_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        # Get file info
        file_size = os.path.getsize(file_path)
        file_size_mb = round(file_size / (1024 * 1024), 2)
        logger.info(f"Recording saved successfully: {filename}, Size: {file_size_mb} MB")
        return JSONResponse({
            "success": True,
            "message": "Recording saved successfully",
            "filename": filename,
            "file_path": file_path,
            "file_size": file_size,
            "file_size_mb": file_size_mb,
            "timestamp": timestamp,
            "download_url": f"/api/v1/voice-recording/download/{filename}"
        })
    except Exception as e:
        logger.error(f"Failed to save recording: {str(e)}")
        return JSONResponse({
            "success": False,
            "error": str(e),
            "message": "Failed to save recording"
        }, status_code=500)

@router.get("/download/{filename}")
async def download_recording(filename: str):
    logger.info(f"Endpoint '/download/{filename}' hit: Attempting to download recording.")
    file_path = os.path.join(RECORDINGS_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Recording not found")
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='audio/wav'
    )

@router.get("/list/")
async def list_recordings():
    logger.info("Endpoint '/list/' hit: Listing all recordings.")
    try:
        recordings = []
        if os.path.exists(RECORDINGS_DIR):
            for filename in os.listdir(RECORDINGS_DIR):
                if filename.endswith(('.wav', '.mp3', '.m4a', '.webm')):
                    file_path = os.path.join(RECORDINGS_DIR, filename)
                    file_size = os.path.getsize(file_path)
                    file_size_mb = round(file_size / (1024 * 1024), 2)
                    # Get file creation time
                    creation_time = os.path.getctime(file_path)
                    creation_date = datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
                    recordings.append({
                        "filename": filename,
                        "file_size": file_size,
                        "file_size_mb": file_size_mb,
                        "creation_date": creation_date,
                        "download_url": f"/api/v1/voice-recording/download/{filename}"
                    })
        # Sort by creation date (newest first)
        recordings.sort(key=lambda x: x['creation_date'], reverse=True)
        logger.info(f"Total recordings found: {len(recordings)}")
        return JSONResponse({
            "success": True,
            "recordings": recordings,
            "total_count": len(recordings)
        })
    except Exception as e:
        logger.error(f"Failed to list recordings: {str(e)}")
        return JSONResponse({
            "success": False,
            "error": str(e),
            "recordings": [],
            "total_count": 0
        }, status_code=500)

@router.delete("/delete/{filename}")
async def delete_recording(filename: str):
    logger.info(f"Endpoint '/delete/{filename}' hit: Attempting to delete recording.")
    try:
        file_path = os.path.join(RECORDINGS_DIR, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Recording not found")
        os.remove(file_path)
        logger.info(f"Recording {filename} deleted successfully.")
        return JSONResponse({
            "success": True,
            "message": f"Recording {filename} deleted successfully"
        })
    except Exception as e:
        logger.error(f"Failed to delete recording {filename}: {str(e)}")
        return JSONResponse({
            "success": False,
            "error": str(e),
            "message": f"Failed to delete recording {filename}"
        }, status_code=500)
