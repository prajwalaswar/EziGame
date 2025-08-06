# config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Medical Voice App"
    debug: bool = True

settings = Settings()
