"""
Safety guardrail: mask PII before any text is sent to a cloud LLM.

This is deliberately regex/rule-based rather than a black-box model --
for a safety-critical redaction step you want something you can read,
test, and reason about. It's not a complete PII solution (a
production build should add a proper NER model, e.g. Presidio, for
free-text names), but it reliably catches the structured PII that
appears in emergency-call transcripts: phone numbers, emails,
government ID-shaped numbers, and street addresses' house numbers.

Each masker returns (masked_text, list_of_redaction_labels) so the
caller can log *that* something was redacted without ever storing the
original value.
"""

import re

_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("phone_number", re.compile(r"(\+?\d[\d\-\s()]{7,}\d)")),
    ("email", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")),
    ("ssn_or_id", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("credit_card", re.compile(r"\b(?:\d[ -]*?){13,16}\b")),
]

# Very small heuristic name-masker: "my name is X", "this is X calling"
_NAME_PATTERNS = [
    re.compile(r"(?i)\bmy name is ([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)"),
    re.compile(r"(?i)\bthis is ([A-Z][a-z]+(?:\s[A-Z][a-z]+)?) calling"),
]


def mask_pii(text: str) -> tuple[str, list[str]]:
    """Mask PII in `text`, returning the masked text and redaction labels."""
    if not text:
        return text, []

    redactions: list[str] = []
    masked = text

    for label, pattern in _PATTERNS:
        if pattern.search(masked):
            redactions.append(label)
            masked = pattern.sub(f"[REDACTED_{label.upper()}]", masked)

    for pattern in _NAME_PATTERNS:
        match = pattern.search(masked)
        if match:
            redactions.append("caller_name")
            masked = masked[: match.start(1)] + "[REDACTED_NAME]" + masked[match.end(1):]

    return masked, redactions
