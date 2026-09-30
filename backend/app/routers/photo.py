import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile

from app.models import DispatchCard, SourceModality
from app.services.pipeline import run_pipeline
from app.services.vision import caption_photo

router = APIRouter(prefix="/api/photo", tags=["photo"])


@router.post("", response_model=DispatchCard)
async def ingest_photo(file: UploadFile) -> DispatchCard:
    suffix = Path(file.filename or "photo.jpg").suffix or ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        caption = caption_photo(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    return run_pipeline(SourceModality.PHOTO, raw_text="", photo_caption=caption)
