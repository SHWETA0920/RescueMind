"""
Wires the individual services together in the order the architecture
requires: mask PII BEFORE any text reaches an LLM, extract structured
entities, then run the deterministic classifier.
"""

from typing import Optional

from app.models import DispatchCard, SourceModality
from app.services.classifier import classify
from app.services.extraction import extract_entities
from app.services.pii import mask_pii
from app.services.store import add_card


def run_pipeline(
    source: SourceModality,
    raw_text: str,
    photo_caption: Optional[str] = None,
) -> DispatchCard:
    combined_raw = raw_text
    if photo_caption:
        combined_raw = f"{raw_text}\n\nScene photo: {photo_caption}".strip()

    masked_text, redactions = mask_pii(combined_raw)
    entities = extract_entities(masked_text)
    urgency = classify(entities)

    card = DispatchCard(
        source=source,
        masked_transcript=masked_text,
        photo_caption=photo_caption,
        entities=entities,
        urgency=urgency,
        pii_redactions=redactions,
    )
    return add_card(card)
