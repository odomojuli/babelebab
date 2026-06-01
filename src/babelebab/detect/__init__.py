"""babelebab detect stage — local language identification from wordlists."""
from __future__ import annotations

from .base import DetectionResult, Detector
from .wordlist_detector import WordlistDetector

__all__ = ["detect", "Detector", "DetectionResult", "WordlistDetector"]

_DEFAULT: WordlistDetector | None = None


def detect(text: str) -> DetectionResult:
    """Detect the language of ``text`` using a shared default WordlistDetector."""
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = WordlistDetector()
    return _DEFAULT.detect(text)
