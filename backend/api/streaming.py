from fastapi import APIRouter, WebSocket
from typing import List
import asyncio
from services.streaming_service import process_streaming_audio
from services.logger import logger

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_transcription(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/stream-audio/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Receive audio chunk
            audio_data = await websocket.receive_bytes()
            
            # Process the audio chunk using Gemini STT
            transcription = await process_streaming_audio(audio_data)
            
            # Send the transcription back to the client
            if transcription:
                await manager.send_transcription(transcription, websocket)
            else:
                await manager.send_transcription("[No transcription available]", websocket)
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        manager.disconnect(websocket)
