import asyncio
from typing import Optional
import numpy as np
import torch
import torchaudio
from services.logger import logger
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

async def process_streaming_audio(audio_chunk: bytes) -> Optional[str]:
    """
    Process a chunk of audio data and return the transcription.
    """
    try:
        # Validate buffer size
        if len(audio_chunk) % 4 != 0:  # Assuming float32 (4 bytes per element)
            raise ValueError("Buffer size must be a multiple of element size (4 bytes for float32)")

        # Convert bytes to numpy array
        audio_np = np.frombuffer(audio_chunk, dtype=np.float32)

        # Ensure the NumPy array is writable
        if not audio_np.flags.writeable:
            audio_np = np.copy(audio_np)

        # Convert to tensor
        audio_tensor = torch.from_numpy(audio_np)

        # Process with Gemini (or your preferred STT service)
        response = await process_with_gemini(audio_tensor)

        return response
    except ValueError as ve:
        logger.error(f"ValueError: {str(ve)}")
        return None
    except Exception as e:
        logger.error(f"Error processing streaming audio: {str(e)}")
        return None

async def process_with_gemini(audio_tensor) -> str:
    """
    Process audio with Gemini API.
    Note: This is a simplified version. You'll need to implement the actual
    Gemini streaming API integration based on their documentation.
    """
    try:
        # Convert tensor to appropriate format for Gemini
        # Implement actual Gemini streaming API call here
        # This is a placeholder
        return "Transcription result would go here"
    except Exception as e:
        logger.error(f"Error with Gemini API: {str(e)}")
        return ""
