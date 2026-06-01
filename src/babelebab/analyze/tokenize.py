"""Simple, Unicode-aware word tokenizer for the analyze stage."""
from __future__ import annotations

import re

_WORD_RE = re.compile(r"\w+", re.UNICODE)


def tokenize_words(text: str) -> list[str]:
    """Return lowercased word tokens, dropping purely numeric tokens.

    Whitespace-delimited languages only; non-spaced scripts (zho/jpn/kor) need a
    dedicated tokenizer, which is out of scope for v1.
    """
    return [t.lower() for t in _WORD_RE.findall(text) if not t.isdigit()]
