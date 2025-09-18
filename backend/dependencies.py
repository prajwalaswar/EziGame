import os
import logging
from typing import Optional
from fastapi import Depends
from services import logger as logger_module

def get_logger() -> logging.Logger:
    """Return the configured application logger.

    This is a thin wrapper around `services.logger.logger` so endpoints can
    obtain the same logger via FastAPI's `Depends` mechanism.
    """
    return logger_module.logger

def get_settings() -> dict:
    """Return a small dict of runtime settings used by services.

    Add other runtime configuration here as needed.
    """
    return {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "GEMINI_LLM_MODEL": os.getenv("GEMINI_LLM_MODEL"),
    }

def get_genai_client(settings: dict = Depends(get_settings)) -> Optional[object]:
    """Create and return a Google GenAI client if available.

    Returns None when the client cannot be created (e.g., SDK not installed or
    API key missing). Callers should handle None and fall back to previous
    behaviour if desired.
    """
    api_key = settings.get("GEMINI_API_KEY")
    try:
        # Import inside function so missing dev deps won't break imports
        import google.genai as genai  # type: ignore

        return genai.Client(api_key=api_key)
    except Exception:
        # Return None if client can't be created; callers should handle it.
        return None
