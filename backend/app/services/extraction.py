"""
Extraction step: turn masked transcript/caption text into the fixed
IncidentEntities schema (app/models.py) using a Groq LLM prompted to
return JSON only.

This is the ONLY place an LLM's output feeds the urgency decision --
and it only ever produces structured fields, never the priority
category itself. The classifier (rule-based) makes that call.

In MOCK_MODE, a small keyword matcher stands in for the LLM so the
whole pipeline runs deterministically offline. It is intentionally
crude, but it understands simple negation ("nobody hurt", "no fire").
"""

import json
import re

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

Only set a boolean to true if the text supports it. Phrases like "isn't \
breathing", "stopped breathing", "no pulse" or "unresponsive" DO mean \
unconscious_or_not_breathing is true. Respect negation: "nobody hurt" means \
injuries_reported is false."""

_NEGATIONS = {
    "no", "not", "nobody", "none", "never", "without", "neither", "nor",
    "cannot", "isnt", "arent", "wasnt", "werent", "dont", "doesnt", "didnt",
}
# A negation only applies within its own clause.
_CLAUSE_BREAK = re.compile(r"[.,;:!?\n]|\b(?:but|however|although|though|and|while|yet)\b")

_NOT_BREATHING = re.compile(
    r"\b(?:not|isn't|isnt|aren't|arent|wasn't|wasnt|stopped|no longer|barely|hardly|"
    r"can't|cant|cannot|unable to)\s+(?:be\s+|really\s+)?(?:breathing|breathe)\b"
    r"|\bno pulse\b|\b(?:not|isn't|isnt)\s+responding\b"
)
_NO_INJURY = re.compile(
    r"\bno injuries\b|\b(?:nobody|no one)\b.{0,15}\b(?:hurt|injured)\b"
    r"|\beveryone (?:is |was )?(?:fine|ok|okay|safe)\b"
    r"|\b(?:not|isn't|wasn't|aren't) (?:\w+ )?(?:hurt|injured)\b"
)


def _normalize(text: str) -> str:
    return text.lower().replace("’", "'")


def _has_term(lowered: str, terms: tuple[str, ...]) -> bool:
    """True if any term appears as a whole word and is not negated in its clause."""
    for term in terms:
        for m in re.finditer(rf"\b{re.escape(term)}\b", lowered):
            clause = _CLAUSE_BREAK.split(lowered[: m.start()])[-1]
            recent = re.findall(r"[a-z']+", clause)[-5:]
            if not any(w.replace("'", "") in _NEGATIONS or w.endswith("n't") for w in recent):
                return True
    return False


def _mock_extract(text: str) -> IncidentEntities:
    lowered = _normalize(text)

    incident_type = IncidentType.OTHER
    if _has_term(lowered, ("fire", "smoke", "flames")):
        incident_type = IncidentType.FIRE
    if _has_term(lowered, ("accident", "collision", "crash")):
        incident_type = IncidentType.ACCIDENT
    if _has_term(lowered, ("gun", "knife", "weapon", "weapons", "assault", "attacked")):
        incident_type = IncidentType.ASSAULT
    if _has_term(lowered, ("gas leak", "chemical", "hazmat")):
        incident_type = IncidentType.HAZMAT

    unconscious = bool(_NOT_BREATHING.search(lowered)) or _has_term(
        lowered, ("unconscious", "unresponsive", "passed out")
    )
    injuries = unconscious or _has_term(
        lowered, ("injured", "injury", "injuries", "hurt", "bleeding", "pain", "wounded")
    )

    severity = InjurySeverity.UNKNOWN
    if unconscious:
        severity = InjurySeverity.SEVERE
    elif injuries:
        severe_words = ("severely", "seriously", "badly", "heavily", "critical", "critically", "life-threatening")
        severity = InjurySeverity.SEVERE if _has_term(lowered, severe_words) else InjurySeverity.MINOR
    elif _NO_INJURY.search(lowered):
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
        fire_present=_has_term(lowered, ("fire", "flames")),
        hazmat_or_explosion_risk=_has_term(lowered, ("gas leak", "explosion", "chemical", "hazmat")),
        weapon_involved=_has_term(lowered, ("gun", "knife", "weapon", "weapons")),
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