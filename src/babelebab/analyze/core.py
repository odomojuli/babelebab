"""The analyze stage: lexical analysis of text against a frequency lexicon."""
from __future__ import annotations

import statistics
from dataclasses import asdict, dataclass, field
from typing import Any

from ..segmentation import split_sentences
from .lexicon import Lexicon
from .tokenize import tokenize_words


@dataclass(frozen=True)
class TokenInfo:
    text: str
    known: bool
    rank: int | None = None
    zipf: float | None = None
    freq_per_million: float | None = None


@dataclass
class AnalysisResult:
    lang: str
    char_count: int
    sentence_count: int
    token_count: int
    type_count: int
    type_token_ratio: float
    known_count: int
    coverage: dict[str, float]
    mean_zipf: float | None
    median_zipf: float | None
    unknown_words: list[str]
    rare_words: list[str]
    tokens: list[TokenInfo] = field(default_factory=list)
    sentences: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def summary(self) -> str:
        known = self.coverage.get("known", 0.0)
        mz = "n/a" if self.mean_zipf is None else f"{self.mean_zipf:.2f}"
        return (
            f"{self.lang}: {self.token_count} tokens across {self.sentence_count} "
            f"sentence(s); {known:.0%} known, mean Zipf {mz}, "
            f"{len(self.unknown_words)} unknown, {len(self.rare_words)} rare."
        )


def analyze(
    text: str,
    lang: str,
    *,
    lexicon: Lexicon | None = None,
    rare_threshold: float = 3.0,
    top_thresholds: tuple[int, ...] = (100, 1000, 5000),
    include_tokens: bool = True,
) -> AnalysisResult:
    """Analyze ``text`` in ``lang`` against its frequency wordlist.

    Returns per-token frequency annotations plus aggregate coverage and
    difficulty metrics. See ``docs/specs/0002-analyze-lexicon-stage.md``.
    """
    lex = lexicon if lexicon is not None else Lexicon(lang)
    sentences = split_sentences(text) if text.strip() else []
    words = tokenize_words(text)

    tokens: list[TokenInfo] = []
    zipfs: list[float] = []
    unknown_seen: dict[str, None] = {}
    rare_seen: dict[str, None] = {}
    top_hits = {k: 0 for k in top_thresholds}
    known_count = 0

    for word in words:
        stats = lex.lookup(word)
        if stats is None:
            tokens.append(TokenInfo(text=word, known=False))
            unknown_seen.setdefault(word, None)
            continue
        known_count += 1
        zipfs.append(stats.zipf)
        for threshold in top_thresholds:
            if stats.rank <= threshold:
                top_hits[threshold] += 1
        if stats.zipf < rare_threshold:
            rare_seen.setdefault(word, None)
        tokens.append(
            TokenInfo(
                text=word,
                known=True,
                rank=stats.rank,
                zipf=stats.zipf,
                freq_per_million=stats.freq_per_million,
            )
        )

    token_count = len(words)
    type_count = len(set(words))
    coverage: dict[str, float] = {}
    if token_count:
        coverage["known"] = known_count / token_count
        for threshold in top_thresholds:
            coverage[f"top{threshold}"] = top_hits[threshold] / token_count

    return AnalysisResult(
        lang=lang,
        char_count=len(text),
        sentence_count=len(sentences),
        token_count=token_count,
        type_count=type_count,
        type_token_ratio=(type_count / token_count) if token_count else 0.0,
        known_count=known_count,
        coverage=coverage,
        mean_zipf=(statistics.mean(zipfs) if zipfs else None),
        median_zipf=(statistics.median(zipfs) if zipfs else None),
        unknown_words=list(unknown_seen),
        rare_words=list(rare_seen),
        tokens=tokens if include_tokens else [],
        sentences=sentences,
    )
