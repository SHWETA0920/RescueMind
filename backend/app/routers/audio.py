import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile

from app.models import DispatchCard, SourceModality
from app.services.pipeline import run_pipeline
from app.services.stt import transcribe

router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.post("", response_model=DispatchCard)
async def ingest_audio(file: UploadFile) -> DispatchCard:
    suffix = Path(file.filename or "audio.wav").suffix or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        transcript = transcribe(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return run_pipeline(SourceModality.AUDIO_CALL, transcript)
