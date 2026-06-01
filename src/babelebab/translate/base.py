"""Core translation interfaces.

An :class:`Engine` turns text in one language into text in another. Concrete
engines (local CTranslate2 models, recorded-data replay, cloud APIs) all
implement the same small surface so the hub can treat them interchangeably.

Languages are referred to by ISO 639-3 code (``"eng"``, ``"fra"``, ...).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TranslationResult:
    """The outcome of translating one piece of text with one engine."""

    text: str
    source: str
    src_lang: str
    tgt_lang: str
    engine: str
    meta: dict[str, Any] = field(default_factory=dict)


class Engine(ABC):
    """Base class for all translation engines.

    Subclasses set :attr:`name` and implement :meth:`translate`.
    """

    name: str = "engine"

    @abstractmethod
    def translate(self, text: str, src_lang: str, tgt_lang: str) -> TranslationResult:
        """Translate ``text`` from ``src_lang`` to ``tgt_lang``."""
        raise NotImplementedError

    def translate_batch(
        self, texts: list[str], src_lang: str, tgt_lang: str
    ) -> list[TranslationResult]:
        """Translate many strings. Override for engines with native batching."""
        return [self.translate(t, src_lang, tgt_lang) for t in texts]
