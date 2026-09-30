from fastapi import APIRouter

from app.models import DispatchCard, SmsIn, SourceModality
from app.services.pipeline import run_pipeline

router = APIRouter(prefix="/api/sms", tags=["sms"])


@router.post("", response_model=DispatchCard)
async def ingest_sms(payload: SmsIn) -> DispatchCard:
    return run_pipeline(SourceModality.SMS, payload.message)
