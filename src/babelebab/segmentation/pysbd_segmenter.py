"""Adapter for pysbd, a pure-Python offline sentence boundary detector.

pysbd is a port of the Ruby pragmatic_segmenter and is built to pass the
sentence-segmentation "Golden Rules". This adapter is optional: enable it with::

    pip install "babelebab[sbd]"

Every function degrades gracefully when pysbd is missing or errors, so callers
can always fall back to the regex splitter.
"""
from __future__ import annotations

import importlib.util
from functools import lru_cache
from typing import Any

_supported_cache: set[str] | None = None


def pysbd_available() -> bool:
    """True if pysbd can be imported."""
    return importlib.util.find_spec("pysbd") is not None


def _supported() -> set[str]:
    global _supported_cache
    if _supported_cache is None:
        try:
            from pysbd.languages import LANGUAGE_CODES

            _supported_cache = set(LANGUAGE_CODES)
        except ImportError:
            _supported_cache = set()
    return _supported_cache


def pysbd_supports(code: str) -> bool:
    """True if pysbd is installed and handles language ``code``."""
    return code in _supported()


@lru_cache(maxsize=None)
def _segmenter(code: str) -> Any:
    import pysbd

    return pysbd.Segmenter(language=code, clean=False)


def pysbd_split(text: str, code: str) -> list[str] | None:
    """Segment ``text`` with pysbd, or return ``None`` if unavailable/erroring."""
    if not text.strip():
        return []
    try:
        segments = _segmenter(code).segment(text)
    except Exception:
        return None
    return [" ".join(s.split()) for s in segments if s.split()]
