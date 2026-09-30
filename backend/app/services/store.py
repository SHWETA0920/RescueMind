"""
In-memory store for dispatch cards.

This is intentionally simple -- a list behind a lock -- so the whole
project runs with zero external services for a demo. Swap this module
for a real database (Postgres, Redis) without touching any router or
service code; every caller only ever imports `add_card` / `list_cards`.
"""

import threading

from app.models import DispatchCard

_lock = threading.Lock()
_cards: list[DispatchCard] = []


def add_card(card: DispatchCard) -> DispatchCard:
    with _lock:
        _cards.append(card)
    return card


def list_cards() -> list[DispatchCard]:
    with _lock:
        # newest first
        return sorted(_cards, key=lambda c: c.created_at, reverse=True)
