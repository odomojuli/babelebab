"""Canonical sentence splitter.

``split_sentences`` is the single public entry point for turning text into a list
of sentences. It uses pysbd (a pure-Python, offline port of pragmatic_segmenter)
when installed and supporting the language, and falls back to the
zero-dependency regex prototype otherwise. See
``docs/specs/0006-finish-splitter.md``.
"""
from __future__ import annotations

from .naive_regex import split_into_sentences
from .pysbd_segmenter import pysbd_split, pysbd_supports

# ISO 639-3 -> pysbd (ISO 639-1/2) for the languages we carry elsewhere.
_ISO3_TO_PYSBD = {
    "eng": "en", "spa": "es", "fra": "fr", "deu": "de", "ita": "it",
    "rus": "ru", "ara": "ar", "fas": "fa", "hin": "hi", "jpn": "ja",
    "zho": "zh", "urd": "ur", "mar": "mr",
}


def split_sentences(text: str, lang: str = "en") -> list[str]:
    """Split ``text`` into a list of whitespace-stripped sentences.

    Args:
        text: the input text.
        lang: a language code, either ISO 639-1/2 (``"en"``) or ISO 639-3
            (``"eng"``). Selects the pysbd ruleset; ignored by the regex
            fallback, which is English-oriented.
    """
    code = _ISO3_TO_PYSBD.get(lang, lang)
    if pysbd_supports(code):
        result = pysbd_split(text, code)
        if result is not None:
            return result
    return split_into_sentences(text)
