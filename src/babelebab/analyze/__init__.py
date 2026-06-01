"""babelebab analyze stage — lexical analysis against frequency wordlists."""
from __future__ import annotations

from .core import AnalysisResult, TokenInfo, analyze
from .lemmatize import Lemmatizer, default_lemmatizer, simplemma_available
from .lexicon import Lexicon, WordStats
from .tokenize import tokenize_words

__all__ = [
    "analyze",
    "AnalysisResult",
    "TokenInfo",
    "Lexicon",
    "WordStats",
    "tokenize_words",
    "Lemmatizer",
    "default_lemmatizer",
    "simplemma_available",
]
