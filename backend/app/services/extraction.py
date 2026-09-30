"""
Extraction step: turn masked transcript/caption text into the fixed
IncidentEntities schema (app/models.py) using a Groq LLM prompted to
return JSON only.

This is the ONLY place an LLM's output feeds the urgency decision --
and it only ever produces structured fields, never the priority
category itself. The classifier (rule-based) makes that call.

In MOCK_MODE, a small keyword matcher stands in for the LLM so the
whole pipeline runs deterministically offline. It's intentionally
crude -- it exists to exercise the pipeline end-to-end, not to be a
real extractor.
"""

import json

from app.config import settings
from app.models import IncidentEntities, IncidentType, InjurySeverity

_EXTRACTION_SYSTEM_PROMPT = """You are an information extraction system for \
emergency dispatch. Given a masked call transcript and/or a photo caption, \
extract ONLY the following fields as a single JSON object, with no \
markdown fences and no extra commentary:

{
  "location": string or null,
  "incident_type": one of ["fire","medical","accident","assault","hazmat","natural_disaster","other"],
  "injuries_reported": boolean,
  "injury_severity": one of ["none","minor","severe","unknown"],
  "unconscious_or_not_breathing": boolean,
  "fire_present": boolean,
  "hazmat_or_explosion_risk": boolean,
  "weapon_involved": boolean,
  "number_of_people_affected": integer or null,
  "raw_summary": a one-sentence neutral summary
}

Be conservative: only set a boolean to true if the text explicitly supports it."""


def _mock_extract(text: str) -> IncidentEntities:
    lowered = text.lower()

    incident_type = IncidentType.OTHER
    if "fire" in lowered or "smoke" in lowered:
        incident_type = IncidentType.FIRE
    if "accident" in lowered or "collision" in lowered or "crash" in lowered:
        incident_type = IncidentType.ACCIDENT
    if any(w in lowered for w in ("gun", "knife", "weapon", "assault", "attacked")):
        incident_type = IncidentType.ASSAULT
    if any(w in lowered for w in ("gas leak", "chemical", "hazmat")):
        incident_type = IncidentType.HAZMAT

    unconscious = "not breathing" in lowered or "unconscious" in lowered
    injuries = unconscious or any(w in lowered for w in ("injured", "hurt", "bleeding", "pain"))

    severity = InjurySeverity.UNKNOWN
    if unconscious:
        severity = InjurySeverity.SEVERE
    elif injuries:
        severity = InjurySeverity.MINOR
    elif "no injuries" in lowered or "everyone is fine" in lowered:
        severity = InjurySeverity.NONE

    location = None
    for marker in (" on ", " near ", " at "):
        if marker in lowered:
            idx = lowered.index(marker)
            location = text[idx + len(marker): idx + len(marker) + 40].split(",")[0].split(".")[0].strip()
            break

    return IncidentEntities(
        location=location,
        incident_type=incident_type,
        injuries_reported=injuries,
        injury_severity=severity,
        unconscious_or_not_breathing=unconscious,
        fire_present="fire" in lowered or "flames" in lowered,
        hazmat_or_explosion_risk=any(w in lowered for w in ("gas leak", "explosion", "chemical", "hazmat")),
        weapon_involved=any(w in lowered for w in ("gun", "knife", "weapon")),
        number_of_people_affected=None,
        raw_summary=text[:180],
    )


def extract_entities(masked_text: str) -> IncidentEntities:
    if settings.MOCK_MODE or not settings.GROQ_API_KEY:
        return _mock_extract(masked_text)

    from groq import Groq  # imported lazily

    client = Groq(api_key=settings.GROQ_API_KEY)
    response = client.chat.completions.create(
        model=settings.GROQ_TEXT_MODEL,
        messages=[
            {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": masked_text},
        ],
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    payload = json.loads(response.choices[0].message.content)
    return IncidentEntities(**payload)
