"""Frequency lexicon loaded from the project's wordlists (``word-lists/``)."""
from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from pathlib import Path


def default_wordlists_root() -> Path:
    env = os.environ.get("BABELEBAB_WORDLISTS_ROOT")
    if env:
        return Path(env)
    # <repo>/src/babelebab/analyze/lexicon.py -> <repo>/word-lists
    return Path(__file__).resolve().parents[3] / "word-lists"


@dataclass(frozen=True)
class WordStats:
    rank: int
    freq_per_million: float
    zipf: float


class Lexicon:
    """Frequency data for one language, read from ``word-lists/<iso3>/``.

    "Known" means the word is in the loaded top-N list, so coverage is relative
    to the list size.
    """

    def __init__(
        self, lang: str, *, wordlists_root: str | os.PathLike[str] | None = None
    ) -> None:
        self.lang = lang
        self._root = (
            Path(wordlists_root) if wordlists_root is not None else default_wordlists_root()
        )
        self._entries: dict[str, WordStats] | None = None

    @property
    def entries(self) -> dict[str, WordStats]:
        if self._entries is None:
            self._entries = self._load()
        return self._entries

    def _csv_path(self) -> Path:
        lang_dir = self._root / self.lang
        candidates = sorted(lang_dir.glob(f"{self.lang}_wordfreq_top*.csv")) or sorted(
            lang_dir.glob(f"{self.lang}_*_top*.csv")
        )
        if not candidates:
            raise FileNotFoundError(f"no wordlist CSV for {self.lang!r} under {lang_dir}")
        return candidates[0]

    def _load(self) -> dict[str, WordStats]:
        entries: dict[str, WordStats] = {}
        with self._csv_path().open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                word = (row.get("word") or "").strip().lower()
                if not word:
                    continue
                try:
                    entries[word] = WordStats(
                        rank=int(row["rank"]),
                        freq_per_million=float(row["freq_per_million"]),
                        zipf=float(row["zipf"]),
                    )
                except (KeyError, ValueError):
                    continue
        return entries

    def lookup(self, word: str) -> WordStats | None:
        return self.entries.get(word.lower())

    def __contains__(self, word: str) -> bool:
        return word.lower() in self.entries

    def __len__(self) -> int:
        return len(self.entries)
