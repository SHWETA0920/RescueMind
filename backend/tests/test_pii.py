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
