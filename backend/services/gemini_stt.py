import os
import logging
from google.genai import Client, types
from google.genai.errors import APIError

logger = logging.getLogger(__name__)

def transcribe_audio(audio_path: str) -> str | None:
    """
    Transcribes audio using the Gemini API.

    Args:
        audio_path (str): Path to the audio file to transcribe.

    Returns:
        str | None: Transcription of the audio, or None if transcription failed.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not set in environment")
        return None

    model = os.getenv("GEMINI_STT_MODEL")
    if not model:
        logger.error("GEMINI_STT_MODEL not set in environment; please set it in backend/.env")
        return None

    try:
        # Initialize the Gemini client
        client = Client(api_key=api_key)

        logger.info(f"[GEMINI] Uploading audio file: {audio_path}")
        # Upload the audio file
        uploaded_file = client.files.upload(file=audio_path)

        # Inspect the uploaded file object
        logger.debug(f"Uploaded file details: {uploaded_file}")

        logger.info(f"[GEMINI] Requesting transcription using model: {model}")
        # Create a Part object for the uploaded file
        with open(audio_path, 'rb') as audio_file:
            file_part = types.Part.from_bytes(data=audio_file.read(), mime_type='audio/wav')

        # Use GenerateContentConfig (this SDK version expects this config type)
        config = types.GenerateContentConfig(
            max_output_tokens=2048,
            temperature=0.0,
        )

        # Request transcription
        response = client.models.generate_content(
            model=model,
            contents=[file_part],
            config=config,
        )

        # Extract the transcription text (SDK returns text attribute for text responses)
        transcript = getattr(response, 'text', None)
        if not transcript:
            logger.warning("[GEMINI] Empty transcription returned by the API")
            return None

        logger.info(f"[GEMINI] Transcription successful. Length: {len(transcript)} characters")
        return transcript

    except APIError as api_err:
        logger.error(f"[GEMINI] API error: {api_err}")
        return None

    except Exception as e:
        logger.exception("[GEMINI] Transcription failed")
        return None
