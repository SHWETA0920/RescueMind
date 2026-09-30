from app.models import IncidentEntities, IncidentType, InjurySeverity, UrgencyCategory
from app.services.classifier import classify


def test_unconscious_is_category_1():
    entities = IncidentEntities(unconscious_or_not_breathing=True)
    result = classify(entities)
    assert result.category == UrgencyCategory.CATEGORY_1
    assert "unconscious_or_not_breathing" in result.triggered_rules


def test_fire_present_is_category_1():
    entities = IncidentEntities(fire_present=True)
    result = classify(entities)
    assert result.category == UrgencyCategory.CATEGORY_1


def test_minor_injury_is_category_2():
    entities = IncidentEntities(injuries_reported=True, injury_severity=InjurySeverity.MINOR)
    result = classify(entities)
    assert result.category == UrgencyCategory.CATEGORY_2


def test_accident_with_no_injuries_is_category_2():
    entities = IncidentEntities(incident_type=IncidentType.ACCIDENT, injuries_reported=False)
    result = classify(entities)
    assert result.category == UrgencyCategory.CATEGORY_2


def test_no_indicators_is_category_3():
    entities = IncidentEntities()
    result = classify(entities)
    assert result.category == UrgencyCategory.CATEGORY_3


def test_category_1_wins_even_with_category_2_signals():
    entities = IncidentEntities(
        injuries_reported=True,
        injury_severity=InjurySeverity.MINOR,
        weapon_involved=True,
    )
    result = classify(entities)
    assert result.category == UrgencyCategory.CATEGORY_1
