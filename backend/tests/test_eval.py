import pytest

from app.models import UrgencyCategory
from app.services.classifier import classify
from app.services.extraction import _mock_extract
from app.services.pii import mask_pii
from app.services.stt import _MOCK_TRANSCRIPT
from app.services.vision import _MOCK_CAPTION

C1, C2, C3 = UrgencyCategory.CATEGORY_1, UrgencyCategory.CATEGORY_2, UrgencyCategory.CATEGORY_3

CASES = [
    ("Fire at the old warehouse on 5th Street", C1),
    ("My dad isn't breathing, please hurry", C1),
    ("He stopped breathing after the fall", C1),
    ("A man with a knife is threatening people near the market", C1),
    ("I'm Rahul Das, my dad isn't breathing, call 9876543210", C1),
    ("Car crash on Elm Street, one person is bleeding", C2),
    ("Car collision on Main Road, nobody hurt", C2),
    ("No fire, but he is bleeding", C2),
    ("Streetlight is out on my road", C3),
    ("Neighbours are playing loud music late at night", C3),
    (_MOCK_TRANSCRIPT, C1),
    (_MOCK_CAPTION, C2),
]


def run_pipeline_steps(text):
    masked, _ = mask_pii(text)
    return classify(_mock_extract(masked)).category


@pytest.mark.parametrize("text,expected", CASES)
def test_expected_category(text, expected):
    assert run_pipeline_steps(text) == expected


def test_life_threatening_reports_are_never_below_category_1():
    for text, expected in CASES:
        if expected == C1:
            assert run_pipeline_steps(text) == C1, text