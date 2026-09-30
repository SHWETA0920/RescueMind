"""
Deterministic urgency scoring engine.

This is intentionally NOT an LLM call. Sorting emergencies has to be
predictable and auditable -- the same entities must always produce
the same category, and a human should be able to see exactly which
rule fired. The extraction LLM's only job is to fill in
IncidentEntities; this module turns that structured data into a
Category 1/2/3 dispatch priority.

Rules are checked in order of severity and the first match for
Category 1 wins; otherwise we fall through to Category 2 checks, then
default to Category 3. `triggered_rules` is returned for every card
so the dashboard can show *why* something was prioritized the way it
was -- this transparency is the main selling point over a pure
LLM-decides-everything pipeline.
"""

from app.models import IncidentEntities, InjurySeverity, UrgencyCategory, UrgencyResult

# (rule_name, predicate, points) -- points are summed for display only;
# category is decided by the highest-severity rule that fired.
_CATEGORY_1_RULES = [
    ("unconscious_or_not_breathing", lambda e: e.unconscious_or_not_breathing, 100),
    ("fire_present", lambda e: e.fire_present, 90),
    ("hazmat_or_explosion_risk", lambda e: e.hazmat_or_explosion_risk, 90),
    ("weapon_involved", lambda e: e.weapon_involved, 85),
    ("severe_injury", lambda e: e.injury_severity == InjurySeverity.SEVERE, 80),
]

_CATEGORY_2_RULES = [
    ("injury_reported", lambda e: e.injuries_reported, 50),
    ("accident_incident", lambda e: e.incident_type.value == "accident", 40),
    ("assault_incident", lambda e: e.incident_type.value == "assault", 45),
    ("multiple_people_affected", lambda e: (e.number_of_people_affected or 0) >= 2, 40),
]


def classify(entities: IncidentEntities) -> UrgencyResult:
    triggered = [name for name, rule, _ in _CATEGORY_1_RULES if rule(entities)]
    if triggered:
        score = max(points for name, rule, points in _CATEGORY_1_RULES if name in triggered)
        return UrgencyResult(
            category=UrgencyCategory.CATEGORY_1,
            score=score,
            triggered_rules=triggered,
        )

    triggered = [name for name, rule, _ in _CATEGORY_2_RULES if rule(entities)]
    if triggered:
        score = max(points for name, rule, points in _CATEGORY_2_RULES if name in triggered)
        return UrgencyResult(
            category=UrgencyCategory.CATEGORY_2,
            score=score,
            triggered_rules=triggered,
        )

    return UrgencyResult(
        category=UrgencyCategory.CATEGORY_3,
        score=10,
        triggered_rules=["no_critical_indicators"],
    )
