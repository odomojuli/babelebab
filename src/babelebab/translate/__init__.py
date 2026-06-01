"""babelebab translation hub.

A small, engine-agnostic layer for translating text through interchangeable
backends -- local CTranslate2 models, recorded-data replay, or (later) cloud
APIs -- and for comparing engines or picking a consensus translation.

Languages are referred to by ISO 639-3 code (``"eng"``, ``"fra"``, ...).
"""
from __future__ import annotations

from .base import Engine, TranslationResult
from .engines import CTranslate2Engine, IdentityEngine, ReplayEngine
from .hub import best_pick, compare, translate
from .registry import available, get, register, unregister

__all__ = [
    "Engine",
    "TranslationResult",
    "translate",
    "compare",
    "best_pick",
    "register",
    "get",
    "available",
    "unregister",
    "IdentityEngine",
    "ReplayEngine",
    "CTranslate2Engine",
]
