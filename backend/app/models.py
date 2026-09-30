"""
Shared data contracts for the triage pipeline.

IncidentEntities is the fixed "contract" that the extraction step
(LLM) must fill in, and that the deterministic classifier consumes.
Keeping this as an explicit schema -- rather than a loose dict -- is
what lets the urgency engine stay rule-based and auditable instead of
depending on the LLM's phrasing.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class IncidentType(str, Enum):
    FIRE = "fire"
    MEDICAL = "medical"
    ACCIDENT = "accident"
    ASSAULT = "assault"
    HAZMAT = "hazmat"
    NATURAL_DISASTER = "natural_disaster"
    OTHER = "other"


class InjurySeverity(str, Enum):
    NONE = "none"
    MINOR = "minor"
    SEVERE = "severe"
    UNKNOWN = "unknown"


class UrgencyCategory(str, Enum):
    CATEGORY_1 = "Category 1 - Immediate"
    CATEGORY_2 = "Category 2 - Urgent"
    CATEGORY_3 = "Category 3 - Non-Urgent"


class SourceModality(str, Enum):
    AUDIO_CALL = "audio_call"
    SMS = "sms"
    PHOTO = "photo"


class IncidentEntities(BaseModel):
    """Structured fields the extraction LLM must populate."""

    location: Optional[str] = None
    incident_type: IncidentType = IncidentType.OTHER
    injuries_reported: bool = False
    injury_severity: InjurySeverity = InjurySeverity.UNKNOWN
    unconscious_or_not_breathing: bool = False
    fire_present: bool = False
    hazmat_or_explosion_risk: bool = False
    weapon_involved: bool = False
    number_of_people_affected: Optional[int] = None
    raw_summary: str = ""


class UrgencyResult(BaseModel):
    category: UrgencyCategory
    score: int
    triggered_rules: list[str] = Field(default_factory=list)


class DispatchCard(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:8])
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source: SourceModality
    masked_transcript: str = ""
    photo_caption: Optional[str] = None
    entities: IncidentEntities
    urgency: UrgencyResult
    pii_redactions: list[str] = Field(default_factory=list)


class SmsIn(BaseModel):
    message: str
