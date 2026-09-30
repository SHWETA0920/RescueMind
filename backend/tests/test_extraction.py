from app.models import InjurySeverity
from app.services.extraction import _mock_extract
from app.services.pii import mask_pii
from app.services.stt import _MOCK_TRANSCRIPT
from app.services.vision import _MOCK_CAPTION


def test_isnt_breathing_is_flagged():
    e = _mock_extract("My dad isn't breathing")
    assert e.unconscious_or_not_breathing is True
    assert e.injury_severity == InjurySeverity.SEVERE


def test_curly_apostrophe_not_breathing():
    assert _mock_extract("He isn\u2019t breathing").unconscious_or_not_breathing is True


def test_stopped_breathing_and_no_pulse():
    assert _mock_extract("She stopped breathing").unconscious_or_not_breathing is True
    assert _mock_extract("There is no pulse").unconscious_or_not_breathing is True


def test_nobody_hurt_is_not_an_injury():
    e = _mock_extract("Minor fender bender, nobody hurt")
    assert e.injuries_reported is False
    assert e.injury_severity == InjurySeverity.NONE


def test_no_fire_is_not_fire():
    assert _mock_extract("Smoke alarm went off but there is no fire").fire_present is False


def test_negation_does_not_hide_a_later_injury():
    e = _mock_extract("No fire, but he is bleeding")
    assert e.fire_present is False
    assert e.injuries_reported is True


def test_negation_stops_at_and():
    assert _mock_extract("There is no smoke and someone is bleeding").injuries_reported is True


def test_gun_is_whole_word_only():
    assert _mock_extract("The fight has begun").weapon_involved is False


def test_heavy_bleeding_is_severe():
    assert _mock_extract("He is bleeding heavily").injury_severity == InjurySeverity.SEVERE


def test_mock_photo_caption_has_no_fire():
    assert _mock_extract(_MOCK_CAPTION).fire_present is False


def test_mock_call_is_masked_and_flags_not_breathing():
    masked, _ = mask_pii(_MOCK_TRANSCRIPT)
    assert "Sarah" not in masked and "555-234-9981" not in masked
    assert _mock_extract(masked).unconscious_or_not_breathing is True