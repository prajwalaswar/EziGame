# voice.py
from pydantic import BaseModel

class VoiceInput(BaseModel):
    audio_file: str

class VoiceOutput(BaseModel):
    text: str
