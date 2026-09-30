"""
Central configuration for the Incident Triage Copilot backend.

All values are read from environment variables (see .env.example).
The service is designed to run in two modes:

  MOCK_MODE=true   -> no external API calls are made. STT, vision and
                      extraction are simulated with deterministic
                      canned logic so the whole pipeline (and the
                      frontend) can be demoed / tested with no API
                      keys and no internet access.

  MOCK_MODE=false  -> real calls are made to Groq (LLM + vision) and
                      a local faster-whisper model for STT.

This mirrors a pattern that's genuinely useful for hackathon/capstone
demos: judges can run the project instantly in mock mode, then you
flip one flag to show it working against real models.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _bool_env(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


class Settings:
    # --- mode -----------------------------------------------------
    MOCK_MODE: bool = _bool_env("MOCK_MODE", True)

    # --- Groq (LLM extraction + vision) ----------------------------
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
    GROQ_TEXT_MODEL: str = os.getenv("GROQ_TEXT_MODEL", "llama-3.3-70b-versatile")
    GROQ_VISION_MODEL: str = os.getenv("GROQ_VISION_MODEL", "llama-3.2-11b-vision-preview")

    # --- faster-whisper (speech-to-text) ---------------------------
    WHISPER_MODEL_SIZE: str = os.getenv("WHISPER_MODEL_SIZE", "small")
    WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "cpu")
    WHISPER_COMPUTE_TYPE: str = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

    # --- server ------------------------------------------------------
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")


settings = Settings()
