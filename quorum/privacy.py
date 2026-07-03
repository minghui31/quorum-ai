"""Privacy helpers.

Quorum's policy, enforced in code and stated in the README:
- Case/CV text lives only inside the request; nothing is written to disk.
- No user content is used for training. There is no telemetry.
- `redact()` strips common PII before text is sent to any LLM backend.
"""
from __future__ import annotations

import re

_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[email]"),
    (re.compile(r"\+?\d[\d\s().-]{7,}\d"), "[phone]"),
    (re.compile(r"\b[A-Z]{1,2}\d{7,9}\b"), "[id-number]"),  # passport-like
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[ssn]"),
]


def redact(text: str) -> str:
    """Best-effort PII redaction. Not a substitute for user consent."""
    for pattern, repl in _PATTERNS:
        text = pattern.sub(repl, text)
    return text
