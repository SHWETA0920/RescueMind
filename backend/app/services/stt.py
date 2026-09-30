"""
Speech-to-text. Uses faster-whisper (CTranslate2-based Whisper) which
installs cleanly on Windows/CPU without extra system dependencies.

In MOCK_MODE, transcription is skipped and a canned emergency-call
transcript is returned instead, so the rest of the pipeline (masking,
extraction, classification, dashboard) can be exercised and demoed
without downloading a model or needing a real audio file.
"""

from app.config import settings

_MODEL = None  # lazy-loaded singleton

_MOCK_TRANSCRIPT = (
    "Please help, this is Sarah Miller calling, my number is 555-234-9981. "
    "There's been a car accident on Elm Street near the gas station, "
    "one person is not breathing and there's smoke coming from the engine."
)


def _get_model():
    global _MODEL
    if _MODEL is None:
        from faster_whisper import WhisperModel  # imported lazily

        _MODEL = WhisperModel(
            settings.WHISPER_MODEL_SIZE,
            device=settings.WHISPER_DEVICE,
            compute_type=settings.WHISPER_COMPUTE_TYPE,
        )
    return _MODEL


def transcribe(audio_path: str) -> str:
    if settings.MOCK_MODE:
        return _MOCK_TRANSCRIPT

    model = _get_model()
    segments, _info = model.transcribe(audio_path, beam_size=5)
    return " ".join(segment.text.strip() for segment in segments)
