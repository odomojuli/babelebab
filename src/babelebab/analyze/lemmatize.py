"""Lemmatization for the analyze stage, backed by simplemma (offline).

A no-op (returns the word unchanged) when simplemma is not installed or the
language is unsupported, so it is always safe to call. Enable real lemmatization
with::

    pip install "babelebab[lemmatize]"
"""
from __future__ import annotations

import importlib.util
from typing import Any

# ISO 639-3 -> simplemma (ISO 639-1) for the languages simplemma supports among
# our wordlist set. Anything else falls through to a no-op.
_ISO3_TO_SIMPLEMMA = {
    "eng": "en", "spa": "es", "fra": "fr", "deu": "de", "ita": "it",
    "por": "pt", "rus": "ru", "tur": "tr", "fas": "fa", "hin": "hi",
}


def simplemma_available() -> bool:
    """True if simplemma can be imported."""
    return importlib.util.find_spec("simplemma") is not None


class Lemmatizer:
    """Callable mapping a surface word to its lemma via simplemma.

    Returns the word unchanged for unsupported languages or when simplemma is
    not installed, so callers never need to guard the call.
    """

    def __init__(self) -> None:
        self._fn: Any = None  # lazily resolved simplemma.lemmatize, or False

    def _resolve(self) -> Any:
        if self._fn is None:
            try:
                from simplemma import lemmatize
            except ImportError:
                self._fn = False
            else:
                self._fn = lemmatize
        return self._fn

    def __call__(self, word: str, lang: str) -> str:
        code = _ISO3_TO_SIMPLEMMA.get(lang)
        if code is None:
            return word
        fn = self._resolve()
        if not fn:
            return word
        try:
            return str(fn(word, lang=code))
        except Exception:
            return word


default_lemmatizer = Lemmatizer()
