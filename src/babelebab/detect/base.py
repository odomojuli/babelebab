"""Core language-detection interfaces."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DetectionResult:
    """Outcome of detecting the language of a piece of text.

    ``lang`` is the best ISO 639-3 guess (``None`` for empty/undetectable input),
    ``confidence`` is a 0–1 margin between the two closest candidates, and
    ``scores`` maps each candidate language to its distance (lower = closer).
    """

    lang: str | None
    confidence: float
    scores: dict[str, float] = field(default_factory=dict)


class Detector(ABC):
    """Base class for language detectors."""

    @abstractmethod
    def detect(self, text: str) -> DetectionResult:
        """Identify the language of ``text``."""
        raise NotImplementedError
