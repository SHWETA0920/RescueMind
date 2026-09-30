from app.services.pii import mask_pii


def test_masks_phone_number():
    text = "Call me back at 555-234-9981 please."
    masked, redactions = mask_pii(text)
    assert "555-234-9981" not in masked
    assert "phone_number" in redactions


def test_masks_email():
    text = "My email is john.doe@example.com"
    masked, redactions = mask_pii(text)
    assert "john.doe@example.com" not in masked
    assert "email" in redactions


def test_masks_stated_name():
    text = "My name is Sarah Miller and I need help."
    masked, redactions = mask_pii(text)
    assert "Sarah Miller" not in masked
    assert "caller_name" in redactions


def test_leaves_clean_text_untouched():
    text = "There is a fire near the old warehouse."
    masked, redactions = mask_pii(text)
    assert masked == text
    assert redactions == []


def test_masks_im_name_and_phone():
    text = "Fire at the old warehouse, my dad isn't breathing. I'm Rahul Das, call 9876543210"
    masked, redactions = mask_pii(text)
    assert "Rahul" not in masked and "Das" not in masked
    assert "9876543210" not in masked
    assert "caller_name" in redactions and "phone_number" in redactions


def test_masks_curly_apostrophe():
    masked, redactions = mask_pii("I\u2019m Rahul Das and there is smoke")
    assert "Rahul" not in masked
    assert "caller_name" in redactions


def test_masks_later_mentions_of_the_name():
    masked, _ = mask_pii("My name is Priya Sen. Priya is at the gate.")
    assert "Priya" not in masked and "Sen" not in masked


def test_name_stops_before_lowercase_words():
    masked, _ = mask_pii("My name is Sarah and I need help")
    assert "and I need help" in masked


def test_im_with_lowercase_word_is_not_a_name():
    text = "I'm scared, there is a fire near the warehouse"
    masked, redactions = mask_pii(text)
    assert masked == text
    assert redactions == []