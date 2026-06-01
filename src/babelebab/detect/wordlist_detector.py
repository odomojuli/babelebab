"""A zero-dependency language detector built from the project's wordlists.

Classic Cavnar–Trenkle out-of-place rank distance over character n-grams, with
per-language profiles derived from each language's frequency list. See
``docs/specs/0004-language-detection.md``.
"""
from __future__ import annotations

import os
from collections import Counter
from pathlib import Path

from ..analyze.lexicon import Lexicon, default_wordlists_root
from .base import DetectionResult, Detector

_NGRAM_MIN = 1
_NGRAM_MAX = 3
_PROFILE_SIZE = 300


def _ngrams(token: str) -> list[str]:
    padded = f"_{token}_"
    grams: list[str] = []
    for n in range(_NGRAM_MIN, _NGRAM_MAX + 1):
        grams.extend(padded[i : i + n] for i in range(len(padded) - n + 1))
    return grams


def _ranked_profile(counts: Counter[str]) -> dict[str, int]:
    return {gram: rank for rank, (gram, _) in enumerate(counts.most_common(_PROFILE_SIZE))}


class WordlistDetector(Detector):
    def __init__(
        self,
        langs: list[str] | None = None,
        *,
        wordlists_root: str | os.PathLike[str] | None = None,
    ) -> None:
        self._root = Path(wordlists_root) if wordlists_root is not None else default_wordlists_root()
        self._langs = langs
        self._profiles: dict[str, dict[str, int]] = {}

    def languages(self) -> list[str]:
        if self._langs is not None:
            return self._langs
        if not self._root.is_dir():
            return []
        return [
            d.name
            for d in sorted(self._root.iterdir())
            if d.is_dir() and any(d.glob(f"{d.name}_*_top*.csv"))
        ]

    def _profile(self, lang: str) -> dict[str, int]:
        if lang not in self._profiles:
            counts: Counter[str] = Counter()
            for word, stats in Lexicon(lang, wordlists_root=self._root).entries.items():
                weight = int(stats.freq_per_million) + 1
                for gram in _ngrams(word):
                    counts[gram] += weight
            self._profiles[lang] = _ranked_profile(counts)
        return self._profiles[lang]

    def _text_profile(self, text: str) -> dict[str, int]:
        counts: Counter[str] = Counter()
        for token in text.lower().split():
            for gram in _ngrams(token):
                counts[gram] += 1
        return _ranked_profile(counts)

    def detect(self, text: str) -> DetectionResult:
        doc = self._text_profile(text)
        if not doc:
            return DetectionResult(lang=None, confidence=0.0)
        distances: dict[str, float] = {}
        for lang in self.languages():
            profile = self._profile(lang)
            if not profile:
                continue
            total = 0
            for gram, doc_rank in doc.items():
                lang_rank = profile.get(gram)
                total += abs(doc_rank - lang_rank) if lang_rank is not None else _PROFILE_SIZE
            distances[lang] = total / len(doc)
        if not distances:
            return DetectionResult(lang=None, confidence=0.0)
        ranked = sorted(distances.items(), key=lambda kv: kv[1])
        best_lang, best = ranked[0]
        confidence = 1.0
        if len(ranked) > 1:
            second = ranked[1][1]
            confidence = max(0.0, (second - best) / second) if second > 0 else 0.0
        return DetectionResult(
            lang=best_lang,
            confidence=round(confidence, 3),
            scores={lang: round(dist, 2) for lang, dist in distances.items()},
        )
