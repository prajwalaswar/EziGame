# health.py
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/")
def root():
    return {
        "message": "Medical Voice Assistant API running",
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }
