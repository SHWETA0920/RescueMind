from fastapi import APIRouter

from app.models import DispatchCard
from app.services.store import list_cards

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/cards", response_model=list[DispatchCard])
async def get_cards() -> list[DispatchCard]:
    return list_cards()
