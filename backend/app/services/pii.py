"""
Safety guardrail: mask PII before any text is sent to a cloud LLM.

Deliberately regex/rule-based so it can be read, tested and reasoned about.
Not a complete PII solution (production should add an NER model such as
Presidio for free-text names). Each masker returns (masked_text, labels) so
callers can log THAT something was redacted without storing the original.
"""

import re

_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("phone_number", re.compile(r"(\+?\d[\d\-\s()]{7,}\d)")),
    ("email", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")),
    ("ssn_or_id", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("credit_card", re.compile(r"\b(?:\d[ -]*?){13,16}\b")),
]

# The lead-in phrase is case-insensitive, but the name itself must be
# Capitalised, so "I'm scared" or "my name is Sarah and" are not over-matched.
_NAME = r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)"
_NAME_PATTERNS = [
    re.compile(r"(?i:\bmy name(?:\s+is|['’]s)|\bthe name is|\bi am|\bi['’]m|\bcall me)\s+" + _NAME),
    re.compile(r"(?i:\bthis is)\s+" + _NAME + r"(?=\s+(?i:calling|speaking|here)\b)"),
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

    # Collect every stated name, then mask ALL later mentions of it too.
    tokens: set[str] = set()
    for pattern in _NAME_PATTERNS:
        for match in pattern.finditer(masked):
            name = match.group(1)
            tokens.add(name)
            tokens.update(name.split())

    if tokens:
        redactions.append("caller_name")
        for token in sorted(tokens, key=len, reverse=True):
            masked = re.sub(rf"\b{re.escape(token)}\b", "[REDACTED_NAME]", masked)

    return masked, redactions